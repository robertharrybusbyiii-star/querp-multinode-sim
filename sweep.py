#!/usr/bin/env python3
"""
Multiplexing / T2 / cutoff / purification sweep for the QuERP repeater chain.

MODEL OUTPUT, NOT MEASURED. Every combination below is a hypothetical scenario
on top of the locked v0.3b link (F_link=0.887, per-slot Γ=85 Hz); only k=1,
gamma_mult=1, T2=3.6 ms, no cutoff, no purification is the locked point.

Usage:
  /workspace/.venv_f/bin/python sweep.py                    # idle-mode raw (default)
  /workspace/.venv_f/bin/python sweep.py --idle-mode full   # harsher sensitivity run
  /workspace/.venv_f/bin/python sweep.py --quick            # tiny grid, for smoke tests
"""

from __future__ import annotations

import argparse
import csv
import itertools
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from querp_sim.baseline import USEFUL_F, USEFUL_RATE_HZ, locked_v03b
from querp_sim.multiplexing import multiplexed_params
from querp_sim.repeater import PurifyConfig, simulate_chain

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "artifacts")
STAMP = "MODEL OUTPUT, NOT MEASURED"

K_VALUES = (1, 2, 5, 10, 20, 50, 100)
# (T2 seconds, label)
T2_VALUES = (
    (0.17e-3, "LITERATURE (SnV- Hahn echo, Rosenthal PRX 13 031022)"),
    (1.8e-3, "LITERATURE (SnV- XY8+256 pulses, Beukers 2024)"),
    (3.6e-3, "LOCKED ASSUMPTION (v0.3b; exceeds literature)"),
    (10e-3, "HYPOTHETICAL"),
    (100e-3, "HYPOTHETICAL"),
)
T2_LABEL = {t: lab for t, lab in T2_VALUES}
GAMMA_MULTS = (0.5, 1.0, 2.0, 4.0)
CUTOFFS = (None, 0.5, 1.0, 2.0)  # multiples of T2; None = no cutoff
PURIFY_MODES = ("off", "link", "swap", "both")  # off | BBPSSW on links | after swaps only | links + after swaps
N_RANGE = tuple(range(2, 18))
TARGET_NS = (3, 5, 9, 17)
PURIFY_TARGET = 0.95
# TPP overlays for the sweep: lock gain is neutral (1.0) because a phase lock cannot
# raise a herald probability; residual 0.01 per round is the existing TUNED default.
LOCK_GAIN = 1.0

COLUMNS = [
    "k", "gamma_mult", "gamma_slot_hz", "gamma_eff_hz", "t2_ms", "t2_label",
    "gamma_eff_t2", "cutoff_t2_mult", "purify", "idle_mode", "n_nodes",
    "protocol", "rate_hz", "fidelity", "pairs_per_e2e", "useful",
]


def purify_config(mode: str, idle_mode: str, lock_gain: float = LOCK_GAIN) -> PurifyConfig | None:
    if mode == "off":
        return None
    if mode not in ("link", "swap", "both"):
        raise ValueError(mode)
    return PurifyConfig(
        enabled=True, f_target=PURIFY_TARGET, when=mode,
        trinity_lock_gain=lock_gain, idle_mode=idle_mode,
    )


