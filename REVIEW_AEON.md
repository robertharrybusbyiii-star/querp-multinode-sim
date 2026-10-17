# REVIEW_AEON — QuERP multinode sim (v0.3b-sim+tpp)
Reviewer: AEON, 2026-10-16. Source files NOT modified. `simulate.py --compare-tpp` ran cleanly (venv `/workspace/.venv_f`, artifacts sent to scratch dir). Sensitivity script and raw output: `/workspace/review_scratch/sens.py`, `sens_out.txt`. Everything below is a review of a *model*; none of it is a hardware measurement.

## 0. Bottom line
- Arithmetic is internally consistent; no result breaks F∈[0.25,1], R≤Γ, or p≤1 (checked over 96 parameter/protocol combos).
- The headline "TPP lets N=3 pass F≥0.88 & R≥1 Hz" is **not a purification result**. It exists because TPP mode defaults to `idle=ideal` (zero memory decoherence, repeater.py:307-309) while the no-TPP baseline has idle on. With `--purify-idle raw|full`, TPP N=3 gives F=0.251 (same as baseline).
- Purification at link level also ignores that the pair waits for its partner copy (≈1/Γ = 3.3·T2). Under the model's own decay law the input drops to F≈0.27 (<0.5), where recurrence cannot help. 18.4 raw pairs/link ≈ 216 ms ≈ 60·T2 of storage is never charged.
- The "2.4× T2", "1.18× success", "1.08 gain" and "0.01 phase floor" are assumptions/tuned. None has a source. The 2.4× T2 factor has **zero** effect on default TPP headline numbers (idle off) and little on no-TPP numbers (F collapses to 0.25 either way).

## 1. Units / dimensional issues
| # | Where | Issue |
|---|---|---|
| U1 | baseline.py:23-31, 71-78 | µW/cm²→mW via `*1e-3` is correct (60 µW/cm² × 900 cm² × 0.62 = 33.48 mW). Formula is duplicated (module constant vs. `NodeParams.p_dc_mw`); the module constant ignores overrides. Assumes all 100 cells see full density at normal incidence, no fill-factor/polarization/mismatch loss. |
| U2 | baseline.py:26 | `ETA_E2E` commented "optical→DC" but the input is RF density. Label error. |
| U3 | baseline.py:36-42, scenarios.py:208-217 | Γ [Hz] = attempt_rate [Hz] × p_succ [dimensionless] is dimensionally fine. But locked Γ=85 Hz ≠ 5000×0.0071=35.5 Hz. The ratio 85/35.5 = **2.39 ≈ 2.4**, the same number as the T2 factor (3.6/1.5). Locked Γ ≈ 5000×0.0071×2.4 — i.e. an undocumented ×2.4 rate multiplier (README calls it "multiplexing factors"). `p_succ` is never used in any e2e calculation; only Γ is. |
| U4 | werner.py:164-170, repeater.py:328 | T2 (a spin *dephasing* time) is used as a *depolarizing* decay of Werner weight w. Pure dephasing of a Bell pair floors at F=0.5, not 0.25. The 0.25 plateau in every table is partly this modeling choice. Also unclear whether the factor is per qubit or per pair (a pair has two memory qubits; e^{-2t/T2} would be the two-qubit dephasing value). |
| U5 | repeater.py:328, 420 | Uses `exp(-E[Δ]/T2)` with mean gap τ=1/Γ. For exponential gaps the correct average is `E[e^{-Δ/T2}] = 1/(1+τ/T2)`. At Γ·T2=0.306: sim factor 0.038 vs 0.234 (single qubit) or 0.133 (two-qubit). N=3 no-TPP F: sim 0.251 vs ≈0.38 / 0.32. The conclusion (F<0.5) survives; the numbers do not. |
| U6 | repeater.py:328-329 | One idle factor is applied to *both* arms (`swap_werner(w_dec, w_dec)`), though only the earlier-arriving pair waits. Double counts decay (docstring says "each arm"). |
| U7 | trinity_purification.py:168-169, 171 | Dimensionless "gains" multiply a probability (p) and a fidelity (F). `residual_phase_error` is named a phase error but is a unitless depolarizing shrink on w (not rad/deg), applied **every round** (compounds), while README calls it a "floor". It also caps reachable F: target 0.99 is unreachable at ε=0.01 (max ≈0.97). |
| U8 | whole model | No distance, fiber loss (dB/km), c, or transmissivity anywhere. "N nodes" has no length. The PLOB repeaterless bound cannot be evaluated; claims about "repeater advantage" are untestable here. No Hz vs rad/s or deg/rad mixing found (all times in s, rates in Hz, `_s/_hz/_mw` suffixes consistent). |
| U9 | repeater.py:246 | `A or B and C` precedence works as intended but is fragile; add parentheses. |

## 2. Assumption vs measured (every input)
Source status: web-verified only where stated. "No source found" = I did not find one; it does not prove none exists.

