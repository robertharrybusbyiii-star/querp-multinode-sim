# QuERP multi-node quantum repeater simulation

> **MODEL OUTPUT UNDER STATED ASSUMPTIONS — NOT MEASURED.** Every number below is
> computed from the inputs registered in `querp_sim/assumptions.py`, each labeled
> MEASURED / LITERATURE / ASSUMPTION / TUNED. As of this version, **none is MEASURED
> for this hardware**. The "Trinity" factors (T2 ×2.4, success ×1.18, purification
> gain 1.08, per-round depolarizing residual 0.01) are **hypothetical scenario
> parameters with no demonstrated physical mechanism**. TPP results with
> `--purify-idle ideal` use no memory decoherence and are an **optimistic upper bound,
> not a prediction**. Rates are per elementary link with **no distance or fiber loss
> modeled**.

Grounded in **LOCKED QuERP Node baseline v0.3b (24 Aug 2026)**.  
This project does **not** invent a different hardware baseline; scenario overrides,
the temporal-cutoff protocol, and the **Trinity Purification Protocol (TPP)** are
labeled **extensions only**.

## Locked per-node operating point (v0.3b)

| Quantity | Locked value |
|----------|--------------|
| RF density | 60 µW/cm² |
| QBEH aperture | 100 cells × 9.0 cm² |
| End-to-end η | 0.62 → **33.5 mW DC** |
| Electronics + control | **12.0 mW** |
| Power margin | **+21.5 mW** |
| Effective T2 | **3.60 ms** |
| Optical p_succ | **0.0071** |
| Adjacent-link rate Γ | **85.0 Hz** |
| Link fidelity F | **0.887** |
| Node Pass thresholds | margin > 0, Γ ≥ 80 Hz, F ≥ 0.88 |

Implication: **Γ·T2 ≈ 0.306**. Mean idle while waiting for a partner link (~1/Γ ≈ 11.8 ms) exceeds T2, so without a temporal cutoff (or deeper multiplexing) end-to-end fidelity after the first swap collapses toward 0.25.

### Without-Trinity comparison (scenario only)

- T2 = 1.5 ms, p_succ = 0.006  
- Γ = attempt_rate × p = **5000 Hz × 0.006 = 30 Hz**  
- Note: locked Γ = 85 Hz is **not** equal to 5000 × 0.0071 (= 35.5 Hz). It is **≈ 2.39× larger** (85 / 35.5), an **undocumented rate multiplier with no derivation** (numerically ≈ the 2.4× T2 factor; the previous README called it "multiplexing factors", but no multiplexing model exists here). It is carried as part of the locked baseline and **not** altered. Only the Without-Trinity scenario uses the raw product. F_link is kept at 0.887 (optical fidelity not remapped).

> **Noise-damping Trinity ≠ Purification Trinity.** The locked Γ/T2/p_succ already
> embed conservative noise-damping / coherence multipliers. The optional
> **Trinity Purification Protocol (TPP)** below is a *separate* bilateral
> purification layer and does **not** remultiply those locked numbers.

## Physical / information model

1. **Elementary heralded links** at Γ, F_link; decoherence during waiting uses T2.
2. **Werner / depolarizing channel**: F = (1+3w)/4, w = (4F−1)/3.
3. **Idle decoherence** (modeling choice): the waiting gap Δ is exponential with mean τ,
   so the Werner weight is multiplied by the **averaged** factor
   E[exp(−Δ/T2)] = **1/(1 + τ/T2)** (not exp(−τ/T2); corrected after the AEON review;
   the exact truncated-exponential average is used with a cutoff). Only the **one
   earlier-arriving pair** idles at each swap (the other arm is fresh). T2 is a spin
   *dephasing* time used here as a *depolarizing* decay of w, so the plateau is
   F = 0.25 (pure dephasing would floor at 0.5); one decay factor per pair, not per
   qubit. These are open modeling choices, not derived results.
4. **Entanglement swap** (SnV⁻ matter-node default):
   - Success probability `p_swap = 1.0` (deterministic CNOT+measure swap).
   - Ideal composition by default (`η_swap = 1.0`): `w_out = η_swap · w_a · w_b`. Use `--eta-swap 0.99` for residual gate noise.
5. **Protocols**
   - **Nested** when L = N−1 = 2ⁿ (both-ready time `(3/2)τ`; idle residual `τ`).
   - **Sequential** left-to-right for other N (growing pair idles mean `1/Γ`).
   - CLI `--protocol auto` (default) selects nested on power-of-two L, else sequential.
