# TARGETS_AEON — published values for the repeater sweep (written 2026-10-16, AEON)

**Purpose:** let each sweep value be tagged PUBLISHED / PLAUSIBLE / BEYOND PUBLISHED. Nothing here is model output.
**How verified (column "Verified"):** `FT` = full text fetched and read; `ABS` = abstract/snippet text returned by web search for that exact paper (numbers not cross-checked in the full text); `SUM` = figure appears only in a search-engine summary of the paper (treat as *unverified recollection* until the PDF is read). I could not reach arXiv's API from the sandbox, so most rows are `ABS`/`SUM`. Where a figure I (or the brief) remembered turned out different, that is flagged **CORRECTION**.

## 1. SnV⁻ electron-spin coherence (T2), T1, temperature
| Quantity | Value | Conditions | Source | Verified |
|---|---|---|---|---|
| Hahn-echo T2 | 170.0 ± 2.8 µs | microwave, naturally strained, 1.7 K | Rosenthal et al., PRX 13, 031022 (2023), arXiv:2306.13199, https://doi.org/10.1103/PhysRevX.13.031022 | ABS |
| XY16 T2 | 650.2 ± 28.4 µs | same device, 1.7 K | same | ABS |
| Hahn-echo T2 (strained membrane) | 100(1) µs (CPMG-1) | 1.7 K; Ramsey T2* 2.5(1) µs | Guo et al., PRX 13, 041037 (2023), arXiv:2307.11916, https://doi.org/10.1103/PhysRevX.13.041037 | ABS |
| CPMG-128 T2 | 1.57(8) ms | 1.7 K, strained membrane; T2 ∝ N^0.593 | Guo et al. (same) | ABS |
| Decoupled T2 at 4 K | 223(10) µs (Hahn ≈ 74 µs) | 4 K, strain raises orbital splitting | Guo et al. (same); Hahn value SUM | ABS / SUM |
| Optical-control DD | T2 = 0.30(8) ms (CPMG-4); Hahn 28.3(6) µs; T2* 1.3(3) µs | all-optical Raman, 1.7 K. Paper does **not** report a 100 mK SnV value (it compares to SiV at 100 mK) | Debroux et al., PRX 11, 041041 (2021), https://doi.org/10.1103/PhysRevX.11.041041 | ABS |
| XY8-256 T2 | **1.7(5) ms** (T2* 2.42(4) µs; echo 129(2) µs) | 256 π pulses; **CORRECTION: 1.7 ms, not 1.8**. Temperature of this electron-spin run not confirmed by me | Beukers et al., PRX 15, 021011 (2025), arXiv:2409.08977, https://doi.org/10.1103/PhysRevX.15.021011 | ABS |
| Hahn echo (SC waveguide) | 179(4) µs (B ∥ axis); **433(23) µs** (B ⟂ axis) | 50 mK, Nb coplanar waveguide, strained membrane | Karapatzakis et al., PRX 14, 031036 (2024), arXiv:2403.00521, https://doi.org/10.1103/PhysRevX.14.031036 | **FT** |
| **Best electron T2 (DD)** | **10(1) ms** (CPMG-64, π-pulse 196 ns) | **50 mK**, B ∥ axis (93 mT), T2 ∝ N^0.95(9), stretched-exp exponent fixed at ξ = 4; T2* 2.1(2) µs; authors attribute near-linear N scaling to no Ohmic heating | Karapatzakis et al. (same) | **FT** |
| T1 vs temperature | unstrained: **1.26 ± 0.28 ms at 4 K**, 10.4 ms at 3.25 K (exponential/phonon-limited) | 0.13 T | Trusheim et al., PRL 124, 023602 (2020), arXiv:1811.07777, https://doi.org/10.1103/PhysRevLett.124.023602 | ABS (10.4 ms: SUM) |
| T1, unstrained / strained | unstrained: >1 ms below 4 K, **>1 s at 50 mK base**; strained SnV-B: 2.59(45) ms at **6.43 K** | strain enlarges ground splitting (>800 GHz unstrained; ~1300 GHz in Guo) | Karapatzakis et al. App. A.4 | **FT** |
| T1 | >20 ms at 1.7 K; T2* 5(1) µs (all-optical CPT) | charge-stabilised SnV | Görlitz et al., npj Quantum Inf. 8, 45 (2022), arXiv:2110.05451 | ABS |
| SiV reference (not SnV) | T2 = 13 ± 1.7 ms (CPMG-32), T1 > 1 s | **100 mK** | Sukachev et al., PRL 119, 223602 (2017), arXiv:1708.08852 | ABS |