| Input | Value | Used at | Effect | Source | Label |
|---|---|---|---|---|---|
| RF density | 60 µW/cm² (0.6 W/m²) | baseline.py:23,28,71; scenarios.py | Only sets DC power & autonomy flag. No effect on any rate/F. Breakeven 21.5 µW/cm². Needs a dedicated transmitter (~7.5 W EIRP at 1 m); ambient levels are far lower. Below FCC general-population MPE (1 mW/cm² at 2.4 GHz; 0.6 mW/cm² at 900 MHz; 47 CFR 1.1310, verified) | No source for *this* node | ASSUMPTION |
| Cell count, area | 100 × 9 cm² | baseline.py:24-25 | P_DC ∝ area | none | ASSUMPTION |
| η_e2e | 0.62 | baseline.py:26 | P_DC | Measured RF-DC of 40–63% exists for good rectennas at µW–mW levels (e.g. 52% at 0 dBm, 63% peak at −2.4 dBm in one 2.45 GHz design; PMC10140817). 0.62 is top-of-range, with ideal capture/matching assumed | LITERATURE-plausible (best case) |
| Electronics | 12 mW | baseline.py:29 | Autonomy margin | none. Ignores the cryostat: SnV⁻ memories are measured at ~1.7 K, whose cooling power is orders above 12 mW | ASSUMPTION |
| T2 | 3.60 ms | baseline.py:36 | Idle decay | SnV⁻ lit: 170 µs Hahn echo, 650 µs XY16 at 1.7 K (Rosenthal, PRX 13, 031022); ~1.7–1.8 ms with XY8 + 256 π pulses (Beukers et al. 2024; arXiv 2409.08977). 3.6 ms is above these, and is a *dynamical-decoupling* T2, not a free-idle memory time | ASSUMPTION (exceeds lit.) |
| **2.4× T2 (Trinity)** = 3.60/1.50 | 2.4 | baseline.py:36 vs scenarios.py:254 | None on default-TPP headline (idle off). No-TPP: F 0.2508→0.2500. Cutoff runs (cut at fixed 3.6 ms): N=3 F 0.459→0.305 | **No source found.** No demonstrated coupling of a 4.38 Hz phase-lock to quantum-memory T2 | ASSUMPTION (hypothetical scenario parameter) |
| **1.18× success** = 0.0071/0.006 | 1.183 | baseline.py:37 vs scenarios.py:255 | Display only in locked run; in `without_trinity` it sets Γ=30. Neutralizing (Γ→71.8) cuts all rates ×0.845 | none | ASSUMPTION |
| Attempt rate | 5000 Hz | baseline.py:42 | Γ only in without_trinity | none; ignores comm. latency | ASSUMPTION |
| Γ | 85 Hz | baseline.py:38 | All rates scale linearly with Γ | none; contains the unexplained ×2.39 | ASSUMPTION/TUNED |
| F_link | 0.887 | baseline.py:39 | Sets everything; Werner form assumed | none; real links are not Werner | ASSUMPTION |
| **TPP lock gain** | 1.08 | trinity_purification.py:69,168 | Multiplies herald prob. (p→0.998 at F≈0.94). Gain=1.0 drops link rate 4.62→3.40 Hz; headline unchanged | **No source found.** Herald probability is fixed by the state and the operation; a phase-lock cannot raise it above the analytical value | TUNED |
| **Residual phase floor** | 0.01 | trinity_purification.py:79,171 | Largest single lever on rate: ε=0 → N=2 rate 9.49 Hz (2×), N=4 F 0.862→0.878 | none | TUNED |
| TPP fidelity gain | 1.0 | :74,169 | neutral by default | none | TUNED (neutral) |
| Purify target / rounds | 0.95 / 8 | :82,85 | N=2 TPP F=0.951 is "first round ≥0.95" | policy | ASSUMPTION |
| p_swap, η_swap | 1.0, 1.0 | repeater.py:84-85 | Ideal swap, no gate noise (also ideal local gates in purification) | none (README says 'SnV default') | ASSUMPTION |
| Idle mode | ideal | repeater.py:108 | **Dominant**: off → TPP N≤3 passes; on → F=0.25 | model choice | ASSUMPTION (flattering) |
| Useful R/F | 1 Hz / 0.88 | baseline.py:50-51 | reporting thresholds | policy | ASSUMPTION |

**Sensitivity (factor set neutral, one at a time, locked hardware otherwise; max N with F≥0.88 & R≥1 Hz)**
| Run | no-TPP | TPP default (ideal idle) |
|---|---|---|
| Baseline | N=2 (N=3: 56.7 Hz, F=0.251) | N=3 (R=3.08 Hz, F=0.905) |
| T2 → 1.5 ms | N=2 | N=3, numbers identical |
| p factor → 1 (Γ=71.8) | N=2 | N=3; R ×0.845 (2.60 Hz) |
| Γ unexplained ×2.39 → 1 (Γ=35.5) | N=2 | N=3; R=1.29 Hz (borderline) |
| All HW factors → 1 (= `without_trinity`) | N=2 | N=3; R=1.09 Hz (borderline) |
| TPP gain → 1.0 | – | N=3; R 3.08→2.26 Hz |
| ε → 0 | – | N=3 (N=4 F=0.878, still <0.88); R ×2.05 |
| Gain=1 & ε=0 (both neutral) | – | N=3; R=5.02 Hz |
| idle = raw / full | – | **N=2 only**; N=3 F=0.251 |
So the "Trinity" hardware factors barely move the TPP headline; what moves it is idle=ideal and ε.