6. **Temporal cutoff (extension)**: `--cutoff-t2-mult m` keeps pairs only if residual idle ≤ m·T2, reducing rate by the acceptance probability and using the exact truncated-exponential average decay factor. Does not change locked Γ/T2/F.
7. **Power autonomy**: each node remains energy-autonomous at the locked QBEH budget unless a scenario overrides RF density or electronics load.
8. **Useful e2e thresholds** (reporting policy): R_e2e ≥ 1 Hz and F_e2e ≥ 0.88.
9. **Trinity Purification Protocol (TPP, extension)**: optional **BBPSSW** (twirled to a
   Werner state after every round — *not* DEJMPS) bilateral purification with
   *separate*, hypothetical Trinity overlays — see below.

### N = 2 sanity check

For N = 2 (L = 1) **without TPP** there is no swap: the model recovers **R = Γ** and **F = F_link** exactly (85 Hz, 0.887 under nominal v0.3b).

With `--trinity-purify` and `--purify-when link|both`, if F_link < `--purify-target`, N = 2 rate drops and fidelity rises (pairs consumed for purification). If F already ≥ target, purification is skipped (identity).

## Trinity Purification Protocol (separate from noise-damping Trinity)

Module: `querp_sim/trinity_purification.py`.

### What TPP is / is not

| | Noise-damping Trinity (locked v0.3b) | Trinity Purification Protocol (TPP) |
|--|--------------------------------------|-------------------------------------|
| Where | Baked into Γ, T2, p_succ | Optional CLI / `PurifyConfig` |
| Effect | Higher coherence & link rate (**assumed**, no demonstrated coupling) | Purification success / per-round depolarizing residual (**TUNED**, no source) |
| Changes locked HW? | *Is* the locked mapping | **No** — never remaps Γ/T2/F_link |

### Analytical BBPSSW, twirled each round (Werner)

> Earlier versions labeled this "DEJMPS". The formulas are **BBPSSW** (Bennett et al.,
> PRL 76, 722 (1996)); the output is re-twirled to Werner every round, which is what
> makes it BBPSSW rather than DEJMPS. First-round values coincide, but iterated DEJMPS
> converges faster, so pair counts / fidelities here are conservative on that axis.
> Local gates/measurements are assumed ideal. The recurrence's fixed point is F = 0.5.

Two identical Werner copies with fidelity F:

\[
p_{\mathrm{BBPSSW}} = F^{2} + \tfrac{2}{3} F(1-F) + \tfrac{5}{9}(1-F)^{2}
\]

\[
F_{\mathrm{out}} = \frac{F^{2} + \tfrac{1}{9}(1-F)^{2}}{p_{\mathrm{BBPSSW}}}
\]

Yield cost (input pairs per successful output): \(2 / p_{\mathrm{success}}\).

### Trinity overlays (all **TUNED**: no source, no demonstrated mechanism)

- `trinity_lock_gain` (default **1.08**, explored 1.0–1.15) — **TUNED**:  
  \(p_{\mathrm{success}} = \min(1,\, p_{\mathrm{BBPSSW}}\cdot g)\).
  A phase lock cannot raise a herald probability above the analytical value fixed by
  the state and operation; this is a hypothetical what-if. Use `1.0` for neutral.
- `trinity_fidelity_gain` (default **1.0**, neutral): multiplier on analytical \(F_{\mathrm{out}}\)
- `depolarizing_residual` ε (default **0.01**) — **TUNED**: after **each** round,
  \(w \leftarrow w(1-\varepsilon)\). It is a **per-round, unitless depolarizing shrink**
  that compounds over rounds — **not a one-time floor and not a phase error in rad/deg**
  (previously named `residual_phase_error` / `--residual-phase-error`; the old CLI flag
  still works as a deprecated alias). It caps the reachable F (target 0.99 is
  unreachable at ε = 0.01; max ≈ 0.97).

`purify_to_target(w, F_target, max_rounds)` iterates rounds until \(F \ge F_{\mathrm{target}}\) (default **0.95**) or the round cap; total pairs = product of per-round yield costs. Time at rate Γ: \(t = N_{\mathrm{pairs}}/\Gamma\).

### Wiring into the repeater