def run_sweep(
    ks=K_VALUES, t2s=T2_VALUES, gmults=GAMMA_MULTS, cutoffs=CUTOFFS,
    purify_modes=PURIFY_MODES, n_range=N_RANGE, idle_mode: str = "raw",
    lock_gain: float = LOCK_GAIN,
) -> list[dict]:
    base = locked_v03b()
    rows: list[dict] = []
    for k, (t2, t2_label), gm, cut, pm in itertools.product(ks, t2s, gmults, cutoffs, purify_modes):
        p = multiplexed_params(base, k, gm, t2_s=t2)
        cfg = purify_config(pm, idle_mode, lock_gain)
        cutoff_s = None if cut is None else cut * t2
        for n in n_range:
            r = simulate_chain(p, n, cutoff_s=cutoff_s, purify=cfg)
            rows.append({
                "k": k, "gamma_mult": gm, "gamma_slot_hz": base.gamma_hz,
                "gamma_eff_hz": p.gamma_hz, "t2_ms": t2 * 1e3, "t2_label": t2_label,
                "gamma_eff_t2": p.gamma_hz * t2,
                "cutoff_t2_mult": "none" if cut is None else cut,
                "purify": pm, "idle_mode": idle_mode if pm != "off" else "n/a",
                "n_nodes": n, "protocol": r.protocol, "rate_hz": r.rate_hz,
                "fidelity": r.fidelity,
                "pairs_per_e2e": "" if r.pairs_per_e2e is None else r.pairs_per_e2e,
                "useful": int(r.rate_hz >= USEFUL_RATE_HZ and r.fidelity >= USEFUL_F),
            })
    return rows


