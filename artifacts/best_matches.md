# Best matches — published-value tiers vs. the multiplexing sweep — MODEL OUTPUT, NOT MEASURED

> **STALE BANDS NOTICE (2026-10-16):** this file uses the OLD published-value bands (p ≤ 2.5e-4 'published', 2.5e-4–2.5e-3 'plausible', k ≤ 4 'published'). AEON's full-text check (`TARGETS_AEON_verified.md` §6) moved those edges. See `artifacts/best_matches_REVISED.md` (`classify_sweep.py --revised`). Revised max N: published 0, plausible 2, beyond published 5 (old: 2 / 3 / 5).


> **MODEL OUTPUT, NOT MEASURED.** Tiers compare the sweep's parameters with the published-value bands of `TARGETS_AEON.md` §7. They say what inputs the *model* needs; they do not claim any hardware can pass.

## Caveats (read first)

- **Purified rows are optimistic.** Link-level purification charges no storage decay while a copy waits for its partner; swap-level rows are more robust. BBPSSW with ideal local gates, ideal swap (p_swap=1, η_swap=1), Werner-state links, F_link=0.887 taken as given.
- **No fiber/distance loss, no power or cryostat load, no slot crosstalk, no memory-slot cost of k** are modeled. Success needs ≥ 2k memory slots per node.
- **AEON's bands are partly unverified.** Only Karapatzakis 2024 (arXiv:2403.00521) was read in full; most other rows are abstract/snippet ('ABS') or search-summary ('SUM') values. The 'published' k band (≤ 4) comes from other platforms (ion-photon), and 'published' T2 up to 10 ms holds only at 50 mK.
- **The p-equivalent is a modelling choice** (p_eq = 0.0071 × Γmult; see `classify_sweep.py` docstring). Because Γmult ≥ 0.5 in the original grid, **every original grid row is 'beyond published' on p**. To show anything below that tier, a SUPPLEMENTAL grid at the p-band edges (Γmult = 0.0352 → p = 2.5e-4; 0.352 → p = 2.5e-3) was run with the same simulator; its rows are tagged `source=extension`.
- **No nuclear-memory or other-platform numbers are stacked** on an SnV node (different platforms; no demonstration of the combination).
- The locked baseline (T2 = 3.6 ms, p = 0.0071, Γ = 85 Hz) is itself *beyond published* on p and above literature at 1.7 K on T2.

## Tier definitions

| Parameter | published | plausible | beyond published |
|---|---|---|---|
| T2 | ≤ 10 ms (≤ 1.7 ms at 1.7 K; > 1.7 ms needs ≤ 50 mK) | 10–100 ms | > 100 ms |
| p per slot (p_eq) | ≤ 2.5×10⁻⁴ | ≤ 2.5×10⁻³ | > 2.5×10⁻³ (locked 0.0071 is here) |
| k slots | ≤ 4 | 5–40 | > 40 |
| overall tier | all three published | worst band plausible | any band beyond |

Cost ordering for 'cheapest': smallest k, then shortest T2, then smallest Γmult, then purification off < link < swap < both, then no cutoff. Main tables use idle=`raw`; idle=`full` is shown as a sensitivity. Thresholds: F ≥ 0.88 and R ≥ 1 Hz.

## N = 2 (reference)

Published tier **passes** at N = 2 (no swap, no purification needed; F = F_link = 0.887 taken as given): k=1, T2=0.17 ms, p_eq=0.00025 (Γmult=0.03521), Γ_eff=2.993 Hz (Γ_eff·T2=0.000509), purify=off, cutoff=none; **F=0.8870, R=2.993 Hz**. Note F_link = 0.887 and Γ ≥ 1 Hz at p = 2.5e-4 are model inputs, not banded; published solid-state remote links reached F ≈ 0.86 (SiV, ~1 Hz) / 0.81 (NV, 6 Hz).

## N = 3

| tier | passing? | cheapest combination (idle=raw) | note |
|---|---|---|---|
| published | **none — no passing combination** | — | inside this tier’s bands, no configuration reaches F≥0.88 & R≥1 Hz at N=3 |
| plausible | yes (8 rows) | k=10, T2=100 ms, p_eq=0.0025 (Γmult=0.3521), Γ_eff=299.3 Hz (Γ_eff·T2=29.9), purify=link, cutoff=none; **F=0.8838, R=7.973 Hz** | at least one parameter in the plausible band (none beyond). Link-only purification: most optimistic (no storage decay while waiting for partner copy). From the supplemental p-edge grid. |
| beyond published | yes (526 rows) | k=1, T2=100 ms, p_eq=0.0284 (Γmult=4), Γ_eff=340 Hz (Γ_eff·T2=34), purify=link, cutoff=none; **F=0.8863, R=9.057 Hz** | worst band: p=beyond published. Link-only purification: most optimistic (no storage decay while waiting for partner copy). |

