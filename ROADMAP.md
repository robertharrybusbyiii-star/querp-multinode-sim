# QuERP Build-and-Test Roadmap

**Waurika Magnetic Laboratory** · Bob Busby · prepared October 16, 2026 (Central time)

> **Read this first.** The multi-node numbers in this project are **model output, not measurement**. Nothing in this roadmap has been validated on hardware. Every dollar figure comes from an existing bench plan (named in the table) unless it is marked **(estimate)**. Every estimate is my rough guess and needs a real quote. No named contacts or prices have been invented.

Sources used: `TARGETS_AEON_verified.md` (AEON's full-text check, newest and authoritative), `TARGETS_AEON.md`, `REVIEW_AEON.md`, `README.md`, `artifacts/best_matches.md` and `artifacts/best_matches_REVISED.md`, and the plans in `/workspace/ppm_test_plan/`, `/workspace/ppm_build_guide/`, `/workspace/trinity_test_plan/` and `/workspace/nv_test_plan/`.

## 1. Honest starting position

1. The v0.3b node (T2 = 3.6 ms, p = 0.0071, Γ = 85 Hz, F = 0.887, 33.5 mW harvest) is a **budget sketch**, not a measured device.
2. Its per-attempt success p is about **28× above** the best published value (≈ 2.5×10⁻⁴, and that point has F ≈ 0.56). It is about 200× above the one point with F ≈ 0.8 (p ≈ 1–3×10⁻⁵).
3. Its T2 of 3.6 ms is **above** the published 1.57 ms at 1.7 K (Guo). The published 10 ms is at 50 mK in a dilution fridge (Karapatzakis), and that fit has caveats (see §6).
4. The "Trinity" factors (T2 ×2.4, success ×1.18) are **assumptions with no source**. The 12 mW electronics budget ignores the cryostat, and the RF harvest assumes a dedicated transmitter.
5. None of the four bench plans on the box measures an SnV⁻ memory, a spin-photon link or a repeater. They build skills and test classical physics. Real quantum steps need a partner lab (§5).

## 2. Ordered phases

### Phase 0: desk work (no hardware, about days to a couple of weeks of reading and coding **(estimate)**)

| Task | Why | Done when |
|---|---|---|
| Read the sources AEON could not verify: Humphreys supplement, Pr:YSO memory temperature, SnV "4-channel" claim (arXiv:2402.18057), Beukers, Stas, Pompili, the cold-atom and ion multiplexing rows | The sim's "published" bands rest partly on abstract-only values | Each row flagged VERIFIED / CORRECTED in a new version of `TARGETS_AEON_verified.md` |
| Read the Nature versions of Knaut, Liu and Humphreys | AEON read the arXiv versions only | Final numbers compared, differences noted |
| Fix open sim gaps (see `README.md` caveats and `REVIEW_AEON.md`): add fibre or distance loss; charge storage decay to link-level purification while a copy waits for its partner; model dephasing correctly (floor 0.5, not 0.25) and decide per-qubit vs per-pair decay; give the sim a real per-attempt p axis instead of the p = 0.0071 × Γmult mapping; model cryostat power and k-slot cost | These gaps make purified rows optimistic and leave N > 3 untestable. Do **not** edit `querp_sim/baseline.py`; add new scenarios beside it | Re-run `classify_sweep.py --revised` and compare with `best_matches_REVISED.md` |
| Set a realistic cap on memory cutoff (about 0.5–1 s for SiV entanglement storage) | Single-spin T2 (2.1 s) is longer than the published entanglement storage (about 0.5 s, about 1 s with error detection) | Cutoff axis capped in the sweep |

**Confirms or rules out:** nothing about hardware. It only makes the model honest.

### Phase 1: Proton precession magnetometer (PPM) bench

Source: `ppm_test_plan/PPM_Test_Plan.md` and `ppm_build_guide/PPM_Build_Guide.md`.

| Item | From the plans |
|---|---|
| Parts | Mumm's circuit: 2 × ~500 turns of 22 AWG on two ~100 ml bottles, NE5532 and LM386 amps, IRLR120N clamp, 12 V SLA polarizing battery, sound-card logging. Full list in Build Guide §2 |
| Cost | **About $41 verified subtotal for the 12 V build** (about $94 for the 36 V variant). Unverified items (bottles, switch, fuse, passives, sound card, charger) come on top. Optional PASCO Helmholtz pair $345 for the linearity test, or home-wound coils (cost not given) |
| Time | Build: "a few weekends" (NV plan's wording). Field day: 10–20 shots about 30 s apart. A second site at least 1 km away on another day. A linearity day. Sim run takes about 2 min |
| Safety | Start at **12 V**. At 36 V the coil energy (about 173 mJ) is above the IRLR120N single-pulse rating (85 mJ). Flyback spike about −100 V. Fuse the battery |

**Pass/fail (pre-registered in the plan):**

| Test | PASS | FAIL | Otherwise |
|---|---|---|---|
| Test 1: field at Waurika | 10-shot median within ±0.5 % of the WMM2025 value (2063.6 Hz expected; 2053.3–2073.9 Hz), scatter under 1 Hz, controls behave | Miss by more than 0.5 % **and** more than 3σ at **two sites** at least 1 km apart | INCONCLUSIVE |
| Test 2: linearity | Slope 42.577 Hz/µT within 1 % with total 1σ ≤ 0.7 % | Miss by more than 1 % **and** more than 2σ | INCONCLUSIVE |

**What a result confirms or rules out:**

- PASS confirms the linear Zeeman law f = γB with your own equipment, and gives you a calibrated field reference (and calibrated coils) for later work.
- A FAIL most likely points to your coil constant, current reading or alignment, not new physics (the plan says so).
- It tests **no** QuERP model assumption: not T2, p, k, F or purification. It does not test the quadratic term or any QBEH or Nexus claim.

### Phase 2: Trinity lock vs no-lock bench (classical analog)

Source: `trinity_test_plan/Trinity_Lock_Test_Plan.md`.

| Item | From the plan |
|---|---|
| Setup A | Two identical wind-up metronomes on a board on soda cans; clamped-board control. Parts about **$60–80** |
| Setup B | Two Arduinos, an NE555 timer, RC filter, a removable LINK jumper. Parts about **$30–40** |
| Time | Setup A session about 3–4 hours; Setup B about 3 hours; pilots first. Phase 2 (modulators on) only after the A = 0 results |
| Pre-registration | Fill in Section 9 and date-stamp it **before** collecting data |

**Pass/fail (decision rule, plan §7):** lock is claimed only if all hold: (1) the coupled K has a 95 % CI excluding 0 in at least 4 of 5 runs, K > |Δ|, and at least 4 of 5 runs are locked; (2) the clamped or unplugged control gives K ≈ 0 and slips at |Δ|/2π (within 30 %); (3) at least one independent method agrees within about 30 %; (4) the label-only and swapped controls behave. If K is above 0 but below |Δ|, report "coupling detected, no lock". If a control fails, make no claim until the stray coupling is found.

**What a result confirms or rules out (be strict):**

- A positive result shows an Adler-type phase controller can grip a **classical** oscillator through an identified link, with K **measured** (the plan expects about 0.1–2 rad/s, not the script's 201 rad/s).
- It is the only bench that touches the sim's "Trinity" idea, but only as a **precondition**. It does **not** measure T2, so it does not validate the assumed ×2.4 T2 or ×1.18 success factors, and it validates no quantum row of the sweep.
- A negative result (coupled K looks like the control) says the controller as built cannot grip even a cooperative bench oscillator. That is a reason to drop or redesign the Trinity factors in the sim.
- Testing the T2 factor itself would need a real spin memory with and without a lock. That is a Phase 4 item and needs a partner lab.

### Phase 3: NV-diamond Zeeman bench (last)

Source: `nv_test_plan/NV_Zeeman_Test_Plan.md`.

| Item | From the plan |
|---|---|
| Parts | Diamond lot ($250–600), ADF4351 microwave source, RF amp and loop, green LED, BPW34 detector with red filter, ESP32, **±1 % gaussmeter** (about $285), field source |
| Cost | DIY **about $650–1,050**; about **$1,000–1,500** with Helmholtz coils and goggles. openUC2 kit about **€1,000** (vendor wording). Other kits: quote only |
| Time | "Weeks" for a first build that shows dips. Getting to 1 % field calibration is a separate job |
| Free first step | Run `nv_zeeman_sim.py` and fit a public ODMR dataset (plan Option C; datasets not yet opened) |
| Safety | Prefer an LED over a laser. Laser goggles if a laser is used. Keep RF antenna small and terminated. Magnet and coil cautions in the plan |

**Pass/fail:** PASS when γ is within ±2 % of 28.03 GHz/T **and** total 1σ is ≤ 1.5 %. FAIL when off by more than 2 % **and** more than 2σ. Otherwise INCONCLUSIVE. With a ±1 % meter the plan's simulation gave PASS 92 % of the time even when the physics was right, so check the field calibration before calling a FAIL real.

**What a result confirms or rules out:**

- PASS reproduces the standard NV Zeeman slope and shows you can run room-temperature ODMR.
- It does **not** measure SnV⁻ coherence, a cryogenic memory, spin-photon entanglement or a remote link. It tells you nothing about p, k or T2 in the repeater sweep.

### Phase 4: real quantum steps (needs a partner lab, not a home bench)

Only after Phase 0. See §4 and §5. **Costs for this phase are not estimated here.** Get quotes.

### Bench cost roll-up (arithmetic on the plan figures only)

| Phase | Low | High | Note |
|---|---|---|---|
| 1 PPM | about $41 | about $94 (+$345 optional Helmholtz) | Unverified small parts extra |
| 2 Trinity | about $90 | about $120 | Sum of Setup A and B ranges |
| 3 NV (DIY) | about $650 | about $1,500 | Helmholtz pair might be shared with Phase 1 **(estimate)** |
| **Total** | **about $781** | **about $1,714** | Before unverified parts and shipping |

## 3. Decision gates

| Gate | Outcome | What it means | Action |
|---|---|---|---|
| G0 (after Phase 0) | Remaining sources contradict a band again | Published bands move again | Re-run `classify_sweep.py --revised` with new edges; update tiers before any spend |
| G0 | Sim with loss and honest purification idle charge passes **no** N ≥ 3 combination even at "beyond published" | The N = 3 and N = 5 results were artifacts | Drop N > 2 as a target; scope the project as a single-link or single-node study |
| G1 (PPM) | Controls fail, or FAIL at two sites after checking clock and Kp | Instrument or site problem, or a real anomaly | Fix and repeat; do not widen the tolerance. Do not proceed to NV until PPM is understood |
| G2 (Trinity) | Control K above 0 | Stray coupling | Find it first (shared table, supply or ground) |
| G2 | Coupled K indistinguishable from control | Controller cannot grip a cooperative oscillator | Stop treating the Trinity factors as anything but a free parameter; remove them from headline claims |
| G2 | Lock confirmed on classical oscillators | Precondition only | Does **not** unlock claims about T2; plan a spin-memory test via a partner (Phase 4) |
| G3 (NV) | PASS | Skills and apparatus work | Decide whether to approach a partner lab |
| G3 | FAIL after recalibration | Apparatus problem (most likely) | Fix before drawing any physics conclusion |
| G4 (partner) | No partner access to a cryogenic color-centre setup | No path to any quantum row | Keep the project as a model and educational bench series |
| G4 | Partner measures p or T2 far below the sim inputs | Sim inputs are optimistic by that factor | Re-baseline v0.3b to the measurement (new version; keep the old one) |

## 4. Realistic targets

**Model side (re-tagged with AEON's revised bands, `best_matches_REVISED.md`; model output only).** The earlier tiers in `best_matches.md` were stale and have been **re-run**. Max chain length N that passes F ≥ 0.88 and R ≥ 1 Hz:

| Tier (revised bands) | Max N (idle = raw) | Max N (idle = full) | Earlier (stale) result |
|---|---|---|---|
| Published (p ≤ 3×10⁻⁵, k = 1, T2 ≤ 10 ms) | **0** | **0** | 2 |
| Plausible (p up to 2.5×10⁻⁴, k up to 40, T2 up to 100 ms) | **2** | **2** | 3 |
| Beyond published | **5** | **4** | 5 |

Reading it plainly:

- **N = 2** (one link) passes only at the plausible tier: either k = 1 with p ≈ 2.5×10⁻⁴ (the edge of published values at low fidelity, F ≈ 0.56 in Knaut), or published-level p ≈ 3×10⁻⁵ with k = 3 slots (R ≈ 1.08 Hz; multi-slot operation at F ≥ 0.8 has not been shown). The F = 0.887 in the model is an **input**, not a result. No published solid-state link combines F ≥ 0.88 with R ≥ 1 Hz.
- **N = 3** needs p ≈ 0.028 (about 114× the best published p) and T2 = 100 ms with optimistic link purification. It is beyond published, and the pass disappears under stricter idle decay unless k ≥ 5 and swap-level purification are added.
- **N = 5** needs k = 50 slots and p ≈ 0.028 (about 114× the best published p, about 950× the p published at F ≈ 0.8). Beyond published on every axis.
- **N = 9 and 17** pass nowhere. They are not bench targets.

**Lab side (what a lab with a dilution fridge could credibly attempt):**

- **N = 2** (two nodes, one heralded link) is the credible target. Published results at roughly this level exist for SiV (F ≈ 0.80 average at about 20 mHz; about 0.56 at about 1 Hz) and NV (F = 0.81 at 6 Hz, attempt-limited), per AEON's verified file. An SnV⁻ spin-photon link has not been shown in anything read so far.
- **N = 3** (one swap) is a stretch goal. Pompili is on AEON's unverified list and should be read first in Phase 0. Do not assume a particular rate or fidelity until it is checked.
- **N ≥ 5** needs a **memory or link-rate breakthrough**: p up to two orders of magnitude above anything published at useful fidelity, k far above the demonstrated memory–memory multiplexing (about 4 modes, F ≈ 0.80 in Liu, about 1.1 entanglements per hour), or memory that survives long enough for purification.
- Nuclear-spin memory (1.35 s on SnV ¹³C at 50 mK; 2.1 s on SiV ²⁹Si at under 200 mK) is a different platform. The 1.35 s SnV number is a single-spin coherence only, with no link attempts or entanglement run on it. SiV entanglement storage was about 0.5 s (about 1 s with error detection). **Do not stack nuclear numbers on electron numbers** until someone demonstrates the combination.

## 5. Partners and collaborations needed (generic)

| Need | Why | Not available at home |
|---|---|---|
| A university or national-lab group with a dilution refrigerator (≤ 50 mK) and a color-centre setup | T2 above 1.7 ms and any remote entanglement need it | Yes |
| Diamond material and processing (growth, implantation, nanofabrication) | SnV⁻ or SiV samples with a cavity or waveguide | Yes |
| Photonics and telecom-conversion expertise | Spin-photon interface and fibre links; the published SiV link needed frequency conversion (5.4 % bidirectional efficiency) | Yes |
| Cryogenic and RF engineering | Thermal load, cabling, pulse sequences and dynamical decoupling | Partly |
| Quantum-network testbed operators (deployed fibre) | Deployed-fibre rates are very low (SiV 35 km: about 0.23 mHz average) | Yes |
| A quantum-information theorist to review the sim | Purification, dephasing model, swap composition | Partly (AEON has reviewed once) |
| Funding or lab-time sponsor | Dilution-fridge time is expensive (cost **not estimated here**) | Yes |

How to approach: share `README.md`, `REVIEW_AEON.md`, `TARGETS_AEON_verified.md` and this roadmap, and lead with the caveats. Offer the model as a question, not a claim.

## 6. Plain-language caveats

- **Model output, not measurement.** The sweep, the tiers and the N = 2 to 5 results describe what the *model* needs. They do not say hardware can do it.
- **Purified rows are optimistic.** Link-level purification charges no storage decay while a copy waits. Under stricter idle decay the plausible N = 3 pass disappears.
- **Not modelled:** fibre loss and distance, power and cryostat load, crosstalk between slots, and the memory slots k costs (at least 2k per node). The 12 mW electronics budget ignores the cryostat. The 33.5 mW harvest assumes 60 µW/cm², which needs a dedicated transmitter.
- **The p-equivalent is a modelling choice** (0.0071 × Γmult). The locked Γ = 85 Hz carries an undocumented ×2.4 against 5000 × 0.0071.
- **Published numbers with corrections (AEON):** Knaut's 35 km deployed link is about 0.23 mHz average (the 6 mHz was a ~20 m run); about 1 Hz comes with average F ≈ 0.56 (0.86 is the best state at the lowest rate); the 100 Hz and F = 0.95 figures are the authors' projections. Humphreys reports no measured p (derived about 3×10⁻⁵ at F = 0.81). Lago-Rivera's "62 modes" is post-hoc sorting of recorded data (raw concurrence about 0.0115). The 92 % and 77 % fidelities belong to photon–memory work, not a link.
- **T2 caveats:** the published 10 ms uses a stretched-exponential fit with exponent fixed at 4 on data normalised to 0.5, measured only to 64 pulses at 50 mK. Do not read it as a free-idle memory time.
- **Unverified:** Humphreys supplement, Pr:YSO temperature, SnV 4-channel claim, Beukers, Stas, Pompili, cold-atom and ion multiplexing rows, and the Nature versions of the papers. The Knaut fidelity-vs-rate values were read off a figure (approximate).
- **Bench plans do not validate QuERP.** PPM and NV test standard Zeeman physics. The Trinity bench tests a classical lock and does not measure T2. A pass on any of them confirms ordinary physics and skills, not a QuERP row.
- **Estimates:** every figure marked **(estimate)** is a guess to replace with quotes or measurements. Phase 4 costs and timelines are deliberately not guessed.

## Files

- Model: `/workspace/querp-multinode-sim/` (`README.md`, `classify_sweep.py`, `artifacts/best_matches_REVISED.md`, `artifacts/best_matches.md` marked stale)
- AEON: `TARGETS_AEON_verified.md`, `TARGETS_AEON.md`, `REVIEW_AEON.md`
- Bench plans: `/workspace/ppm_test_plan/`, `/workspace/ppm_build_guide/`, `/workspace/trinity_test_plan/`, `/workspace/nv_test_plan/`