**Reading:** the dominant lever is temperature + strain + DD pulse count + no Ohmic heating, not a free-idle memory time. Free-evolution coherence (T2*) is ~1–5 µs in every SnV paper. The ~10 ms figure needs a dilution fridge (50 mK), a superconducting drive line, and 64 π pulses applied during the wait.

## 2. Spin-photon interface (cooperativity, efficiency, per-attempt success)
| Quantity | Value | Conditions | Source | Verified |
|---|---|---|---|---|
| SnV Purcell / coherent cooperativity | C = 20.6(11); **C_coh = 8.3(12)**; Q up to 25.4×10³; 98.8 % resonant extinction | photonic-crystal cavities; abstract also cites room-temp survey of 327 cavities | Codreanu et al., PRX (2025/26), arXiv:2511.13375, https://doi.org/10.1103/z514-v4n6 | ABS |
| SnV cavity chiplet | 4 of 6 channels Purcell-enhanced, mean F_P ≈ 7 (6.98 ± 0.42; best 10.40 ± 1.06) | SnV in diamond microchiplet on SiN PIC | arXiv:2402.18057, https://arxiv.org/abs/2402.18057 (authors not retrieved) | ABS |
| SnV waveguide | up to 25 % single-photon transmission extinction | 1-D diamond waveguide; **no spin-photon entanglement** | Pasini et al., PRL 133, 023603 (2024), https://doi.org/10.1103/PhysRevLett.133.023603 | ABS |
| SnV spin-photon entanglement | **none demonstrated** as of my search; Delft 2025 reports spin control, two-photon interference, projected max fidelity 0.94 ± 0.04 | — | Waas et al., Quantum 2025 abstract, https://phantomsfoundation.com/QUANTUM/2025/Abstracts/2025_Waas_Christopher_96.pdf | SUM |
| SiV cooperativity (best) | **C = 105 ± 11** (g = 8.38 GHz, κ = 21.8 GHz, γ = 0.123 GHz); overall η = 0.423 ± 0.004 | SiV nanocavity | Bhaskar et al., Nature 580, 60 (2020), arXiv:1909.01323, https://doi.org/10.1038/s41586-020-2103-5 | ABS |
| SiV C in networked node | C = 1.6 | 29SiV node | Stas et al., Science 378, 557 (2022), arXiv:2207.13128, https://doi.org/10.1126/science.add9771 | SUM |
| Spin-photon (electron-photon) Bell fidelity | 0.91 ± 0.02 @ 0.1 K; 0.90 ± 0.01 @ 1.5 K. Nuclear-photon (PHONE): 0.85 ± 0.02 @ 0.1 K; 0.66 ± 0.02 @ 4.3 K (0.71 with flag error detection) | SiV | Stas et al. (same) | ABS |
| End-to-end remote heralding prob. per attempt | electron–electron 7.7×10⁻⁶ to 2.5×10⁻⁴; nuclear–nuclear 2.0×10⁻⁵ (1.4 kHz rep rate, 20 % duty) | SiV, deployed 35 km (17 dB) fibre | Knaut et al., Nature (2024), arXiv:2310.01316, https://doi.org/10.1038/s41586-024-07252-z | SUM |
| SiV remote rate / fidelity | electron spins: up to ~1 Hz, Bell F = 0.86(3) / 0.74(3); nuclear: 6 mHz, F = 0.69(7) after error detection over 35 km (0.77(5) local) | **CORRECTION:** 35 km fidelity 0.69 is *nuclear*; supplement *projects* ~0.95 / ~100 Hz after improvements (SUM, not read) | Knaut et al. (same) | ABS / SUM |
| NV per-attempt success | 2·p_det·α, p_det ≈ 4×10⁻⁴ → ≈ 4×10⁻⁵ (α = 0.05) to 2.4×10⁻⁴ (α = 0.3); attempt ≈ 5.5 µs | NV, 2 m | Humphreys et al., Nature (2018), arXiv:1712.07567 | SUM |
| Ion per-attempt success | 2.18×10⁻⁴ at 833 kHz attempt rate | ⁸⁸Sr⁺, 2 m fibre | Stephenson et al., PRL 124, 110501 (2020), arXiv:1911.10841 | ABS |

