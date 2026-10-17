# TARGETS_AEON_verified — full-text check of the key sources behind TARGETS_AEON.md
Written 2026-10-16 (America/Chicago) by AEON. Nothing here is model output. No other repo file was changed.

**Method.** Full PDFs fetched from `https://arxiv.org/pdf/<id>` with curl and converted with `pdftotext`. Numbers below were read in the extracted text. Figure values were read off a rendered page image, marked "(read off figure, approximate)".
Sources fully read: arXiv:2310.01316v2 (Knaut, **main text + Extended Data + Supplementary Information, all inside the arXiv PDF**), 1712.07567 (Humphreys, **7-page main text only; its Supplementary Information is NOT in the arXiv PDF and was not read**), 2101.04945v2 (Liu), 2101.05097 (Lago-Rivera), 2106.05079v3 (Rakonjac/Lago-Rivera, read because TARGETS cited it), 2509.03354v1 (Resch/Karapatzakis), 2403.00521 (Karapatzakis), 2307.11916 (Guo).
Not re-checked (still as in TARGETS_AEON.md, i.e. ABS/SUM): every other row, including Rosenthal, Debroux, Beukers, Trusheim, Görlitz, Sukachev, Bhaskar, Stas, Pompili, Hermans, Stolk, Kalb, Stephenson, Krutyanskiy, Wang, Pu, Sinclair, Ortu, arXiv:2402.18057, 2403.13623, 2501.04131.
Flags: VERIFIED = matches full text; CORRECTED = TARGETS value was wrong or misleading; ABSTRACT-ONLY = could not confirm beyond the abstract; COULD NOT ACCESS.

---
## 1. Knaut et al., Nature 2024 — SiV, arXiv:2310.01316 (full text incl. SI)
Setup facts: two SiV nodes in separate dilution fridges, **base temperature < 200 mK** (Fig. 1 caption; Methods). 6 m line-of-sight; ~20 m fibre (electron-electron run) or 20 m + spools/35 km loop with QFC (nuclear runs). Cooperativity node A 12.4, node B 1.5. Weak coherent states (not single photons) encode the time-bin qubit.