Sensitivity, idle=`full`: published: none; plausible: none; beyond published: k=5, T2=10 ms, p_eq=0.0284, purify=swap, F=0.950, R=1.03 Hz.

**Best tier achievable at N=3: plausible.**

What would need to be shown on a bench for N=3:

- **T2:** electron-spin DD T2 of 100 ms is in the *plausible* band (published best 10 ms at 50 mK, Karapatzakis 2024, T2∝N^0.95 not yet saturated); needs more π pulses / pulse-error control and a dilution-fridge-class setup. Not shown at 1.7 K (best ~1.7 ms).
- **p (per-attempt remote success):** needs p ≈ 0.0025 per slot, i.e. 10× the best published remote value (2.5×10⁻⁴); no SnV spin-photon entanglement has been demonstrated at all yet.
- **k:** k = 10 link slots per node (published color-center hardware: k ≤ 4 Purcell channels, no remote-entanglement multiplexing). Needs ≥ 2k memory slots, tuning, crosstalk control (none modeled).
- **Purification (link):** BBPSSW with ideal local gates; link-level rows ignore storage decay while waiting for the partner copy, so this row is the most optimistic. Needs heralded high-fidelity two-qubit gates on the node.
- **Memory:** no nuclear memory used (do not add one on top without a demo of that combination on the same SnV node).
- **Published-only (all three inside published bands) does not pass N = 3** in this model (best published-band Γ_eff ≈ 12 Hz vs ≳ 3×10² Hz (link-only purification, T2 = 100 ms) to ≳ 2×10³ Hz (swap-level, T2 ≤ 10 ms) needed).
- **Robustness:** the plausible-tier N = 3 pass exists only with a link-level purification stage (`link`, or `both`, which includes it; the most optimistic mode) and only under idle=raw; no swap-only plausible-tier pass exists (max Γ_eff = 40·0.352·85 ≈ 1.2×10³ Hz < ≈ 1.36×10³ Hz needed), and nothing in the plausible tier passes under idle=full.

## N = 5

| tier | passing? | cheapest combination (idle=raw) | note |
|---|---|---|---|
| published | **none — no passing combination** | — | inside this tier’s bands, no configuration reaches F≥0.88 & R≥1 Hz at N=5 |
| plausible | **none — no passing combination** | — | inside this tier’s bands, no configuration reaches F≥0.88 & R≥1 Hz at N=5 |
| beyond published | yes (40 rows) | k=50, T2=10 ms, p_eq=0.0284 (Γmult=4), Γ_eff=1.7e+04 Hz (Γ_eff·T2=170), purify=both, cutoff=none; **F=0.9506, R=1.181 Hz** | worst band: k=beyond published, p=beyond published. |

Sensitivity, idle=`full`: published: none; plausible: none; beyond published: none.

**Best tier achievable at N=5: beyond published.**

What would need to be shown on a bench for N=5:

- **p:** the grid passes only with p_eq ≈ 0.028 per slot (≈ 114× the published 2.5×10⁻⁴) **and** k = 50 (> 40 → beyond).
- **k:** k = 50 parallel slots per node — beyond anything shown on color centers.
- **T2:** 10 ms (published; > 1.7 ms is published only at ≤ 50 mK, not at 1.7 K).
- **Purification:** needs swap-level (nested) BBPSSW at every level (`both`/`swap`), ~hundreds of raw pairs per end-to-end pair; needs ideal local gates and fast classical feed-forward.
- **Memory:** model uses an electron-spin memory only; a nuclear memory would relax the T2 demand but is a different platform and unstacked here.
- **Within plausible bands (k ≤ 40, p ≤ 2.5×10⁻³, T2 ≤ 100 ms): no passing combination**, even N = 5 at T2 = 100 ms (max Γ_eff = 40·0.352·85 ≈ 1.2×10³ Hz vs ≈ 1.5×10⁴ Hz needed).

## N = 9

| tier | passing? | cheapest combination (idle=raw) | note |
|---|---|---|---|
| published | **none — no passing combination** | — | inside this tier’s bands, no configuration reaches F≥0.88 & R≥1 Hz at N=9 |
| plausible | **none — no passing combination** | — | inside this tier’s bands, no configuration reaches F≥0.88 & R≥1 Hz at N=9 |
| beyond published | **no passing grid combination** | extrapolation only: Γ_eff ≈ 2.46e+05 Hz (k_equiv ≈ 2.9e+03), T2=3.6 ms, both, cutoff none; F=0.951, R=1.09 Hz | needs k_equiv ≫ 40 at the locked p, so it is beyond published on k (and p if Γmult is raised instead). Not a grid result. |