## 3. Nuclear-spin memory times
| Quantity | Value | Conditions | Source | Verified |
|---|---|---|---|---|
| ¹³C coupled to SnV, DD | **1.35(3) s**; Ramsey T2* 1.5(1) ms; Hahn ≈ 167 ms; gate fidelity 99.92(1) %; init 99.74(3) % | 50 mK, SC waveguide | "High-fidelity control of a ¹³C nuclear spin coupled to a tin-vacancy center in diamond", arXiv:2509.03354, https://doi.org/10.1103/bmc6-qvwq (authors not retrieved; KIT repository listing) | ABS (Hahn: SUM) |
| ¹³C coupled to SnV | T2* = 17.2(6) ms (Ramsey, **not** echo); e–n entanglement 72(3) % | ~0.4 K (SUM) | Beukers et al. (PRX 15, 021011) | ABS / SUM |
| ²⁹Si coupled to SiV | **2.1 ± 0.1 s** (XY8-128) | 0.1 K–1.5 K node | Stas et al. (2022) | ABS |
| NV ¹³C register | memory **>75 s**; two-qubit entanglement >10 s; 10 qubits | NV, natural-ish diamond | Bradley et al., PRX 9, 031045 (2019), arXiv:1905.02094 | ABS |
| NV ¹³C under link attempts | 1.20 s *continuous-attempt* lifetime | isotopically purified diamond. **CORRECTION:** this is npj Quantum Inf. 2022 (not Science) | Bradley et al., npj Quantum Inf. (2022), https://doi.org/10.1038/s41534-022-00637-w | ABS |
| NV nuclear spins vs attempts | coherence for **>1000** attempts (2-spin decoherence-protected subspace) | NV, 5 nuclear spins | Reiserer et al., PRX 6, 021040 (2016), arXiv:1603.01602 | ABS |
| NV **electron** spin (not nuclear) | 1.58 s, 10,240 pulses | **CORRECTION:** Abobeih 2018 is electron-spin DD, not a ~1 min nuclear memory | Abobeih et al., Nat. Commun. (2018), arXiv:1801.01196 | ABS |