| Quantity | Value in TARGETS_AEON.md | Value found in full text (ref) | Flag | Note |
|---|---|---|---|---|
| Per-attempt heralding probability, e–e | 7.7×10⁻⁶ to 2.5×10⁻⁴ | Same: Extended Data Table I (7.7×10⁻⁶ – 2.5×10⁻⁴; R = 10 kHz, D = 34 %, r_suc 16 mHz – 1050 mHz) | VERIFIED | η varies with mean photon number µ of the WCS. Higher µ gives higher η and lower F (Fig. 2c). Table S3 gives a representative η = 5.0×10⁻⁵ (visible shifting) and 3.7×10⁻⁵ (telecom QFC) at µ = 0.1. |
| Per-attempt p, nuclear–nuclear | 2.0×10⁻⁵ (1.4 kHz rep, 20 % duty) | Same: ED Table I (η = 2.0×10⁻⁵, R = 1.4 kHz, D = 20 %) | VERIFIED | This is the **decoupling-run (≈20 m fibre)** value, not the deployed-loop value. |
| Peak e–e success rate | up to ~1 Hz | "success rate up to 1 Hz" (Intro, Fig. 2c); max 1050 mHz (ED Table I) | VERIFIED | |
| e–e Bell fidelity | 0.86(3) / 0.74(3) | F(Φ⁻ee) = 0.86(3), F(Φ⁺ee) = 0.74(3) (Fig. 2b caption and text) | VERIFIED | The two numbers are for the two heralded Bell states. Their mean is ≈ 0.80. |
| **e–e fidelity vs rate (not in TARGETS as a pair)** | TARGETS pairs "~1 Hz" with "F = 0.86" | Fig. 2c: average state fidelity ≈ 0.80 at ≈ 17–20 mHz, ≈ 0.77 at ≈ 70 mHz, ≈ 0.66 at ≈ 200 mHz, ≈ 0.58 at ≈ 450 mHz, **≈ 0.56 at ≈ 1 Hz** (read off figure, approximate; error bars ≈ ±0.02–0.03). Paper says entanglement stays above the 0.5 classical limit up to 1 Hz | **CORRECTED** | "~1 Hz at F = 0.86" is misleading. 0.86 is the Φ⁻ state at the lowest-rate point. At ~1 Hz the average fidelity is ≈ 0.56. |
| Nuclear (²⁹Si) Bell F, 35 km deployed loop | 0.69(7) after error detection (nuclear) | F(ED, Φ⁻nn) = 0.69(7) (Fig. 4c; text) | VERIFIED | Error-detection (ED) postselected on flag qubit. |
| Nuclear Bell F, local, XY8-1 10 ms | 0.77(5) with ED | F(ED) = 0.77(5); raw (no ED) 0.64(5) (Fig. 3b caption) | VERIFIED | Raw value 0.64(5) was missing from TARGETS. |
| Nuclear link rate | "6 mHz" stated next to the 35 km result | 6 mHz is the **decoupling-run average** (ED Table I, ~20 m fibre). Table S6: average rate 8.2 mHz at 0 km, 5.8 / 2.9 / 5.0 / 1.5 mHz at 10 / 20 / 30 / 40 km spools, **0.23 mHz average at 35 km deployed (ED rate 0.10 mHz Φ⁻, 0.14 mHz Φ⁺)** | **CORRECTED** | The 35 km deployed nuclear rate is ≈ 0.1–0.2 mHz (≈ 1 per 1.5–3 h), about 26–60× below "6 mHz". Source of the deployed-loop rate is Table S6 only. |
| Rate loss factor from QFC | — | Bidirectional QFC total efficiency 5.4 % (Methods); total photonic link efficiency 0.15 % (QFC) vs 0.20 % (visible frequency shifting) (Table S3) | new (VERIFIED) | |
| Projected improvements | "~0.95 / ~100 Hz after improvements (SUM, not read)" | Supplement §VII: fidelities "around 0.95 could be achievable in the near future"; with 95 % fibre coupling and cavity reflectance 90 %: ×7.7 → ≈ 8 Hz; removing frequency shifting via strain tuning ×13.5 → ≈ 100 Hz (SI §VII, last paragraph) | VERIFIED as a projection | Authors' projection only, not a measurement. The 0.95 and 100 Hz are separate statements and not shown as a joint operating point. |
| Electron-spin T2 and temperature | — (not in TARGETS for SiV electron) | T2,e (XY8-1) = 125 µs (node A), 134 µs (node B); B ≈ 0.39–0.40 T; T < 200 mK (Table S4, Fig. 1) | new (VERIFIED) | Paper estimates electron decoherence limits nodes to ≈ 25 km. |
| Nuclear (²⁹Si) memory time | 2.1 ± 0.1 s (via Stas 2022, ABS) | T2,n (XY8-1) = 339 ms (A), 140 ms (B); **T2,n (XY8-128) = 2.11 s (A), 2.1 s (B)** (Table S4, Fig. S4). Saturates near 2 s (SI §VIII). Remote nuclear entanglement survives XY8-128 to **≈ 500 ms without ED, ≈ 1 s with ED** (Fig. 3c) | VERIFIED | Entanglement storage (≈ 0.5–1 s) is shorter than single-spin T2 (2.1 s). |
| Multiplexing mode count | none | No multiplexing in this paper. Only a mention of future multi-qubit/chip scaling | VERIFIED (nothing to find) | |

