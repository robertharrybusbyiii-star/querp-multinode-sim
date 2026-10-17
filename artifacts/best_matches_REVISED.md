# Best matches under REVISED bands — MODEL OUTPUT, NOT MEASURED

> **MODEL OUTPUT, NOT MEASURED.** Same simulator and same sweep as `best_matches.md`; only the published-value band edges changed, following `TARGETS_AEON_verified.md` section 6 (AEON's full-text check). The earlier `best_matches.md` used the OLD bands and is stale on p and k.

## Revised band edges (changes marked)

| Parameter | published | plausible | beyond published |
|---|---|---|---|
| T2 (unchanged) | ≤ 10 ms (only at ≤ 50 mK; ≤ 1.7 ms at 1.7 K) | 10–100 ms | > 100 ms |
| p per slot (**CHANGED**) | ≤ 3×10⁻⁵ (the only published p with F ≈ 0.8) | 3×10⁻⁵ – 2.5×10⁻⁴ (published only at F ≈ 0.56–0.60) | > 2.5×10⁻⁴ |
| k slots (**CHANGED**) | 1 (no published multimode memory–memory demo at F ≥ 0.8) | 2–40 (k ≈ 4 shown only at low fidelity) | > 40 |

Thresholds F ≥ 0.88, R ≥ 1 Hz. Cost ordering as in `best_matches.md`. Main rows idle=`raw`; idle=`full` shown as sensitivity. Caveats from `best_matches.md` all still apply (optimistic link purification, no loss/power/crosstalk, p_eq is a modelling choice, no nuclear-memory stacking).

## N = 2

| tier | passing? | cheapest combination (idle=raw) |
|---|---|---|
| published | **none** | — |
| plausible | yes (340 rows) | k=1, T2=0.17 ms, p_eq=0.00025 (Γmult=0.03521), Γ_eff=2.993 Hz (Γ_eff·T2=0.000509), purify=off, cutoff=none; **F=0.8870, R=2.993 Hz** |
| beyond published | yes (2240 rows) | k=1, T2=0.17 ms, p_eq=0.00355 (Γmult=0.5), Γ_eff=42.5 Hz (Γ_eff·T2=0.00722), purify=off, cutoff=none; **F=0.8870, R=42.5 Hz** |

Sensitivity idle=`full`: published: none; plausible: k=1, T2=0.17 ms, p_eq=0.00025, purify=off, F=0.887, R=2.99 Hz; beyond published: k=1, T2=0.17 ms, p_eq=0.00355, purify=off, F=0.887, R=42.5 Hz.

## N = 3

| tier | passing? | cheapest combination (idle=raw) |
|---|---|---|
| published | **none** | — |
| plausible | **none** | — |
| beyond published | yes (526 rows) | k=1, T2=100 ms, p_eq=0.0284 (Γmult=4), Γ_eff=340 Hz (Γ_eff·T2=34), purify=link, cutoff=none; **F=0.8863, R=9.057 Hz** — link-only purification, most optimistic |

Sensitivity idle=`full`: published: none; plausible: none; beyond published: k=5, T2=10 ms, p_eq=0.0284, purify=swap, F=0.950, R=1.03 Hz.

## N = 5

| tier | passing? | cheapest combination (idle=raw) |
|---|---|---|
| published | **none** | — |
| plausible | **none** | — |
| beyond published | yes (40 rows) | k=50, T2=10 ms, p_eq=0.0284 (Γmult=4), Γ_eff=1.7e+04 Hz (Γ_eff·T2=170), purify=both, cutoff=none; **F=0.9506, R=1.181 Hz** |

Sensitivity idle=`full`: published: none; plausible: none; beyond published: none.

## N = 9

| tier | passing? | cheapest combination (idle=raw) |
|---|---|---|
| published | **none** | — |
| plausible | **none** | — |
| beyond published | **none** | — |

Sensitivity idle=`full`: published: none; plausible: none; beyond published: none.

## N = 17

| tier | passing? | cheapest combination (idle=raw) |
|---|---|---|
| published | **none** | — |
| plausible | **none** | — |
| beyond published | **none** | — |

Sensitivity idle=`full`: published: none; plausible: none; beyond published: none.

## Summary — max N per tier (cumulative; idle=raw | idle=full)

| tier | max N (raw) | max N (full) |
|---|---|---|
| published | 0 | 0 |
| plausible | 2 | 2 |
| beyond published | 5 | 4 |

N = 9 and 17 do not pass in any grid (see `sweep_required_gamma.md`); that conclusion does not depend on the band edges.