## 4. Multiplexing demonstrated (modes, fidelity, time)
| Quantity | Value | Conditions | Source | Verified |
|---|---|---|---|---|
| Multiplexed repeater theory | proposal only: multiplexing reduces memory-coherence requirement | — | Collins et al., PRL 98, 060502 (2007), https://doi.org/10.1103/PhysRevLett.98.060502 | ABS |
| Spectral modes | 26 time-bin qubits stored simultaneously, F = 97 % | Ti:Tm:LiNbO₃ AFC, 60 ns delay | Sinclair et al., PRL 113, 053603 (2014), arXiv:1309.3202 | ABS |
| Spatial cells | 225 (15×15) cells; atom-photon entanglement F ≈ 90 %; decay ≈ 28 µs; >threshold at 35 µs | cold ⁸⁷Rb DLCZ | Pu et al., Nat. Commun. 8, 15359 (2017), arXiv:1707.07267 | ABS |
| Multi-DOF | 12 modes (3 OAM × 2 spectral × 2 temporal); spin-wave eff. ≈ 5 % | REI crystal | Yang et al., Nat. Commun. (2018), arXiv:1808.01565 | ABS |
| Multimode heralded memory-memory entanglement (REI) | **62 temporal modes**, heralding up to 1.4 kHz, storage up to 25 µs; follow-up conditional fidelities 92(2) % (excited-state) / 77(2) % (spin-wave) | Pr:YSO, telecom heralding. Fidelity not in the Nature abstract | Lago-Rivera et al., Nature (2021), arXiv:2101.05097; follow-up arXiv:2106.05079 | ABS |
| Absorptive memories | F = 80.4 ± 2.2 %; storage eff. ≈ 12–14 % at 55.6 ns; ~4 temporal modes used (time-bandwidth allows ~56) | AFC | Liu et al., Nature (2021), arXiv:2101.04945 | SUM |
| AFC capacity | Eu:YSO 100 modes (fixed delay 50.7 µs), Pr:YSO 40 modes (25 µs); on-demand spin-wave 6 (Eu) / 30 (Pr) | model + experiment | Ortu et al., Quantum Sci. Technol. 7, 035024 (2022), arXiv:2202.12383 | ABS |
| Multiplexed repeater link (atoms) | 12 temporal modes → **11.79 ± 0.35 × rate**; 70 % retrieval; concurrence 0.040(2) at 1 µs (low) | cold-atom DLCZ | Wang et al., arXiv:2308.14587 (Laser Photon. Rev. 2024, doi 10.1002/lpor.202300825) | ABS |
| Multiplexed 12 km link (atoms) | **280 modes** (70 cells × 4 angles); 1.95 kHz per 240 µs round (187 Hz with overhead); 0.46 expected correlations inside 235 µs coherence | atom-photon only, not memory-memory | Nat. Commun. (2024), arXiv:2403.13623, https://doi.org/10.1038/s41467-024-54691-3 | ABS |
| REI on-demand multiplexed | 15 temporal modes, up to 500 cps heralding | Pr:YSO, spin-wave | arXiv:2501.04131 | SUM |
| Trapped ions | 3 ions → 2.85(7) Hz vs 1.23(5) Hz single (2.3× ); Bell F 0.89(2); 101 km fibre | **ion-photon**, not ion-ion | Krutyanskiy et al., PRX Quantum 5, 020308 (2024), arXiv:2308.08891 | ABS |
| Color-center multiplexing | **no remote-entanglement multiplexing demonstrated** found; hardware step = 4 SnV channels (above); Yb:YVO ions: spectrally multiplexed 2-node W-state (Ruskuc et al., arXiv:2402.16224) | — | — | ABS |

## 5. State of the art for remote nodes, chains, distillation
| Quantity | Value | Platform | Source | Verified |
|---|---|---|---|---|
| Rate vs fidelity | **39 Hz @ F 0.60(2)**; **6 Hz @ F 0.81(2)**; deterministic 9.9 Hz @ 0.56(1) | NV, 2 m | Humphreys 2018 | SUM |
| 3-node network | links F > 0.8 at 9 Hz / 7 Hz; swapped A–C F 0.587(28) (avg 0.551(13)) ~1 per 40 s; GHZ F 0.538(18) ~1 per 90 s | NV | Pompili et al., Science 372, 259 (2021), https://doi.org/10.1126/science.abg1919 | ABS |
| Teleportation, non-neighbours | conditional F 0.702(11) at 1/117 s; unconditional 0.688(10) at 1/100 s | NV 3-node | Hermans et al., Nature 605, 663 (2022), https://doi.org/10.1038/s41586-022-04697-y | ABS |
| Metropolitan | real-time heralded F 0.534(15) at 0.022 s⁻¹ (1.3/min); post-selected 0.48 Hz | NV, 10 km / 25 km fibre | Stolk et al., Sci. Adv. (2024), arXiv:2404.03723, https://doi.org/10.1126/sciadv.adp6442 | ABS |
| Distillation | raw ≤ 0.5 → distilled **0.65(3)**; rate very low | NV + ¹³C | Kalb et al., Science (2017), arXiv:1703.03244 | ABS |
| Memory-enhanced comms | beat direct-transmission limit by 4.1 ± 0.5 (after distillation); ~1.2 MHz effective clock | SiV | Bhaskar 2020 | ABS |
| High rate **and** high fidelity (benchmark) | **182 s⁻¹ at F = 94.0(5) %** | trapped ions (not solid-state) | Stephenson 2020 | ABS |
| Solid-state chain >3 nodes | none found; best = 3 nodes (Pompili) | — | — | — |