Sensitivity, idle=`full`: published: none; plausible: none; beyond published: none.

**Best tier achievable at N=9: beyond published (extrapolation only, not in grid).**

What would need to be shown on a bench for N=9:

- **Not in the sweep grid.** Model extrapolation (idle=raw, best T2 ≤ 100 ms) needs Γ_eff ≈ 2.46e+05 Hz (k_equiv ≈ 2.9e+03 at the locked 85 Hz/slot; T2=3.6 ms, both, cutoff none).
- **p / k trade:** at the plausible-max k = 40 each slot would need Γmult ≈ 72.4, i.e. p_eq ≈ 0.514; at k = 4, Γmult ≈ 724, p_eq ≈ 5.14 (> 1: impossible).
- Reaching it requires k, p **and** a new memory class all beyond published at once, plus losses/power/crosstalk that are not modeled. Memory must beat published electron-spin values or move to a nuclear memory (1.35 s ¹³C at 50 mK for SnV; different platform, no demonstrated combination with multiplexing).
- Treat as 'needs a different architecture' (e.g. very high-rate sources, multi-mode memories, higher-fidelity swaps), not as a bench target.

## N = 17

| tier | passing? | cheapest combination (idle=raw) | note |
|---|---|---|---|
| published | **none — no passing combination** | — | inside this tier’s bands, no configuration reaches F≥0.88 & R≥1 Hz at N=17 |
| plausible | **none — no passing combination** | — | inside this tier’s bands, no configuration reaches F≥0.88 & R≥1 Hz at N=17 |
| beyond published | **no passing grid combination** | extrapolation only: Γ_eff ≈ 7.88e+06 Hz (k_equiv ≈ 9.27e+04), T2=1.8 ms, both, cutoff none; F=0.958, R=1.02 Hz | needs k_equiv ≫ 40 at the locked p, so it is beyond published on k (and p if Γmult is raised instead). Not a grid result. |

Sensitivity, idle=`full`: published: none; plausible: none; beyond published: none.

**Best tier achievable at N=17: beyond published (extrapolation only, not in grid).**

What would need to be shown on a bench for N=17:

- **Not in the sweep grid.** Model extrapolation (idle=raw, best T2 ≤ 100 ms) needs Γ_eff ≈ 7.88e+06 Hz (k_equiv ≈ 9.27e+04 at the locked 85 Hz/slot; T2=1.8 ms, both, cutoff none).
- **p / k trade:** at the plausible-max k = 40 each slot would need Γmult ≈ 2.32e+03, i.e. p_eq ≈ 16.5 (> 1: impossible); at k = 4, Γmult ≈ 2.32e+04, p_eq ≈ 165 (> 1: impossible).
- Reaching it requires k, p **and** a new memory class all beyond published at once, plus losses/power/crosstalk that are not modeled. Memory must beat published electron-spin values or move to a nuclear memory (1.35 s ¹³C at 50 mK for SnV; different platform, no demonstrated combination with multiplexing).
- Treat as 'needs a different architecture' (e.g. very high-rate sources, multi-mode memories, higher-fidelity swaps), not as a bench target.

## Summary — max N per tier (cumulative; idle=raw | idle=full)

| tier | max N (raw) | max N (full) |
|---|---|---|
| published | 2 | 2 |
| plausible | 3 | 2 |
| beyond published | 5 | 4 |

N = 9 and 17 pass nowhere in the grids; they appear only in the beyond-grid extrapolation (`sweep_required_gamma.md`), which is beyond published on every axis.

## Bench plans

Bench plans in this workspace and their relevance:
- `/workspace/trinity_test_plan/` (Trinity Lock vs No-Lock): **relevant only to the 'Trinity' T2 ×2.4 / success ×1.18 assumptions** that are baked into the locked baseline. It tests phase lock on classical oscillators (metronomes / Arduino+555); it does **not** measure SnV⁻ T2, per-attempt p, or multiplexing. A positive result there would not validate any row of this report.
- `/workspace/ppm_test_plan/` (proton precession magnetometer) and `/workspace/nv_test_plan/` (NV Zeeman spectroscopy): **not relevant** to the tier requirements here. The NV plan is the nearest diamond-colour-centre hands-on skill-builder (ODMR/Zeeman), but it measures neither SnV⁻ coherence nor remote entanglement.
- Closing any N ≥ 3 gap needs a cryogenic SnV⁻ (or similar) lab setup (≤ 1.7 K, ideally ≤ 50 mK), a cavity/waveguide spin-photon interface and a second node; none of the bench plans here is a substitute.

## Files

- `classify_sweep.py` (this report's generator); `artifacts/sweep_results_classified.csv`, `sweep_results_idle_full_classified.csv`, `sweep_extension_p_bands_classified.csv`; `artifacts/best_matches_tiers.png`.