---
## 2. Humphreys et al., Nature 2018 — NV, arXiv:1712.07567 (main text only; SI not available)
| Quantity | Value in TARGETS_AEON.md | Value found in full text (ref) | Flag | Note |
|---|---|---|---|---|
| p_det | ≈ 4×10⁻⁴ | "for our system's p_det ∼ 4×10⁻⁴" (p. 3, text after Eq. 5) | VERIFIED | |
| Per-attempt success formula | 2·p_det·α | "probability of successfully heralding entanglement is given by 2 p_det α" (p. 3); fidelity F = 1 − α | VERIFIED | |
| Per-attempt p numbers | 4×10⁻⁵ (α = 0.05) to 2.4×10⁻⁴ (α = 0.3); attempt ≈ 5.5 µs | Attempt duration 5.5 µs (Fig. 2 caption). Formula gives 4.0×10⁻⁵ and 2.4×10⁻⁴ (arithmetic). Implied by the reported rates × 5.5 µs: 6 Hz → 3.3×10⁻⁵, 39 Hz → 2.1×10⁻⁴ (my arithmetic) | VERIFIED (formula, attempt time); **p not reported directly** | The paper reports rates, not a measured p per attempt. Treat p ≈ 3×10⁻⁵ (F 0.81) and ≈ 2×10⁻⁴ (F 0.60) as derived. |
| Rate vs fidelity | 39 Hz @ F 0.60(2); 6 Hz @ F 0.81(2) | "F = 0.81(2) at r_ent = 6 Hz (α = 0.05)"; "r_ent = 39 Hz with F = 0.60(2) (α = 0.3)" (p. 4; abstract: up to 39 Hz) | VERIFIED | Fig. 2e caption: the rate is calculated from the 5.5 µs attempt duration and the heralding probability. I read this as an **attempt-limited rate** that excludes phase-stabilisation and NV-check overhead (my reading; the overhead details are in the SI, not available). |
| Deterministic delivery | 9.9 Hz @ 0.56(1) | "α = 0.2 and a rate of 9.9 Hz … fidelity of 0.56(1)" (p. 6); with classically correlated state delivered on failed cycles: 0.62(1) at 9.9 Hz | VERIFIED | 9.9 Hz is the **delivery clock**, with an unentangled state (F_unent = 0.04) delivered when no herald occurs. Delivery clocks tested 7–12 Hz, α = 0.12 and 0.2; offline cycles 0.8 % (p. 6). |
| Entangled-state decoherence | — | Coherence time of the remote entangled state 200(10) ms (r_dec = 5.0(3) Hz); single-node T2 with XY8: 290(20) ms and 680(70) ms (from T2* ≈ 5 µs) (p. 5–6). Quantum link efficiency η_link ≈ 8 | new (VERIFIED) | Temperature of the NV cryostats **not stated in the main text** (SI). |
| Multiplexing | none | None | VERIFIED (nothing to find) | |

---
## 3. Liu et al., Nature 2021 — absorptive memories (Nd:YVO₄), arXiv:2101.04945v2; and Lago-Rivera et al., Nature 2021 (Pr:YSO), arXiv:2101.05097
### 3a. Liu (arXiv:2101.04945)
| Quantity | Value in TARGETS_AEON.md | Value found in full text (ref) | Flag | Note |
|---|---|---|---|---|
| Fidelity | F = 80.4 ± 2.2 % | "F = (80.4 ± 2.2)%" (main text; abstract) | VERIFIED | Fidelity of the heralded two-photon entanglement stored in the memories; Bell S = 2.43 ± 0.13 at best. |
| Storage efficiency, storage time | ≈ 12–14 % at 55.6 ns | 14.3(1) % (node A), 12.5(1) % (node B), 55.6 ns; extendable to > 1,250 ns with lower efficiency (main text) | VERIFIED | Memories at **1.5 K**, closed-cycle cryostats (Methods). |
| Temporal modes used | ~4 (≈ 56 allowed by time-bandwidth) | "55.6 ns / 12.5 ns ≈ 4 distinguishable temporal modes … actually stored simultaneously"; "can be further increased to approximately 56" (p. 7) | VERIFIED | The ~56 is a stated potential, not demonstrated. |
| Rate | — | Entanglement distribution rate ≈ 1.1 per hour (4-fold coincidences); average heralding rate 100 Hz; Nd:YVO₄ has stored "100 temporal modes" and "51 spatial modes" in **earlier work** cited from refs 21, 22 (p. 7) | new (VERIFIED) | EDR is 1.1/h, so this is not a high-rate link. Nodes 3.5 m apart. |