## 6. Where the sim baseline sits (T2 = 3.6 ms, p_succ 0.0071, Γ = 85 Hz, F = 0.887)
- **T2 3.6 ms** is ≈ 2.1× above the best 1.7 K DD values (1.7 ms Beukers; 1.57 ms Guo), ≈ 2.8× **below** the best overall (10 ms, 50 mK, Karapatzakis), ≈ 8× above the best Hahn echo (433 µs) and ≈ 21× above 170 µs (Rosenthal). It is reachable only as a DD time at ≲ 50 mK-class conditions, not at 1.7 K. Recollections check: 170 µs ✔, 650 µs XY16 ✔, ~1.8 ms → **1.7(5) ms** (README's "1.7–1.8" fine). README omits the 10 ms result.
- **p_succ 0.0071** is ≈ 30× above the best published *remote* per-attempt probabilities (≈ 2.2–2.5×10⁻⁴: ions, NV, SiV). (My arithmetic, not a citation: for a double-click protocol p ≈ η²/2, so 0.0071 needs ≈ 12 % end-to-end efficiency per node; Bhaskar's single-node η = 0.42 is above that but with no frequency conversion and no remote link.)
- **Γ = 85 Hz with F = 0.887** exceeds published solid-state remote links (NV ≤ 9 Hz at F > 0.8 or 39 Hz at 0.60; SiV ~1 Hz at 0.86). Only trapped ions (182 Hz at 0.94) are in that region.
- **Attempt rate 5 kHz** lies within published range (1.4 kHz SiV, ~180 kHz NV, 833 kHz ion). Published DD envelopes are stretched exponentials (ξ up to 4 in Karapatzakis), not the sim's simple exp(−t/T2).

## 7. Suggested sweep bands
| Parameter | PUBLISHED (≤ best published) | PLAUSIBLE (≤ ~10×, with reason) | BEYOND PUBLISHED |
|---|---|---|---|
| **SnV T2** | ≤ 0.43 ms Hahn; ≤ 1.7 ms DD at 1.7 K; ≤ **10 ms** DD at 50 mK | **10–100 ms**: T2 ∝ N^0.95 not yet saturated at N = 64 (Karapatzakis); SiV reaches 13 ms at 100 mK; needs more pulses + pulse-error control | > 100 ms for the SnV *electron* (no mechanism shown). Nuclear ¹³C memory published to 1.35 s is a different qubit and needs a coupled ¹³C |
| **Per-attempt success p** | ≤ **2.5×10⁻⁴** (remote entanglement, any platform) | 2.5×10⁻⁴ – **2.5×10⁻³**: SnV C_coh = 8.3 and SiV η = 0.42 exceed what the remote experiments used; Knaut's supplement projects ~100 Hz (SUM) | > 2.5×10⁻³ (includes baseline 0.0071): needs ≳ 12 % per-node efficiency incl. frequency conversion and fibre, not shown |
| **Multiplexing k** (independent link slots per node) | k ≤ 3 (ions, ion-photon); SnV hardware k ≤ 4 (Purcell only); REI memories 12–62 temporal modes and cold atoms 280, **other platforms** | k = 5–**40** for SnV/SiV: spatial emitter arrays + Stark/strain tuning; ~linear rate gain, bounded by memory time and tuning | k > 40 on color centers; any k with a stacked nuclear memory without a demo |
| **Cutoff** (wait before discarding a pair; sim uses m × T2) | absolute cutoff ≤ the published memory time of the qubit actually used (electron ≤ 10 ms @ 50 mK; ≤ 1.7 ms @ 1.7 K; nuclear ≤ 1.35 s SnV, 2.1 s SiV) | m ≈ 1–3 × T2: DD envelopes are flat then collapse (ξ up to 4), so a cutoff near T2 is natural (my reasoning, not a citation) | cutoff that depends on T2 > 100 ms (electron) or an electron memory held over the ~12 ms/Γ idle without DD pulses |

**Note:** nuclear-spin memory times (SnV ¹³C 1.35 s; SiV ²⁹Si 2.1 s; NV ¹³C 75 s), multiplexing results (REI, cold atoms, ions) and SnV electron T2 / cooperativity are from different platforms and devices. They cannot be stacked on one SnV node (e.g. "10 ms electron + 1 s nuclear + k = 62 + p = 0.007") without a demonstration of that combination. In particular no color-center experiment has combined multiplexing with remote entanglement.

*Items to read in full before relying on them: Knaut (all numbers `SUM`), Humphreys per-attempt p, Liu temporal-mode count, 2509.03354 (Hahn 167 ms, authors, temperature).*