- `--purify-when link`: purify elementary links before nesting / sequential swap
- `--purify-when swap`: purify after each swap / nesting level
- `--purify-when link` (**default** when TPP is enabled): purify elementary links only
- `--purify-when both`: link then swap-level (high fidelity, much lower rate)
- Rate accounting charges for pairs consumed and retries (rate ↓, fidelity ↑)
- Skip purify when already above target (unless `--force-purify`)
- `--purify-idle raw|full|ideal` (default **raw**, changed from `ideal`): under TPP,
  `raw` = memory decoherence ON with the pre-purification-tax τ; `full` = decoherence ON
  with the rate τ (harsher). Rate always pays pair cost.
  **`ideal` = zero memory decoherence: an optimistic upper bound, not a prediction**,
  and *not* like-for-like with the no-TPP baseline (which has decoherence on). It is
  kept only to show the Werner-composition bound. At locked Γ·T2≈0.306 the physical
  modes collapse F for N≥3.
- **Known limitation:** link-level purification does not charge storage decoherence for a
  pair waiting for its partner copy (≈ 1/Γ ≈ 3.3·T2; ~18 raw pairs/link ≈ 60·T2 of
  storage). Even `raw`/`full` therefore remain optimistic for TPP.

### CLI

```bash
# Baseline (no TPP) — N=2 stays 85 Hz / 0.887
python simulate.py --n-max 17

# Compare baseline vs TPP on nominal + without_trinity
python simulate.py --compare-tpp \
  --scenarios nominal_v0.3b without_trinity \
  --purify-target 0.95 --purify-when both \
  --trinity-purify-gain 1.08

# Optimistic upper bound only (no memory decoherence) — NOT a prediction
python simulate.py --compare-tpp --purify-idle ideal

# TPP only (still also prints no-TPP curves when using --compare-tpp;
# --trinity-purify alone adds TPP curves alongside the no-TPP sweep)
python simulate.py --trinity-purify --purify-target 0.95 --purify-when both
python simulate.py --trinity-purify --purify-when link --trinity-purify-gain 1.10
python simulate.py --no-trinity-purify   # explicit off
```

## Scenarios

| Name | What changes |
|------|----------------|
| `nominal_v0.3b` | Locked defaults |
| `half_rf` | RF density → 30 µW/cm² |
| `high_electronics` | Electronics → 24.0 mW |
| `half_rf_high_elec` | Half RF + 24.0 mW electronics (not autonomous) |
| `without_trinity` | T2=1.5 ms, p_succ=0.006, Γ=30 Hz (**no** noise-damping Trinity) |

Cross scenario: run `without_trinity` **with** `--trinity-purify` / `--compare-tpp` to see purification on top of the non–noise-damped hardware point (TPP still does not rewrite Γ/T2).

## How to run

```bash
cd /workspace/querp-multinode-sim
source .venv/bin/activate
pip install -r requirements.txt   # if needed
python simulate.py --compare-tpp --scenarios nominal_v0.3b without_trinity
```

Other examples:

```bash
python simulate.py --n-max 17 --protocol auto
python simulate.py --scenarios nominal_v0.3b without_trinity --cutoff-t2-mult 1.0
python simulate.py --protocol sequential --n-max 9
python simulate.py --p-swap 0.5   # linear-optics BSM comparison
python simulate.py --trinity-purify --purify-target 0.95 --purify-when both
```

Outputs:

- Summary tables on stdout (rate, fidelity, usefulness vs N)
- `artifacts/rate_vs_N.png`
- `artifacts/fidelity_vs_N.png`
- `artifacts/summary_nominal_v0.3b.csv`
- `artifacts/summary_with_trinity_purify.csv` (when TPP curves are generated)
- `artifacts/summary_nominal_v0.3b_cutoff.csv` (when cutoff enabled)

## Project layout

```
querp-multinode-sim/
  simulate.py                    # CLI entry point
  requirements.txt
  README.md
  querp_sim/
    baseline.py                  # LOCKED v0.3b constants (values unchanged)
    assumptions.py               # per-input labels (ASSUMPTION/TUNED/...)
    werner.py                    # Werner helpers
    repeater.py                  # nested + sequential (+ cutoff + TPP)
    trinity_purification.py      # Trinity Purification Protocol (BBPSSW; SEPARATE)
    power.py                     # QBEH autonomy
    scenarios.py                 # labeled extensions
    multiplexing.py              # k parallel slots: Γ_eff = k·Γmult·Γ (earliest-of-k)
  sweep.py                       # k × T2 × Γmult × cutoff × purification × N sweep
  tests/test_sanity.py           # sanity + analytic checks
  tests/test_sweep.py            # multiplexing + sweep tests
  artifacts/                     # PNG + CSV outputs
```

## Key analytic bound (no purification)