### 3b. Lago-Rivera (arXiv:2101.05097)
| Quantity | Value in TARGETS_AEON.md | Value found in full text (ref) | Flag | Note |
|---|---|---|---|---|
| Heralding rate | up to 1.4 kHz | "1.43 kHz at one output of the idler beam-splitter, with a duty cycle of 43 %" (p. 3). It was measured in the 2 µs-storage configuration (heralding rate drops at longer storage, Fig. 3b) | VERIFIED | Duty cycle was not in TARGETS. |
| Storage time | up to 25 µs | Up to 25 µs, concurrence positive for all storage times; **at 25 µs concurrence is positive at > 5σ** (p. 4) | VERIFIED | |
| **Entanglement quality** | "Fidelity not in the Nature abstract" (blank) | Total concurrence C₁ = 1.15(5)×10⁻², C₂ = 1.15(7)×10⁻² (2 µs storage); two-photon suppression h_c⁽²⁾ = 0.036(8); visibilities 84(2) % and 84(4) %. Concurrence rescaled to the crystal (loss-corrected): 7.3(5)×10⁻² and 7.4(5)×10⁻². **"Effective fidelity" F_eff = 0.92(1) and 0.92(2) uses only the 1- and 2-excitation terms of the density matrix** (excludes the vacuum term p₀₀) (p. 3) | **CORRECTED / new** | Raw concurrence ≈ 0.01 is just above zero, with the vacuum term dominant. The 0.92 is an effective fidelity that excludes loss. It is not comparable to the Bell-state fidelities of NV/SiV nodes. |
| Mode count | 62 temporal modes | "Considering a single temporal mode duration of 400 ns … we split τ into 62 temporal modes. By dividing the whole measuring time in 'communication trials' of 25 µs, we sorted the idlers into the 62 modes according to their arrival time" (p. 4, Fig. 4c). Heralding rate rose linearly with allowed modes, concurrence unchanged | **CORRECTED (meaning)** | 62 is the count obtained by **post-processing the data of the 25 µs storage run** (t_com = 25 µs ≈ 5 km), not 62 separately heralded memory slots operated in real time. The linear rate gain is a calculation from that sorting. Mode-resolved real-time multiplexing was not demonstrated. |
| Platform/temperature | — | Pr³⁺:Y₂SiO₅, closed-cycle cryostats; memories use N ≈ 10⁷ ions (p. 2). Temperature not stated in main text | new | Pr:YSO in the follow-up is at 3 K (see 3c). |
| Pump-limited potential | — | "could be boosted to ∼15.6 kHz while maintaining positive concurrence" (p. 4) | new (VERIFIED, projection) | |

### 3c. Follow-up arXiv:2106.05079 (Rakonjac et al.)
| Quantity | Value in TARGETS_AEON.md | Value found in full text (ref) | Flag | Note |
|---|---|---|---|---|
| Fidelities 92(2) % / 77(2) % | Listed under "Multimode heralded memory-memory entanglement (REI)" as "follow-up conditional fidelities" | Title: "Entanglement between a telecom photon and an on-demand multimode solid-state quantum memory". Conditional fidelity 92(2) % (excited-state storage, visibilities 90(3) %, 88(3) %) and 77(2) % (spin-wave storage, visibilities 71(3) %, 68(5) %), computed as (3V+1)/4 assuming white noise (p. 3–4). Storage up to 47.7 µs. Memory at 3 K | **CORRECTED** | This is **photon–memory** entanglement (one memory, one telecom photon), **not memory–memory**. It must not be quoted as a repeater-link fidelity. |
| Mode count (spin-wave) | — | "Our system allows the storage of **17** independent temporal modes" (420 ns width; AFC storage + 3 µs control pulse); "would allow an increase in entanglement rate of a factor of 17 … or half of this for time-bin" (p. 3, 5) | new (VERIFIED) | A capacity statement, not a multiplexing demonstration. |