def write_csv(rows: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            out = dict(r)
            out["rate_hz"] = f"{r['rate_hz']:.6g}"
            out["fidelity"] = f"{r['fidelity']:.6f}"
            out["gamma_eff_t2"] = f"{r['gamma_eff_t2']:.6g}"
            out["gamma_eff_hz"] = f"{r['gamma_eff_hz']:.6g}"
            out["t2_ms"] = f"{r['t2_ms']:.6g}"
            if r["pairs_per_e2e"] != "":
                out["pairs_per_e2e"] = f"{r['pairs_per_e2e']:.6g}"
            w.writerow(out)


# ----------------------------------------------------------------------------
# Aggregation helpers
# ----------------------------------------------------------------------------
CFG_KEYS = ("k", "gamma_mult", "t2_ms", "cutoff_t2_mult", "purify")


def config_key(r: dict) -> tuple:
    return tuple(r[c] for c in CFG_KEYS)


def max_useful_n(rows: list[dict]) -> dict[tuple, int]:
    """Largest N in the sweep with F>=0.88 and R>=1 Hz, per configuration (0 = none)."""
    best: dict[tuple, int] = {}
    for r in rows:
        key = config_key(r)
        best.setdefault(key, 0)
        if r["useful"]:
            best[key] = max(best[key], r["n_nodes"])
    return best


_PUR_ORDER = {"off": 0, "link": 1, "swap": 2, "both": 3}


def _cutoff_order(c) -> float:
    return float("inf") if c == "none" else float(c)


def cheapness(r: dict) -> tuple:
    """Lexicographic cost: smallest k, shortest T2, smallest Γ multiplier, then
    no purification < link < both, then no cutoff before cutoff (smaller cutoff last tiebreak)."""
    return (r["k"], r["t2_ms"], r["gamma_mult"], _PUR_ORDER[r["purify"]],
            0 if r["cutoff_t2_mult"] == "none" else 1, _cutoff_order(r["cutoff_t2_mult"]), -r["rate_hz"])


def _dedupe(cands: list[dict]) -> list[dict]:
    """Collapse rows that differ only by cutoff (keep the first, i.e. no-cutoff if it passes)."""
    seen, out = set(), []
    for r in cands:
        key = (r["k"], r["gamma_mult"], r["t2_ms"], r["purify"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def ranked_for_target(rows: list[dict], n_target: int, top: int = 5, purify: str | None = None,
                      gamma_mult: float | None = None):
    """Configs for which chain length exactly n_target passes (F>=0.88, R>=1 Hz), cheapest first.
    Rows differing only by cutoff are collapsed. Returns (top rows, number of passing configs)."""
    cands = [r for r in rows if r["n_nodes"] == n_target and r["useful"]
             and (purify is None or r["purify"] == purify)
             and (gamma_mult is None or r["gamma_mult"] == gamma_mult)]
    cands.sort(key=cheapness)
    return _dedupe(cands)[:top], len(cands)


def min_k_per_t2(rows: list[dict], n_target: int, gamma_mult: float | None = None):
    """For each T2, the cheapest passing configuration at N=n_target (or None)."""
    out = {}
    for t2, _ in T2_VALUES:
        c = [r for r in rows if r["n_nodes"] == n_target and r["useful"]
             and abs(r["t2_ms"] - t2 * 1e3) < 1e-9
             and (gamma_mult is None or r["gamma_mult"] == gamma_mult)]
        c.sort(key=cheapness)
        out[t2 * 1e3] = c[0] if c else None
    return out


def _desc(r: dict) -> str:
    return (f"k={r['k']}, Γmult={r['gamma_mult']:g}, T2={r['t2_ms']:g} ms, "
            f"cutoff={r['cutoff_t2_mult']}{'' if r['cutoff_t2_mult']=='none' else '×T2'}, "
            f"purify={r['purify']}")


def _table(top: list[dict]) -> list[str]:
    lines = ["| rank | k | Γmult | T2 (ms) | cutoff | purify | Γ_eff (Hz) | Γ_eff·T2 | F | R (Hz) |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(top, 1):
        lines.append(f"| {i} | {r['k']} | {r['gamma_mult']:g} | {r['t2_ms']:g} | {r['cutoff_t2_mult']} | "
                     f"{r['purify']} | {r['gamma_eff_hz']:.4g} | {r['gamma_eff_t2']:.3g} | "
                     f"{r['fidelity']:.4f} | {r['rate_hz']:.4g} |")
    return lines


def format_ranked_markdown(rows: list[dict], idle_mode: str) -> str:
    lines = [f"# Cheapest combos reaching N (F≥{USEFUL_F}, R≥{USEFUL_RATE_HZ:g} Hz) — {STAMP}", "",
             f"idle-mode for purified runs: `{idle_mode}`. Cost order: smallest k, then shortest T2, "
             "then smallest Γ multiplier, then purification off<link<swap<both, then cutoff "
             "(rows differing only by cutoff are collapsed; the cutoff column shows the cheapest = 'none' when it passes). "
             "T2 0.17 / 1.8 ms are published SnV⁻ values; 3.6 ms is the locked assumption; "
             "10 / 100 ms and every k>1 are HYPOTHETICAL. Γ_eff = k·Γmult·85 Hz.", ""]
    for n in TARGET_NS:
        top, total = ranked_for_target(rows, n, gamma_mult=1.0)
        lines += [f"## N = {n}", ""]
        lines += [f"### A. Pure multiplexing (Γmult = 1, locked per-slot Γ = 85 Hz): {total} passing grid configs", ""]
        if not top:
            lines += ["**No configuration in the grid passes.** (See `sweep_required_gamma.md` for the "
                      "Γ_eff the model would need beyond the grid.)", ""]
        else:
            lines += _table(top)
            lines += ["", f"Cheapest per T2 at N={n} (Γmult = 1):", "",
                      "| T2 (ms) | cheapest passing config | Γ_eff·T2 | F | R (Hz) |", "|---|---|---|---|---|"]
            for t2ms, r in min_k_per_t2(rows, n, gamma_mult=1.0).items():
                if r is None:
                    lines.append(f"| {t2ms:g} | — none passes — | | | |")
                else:
                    lines.append(f"| {t2ms:g} | {_desc(r)} | {r['gamma_eff_t2']:.3g} | "
                                 f"{r['fidelity']:.4f} | {r['rate_hz']:.4g} |")
            lines.append("")
        topb, totb = ranked_for_target(rows, n, top=3)
        lines += [f"### B. Any Γmult ∈ {{{', '.join(f'{g:g}' for g in GAMMA_MULTS)}}} ({totb} passing grid configs; "
                  "Γmult is just another rate multiplier, only k·Γmult matters)", ""]
        lines += _table(topb) if topb else ["**No configuration in the grid passes.**"]
        top_np, tot_np = ranked_for_target(rows, n, top=1, purify="off")
        lines += ["", f"Without purification: {tot_np} passing grid configurations"
                  + (f"; cheapest {_desc(top_np[0])}" if top_np else "") + ".", ""]
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Beyond-grid extrapolation: what Γ_eff would the MODEL need?
# ----------------------------------------------------------------------------
def required_gamma_eff(n: int, t2_s: float, purify_mode: str, idle_mode: str = "raw",
                       cutoff_mult: float | None = None, lock_gain: float = LOCK_GAIN,
                       g_lo: float = 42.5, g_hi: float = 1e10, step: float = 2 ** 0.25):
    """
    Smallest Γ_eff on a log grid (ratio 2^(1/4) ≈ 1.19) at which chain length n passes
    (F≥0.88, R≥1 Hz) for fixed T2 / purification mode.  Returns (Γ_eff, rate, F) or None.
    Γ_eff = k·Γmult·85 Hz, so k_equiv = Γ_eff/85 at Γmult=1.  Extrapolation beyond the
    published sweep grid; same model and caveats.
    """
    base = locked_v03b()
    cfg = purify_config(purify_mode, idle_mode, lock_gain)
    g = g_lo
    while g <= g_hi:
        p = multiplexed_params(base, 1, g / base.gamma_hz, t2_s=t2_s)
        r = simulate_chain(p, n, cutoff_s=None if cutoff_mult is None else cutoff_mult * t2_s, purify=cfg)
        if r.rate_hz >= USEFUL_RATE_HZ and r.fidelity >= USEFUL_F:
            return g, r.rate_hz, r.fidelity
        g *= step
    return None


def required_gamma_table(idle_modes=("raw", "full"), modes=("link", "swap", "both"),
                         targets=TARGET_NS, cutoffs=(None, 1.0)) -> list[dict]:
    base = locked_v03b()
    out = []
    for n in targets:
        for t2, _ in T2_VALUES:
            for im in idle_modes:
                for pm in modes:
                    for cut in cutoffs:
                        res = required_gamma_eff(n, t2, pm, im, cut)
                        out.append({
                            "n_nodes": n, "t2_ms": t2 * 1e3, "idle_mode": im, "purify": pm,
                            "cutoff_t2_mult": "none" if cut is None else cut,
                            "gamma_eff_hz": None if res is None else res[0],
                            "k_equiv_at_85hz": None if res is None else res[0] / base.gamma_hz,
                            "gamma_eff_t2": None if res is None else res[0] * t2,
                            "rate_hz": None if res is None else res[1],
                            "fidelity": None if res is None else res[2],
                        })
    return out


def write_required_outputs(tab: list[dict], csv_path: str, md_path: str) -> None:
    cols = ["n_nodes", "t2_ms", "idle_mode", "purify", "cutoff_t2_mult", "gamma_eff_hz",
            "k_equiv_at_85hz", "gamma_eff_t2", "rate_hz", "fidelity"]
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in tab:
            w.writerow({c: ("" if r[c] is None else (f"{r[c]:.6g}" if isinstance(r[c], float) else r[c]))
                        for c in cols})
    lines = [f"# Γ_eff the model needs (beyond-grid extrapolation) — {STAMP}", "",
             "Smallest effective link rate Γ_eff (log grid, ratio 2^¼) at which N passes F≥0.88 & R≥1 Hz, "
             "best over purification mode {link, swap, both} and cutoff {none, 1×T2}, per T2 and idle-mode. "
             "BBPSSW target 0.95, TPP lock gain 1.0. k_equiv = Γ_eff / 85 Hz (i.e. Γmult = 1). "
             "This is what the *model* asks for; no claim that any hardware can provide it.", ""]
    for im in sorted({r["idle_mode"] for r in tab}):
        lines += [f"## idle-mode `{im}`", "",
                  "| N | T2 (ms) | best mode | cutoff | Γ_eff (Hz) | k_equiv | Γ_eff·T2 | R (Hz) | F |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for n in sorted({r["n_nodes"] for r in tab}):
            for t2 in sorted({r["t2_ms"] for r in tab}):
                c = [r for r in tab if r["n_nodes"] == n and r["t2_ms"] == t2 and r["idle_mode"] == im
                     and r["gamma_eff_hz"] is not None]
                if not c:
                    lines.append(f"| {n} | {t2:g} | none up to 1e10 Hz | | | | | | |")
                    continue
                r = min(c, key=lambda x: x["gamma_eff_hz"])
                lines.append(f"| {n} | {t2:g} | {r['purify']} | {r['cutoff_t2_mult']} | {r['gamma_eff_hz']:.3g} | "
                             f"{r['k_equiv_at_85hz']:.3g} | {r['gamma_eff_t2']:.3g} | {r['rate_hz']:.3g} | {r['fidelity']:.4f} |")
        lines.append("")
    with open(md_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


# ----------------------------------------------------------------------------
# Plots
# ----------------------------------------------------------------------------
def make_plots(rows: list[dict], tag: str = "") -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    best = max_useful_n(rows)
    t2ms = sorted({r["t2_ms"] for r in rows})
    ks = sorted({r["k"] for r in rows})
    paths = []

    def grid(filter_fn):
        g = np.zeros((len(t2ms), len(ks)))
        for key, n in best.items():
            k, gm, t2, cut, pm = key
            if not filter_fn(gm, cut, pm):
                continue
            i, j = t2ms.index(t2), ks.index(k)
            g[i, j] = max(g[i, j], n)
        return g

    panels = [
        ("no purification", lambda gm, c, pm: pm == "off" and gm == 1.0),
        ("BBPSSW on links (target 0.95)", lambda gm, c, pm: pm == "link" and gm == 1.0),
        ("BBPSSW after swaps only", lambda gm, c, pm: pm == "swap" and gm == 1.0),
        ("BBPSSW links + after swaps", lambda gm, c, pm: pm == "both" and gm == 1.0),
        ("any purification, any Γ mult", lambda gm, c, pm: True),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(17, 9))
    axes = axes.ravel()
    axes[-1].set_visible(False)  # 5 panels on a 2x3 grid
    for ax, (title, fn) in zip(axes, panels):
        g = grid(fn)
        im = ax.imshow(g, origin="lower", cmap="viridis", vmin=0, vmax=17, aspect="auto")
        ax.set_xticks(range(len(ks)), [str(k) for k in ks])
        ax.set_yticks(range(len(t2ms)), [f"{t:g}" for t in t2ms])
        ax.set_xlabel("k (parallel slots per link)")
        ax.set_ylabel("T2 (ms)")
        ax.set_title(title + "\n(best over cutoff" + ("" if "any Γ" in title else "; Γmult=1") + ")", fontsize=9)
        for i in range(len(t2ms)):
            for j in range(len(ks)):
                v = int(g[i, j])
                ax.text(j, i, str(v) if v else "–", ha="center", va="center",
                        color="white" if v < 9 else "black", fontsize=8)
        fig.colorbar(im, ax=ax, label="max N with F≥0.88 & R≥1 Hz (0/– = none, even N=2)")
    fig.suptitle(f"Max chain length N vs multiplexing k and T2\n{STAMP}", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    p = os.path.join(ART, f"sweep_maxN_heatmap{tag}.png")
    fig.savefig(p, dpi=140); plt.close(fig); paths.append(p)

    # line plots: max N vs k, one line per T2 (best over everything else)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, (title, fn) in zip(axes, [("no purification", lambda gm, c, pm: pm == "off"),
                                      ("any purification mode / cutoff / Γ mult", lambda gm, c, pm: True)]):
        g = grid(fn)
        for i, t in enumerate(t2ms):
            ax.plot(ks, g[i], marker="o", label=f"T2={t:g} ms")
        ax.set_xscale("log"); ax.set_xticks(ks, [str(k) for k in ks])
        ax.set_xlabel("k (parallel slots per link)"); ax.set_ylabel("max N (F≥0.88, R≥1 Hz)")
        ax.set_ylim(-0.5, 17.5); ax.grid(alpha=0.3); ax.legend(fontsize=8)
        ax.set_title(title, fontsize=10)
    fig.suptitle(f"Max N vs k per T2\n{STAMP}", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    p = os.path.join(ART, f"sweep_maxN_vs_k{tag}.png")
    fig.savefig(p, dpi=140); plt.close(fig); paths.append(p)

    # Max N vs Γ_eff·T2 scatter
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    xs = {}
    for r in rows:
        if not r["useful"]:
            continue
        xs[(r["gamma_eff_t2"], r["purify"])] = max(xs.get((r["gamma_eff_t2"], r["purify"]), 0), r["n_nodes"])
    for pm, c in (("off", "tab:gray"), ("link", "tab:blue"), ("swap", "tab:green"), ("both", "tab:red")):
        pts = sorted((x, n) for (x, p_), n in xs.items() if p_ == pm)
        if pts:
            ax.scatter([p_[0] for p_ in pts], [p_[1] for p_ in pts], s=14, c=c, label=f"purify={pm}", alpha=0.7)
    ax.set_xscale("log"); ax.set_xlabel("Γ_eff · T2"); ax.set_ylabel("max passing N")
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
    ax.set_title(f"Max N vs Γ_eff·T2\n{STAMP}", fontsize=10)
    fig.tight_layout()
    p = os.path.join(ART, f"sweep_maxN_vs_gammaT2{tag}.png")
    fig.savefig(p, dpi=140); plt.close(fig); paths.append(p)
    return paths


def summarize(rows: list[dict]) -> str:
    best = max_useful_n(rows)
    top = max(best.values())
    out = [f"Largest passing N anywhere in grid: {top}"]
    for pm in PURIFY_MODES:
        v = max((n for k_, n in best.items() if k_[4] == pm), default=0)
        out.append(f"  purify={pm}: max N = {v}")
    return "\n".join(out)


def main(argv=None) -> int:
    global ART
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--idle-mode", choices=("raw", "full"), default="raw",
                    help="purified-run idle model (default raw; 'full' is harsher). 'ideal' is not offered.")
    ap.add_argument("--lock-gain", type=float, default=LOCK_GAIN,
                    help="TPP trinity_lock_gain (TUNED, default neutral 1.0)")
    ap.add_argument("--no-required", action="store_true", help="skip the beyond-grid Γ_eff table")
    ap.add_argument("--quick", action="store_true", help="tiny grid for smoke testing")
    ap.add_argument("--out-dir", default=ART)
    a = ap.parse_args(argv)

    ART = a.out_dir
    kw = {}
    if a.quick:
        kw = dict(ks=(1, 10), t2s=T2_VALUES[2:4], gmults=(1.0,), cutoffs=(None, 1.0))
    rows = run_sweep(idle_mode=a.idle_mode, lock_gain=a.lock_gain, **kw)
    tag = "" if a.idle_mode == "raw" else f"_idle_{a.idle_mode}"
    csv_path = os.path.join(ART, f"sweep_results{tag}.csv")
    write_csv(rows, csv_path)
    md = format_ranked_markdown(rows, a.idle_mode)
    md_path = os.path.join(ART, f"sweep_ranked{tag}.md")
    with open(md_path, "w") as fh:
        fh.write(md + "\n")
    paths = make_plots(rows, tag)
    extra = []
    if not a.no_required and not a.quick:
        tab = required_gamma_table()
        rc, rm = os.path.join(ART, "sweep_required_gamma.csv"), os.path.join(ART, "sweep_required_gamma.md")
        write_required_outputs(tab, rc, rm)
        extra = [rc, rm]
    print(f"{STAMP}\nrows={len(rows)}  idle_mode={a.idle_mode}  lock_gain={a.lock_gain}")
    print(summarize(rows))
    print(md)
    print("wrote:", csv_path, md_path, *paths, *extra, sep="\n  ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