Two elementary Werner links with F_link = 0.887 have w = (4F−1)/3 ≈ 0.849.
Ideal swap with **zero idle** yields w_out = w² ≈ 0.721 → **F_out ≈ 0.791**.
Therefore **F_e2e ≥ 0.88 is impossible for any N ≥ 3** under pure Werner swapping
without entanglement purification.

### With default TPP (regenerated sweep, `idle=raw`)

Defaults: `--purify-target 0.95 --purify-when link --trinity-purify-gain 1.08
--purify-idle raw` (noise-damping Trinity locked numbers unchanged).

| Scenario | max N with F≥0.88 & R≥1 Hz (**before**: idle=ideal, old decay) | **now** (idle=raw, corrected decay) |
|----------|------------------|-----------------|
| `nominal_v0.3b` without TPP | N = 2 | **N = 2** (N=3: F 0.251 → 0.377) |
| `nominal_v0.3b` with TPP | N = 2, 3 (max 3) | **N = 2** only (N=3: R 3.08 Hz, **F 0.905 → 0.404**) |
| `without_trinity` without TPP | N = 2 | **N = 2** |
| `without_trinity` with TPP | N = 2, 3 | **N = 2** |
| `nominal_v0.3b` TPP, `--purify-idle ideal` (upper bound, not a prediction) | N = 2, 3 | N = 2, 3 (unchanged: R 3.08 Hz, F 0.905) |

**The earlier headline "TPP lets N=3 pass F≥0.88" was an artifact of `idle=ideal`
(memory decoherence switched off in the TPP run only).** With decoherence on, TPP
does **not** extend the passing chain beyond N = 2 in this model. TPP still helps the
N = 2 link itself (85 Hz / F 0.887 → 4.62 Hz / F 0.951 at a rate cost of ~18 raw pairs).
Under `idle=ideal` the N=4 point is F≈0.862 (<0.88).

## Caveats / gray-area assumptions

- Transparent analytic mean-time model (not a full Monte-Carlo event sim). The
  nested rate recursion τ_k = 1.5·τ_{k−1}/p is an approximation (max of two
  exponentials is not exponential above level 1); rate vs N is non-monotonic because
  the protocol switches between nested and sequential (plot artifact, not physics).
- TPP `trinity_lock_gain=1.08` and `depolarizing_residual=0.01` are **TUNED
  hypothetical overlays** (no source, no mechanism), not locked hardware numbers.
- Default `trinity_fidelity_gain=1.0` stays on the analytical BBPSSW F curve.
- `--purify-idle ideal` is an optimistic upper bound (see above); default is `raw`.
- Link-level purification ignores storage decoherence while waiting for the partner
  pair, and ignores local gate/measurement error and classical-communication time.
- Swap-level purification assumes two independent copies of the same nesting
  level are available (standard recurrence scheduling abstraction).
- No distance, fiber loss (dB/km), or transmissivity: the PLOB repeaterless bound
  cannot be evaluated, so "repeater advantage" claims are untestable here.
- Idle decay uses dephasing T2 as a depolarizing decay (F floor 0.25), one factor per
  pair; a per-qubit/two-qubit treatment would be harsher (e^{−2t/T2}).
- Cutoff / multimode scheduling beyond the simple gap acceptance model is future work.
- Default no-cutoff, no-TPP sweep shows the raw consequence of Γ·T2 ≪ 1.

## Status of claims (read first)

All results here are **model output**, not measurements.
- v0.3b is a theoretical budget sketch, not a validated hardware design.
- The Trinity coherence-time and success-probability multipliers are **assumptions**, not a measured SnV⁻ coupling.
- The Trinity purification gain and residual phase floor are tunable assumptions, not locked hardware values.
- Any phase-lock coupling strength ("K") should come from bench data, not be set in this script.

### Status of claims — per-input labels (extended; see `querp_sim/assumptions.py`)

Source status comes from the AEON review (`REVIEW_AEON.md`). "No source found" means a
reviewer did not find one, not proof none exists. **No input is MEASURED for this hardware.**