---
## 4. arXiv:2509.03354 — ¹³C nuclear spin on SnV (full text)
**Authors / title (resolved):** J. Resch, I. Karapatzakis (equal contribution), M. Elshorbagy, M. Schrodin, P. Fuchs, P. Graßhoff, L. Kussi, C. Sürgers, C. Popov, C. Becher, W. Wernsdorfer, D. Hunger. "High-fidelity control of a ¹³C nuclear spin coupled to a tin-vacancy center in diamond" (KIT / Saarland / Kassel). arXiv v1, 3 Sep 2025.

| Quantity | Value in TARGETS_AEON.md | Value found in full text (ref) | Flag | Note |
|---|---|---|---|---|
| Temperature | 50 mK | Sample in a home-built dilution cryostat, **base temperature 50 mK**, Nb coplanar waveguide, 3D vector magnet (§I) | VERIFIED | The sample temperature itself is not separately reported. |
| Nuclear DD coherence | 1.35(3) s | T₂(N=128) = **1.35(3) s** with CPMG-128; T₂(N=1) = 233(8) ms (§V, Fig. 3) | VERIFIED | |
| Hahn-echo T2 | ≈ 167 ms (SUM) | **T₂ = 167(9) ms**, stretch ξ = 1.7(2) (§V) | VERIFIED (was SUM) | |
| T2* | 1.5(1) ms | Mean T₂* = 1.5(1) ms from Ramsey (Fig. 2d); Gaussian decay | VERIFIED | |
| Scaling with N | — | T₂ ∝ N^β with **β = 0.36** (below the 2/3 expected for an Ornstein-Uhlenbeck bath); stretch ξ from 1.5 to 2.4 (mean 2.0(1)). Authors say not limited by electron-spin lifetime and visibility does not fall with pulse number | new | Sub-linear. 1.35 s was the longest tested (N = 128), not a saturation. |
| Single-qubit gate fidelity | 99.92(1) % | "single-qubit gate fidelity of 99.92(1) %" (primitive gate); Clifford fidelity 99.85(2) % (§IV) | VERIFIED | |
| Initialisation | 99.74(3) % | F_init = 99.74(3) %, 5–10 ms pumping (Fig. 1c, §II) | VERIFIED | |
| Conditions | "SC waveguide" | B = 60 mT (Rabi), 106 mT (coherent-control quality); hyperfine ODMR splitting 44.5 MHz ("most probably one of the next neighbours"); natural-abundance (1.1 %) ¹³C membrane; nuclear Rabi frequency 13 kHz at 10 dBm RF (§II–III) | new | A **strongly coupled** ¹³C. The field for the DD run was not extracted. |
| What is NOT shown | — | No spin-photon or nuclear-photon entanglement, no remote entanglement, no storage-while-attempting experiment. Readout goes through the electron spin | new | It is a memory-qubit control result only. |