## 3. Physics sanity
- **Werner math OK.** F=(1+3w)/4; swap w=w_a·w_b is exact for ideal BSM on Werner states (N=3 zero-idle F=0.791 matches README). Fidelity-threshold claim "N≥3 can't reach 0.88 without purification" is correct for ideal swapping.
- **Purification formulas match BBPSSW** (Bennett 1996): p=F²+2F(1−F)/3+5(1−F)²/9, F'=(F²+(1−F)²/9)/p; fixed point 0.5 (code stops at ≤0.5, :237). Label issue: code re-twirls to Werner each round, so it is **BBPSSW, not DEJMPS**. Single-round values coincide; iterated DEJMPS is faster (my quick Bell-diagonal calc: F 0.887→0.916→0.985→0.999 vs 0.909→0.927→0.941→0.951). Not a correctness bug, but the README label is wrong and the pairs/F numbers are conservative on this axis.
- **Cost model:** 2/p per round compounding is the right expected-pair accounting. Missing: waiting/storage decoherence between copies (see §0), local gate/measurement error (threshold is a few %, so ideal gates at 0.887 inputs are a strong assumption), classical-communication time, nonexponential waiting-time distributions above nesting level 1.
- **Rate scaling:** nested τ_k=1.5τ_{k−1}/p_acc is an approximation (the max of two exponentials is not exponential at higher levels). Rate vs N is non-monotonic (N=3 56.7, N=4 28.3, N=5 37.8 Hz) because protocol switches nested↔sequential; a plotting artifact, not physics.
- **Bounds:** F∈[0.25,1], p≤1 (capped), R≤Γ all hold. PLOB (−log₂(1−η), arXiv:1510.08863) cannot be tested: no η or distance in the model. A memory-assisted link may exceed PLOB legitimately, but nothing here shows it.
- **Trinity (4.38 Hz phase lock):** no demonstrated physical coupling to quantum-memory T2, herald probability, or purification success. The 2.4× T2 factor (and 1.18×, 1.08, 0.01) must be treated as *hypothetical scenario parameters*, not results.
- **RF at 60 µW/cm²:** no established mechanism for any effect on spin coherence or link success; this is untested. In the model it only feeds the power budget.

## 4. Recommended labeling and minimum code changes (not applied)
**README banner (copy-paste):**
> **MODEL OUTPUT UNDER STATED ASSUMPTIONS — NOT MEASURED.** Every number below is computed from the inputs in `ASSUMPTIONS` (querp_sim/assumptions.py), each labeled MEASURED / LITERATURE / ASSUMPTION / TUNED. As of this version, none is MEASURED for this hardware. The "Trinity" factors (T2 ×2.4, success ×1.18, purification gain 1.08, residual phase floor 0.01) are hypothetical scenario parameters with no demonstrated physical mechanism. TPP results use `idle=ideal` (no memory decoherence) and are an upper bound, not a prediction. Rates are in Hz per elementary link with no distance or fiber loss modeled.

**Minimum code changes**
1. Add one `ASSUMPTIONS` dict `{name: (value, unit, label, source_or_"no source found")}`; read all constants (baseline.py, scenarios.py, trinity_purification.py, repeater.py defaults) from it; print it at the top of `simulate.py` and write it into each CSV header.
2. Name the implicit factors: `T2_TRINITY_FACTOR=2.4`, `P_SUCC_TRINITY_FACTOR=1.183`, `GAMMA_UNEXPLAINED_FACTOR=2.39`; derive `without_trinity` from them (`factor=1.0` = neutral).
3. Stamp every table/plot title and the summary line with "idle=ideal (no decoherence)" when TPP is on; add a TPP row with `idle=raw` next to each headline.
4. Fix idle decay to `E[e^{-Δ/T2}]=1/(1+τ/T2)` (or Monte Carlo), apply it to one arm only, and document dephasing-vs-depolarizing.
5. Rename "DEJMPS" → "BBPSSW (twirled)"; relabel `residual_phase_error` as per-round `depolarizing_residual` (dimensionless); relabel `ETA_E2E` as RF→DC.
6. Cap TPP `p_success` at the analytical value by default (gain only via an explicit `--hypothetical-lock-gain` flag).
7. Add `assert 0.25<=F<=1`, `R<=Γ` and a unit-test for the N=2 and N=3 zero-idle analytic values.