| Input | Value | Label | Notes |
|-------|-------|-------|-------|
| RF density | 60 µW/cm² | **ASSUMPTION** | Needs a dedicated transmitter (~7.5 W EIRP at 1 m); ambient levels are far lower. No established effect on spin coherence or link success; here it only sets DC power. |
| QBEH cells × area | 100 × 9 cm² | ASSUMPTION | No source. |
| η RF→DC | 0.62 | LITERATURE (best case) | Measured rectenna RF-DC of 40–63% exists; 0.62 is top of range with ideal matching. |
| Electronics + control | 12 mW | ASSUMPTION | Ignores the cryostat; SnV⁻ memories are measured at ~1.7 K and cooling power is orders of magnitude above 12 mW. |
| T2 | 3.60 ms | **ASSUMPTION (exceeds literature)** | Published SnV⁻: 170 µs Hahn echo, 650 µs XY16 at 1.7 K (Rosenthal, PRX 13, 031022); ~1.7–1.8 ms with XY8 + 256 π pulses (Beukers et al. 2024, arXiv 2409.08977). 3.6 ms is above these and is a dynamical-decoupling T2, not a free-idle memory time. |
| **2.4× T2 factor** (3.6/1.5) | 2.4 | **ASSUMPTION** | No demonstrated coupling of a phase lock to quantum-memory T2. Hypothetical scenario parameter; it is not a code parameter, only the ratio between the locked and `without_trinity` values. |
| **1.18× success factor** (0.0071/0.006) | 1.183 | **ASSUMPTION** | No source. `p_succ` is never used in end-to-end results; only Γ is. |
| Attempt rate | 5000 Hz | ASSUMPTION | No source; ignores communication latency. |
| **Γ (locked)** | 85 Hz | **ASSUMPTION / TUNED** | Carries an **undocumented ≈2.39× factor** over 5000 × 0.0071 = 35.5 Hz (≈ the T2 factor). All rates scale linearly with Γ. |
| F_link | 0.887 | ASSUMPTION | Werner form assumed; real links are not Werner. |
| p_swap, η_swap | 1.0, 1.0 | ASSUMPTION | Ideal swap and ideal local gates. |
| **TPP lock gain** | 1.08 | **TUNED** | No source; herald probability is fixed by state and operation, a lock cannot raise it. Gain 1.0 is neutral. |
| **Per-round depolarizing residual** (ex "residual phase floor") | 0.01 | **TUNED** | No source. Per-round unitless shrink, compounds; not a floor or phase angle. Largest single lever on TPP rate. |
| TPP fidelity gain | 1.0 | TUNED (neutral) | — |
| Purify target / rounds | 0.95 / 8 | ASSUMPTION | Policy choice. |
| Idle mode | `raw` (default) | ASSUMPTION | `ideal` is flattering and dominates the old N=3 headline. |
| Distance / fiber loss | — | **NOT MODELED** | PLOB bound untestable. |
| Useful thresholds | R ≥ 1 Hz, F ≥ 0.88 | ASSUMPTION | Reporting policy. |

Bottom line: the Trinity hardware factors barely move the TPP result; what moved the old
headline was `idle=ideal`. **Trinity has no demonstrated coupling to memory T2, herald
probability, or purification success.**

## Multiplexing / T2 / cutoff / purification sweep (`sweep.py`)

> **MODEL OUTPUT, NOT MEASURED.** This sweep asks what the *model* needs for a chain of N nodes
> to clear **F_e2e ≥ 0.88 and R_e2e ≥ 1 Hz**. It makes **no claim that any hardware can provide
> the required k, T2 or Γ_eff.** Locked v0.3b values in `baseline.py` are unchanged; every
> k > 1, every T2 other than the two literature values, and every Γ multiplier is a
> **HYPOTHETICAL** scenario parameter.

### Multiplexing model (`querp_sim/multiplexing.py`)

- Each node has **k parallel link-attempt slots**; slot i succeeds after i.i.d. T_i ~ Exp(Γ_slot).
  A link is available at the **earliest of k arrivals**: T_link = min(T_1..T_k) ~ Exp(k·Γ_slot),
  so **Γ_eff = k · Γmult · Γ_slot** with locked Γ_slot = 85 Hz (k=1, Γmult=1 is exactly v0.3b).
- **Idle-wait distribution:** the partner link is also an earliest-of-k arrival, so by
  memorylessness the residual gap between the two is again Exp(mean 1/Γ_eff). The existing
  idle machinery (E[e^{−Δ/T2}] = 1/(1+τ/T2), the truncated form with cutoff, acceptance probability
  1−e^{−t_cut/τ}, nested 3/2·τ recursion) therefore applies unchanged with Γ → Γ_eff. A
  Monte-Carlo test checks the min-of-k mean and the gap-decay average.
- **Memory decoherence stays ON** (`purify-idle=raw` for purified runs). Key figure of merit: **Γ_eff·T2**
  (stored in every CSV row).