---
## 5. Karapatzakis 2024 (arXiv:2403.00521) and Guo 2023 (arXiv:2307.11916) — re-check
| Quantity | Value in TARGETS_AEON.md | Value found in full text (ref) | Flag | Note |
|---|---|---|---|---|
| Best electron T2 | 10(1) ms, CPMG-64, 50 mK | T₂,CPMG64 = 10(1) ms (§IV); 50 mK dilution refrigerator (§I) | VERIFIED | Fit uses a **stretched exponent fixed at ξ = 4**, and the data are normalised so the final saturating points correspond to fidelity 0.5 (App. C). The paper notes the decoupling fidelity decreases with pulse number because of pulse errors from the proximal nuclear spin. |
| Scaling | T₂ ∝ N^0.95(9) | β = 0.95(9) ("almost linear"), attributed to strongly reduced Ohmic losses with the SC waveguide (§IV) | VERIFIED | Measured only to N = 64. |
| Hahn echo | 179(4) µs (B ∥); 433(23) µs (B ⟂) | Same (§IV) | VERIFIED | CPMG was only run in the parallel field. |
| Field for CPMG | "B ∥ axis (93 mT)" | Main text says B∥ = 96 mT (§III); App. C says 93 mT for the coherence measurements; Fit gives B_par = 96.7(2) mT | VERIFIED with a note | Paper is internally inconsistent (93 vs 96 mT). |
| T2*, π pulse | 2.1(2) µs; 196 ns | 2.1(2) µs (Ramsey); 196 ns π-pulse at 10 dBm, 3149.1 MHz (App. C) | VERIFIED | |
| T1 | >1 s at 50 mK (unstrained); 2.59(45) ms at 6.43 K (strained) | Already FT in TARGETS. This pass re-confirmed: unstrained T₁ > 1 ms below 4 K, > 1 s at base temperature (App. A) | VERIFIED | |
| Guo: Hahn / CPMG-128 | 100(1) µs; 1.57(8) ms; T₂ ∝ N^0.593(8); 1.7 K | CPMG-1 100(1) µs; CPMG-128 1.57(8) ms; β = 0.593(8); T₂* 2.5(1) µs; all at 1.7 K (Fig. 4, text) | VERIFIED (was ABS) | |
| Guo: 4 K | 223(10) µs; Hahn ≈ 74 µs | T₂,2XY8 = 223(10) µs ("depolarization-limited"); T₂,echo = 74(2) µs; T₂* = 2.7(1) µs at 4 K | VERIFIED (74 µs was SUM) | |

---
## 6. Revised sweep bands (changes to §7 of TARGETS_AEON.md)
Unchanged: SnV electron T2 bands (PUBLISHED ≤ 10 ms at 50 mK, ≤ 1.57–1.7 ms at 1.7 K, ≤ 0.43 ms Hahn). Add the caveats that the 10 ms comes from a ξ = 4 stretched-exponential fit of data normalised to 0.5, and that CPMG was measured only to N = 64.

