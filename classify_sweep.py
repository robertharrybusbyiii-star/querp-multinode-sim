#!/usr/bin/env python3
"""
Tag every sweep row with a published-value band (T2, k, per-slot p) and an overall
tier, then write the 'best matches' report and tier plot.

MODEL OUTPUT, NOT MEASURED.  Bands come from TARGETS_AEON.md section 7, which is
PARTLY UNVERIFIED (only Karapatzakis 2024 was read in full; most rows are from
abstracts / search snippets).  Locked values in querp_sim/baseline.py are only read.

Usage:
  /workspace/.venv_f/bin/python classify_sweep.py            # classify + extension + report + plot
  /workspace/.venv_f/bin/python classify_sweep.py --no-extension

Outputs (artifacts/):
  sweep_results_classified.csv              every row of sweep_results.csv + bands + tier
  sweep_results_idle_full_classified.csv    same for the harsher idle=full sensitivity run
  sweep_extension_p_bands_classified.csv    SUPPLEMENTAL grid (see below), raw + full idle
  best_matches.md                           cheapest passing combo per N per tier
  best_matches_tiers.png                    max N per tier

BAND DEFINITIONS (TARGETS_AEON.md sec. 7; boundaries inclusive on the better side)
  T2 :  <= 10 ms published | (10, 100] ms plausible | > 100 ms beyond
        (NOTE: T2 > 1.7 ms is published only at <= 50 mK in a dilution fridge; at 1.7 K
         the best is ~1.7 ms.  The 'published' T2 band follows the brief and is flagged
         by t2_note.)
  k  :  <= 4 published | 5..40 plausible | > 40 beyond   (published k are other platforms)
  p  :  <= 2.5e-4 published | <= 2.5e-3 plausible | above beyond
  tier = worst of the three.

HOW p-EQUIVALENT IS DERIVED FROM THE GAMMA MULTIPLIER
  The sweep has no p axis.  Each slot's rate is  Gamma_slot = gamma_mult * 85 Hz  (85 Hz =
  locked Gamma at gamma_mult = 1, which goes with the locked p_succ = 0.0071).  We assume
  the multiplier is a change of per-attempt success at fixed attempt rate, so

        p_eq = P_SUCC_locked * gamma_mult = 0.0071 * gamma_mult .

  At gamma_mult = 1 this reproduces the locked 0.0071 (beyond published, as stated in
  the brief).  Alternative reading used as a sensitivity column p_eq_strict:
  Gamma_slot / 5 kHz attempt rate = 0.017 * gamma_mult (stricter: locked Gamma already
  carries an undocumented 2.39x over 5000*0.0071).  Both give the same band for every
  gamma_mult >= 0.5, i.e. every row of the ORIGINAL grid has p_eq >= 3.55e-3 > 2.5e-3
  => 'beyond published' on p.  If gamma_mult were instead read as a faster attempt rate
  (published up to ~833 kHz for ions, 180 kHz NV, 1.4 kHz SiV) the p band would not
  apply, but that stacks platforms and is not used.

SUPPLEMENTAL p-EDGE EXTENSION (needed because the original grid is all 'beyond' on p)
  Re-runs the same simulator (sweep.run_sweep, unchanged) with gamma_mult set to the band
  edges p = 2.5e-4 (gamma_mult = 0.03521) and p = 2.5e-3 (gamma_mult = 0.3521), and
  k in {1,2,3,4,5,10,20,40}, to show what the model gives when p and k stay inside the
  published / plausible bands.  Cutoff in {none, 1xT2}; T2 and purify as in the sweep.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from querp_sim.baseline import ATTEMPT_RATE_HZ, GAMMA_HZ, P_SUCC  # read-only
import sweep as sw

ART = os.path.join(HERE, "artifacts")
STAMP = "MODEL OUTPUT, NOT MEASURED"
TIERS = ("published", "plausible", "beyond published")
RANK = {t: i for i, t in enumerate(TIERS)}

P_PUB, P_PLAUS = 2.5e-4, 2.5e-3
T2_PUB_MS, T2_PLAUS_MS = 10.0, 100.0
K_PUB, K_PLAUS = 4, 40
GM_PUB = P_PUB / P_SUCC
GM_PLAUS = P_PLAUS / P_SUCC


def band_t2(t2_ms: float) -> str:
    return TIERS[0] if t2_ms <= T2_PUB_MS else TIERS[1] if t2_ms <= T2_PLAUS_MS else TIERS[2]


def band_k(k: float) -> str:
    return TIERS[0] if k <= K_PUB else TIERS[1] if k <= K_PLAUS else TIERS[2]


def band_p(p: float) -> str:
    return TIERS[0] if p <= P_PUB * (1 + 1e-9) else TIERS[1] if p <= P_PLAUS * (1 + 1e-9) else TIERS[2]


def p_eq(gamma_mult: float) -> float:
    return P_SUCC * gamma_mult


def p_eq_strict(gamma_mult: float) -> float:
    return gamma_mult * GAMMA_HZ / ATTEMPT_RATE_HZ


def classify(r: dict) -> dict:
    t2 = float(r["t2_ms"]); k = int(r["k"]); gm = float(r["gamma_mult"])
    bt, bk, bp = band_t2(t2), band_k(k), band_p(p_eq(gm))
    tier = max((bt, bk, bp), key=RANK.get)
    out = dict(r)
    out.update({
        "p_eq": f"{p_eq(gm):.4g}", "p_eq_strict": f"{p_eq_strict(gm):.4g}",
        "t2_band": bt, "k_band": bk, "p_band": bp, "tier": tier,
        "t2_note": "published only at <=50 mK (1.7 K best ~1.7 ms)" if 1.7 < t2 <= 10 else
                   ("above literature at 1.7 K; locked assumption" if abs(t2 - 3.6) < 1e-9 else ""),
    })
    return out


def as_typed(row: dict) -> dict:
    r = dict(row)
    for c in ("k", "n_nodes", "useful"):
        r[c] = int(r[c])
    for c in ("gamma_mult", "gamma_slot_hz", "gamma_eff_hz", "t2_ms", "gamma_eff_t2", "rate_hz", "fidelity"):
        r[c] = float(r[c])
    if r["cutoff_t2_mult"] != "none":
        r["cutoff_t2_mult"] = float(r["cutoff_t2_mult"])
    return r


CLS_COLS = sw.COLUMNS + ["p_eq", "p_eq_strict", "t2_band", "k_band", "p_band", "tier", "t2_note"]


def write_classified(rows: list[dict], path: str, extra: list[str] = ()) -> None:
    cols = list(extra) + CLS_COLS
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            o = dict(r)
            o["rate_hz"] = f"{r['rate_hz']:.6g}"
            o["fidelity"] = f"{r['fidelity']:.6f}"
            o["gamma_eff_t2"] = f"{r['gamma_eff_t2']:.6g}"
            o["gamma_eff_hz"] = f"{r['gamma_eff_hz']:.6g}"
            if r.get("pairs_per_e2e", "") != "":
                o["pairs_per_e2e"] = f"{float(r['pairs_per_e2e']):.6g}"
            w.writerow(o)


def load_grid(path: str) -> list[dict]:
    with open(path) as fh:
        return [classify(as_typed(r)) for r in csv.DictReader(fh)]


def run_extension(idle_mode: str) -> list[dict]:
    rows = sw.run_sweep(ks=(1, 2, 3, 4, 5, 10, 20, 40), gmults=(GM_PUB, GM_PLAUS),
                        cutoffs=(None, 1.0), idle_mode=idle_mode)
    out = []
    for r in rows:
        r = dict(r); r["run_idle_mode"] = idle_mode
        out.append(classify(r))
    return out


# ----------------------------------------------------------------------------
def cost(r: dict) -> tuple:
    """Same ordering as sweep.cheapness: smallest k, shortest T2, smallest gamma_mult,
    purify off<link<swap<both, no-cutoff before cutoff, higher rate."""
    return sw.cheapness(r)


def cheapest(rows, n, tier, exact=True):
    c = [r for r in rows if r["n_nodes"] == n and r["useful"]
         and ((r["tier"] == tier) if exact else RANK[r["tier"]] <= RANK[tier])]
    c.sort(key=cost)
    return (c[0] if c else None), len(c)


def max_n(rows, tier_max: str) -> int:
    return max((r["n_nodes"] for r in rows if r["useful"] and RANK[r["tier"]] <= RANK[tier_max]), default=0)


def _cut(c):
    return "none" if c == "none" else f"{c:g}×T2"


def row_line(r) -> str:
    return (f"k={r['k']}, T2={r['t2_ms']:g} ms, p_eq={float(r['p_eq']):.3g} (Γmult={r['gamma_mult']:.4g}), "
            f"Γ_eff={r['gamma_eff_hz']:.4g} Hz (Γ_eff·T2={r['gamma_eff_t2']:.3g}), purify={r['purify']}, "
            f"cutoff={_cut(r['cutoff_t2_mult'])}; **F={r['fidelity']:.4f}, R={r['rate_hz']:.4g} Hz**")


def load_required(path: str) -> list[dict]:
    out = []
    with open(path) as fh:
        for r in csv.DictReader(fh):
            if r["gamma_eff_hz"] == "":
                continue
            out.append({**r, "n_nodes": int(r["n_nodes"]), "t2_ms": float(r["t2_ms"]),
                        "gamma_eff_hz": float(r["gamma_eff_hz"]), "k_equiv": float(r["k_equiv_at_85hz"]),
                        "gamma_eff_t2": float(r["gamma_eff_t2"]), "rate_hz": float(r["rate_hz"]),
                        "fidelity": float(r["fidelity"])})
    return out


def best_required(req, n, idle_mode):
    c = [r for r in req if r["n_nodes"] == n and r["idle_mode"] == idle_mode and band_t2(r["t2_ms"]) != TIERS[2]]
    return min(c, key=lambda r: r["gamma_eff_hz"]) if c else None


# ----------------------------------------------------------------------------
def bench_list(n: int, achieved: dict, req_row) -> list[str]:
    """What must be demonstrated on a bench for the model to pass at N (generated from the picks)."""
    L = []
    if n == 3:
        r = achieved["plausible"]
        rb = achieved["beyond published"]
        if r is not None:
            L += [f"- **T2:** electron-spin DD T2 of {r['t2_ms']:g} ms is in the *plausible* band (published best 10 ms at 50 mK, "
                  "Karapatzakis 2024, T2∝N^0.95 not yet saturated); needs more π pulses / pulse-error control and a dilution-fridge-class setup. "
                  "Not shown at 1.7 K (best ~1.7 ms).",
                  f"- **p (per-attempt remote success):** needs p ≈ {float(r['p_eq']):.2g} per slot, i.e. 10× the best published remote value "
                  "(2.5×10⁻⁴); no SnV spin-photon entanglement has been demonstrated at all yet.",
                  f"- **k:** k = {r['k']} link slots per node (published color-center hardware: k ≤ 4 Purcell channels, no remote-entanglement multiplexing). "
                  "Needs ≥ 2k memory slots, tuning, crosstalk control (none modeled).",
                  f"- **Purification ({r['purify']}):** BBPSSW with ideal local gates; link-level rows ignore storage decay while waiting for the partner copy, so this "
                  "row is the most optimistic. Needs heralded high-fidelity two-qubit gates on the node.",
                  "- **Memory:** no nuclear memory used (do not add one on top without a demo of that combination on the same SnV node)."]
        L += ["- **Published-only (all three inside published bands) does not pass N = 3** in this model (best published-band Γ_eff ≈ 12 Hz vs ≳ 3×10² Hz (link-only purification, T2 = 100 ms) to ≳ 2×10³ Hz (swap-level, T2 ≤ 10 ms) needed).",
              "- **Robustness:** the plausible-tier N = 3 pass exists only with a link-level purification stage (`link`, or `both`, which includes it; the most optimistic mode) and only under idle=raw; no swap-only plausible-tier pass exists (max Γ_eff = 40·0.352·85 ≈ 1.2×10³ Hz < ≈ 1.36×10³ Hz needed), and nothing in the plausible tier passes under idle=full."]
    elif n == 5:
        r = achieved["beyond published"]
        L += [f"- **p:** the grid passes only with p_eq ≈ {float(r['p_eq']):.2g} per slot (≈ {float(r['p_eq'])/P_PUB:.0f}× the published 2.5×10⁻⁴) **and** k = {r['k']} (> 40 → beyond).",
              f"- **k:** k = {r['k']} parallel slots per node — beyond anything shown on color centers.",
              f"- **T2:** {r['t2_ms']:g} ms ({band_t2(r['t2_ms'])}; > 1.7 ms is published only at ≤ 50 mK, not at 1.7 K).",
              "- **Purification:** needs swap-level (nested) BBPSSW at every level (`both`/`swap`), ~hundreds of raw pairs per end-to-end pair; needs ideal local gates and fast classical feed-forward.",
              "- **Memory:** model uses an electron-spin memory only; a nuclear memory would relax the T2 demand but is a different platform and unstacked here.",
              "- **Within plausible bands (k ≤ 40, p ≤ 2.5×10⁻³, T2 ≤ 100 ms): no passing combination**, even N = 5 at T2 = 100 ms (max Γ_eff = 40·0.352·85 ≈ 1.2×10³ Hz vs ≈ 1.5×10⁴ Hz needed)."]
    else:
        r = req_row
        if r is not None:
            kneed40 = r["gamma_eff_hz"] / (40 * GAMMA_HZ)
            kneed4 = r["gamma_eff_hz"] / (4 * GAMMA_HZ)
            L += [f"- **Not in the sweep grid.** Model extrapolation (idle=raw, best T2 ≤ 100 ms) needs Γ_eff ≈ {r['gamma_eff_hz']:.3g} Hz "
                  f"(k_equiv ≈ {r['k_equiv']:.3g} at the locked 85 Hz/slot; T2={r['t2_ms']:g} ms, {r['purify']}, cutoff {r['cutoff_t2_mult']}).",
                  f"- **p / k trade:** at the plausible-max k = 40 each slot would need Γmult ≈ {kneed40:.3g}, i.e. p_eq ≈ {P_SUCC*kneed40:.3g}"
                  + (" (> 1: impossible)" if P_SUCC * kneed40 > 1 else "") + f"; at k = 4, Γmult ≈ {kneed4:.3g}, p_eq ≈ {P_SUCC*kneed4:.3g}"
                  + (" (> 1: impossible)" if P_SUCC * kneed4 > 1 else "") + ".",
                  "- Reaching it requires k, p **and** a new memory class all beyond published at once, plus losses/power/crosstalk that are not modeled. "
                  "Memory must beat published electron-spin values or move to a nuclear memory (1.35 s ¹³C at 50 mK for SnV; different platform, no demonstrated combination with multiplexing).",
                  "- Treat as 'needs a different architecture' (e.g. very high-rate sources, multi-mode memories, higher-fidelity swaps), not as a bench target."]
    return L


def bench_plans_note() -> list[str]:
    return [
        "Bench plans in this workspace and their relevance:",
        "- `/workspace/trinity_test_plan/` (Trinity Lock vs No-Lock): **relevant only to the 'Trinity' T2 ×2.4 / success ×1.18 assumptions** that are baked into "
        "the locked baseline. It tests phase lock on classical oscillators (metronomes / Arduino+555); it does **not** measure SnV⁻ T2, per-attempt p, or multiplexing. "
        "A positive result there would not validate any row of this report.",
        "- `/workspace/ppm_test_plan/` (proton precession magnetometer) and `/workspace/nv_test_plan/` (NV Zeeman spectroscopy): **not relevant** to the tier "
        "requirements here. The NV plan is the nearest diamond-colour-centre hands-on skill-builder (ODMR/Zeeman), but it measures neither SnV⁻ coherence nor remote entanglement.",
        "- Closing any N ≥ 3 gap needs a cryogenic SnV⁻ (or similar) lab setup (≤ 1.7 K, ideally ≤ 50 mK), a cavity/waveguide spin-photon interface and a second node; "
        "none of the bench plans here is a substitute.",
    ]


# ----------------------------------------------------------------------------
def all_pub_rows(rows):
    return rows


def make_plot(raw_rows, full_rows, req_raw, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    ncls = {m: [max_n(rows, t) for t in TIERS] for m, rows in (("raw", raw_rows), ("full", full_rows))}
    # published band = tier published only; cumulative so plausible >= published, beyond >= plausible
    x = np.arange(3); w = 0.38
    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    b1 = ax.bar(x - w / 2, ncls["raw"], w, label="idle=raw (default)", color="tab:blue")
    b2 = ax.bar(x + w / 2, ncls["full"], w, label="idle=full (harsher)", color="tab:orange")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.2, f"N={int(b.get_height())}", ha="center", fontsize=9)
    ex = {n: best_required(req_raw, n, "raw") for n in (9, 17)}
    for n, r in ex.items():
        if r is not None:
            ax.hlines(n, 1.6, 2.4, colors="tab:red", linestyles="dashed")
            ax.text(2.42, n, f"N={n}: model extrapolation only,\nneeds Γ_eff≈{r['gamma_eff_hz']:.2g} Hz (not in grid)", fontsize=7.5, va="center", color="tab:red")
    ax.set_xticks(x, ["published\n(T2≤10 ms, k≤4, p≤2.5e-4)", "plausible\n(≤100 ms, k≤40, p≤2.5e-3)", "beyond published\n(anything in grid)"], fontsize=8.5)
    ax.set_ylabel("max chain length N with F≥0.88 and R≥1 Hz")
    ax.set_ylim(0, 19); ax.set_xlim(-0.6, 3.6)
    ax.grid(axis="y", alpha=0.3); ax.legend(loc="upper left", fontsize=8)
    ax.set_title(f"Max N achievable per published-value tier (cumulative)\n{STAMP}", fontsize=11)
    fig.text(0.5, 0.01, "Purified rows optimistic; no loss/power/crosstalk modeled; AEON bands partly unverified. "
             "Includes supplemental p-edge runs.", ha="center", fontsize=7.5)
    fig.text(0.5, 0.5, STAMP, ha="center", va="center", fontsize=30, color="gray", alpha=0.12, rotation=25)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=140); plt.close(fig)
    return ncls


# ----------------------------------------------------------------------------
def write_report(raw_rows, full_rows, req_raw, req_full, ncls, path, have_ext):
    L = [f"# Best matches — published-value tiers vs. the multiplexing sweep — {STAMP}", "",
         "> **STALE BANDS NOTICE (2026-10-16):** this file uses the OLD published-value bands (p <= 2.5e-4 'published', 2.5e-4-2.5e-3 'plausible', k <= 4 'published'). "
         "AEON's full-text check (`TARGETS_AEON_verified.md` s.6) moved those edges. See `artifacts/best_matches_REVISED.md` (`classify_sweep.py --revised`).", "",
         "> **MODEL OUTPUT, NOT MEASURED.** Tiers compare the sweep's parameters with the published-value bands of "
         "`TARGETS_AEON.md` §7. They say what inputs the *model* needs; they do not claim any hardware can pass.", "",
         "## Caveats (read first)", "",
         "- **Purified rows are optimistic.** Link-level purification charges no storage decay while a copy waits for its partner; swap-level rows are more robust. "
         "BBPSSW with ideal local gates, ideal swap (p_swap=1, η_swap=1), Werner-state links, F_link=0.887 taken as given.",
         "- **No fiber/distance loss, no power or cryostat load, no slot crosstalk, no memory-slot cost of k** are modeled. Success needs ≥ 2k memory slots per node.",
         "- **AEON's bands are partly unverified.** Only Karapatzakis 2024 (arXiv:2403.00521) was read in full; most other rows are abstract/snippet ('ABS') or "
         "search-summary ('SUM') values. The 'published' k band (≤ 4) comes from other platforms (ion-photon), and 'published' T2 up to 10 ms holds only at 50 mK.",
         "- **The p-equivalent is a modelling choice** (p_eq = 0.0071 × Γmult; see `classify_sweep.py` docstring). Because Γmult ≥ 0.5 in the original grid, "
         "**every original grid row is 'beyond published' on p**. To show anything below that tier, a SUPPLEMENTAL grid at the p-band edges "
         "(Γmult = 0.0352 → p = 2.5e-4; 0.352 → p = 2.5e-3) was run with the same simulator; its rows are tagged `source=extension`.",
         "- **No nuclear-memory or other-platform numbers are stacked** on an SnV node (different platforms; no demonstration of the combination).",
         "- The locked baseline (T2 = 3.6 ms, p = 0.0071, Γ = 85 Hz) is itself *beyond published* on p and above literature at 1.7 K on T2.", "",
         "## Tier definitions", "",
         "| Parameter | published | plausible | beyond published |", "|---|---|---|---|",
         "| T2 | ≤ 10 ms (≤ 1.7 ms at 1.7 K; > 1.7 ms needs ≤ 50 mK) | 10–100 ms | > 100 ms |",
         "| p per slot (p_eq) | ≤ 2.5×10⁻⁴ | ≤ 2.5×10⁻³ | > 2.5×10⁻³ (locked 0.0071 is here) |",
         "| k slots | ≤ 4 | 5–40 | > 40 |",
         "| overall tier | all three published | worst band plausible | any band beyond |", "",
         f"Cost ordering for 'cheapest': smallest k, then shortest T2, then smallest Γmult, then purification off < link < swap < both, then no cutoff. "
         f"Main tables use idle=`raw`; idle=`full` is shown as a sensitivity. Thresholds: F ≥ 0.88 and R ≥ 1 Hz.", ""]

    r2, c2 = cheapest(all_pub_rows(raw_rows), 2, TIERS[0])
    L += ["## N = 2 (reference)", "",
          "Published tier **passes** at N = 2 (no swap, no purification needed; F = F_link = 0.887 taken as given): "
          + (row_line(r2) if r2 else "none") + ". Note F_link = 0.887 and Γ ≥ 1 Hz at p = 2.5e-4 are model inputs, not banded; published solid-state remote links "
          "reached F ≈ 0.86 (SiV, ~1 Hz) / 0.81 (NV, 6 Hz).", ""]
    achieved_by_n = {}
    for n in (3, 5, 9, 17):
        L += [f"## N = {n}", "", "| tier | passing? | cheapest combination (idle=raw) | note |", "|---|---|---|---|"]
        picks = {}
        for tier in TIERS:
            r, cnt = cheapest(raw_rows, n, tier)
            picks[tier] = r
            if r is None:
                if n >= 9 and tier == TIERS[2]:
                    rr = best_required(req_raw, n, "raw")
                    L.append(f"| {tier} | **no passing grid combination** | extrapolation only: Γ_eff ≈ {rr['gamma_eff_hz']:.3g} Hz (k_equiv ≈ {rr['k_equiv']:.3g}), "
                             f"T2={rr['t2_ms']:g} ms, {rr['purify']}, cutoff {rr['cutoff_t2_mult']}; F={rr['fidelity']:.3f}, R={rr['rate_hz']:.3g} Hz | "
                             f"needs k_equiv ≫ 40 at the locked p, so it is beyond published on k (and p if Γmult is raised instead). Not a grid result. |")
                else:
                    L.append(f"| {tier} | **none — no passing combination** | — | {'inside this tier’s bands, no configuration reaches F≥0.88 & R≥1 Hz at N=%d' % n} |")
            else:
                note = {"published": "all three parameters inside published bands.",
                        "plausible": "at least one parameter in the plausible band (none beyond).",
                        "beyond published": "worst band: " + ", ".join(f"{nm}={b}" for nm, b in
                                           (("T2", r['t2_band']), ("k", r['k_band']), ("p", r['p_band'])) if b == TIERS[2]) + "."}[tier]
                if r["purify"] == "link":
                    note += " Link-only purification: most optimistic (no storage decay while waiting for partner copy)."
                if r["source"] == "extension":
                    note += " From the supplemental p-edge grid."
                L.append(f"| {tier} | yes ({cnt} rows) | {row_line(r)} | {note} |")
        # idle=full sensitivity
        fl = []
        for tier in TIERS:
            r, cnt = cheapest(full_rows, n, tier)
            fl.append(f"{tier}: " + ("none" if r is None else
                      f"k={r['k']}, T2={r['t2_ms']:g} ms, p_eq={float(r['p_eq']):.3g}, purify={r['purify']}, F={r['fidelity']:.3f}, R={r['rate_hz']:.3g} Hz"))
        L += ["", "Sensitivity, idle=`full`: " + "; ".join(fl) + ".", ""]
        achieved_by_n[n] = picks
        # best tier achievable
        best_t = next((t for t in TIERS if picks[t] is not None), None)
        if best_t is None and n >= 9:
            best_t = "beyond published (extrapolation only, not in grid)"
        L += [f"**Best tier achievable at N={n}: {best_t if best_t else 'none'}.**", "",
              f"What would need to be shown on a bench for N={n}:", ""]
        L += bench_list(n, picks, best_required(req_raw, n, "raw")) + [""]

    L += ["## Summary — max N per tier (cumulative; idle=raw | idle=full)", "",
          "| tier | max N (raw) | max N (full) |", "|---|---|---|"]
    for i, t in enumerate(TIERS):
        L.append(f"| {t} | {ncls['raw'][i]} | {ncls['full'][i]} |")
    L += ["", "N = 9 and 17 pass nowhere in the grids; they appear only in the beyond-grid extrapolation "
          "(`sweep_required_gamma.md`), which is beyond published on every axis.", ""]
    L += ["## Bench plans", ""] + bench_plans_note() + [""]
    L += ["## Files", "",
          "- `classify_sweep.py` (this report's generator); `artifacts/sweep_results_classified.csv`, `sweep_results_idle_full_classified.csv`, "
          "`sweep_extension_p_bands_classified.csv`; `artifacts/best_matches_tiers.png`.", ""]
    with open(path, "w") as fh:
        fh.write("\n".join(L) + "\n")


# ----------------------------------------------------------------------------
# REVISED BANDS (added 2026-10-16) -- based on TARGETS_AEON_verified.md section 6.
# Original bands above are left untouched; the default run still reproduces best_matches.md.
#   p : published <= 3e-5 (F ~0.8 links: Knaut ~1e-5, Humphreys derived ~3e-5; the ONLY published
#        p for a F>=0.8 link); plausible (3e-5, 2.5e-4] (published only at F ~0.56-0.60);
#        beyond > 2.5e-4  (old 'plausible' 2.5e-4..2.5e-3 is now beyond published).
#   k : published k=1 (no published multimode memory-memory demo at F>=0.8); plausible 2..40
#        (k<=4 demonstrated only at low fidelity, Liu ~4 modes); beyond > 40.
#   T2: unchanged (<=10 ms at 50 mK, <=1.7 ms at 1.7 K; 10-100 ms plausible; >100 ms beyond).
# The p_eq = 0.0071*gamma_mult mapping is the same modelling choice as before.
REV_TAG = "REVISED BANDS (TARGETS_AEON_verified.md s.6)"


def use_revised_bands() -> None:
    global P_PUB, P_PLAUS, K_PUB, K_PLAUS, GM_PUB, GM_PLAUS
    P_PUB, P_PLAUS, K_PUB, K_PLAUS = 3e-5, 2.5e-4, 1, 40
    GM_PUB, GM_PLAUS = P_PUB / P_SUCC, P_PLAUS / P_SUCC


def write_revised_report(raw_rows, full_rows, path) -> dict:
    L = [f"# Best matches under REVISED bands — {STAMP}", "",
         "> **MODEL OUTPUT, NOT MEASURED.** Same simulator and same sweep as `best_matches.md`; only the published-value band edges "
         "changed, following `TARGETS_AEON_verified.md` section 6 (AEON's full-text check). The earlier `best_matches.md` used the OLD bands and is stale on p and k.", "",
         "## Revised band edges (changes marked)", "",
         "| Parameter | published | plausible | beyond published |", "|---|---|---|---|",
         "| T2 (unchanged) | ≤ 10 ms (only at ≤ 50 mK; ≤ 1.7 ms at 1.7 K) | 10–100 ms | > 100 ms |",
         "| p per slot (**CHANGED**) | ≤ 3×10⁻⁵ (the only published p with F ≈ 0.8) | 3×10⁻⁵ – 2.5×10⁻⁴ (published only at F ≈ 0.56–0.60) | > 2.5×10⁻⁴ |",
         "| k slots (**CHANGED**) | 1 (no published multimode memory–memory demo at F ≥ 0.8) | 2–40 (k ≈ 4 shown only at low fidelity) | > 40 |", "",
         "Thresholds F ≥ 0.88, R ≥ 1 Hz. Cost ordering as in `best_matches.md`. Main rows idle=`raw`; idle=`full` shown as sensitivity. "
         "Caveats from `best_matches.md` all still apply (optimistic link purification, no loss/power/crosstalk, p_eq is a modelling choice, no nuclear-memory stacking).", ""]
    summary = {}
    for n in (2, 3, 5, 9, 17):
        L += [f"## N = {n}", "", "| tier | passing? | cheapest combination (idle=raw) |", "|---|---|---|"]
        for tier in TIERS:
            r, cnt = cheapest(raw_rows, n, tier)
            L.append(f"| {tier} | " + (f"yes ({cnt} rows) | {row_line(r)}" + (" — link-only purification, most optimistic" if r['purify'] == 'link' else "") + " |"
                                       if r else "**none** | — |"))
        fl = []
        for tier in TIERS:
            r, cnt = cheapest(full_rows, n, tier)
            fl.append(f"{tier}: " + ("none" if r is None else f"k={r['k']}, T2={r['t2_ms']:g} ms, p_eq={float(r['p_eq']):.3g}, purify={r['purify']}, F={r['fidelity']:.3f}, R={r['rate_hz']:.3g} Hz"))
        L += ["", "Sensitivity idle=`full`: " + "; ".join(fl) + ".", ""]
    L += ["## Summary — max N per tier (cumulative; idle=raw | idle=full)", "", "| tier | max N (raw) | max N (full) |", "|---|---|---|"]
    for t in TIERS:
        summary[t] = (max_n(raw_rows, t), max_n(full_rows, t))
        L.append(f"| {t} | {summary[t][0]} | {summary[t][1]} |")
    L += ["", "N = 9 and 17 do not pass in any grid (see `sweep_required_gamma.md`); that conclusion does not depend on the band edges.", ""]
    open(path, "w").write("\n".join(L) + "\n")
    return summary


def main_revised() -> int:
    use_revised_bands()
    raw = load_grid(os.path.join(ART, "sweep_results.csv"))
    full = load_grid(os.path.join(ART, "sweep_results_idle_full.csv"))
    for r in raw + full:
        r["source"] = "grid"
    ext_raw, ext_full = run_extension("raw"), run_extension("full")
    for r in ext_raw + ext_full:
        r["source"] = "extension"
    write_classified(ext_raw + ext_full, os.path.join(ART, "sweep_extension_p_bands_REVISED_classified.csv"),
                     extra=["source", "run_idle_mode"])
    s = write_revised_report(raw + ext_raw, full + ext_full, os.path.join(ART, "best_matches_REVISED.md"))
    print(STAMP, REV_TAG); print("max N per tier (raw, full):", s)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-extension", action="store_true", help="skip the supplemental p-edge runs")
    ap.add_argument("--revised", action="store_true", help="use REVISED bands from TARGETS_AEON_verified.md; writes best_matches_REVISED.md only")
    a = ap.parse_args(argv)
    if a.revised:
        return main_revised()

    raw = load_grid(os.path.join(ART, "sweep_results.csv"))
    full = load_grid(os.path.join(ART, "sweep_results_idle_full.csv"))
    for r in raw + full:
        r["source"] = "grid"
    write_classified(raw, os.path.join(ART, "sweep_results_classified.csv"), extra=["source"])
    write_classified(full, os.path.join(ART, "sweep_results_idle_full_classified.csv"), extra=["source"])

    ext_raw, ext_full = [], []
    if not a.no_extension:
        ext_raw, ext_full = run_extension("raw"), run_extension("full")
        for r in ext_raw + ext_full:
            r["source"] = "extension"
        write_classified(ext_raw + ext_full, os.path.join(ART, "sweep_extension_p_bands_classified.csv"),
                         extra=["source", "run_idle_mode"])
    all_raw, all_full = raw + ext_raw, full + ext_full

    req_raw = load_required(os.path.join(ART, "sweep_required_gamma.csv"))
    req_full = req_raw
    ncls = make_plot(all_raw, all_full, req_raw, os.path.join(ART, "best_matches_tiers.png"))
    write_report(all_raw, all_full, req_raw, req_full, ncls, os.path.join(ART, "best_matches.md"), not a.no_extension)

    from collections import Counter
    print(STAMP)
    print("original grid tiers:", dict(Counter(r["tier"] for r in raw)))
    print("max N per tier (raw, full):", ncls)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