- **Not modeled:** power / cryostat / memory-slot cost of k (the power margin does not change with k;
  a node needs ≥ 2k memory slots), slot crosstalk, switching / feed-forward latency, source rate limits.
  The k−1 later-succeeding slots are discarded (conservative: a scheme could use the freshest pair).
  No distance or fiber loss, as everywhere in this project.

### Grid

| Axis | Values | Label |
|------|--------|-------|
| k | 1, 2, 5, 10, 20, 50, 100 | k=1 locked; k>1 hypothetical |
| T2 | 0.17, 1.8, 3.6, 10, 100 ms | 0.17 (Hahn echo) & 1.8 (XY8+256 π) = published SnV⁻ values (AEON review); **3.6 = locked assumption (exceeds literature)**; 10, 100 = hypothetical |
| Γ multiplier | 0.5, 1, 2, 4 | hypothetical; only k·Γmult matters |
| Cutoff | none, 0.5, 1, 2 × T2 | protocol extension |
| Purification | off · `link` · `swap` · `both` (BBPSSW, target 0.95) | `link` = elementary links only; `swap` = after each swap/nesting level only; `both` = both |
| N | 2 … 17 | protocol auto (nested for L = 2ⁿ, else sequential) |

35,840 rows (2,240 configurations × 16 N). Purified runs use the TPP overlays at **neutral lock gain 1.0**
(a phase lock cannot raise a herald probability; the 1.08 CLI default is not used here) and the
existing TUNED per-round depolarizing residual 0.01. "Passes at N" means that exact N meets
both thresholds; "max N" is the largest passing N in N = 2…17.

```bash
/workspace/.venv_f/bin/python sweep.py                    # raw idle (default) -> artifacts/sweep_*.{csv,md,png}
/workspace/.venv_f/bin/python sweep.py --idle-mode full   # harsher purified-idle sensitivity (_idle_full files)
/workspace/.venv_f/bin/python sweep.py --quick            # tiny smoke grid
/workspace/.venv_f/bin/python tests/test_sanity.py && /workspace/.venv_f/bin/python tests/test_sweep.py
```

### Outputs

- `artifacts/sweep_results.csv` — all rows (k, Γmult, Γ_eff, T2, Γ_eff·T2, cutoff, purify, N, protocol, R, F, pairs, useful); `sweep_results_idle_full.csv` for the sensitivity run
- `artifacts/sweep_maxN_heatmap.png`, `sweep_maxN_vs_k.png`, `sweep_maxN_vs_gammaT2.png` (stamped "MODEL OUTPUT, NOT MEASURED"; `_idle_full` variants)
- `artifacts/sweep_ranked.md` — cheapest combos reaching N = 3, 5, 9, 17 (smallest k, then shortest T2), with Γ_eff·T2
- `artifacts/sweep_required_gamma.{md,csv}` — beyond-grid extrapolation: Γ_eff the model needs for N = 3, 5, 9, 17 per T2

### Findings (what the model says)

1. **Without purification, multiplexing never gets past N = 2.** Even with zero idle the ideal Werner swap of
   two F=0.887 links gives F = 0.791 (<0.88), so k, T2 and cutoff cannot fix F for N ≥ 3. Multiplexing only
   helps by letting purification fit inside the rate and decoherence budget.
2. **Largest N in the k ≤ 100 grid is 5** (raw idle): only with k·Γmult ≥ 200 (Γ_eff ≥ 1.7·10⁴ Hz, i.e. k = 100 with Γmult ≥ 2 or k ≥ 50 with Γmult = 4;
   with Γmult = 1 the grid tops out at Γ_eff = 8.5·10³ Hz and N = 5 never passes), `both` purification and T2 ≥ 1.8 ms; **N = 9 and N = 17 pass nowhere in the grid.** With the harsher
   `full` idle model the grid maximum is N = 4.
3. **N = 3** (pure multiplexing, Γmult = 1; raw idle; Γ_eff·T2 in brackets):

   | T2 | cheapest k | purification | Γ_eff·T2 |
   |----|-----------|--------------|----------|
   | 0.17 ms (published) | 100 (+ cutoff 0.5×T2) | swap | 1.45 |
   | 1.8 ms (published) | 50 | swap | 7.7 |
   | 3.6 ms (locked) | 50 | swap | 15.3 |
   | 10 ms (hypothetical) | 20 | swap | 17 |
   | 100 ms (hypothetical) | 5 | link | 42.5 |

   `link`-only passes at k=5 / T2=100 ms only because link-level purification still ignores storage decay
   while a copy waits for its partner (see Known limitation): treat it as the most optimistic entry.
   The `swap` entries are identical under `raw` and `full` idle and are the more robust ones.