| Parameter | Change |
|---|---|
| **Per-attempt success p** | **Split by fidelity.** PUBLISHED, any F above 0.5: p ≤ 2.5×10⁻⁴ (Knaut, F ≈ 0.56 at ~1 Hz; Humphreys ≈ 2.1×10⁻⁴ derived, F = 0.60). PUBLISHED at F ≈ 0.8: p ≈ 1–3×10⁻⁵ (Knaut ≈ 0.80 at ~20 mHz, η ~ 10⁻⁵; Humphreys ≈ 3×10⁻⁵ derived, F = 0.81). No published solid-state link combines p ≳ 10⁻⁴ with F ≥ 0.8. PLAUSIBLE band (2.5×10⁻⁴ – 2.5×10⁻³) now reads **BEYOND for a target of F ≥ 0.88**. The baseline 0.0071 is ≈ 28× above the best p and ≈ 200× above the F ≈ 0.8 point. |
| **Link rate / fidelity pair** | Knaut's "~1 Hz at 0.86" must be read as **≈ 1 Hz at F ≈ 0.56** (0.86 is the Φ⁻ state at the lowest-rate point, ≈ 0.80 average at ≈ 20 mHz). Published solid-state pairs for the sweep: NV 6 Hz @ 0.81, 39 Hz @ 0.60 (attempt-limited rates); SiV ≈ 0.02 Hz @ 0.80, ≈ 1 Hz @ 0.56. Any F ≥ 0.88 with R ≥ 1 Hz is BEYOND PUBLISHED for solid-state. |
| **Deployed-fibre rate** | A 35 km nuclear link has a published rate of ≈ 0.2 mHz (F = 0.69(7) with ED), not 6 mHz. Use ≈ 0.2 mHz if the sweep is anchored to deployed fibre. |
| **Multiplexing k** | Lago-Rivera's 62 modes are a post-processed count with concurrence ≈ 0.01 (F_eff 0.92 excludes loss), and Liu's actual experiment stored ≈ 4 modes at once (≈ 56 potential). Rakonjac's 17 spin-wave modes are a capacity statement for photon–memory entanglement. Keep k ≤ 4 as the **demonstrated memory–memory** value (Liu) and k ≤ 62 as "published as an analysis-based mode count, low-fidelity regime". For quality-matched sweeps (F ≥ 0.8) there is no published multimode memory–memory demonstration, so k > 1 is PLAUSIBLE at best. SnV hardware "k ≤ 4" (arXiv:2402.18057) is still ABSTRACT-ONLY. |
| **Cutoff / nuclear memory** | The published **entanglement** storage time on SiV is ≈ 0.5 s (≈ 1 s with ED), shorter than the 2.1 s single-spin T₂. Cap an "entanglement cutoff" at ≈ 0.5–1 s for ²⁹Si (Knaut). SnV ¹³C: 1.35 s is a single-spin DD coherence (strongly coupled ¹³C, N = 128, β = 0.36), with no entanglement or link attempts run on it. |

## 7. Summary
**Corrections (4 substantive):**
1. Knaut deployed nuclear link rate is **0.23 mHz average (0.1–0.14 mHz after ED)** at 35 km (Table S6). The "6 mHz" is the local decoupling-run rate.
2. Knaut "~1 Hz at F = 0.86" conflates two points. At ≈ 1 Hz the average fidelity is ≈ 0.56 (read off Fig. 2c), and 0.86 is Φ⁻ at ≈ 20 mHz.
3. Lago-Rivera's "62 temporal modes" is a post-processed mode count from the 25 µs storage run, with total concurrence ≈ 1.15×10⁻² and an effective fidelity of 0.92 that excludes the vacuum term. The "92(2) % / 77(2) %" fidelities in TARGETS belong to **photon–memory** entanglement (arXiv:2106.05079), not memory–memory.
4. Humphreys' per-attempt p is not reported directly. It is derived from p = 2·p_det·α and the reported rates. The 39 Hz / 6 Hz are attempt-limited rates, and 9.9 Hz is a delivery clock.

**Verified (previously ABS/SUM):** Knaut η range, rates, Bell fidelities, T2 values, 2.1 s nuclear T2 and the 100 Hz projection. Humphreys p_det ≈ 4×10⁻⁴, 39 Hz @ 0.60, 6 Hz @ 0.81, 9.9 Hz @ 0.56. Liu F = 80.4 ± 2.2 %, efficiencies, ~4 modes. arXiv:2509.03354 (Resch/Karapatzakis…), 1.35(3) s, Hahn 167(9) ms, 50 mK base, 99.92(1) %. Karapatzakis 10(1) ms CPMG-64 at 50 mK. Guo 1.57(8) ms at 1.7 K.

**Could not verify:**
- Humphreys SI (not in the arXiv PDF): NV cryostat temperature, overhead-inclusive wall-clock rates, and the measured p_det.
- Knaut Fig. 2c fidelity-vs-rate values: read off a rendered figure, approximate only.
- Temperature of the Lago-Rivera 2021 Pr:YSO memories (not in the main text).
- All rows listed as "Not re-checked" above remain ABS/SUM.
- The Nature versions were not read; text is the arXiv versions (Knaut v2, Liu v2, Humphreys v1-era PDF). Final published numbers could differ slightly.