4. **N = 5, 9, 17 need Γ_eff far beyond k = 100** (beyond-grid extrapolation, best purification mode, Γ_eff = k_equiv·85 Hz).
   The rate budget, not decoherence, dominates: each purified swap level costs a large pair-count multiplier.

   | N | idle=raw: Γ_eff needed (k_equiv at Γmult=1) | idle=full |
   |---|------------------------------------------|-----------|
   | 5 | ≈1.5·10⁴ Hz (k_equiv ≈ 180) at T2 ≥ 10 ms; ≈3.7·10⁴ Hz (≈430) at 1.8–3.6 ms; ≈1.5·10⁵ Hz (≈1.7·10³) at 0.17 ms | ≈1·10⁵–1.7·10⁶ Hz (k_equiv ≈ 1.2·10³–2·10⁴) for T2 = 100–1.8 ms; ≈5.6·10⁶ Hz at 0.17 ms |
   | 9 | ≈2.5·10⁵ Hz (≈2.9·10³) at T2 ≥ 3.6 ms; ≈3.5·10⁵ Hz (≈4·10³) at 1.8 ms; ≈8·10⁵ Hz at 0.17 ms | ≈2·10⁶–1.8·10⁸ Hz (k_equiv ≈ 2·10⁴–2·10⁶) |
   | 17 | ≈7.9·10⁶ Hz (≈9·10⁴) for T2 ≥ 1.8 ms; ≈9.4·10⁶ Hz at 0.17 ms | ≈3·10⁷–2.9·10⁹ Hz (k_equiv ≈ 4·10⁵–3·10⁷) |

   Under `raw` idle the N = 17 requirement is rate-limited (essentially the same for every T2 ≥ 1.8 ms), which is exactly
   the flattering assumption: `raw` does not stretch the idle clock by the purification pair cost. Under `full` the required
   Γ_eff·T2 stays ≥ ~10³–10⁶ for N = 5–17. Γ_eff·T2 needed: N=3 ≈ 2–140, N=5 ≈ 25–10⁴, N=9 ≈ 10²–2·10⁵, N=17 ≈ 10³–3·10⁶ (all modes/T2, raw+full).
5. **T2 matters less than k once Γ_eff·T2 ≳ ~20–50.** Moving T2 from 10 to 100 ms barely changes the Γ_eff needed
   at N ≥ 5 (raw); shortening T2 to the published 0.17 ms costs roughly 3–10× in Γ_eff at N = 3–9 (raw) and, at N = 3, needs the cutoff.
6. **Cutoff** (0.5–2 × T2) is irrelevant when Γ_eff·T2 ≫ 1 and matters mainly at the shortest T2 (0.17 ms with k=100 at N = 3).
7. **Gamma multiplier** is interchangeable with k (the cheapest-listing in section B of `sweep_ranked.md` uses Γmult = 4).

### Sweep caveats

- **All Γ_eff and k numbers are what the model asks for, not demonstrated or feasible values.** k = 100 slots with
  Γ_eff > 10⁴ Hz would exceed the 5 kHz attempt rate in `baseline.py` by itself unless slots are separate emitters/channels;
  the sweep does not model that limit (`ATTEMPT_RATE_HZ` is not used by e2e results).
- Purified-run decoherence is optimistic: link-level purification charges no storage decay while a copy waits for its
  partner, and under `raw` neither purification pair-cost stretching of the idle clock nor swap-level waiting is charged.
  `--idle-mode full` is a partial fix (only the nested path stretches the idle clock; sequential swap-level purification does not).
  Real BBPSSW also assumes ideal local gates; DEJMPS would converge faster. Results are therefore upper bounds for the purified rows.
- Purification overlays (residual 0.01 per round, target 0.95, max 8 rounds) are TUNED/policy values; the target 0.95 caps how many
  links can be chained with link-only purification (F_link after purification ≈ 0.95, so w^L falls below the 0.88 requirement at L ≥ 3).
- Rate vs N is non-monotonic because the protocol switches nested ↔ sequential; "max N" is the largest passing N, not a contiguous run.
- Gamma_eff on the log-grid search in `sweep_required_gamma.md` is resolved to a factor 2^¼ ≈ 1.19 and was only searched over
  cutoff ∈ {none, 1×T2} and the three purification modes.
- Locked-baseline inconsistencies (undocumented 2.39× in Γ, T2 above literature) still apply; the k=1 / Γmult=1 / T2=3.6 ms point
  is the only locked one.

## Changelog (AEON review fixes)

- README: model-output banner, per-input labels, results re-stated with `idle=raw`.
- Mislabel fix: purification is **BBPSSW (twirled each round)**, not DEJMPS
  (`dejmps_analytical` kept as a deprecated alias of `bbpssw_analytical`).
- `residual_phase_error` → `depolarizing_residual` (per-round unitless shrink; old CLI flag kept as alias).
- `--purify-idle` default `ideal` → `raw`; `ideal` labeled an optimistic upper bound.
- Idle decay now `E[e^{−Δ/T2}] = 1/(1+τ/T2)` (exact truncated form with cutoff), applied to the
  one earlier-arriving pair only (previously exp(−mean/T2) on both arms in nested).
- `ETA_E2E` comment corrected to RF→DC; `A or B and C` precedence parenthesized.
- New `querp_sim/assumptions.py` registry (printed at run start), plot titles stamped
  "MODEL OUTPUT, NOT MEASURED", runtime bound checks (0.25 ≤ F ≤ 1, R ≤ Γ), and
  `tests/test_sanity.py` (locked values, N=2 = 85 Hz/0.887, N=3 zero-idle F=0.791, decay average).
- **Locked v0.3b values in `baseline.py` are unchanged** (only comments edited).
- **Not applied (deliberately):** capping TPP p_success at the analytical
  value by default, per-qubit/two-qubit and dephasing-vs-depolarizing decay changes,
  charging link-purification storage time, refactoring constants to read from the registry.

- **Multiplexing sweep added** (`querp_sim/multiplexing.py`, `sweep.py`, `tests/test_sweep.py`, registry entries in `assumptions.py`); `baseline.py` and the 6 existing tests untouched.

## Best matches vs published-value tiers (`classify_sweep.py`)

> **MODEL OUTPUT, NOT MEASURED.** Tags every sweep row with a band for T2, k and
> per-slot success p (bands from `TARGETS_AEON.md` §7) and an overall tier = worst band
> (`published` / `plausible` / `beyond published`), then reports the cheapest passing
> combination per tier for N = 3, 5, 9, 17.

```bash
/workspace/.venv_f/bin/python classify_sweep.py
```

- `artifacts/best_matches.md` — per-N, per-tier cheapest combination, "none" where a tier has no pass, and a per-N list of what would need to be shown on a bench.
- `artifacts/best_matches_tiers.png` — max N achievable per tier (stamped).
- `artifacts/sweep_results_classified.csv` (+ `_idle_full_`) — all 35,840 rows with `p_eq`, `t2_band`, `k_band`, `p_band`, `tier`.
- `artifacts/sweep_extension_p_bands_classified.csv` — supplemental runs at the p-band edges.

**p-equivalent:** `p_eq = 0.0071 × Γmult` (Γmult is read as a per-attempt success multiplier;
the `p_eq_strict` column uses Γ_slot / 5 kHz). Γmult ≥ 0.5 in the original grid, so **every
original row is `beyond published` on p**; the supplemental grid (Γmult = 0.0352 → p = 2.5e-4,
0.352 → p = 2.5e-3, k ≤ 40) shows what the model gives inside the lower tiers.

**Result (idle=raw):** max N = 2 published, 3 plausible, 5 beyond published; N = 9 and 17
pass nowhere in the grids (extrapolation only, beyond published on every axis).

**Caveats (repeated):** purified rows are optimistic (link-level purification charges no
storage decay while waiting for its partner; the plausible N = 3 pass needs a link-level purification stage and
fails under idle=full); no fiber/distance loss, power/cryostat load, slot crosstalk or
memory-slot cost is modeled; AEON's bands are partly unverified (only Karapatzakis 2024
was read in full; "published" k ≤ 4 and T2 > 1.7 ms hold on other platforms / at ≤ 50 mK);
nuclear-memory and other-platform numbers are never stacked on an SnV node.


## Revised bands (2026-10-16)

`classify_sweep.py --revised` re-tags the same sweep with the band edges from `TARGETS_AEON_verified.md` §6 (p published ≤ 3e-5, plausible ≤ 2.5e-4; k published = 1, plausible 2–40; T2 unchanged) and writes `artifacts/best_matches_REVISED.md`. `best_matches.md` (old bands) is marked stale. Revised max N (raw|full): published 0|0, plausible 2|2, beyond published 5|4. Model output, not measured; `querp_sim/baseline.py` is unchanged. See `ROADMAP.md`.
