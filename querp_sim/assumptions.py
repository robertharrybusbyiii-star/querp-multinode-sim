"""
Registry of every model input with its epistemic label.

This module is DESCRIPTIVE: it does not feed any constants into the model (the
locked values stay in baseline.py). tests/test_sanity.py asserts that the
registry values equal the live constants so the two cannot drift apart.

Labels
------
MEASURED     : measured on this hardware (NONE yet)
LITERATURE   : value within published ranges for comparable systems
ASSUMPTION   : design/scenario choice with no source found
TUNED        : free parameter adjusted by hand, no source, no mechanism
Sources come from AEON's review (REVIEW_AEON.md); "no source found" means a
reviewer did not find one, not proof that none exists.
"""

from __future__ import annotations

from . import baseline as B
from . import trinity_purification as T

NO_SRC = "no source found"

# name: (value, unit, label, source/notes)
ASSUMPTIONS: dict[str, tuple] = {
    "RF density": (B.RF_DENSITY_UW_CM2, "uW/cm2", "ASSUMPTION",
                   "Needs a dedicated transmitter (~7.5 W EIRP at 1 m); ambient levels far lower. "
                   "No established effect on spin coherence/link success; only sets DC power here."),
    "QBEH cells x area": (f"{B.N_CELLS} x {B.CELL_AREA_CM2}", "cm2", "ASSUMPTION", NO_SRC),
    "eta RF->DC": (B.ETA_E2E, "-", "LITERATURE (best case)",
                   "Measured rectenna RF-DC 40-63% exists (e.g. PMC10140817); 0.62 is top of range, ideal matching."),
    "Electronics+control": (B.P_ELECTRONICS_MW, "mW", "ASSUMPTION",
                            "Ignores cryostat: SnV- memories measured at ~1.7 K; cooling power >> 12 mW."),
    "T2": (B.T2_S, "s", "ASSUMPTION (exceeds literature)",
           "SnV-: 170 us Hahn echo, 650 us XY16 (Rosenthal PRX 13 031022); ~1.7-1.8 ms XY8+256 pi pulses "
           "(Beukers 2024, arXiv 2409.08977). 3.6 ms is above these and is a dynamical-decoupling T2."),
    "Trinity T2 factor (3.6/1.5)": (B.T2_S / 1.5e-3, "x", "ASSUMPTION",
                                    "No demonstrated coupling of a phase lock to memory T2. Hypothetical."),
    "Trinity success factor (0.0071/0.006)": (B.P_SUCC / 0.006, "x", "ASSUMPTION", NO_SRC),
    "p_succ (locked)": (B.P_SUCC, "-", "ASSUMPTION", NO_SRC + "; never used in e2e calcs (only Gamma is)"),
    "Attempt rate": (B.ATTEMPT_RATE_HZ, "Hz", "ASSUMPTION", NO_SRC + "; ignores communication latency"),
    "Gamma (locked)": (B.GAMMA_HZ, "Hz", "ASSUMPTION/TUNED",
                       "Equals ~2.39x (attempt x p_succ = 35.5 Hz); undocumented multiplier, ~= the T2 factor 2.4."),
    "Gamma unexplained factor": (B.GAMMA_HZ / (B.ATTEMPT_RATE_HZ * B.P_SUCC), "x", "TUNED/UNEXPLAINED",
                                 "Called 'multiplexing factors' in README; no derivation."),
    "F_link": (B.F_LINK, "-", "ASSUMPTION", "Werner form assumed; real links are not Werner."),
    "p_swap / eta_swap": ("1.0 / 1.0", "-", "ASSUMPTION", "Ideal swap and ideal local gates."),
    "TPP lock gain": (T.TRINITY_LOCK_GAIN_DEFAULT, "x", "TUNED",
                      "A phase lock cannot raise herald probability above its analytical value."),
    "TPP fidelity gain": (T.TRINITY_FIDELITY_GAIN_DEFAULT, "x", "TUNED (neutral)", NO_SRC),
    "TPP depolarizing residual (per round)": (T.DEPOLARIZING_RESIDUAL_DEFAULT, "-", "TUNED",
                                              "Per-round unitless shrink of Werner weight, not a floor/angle."),
    "Purify target / max rounds": (f"{T.PURIFY_TARGET_DEFAULT} / {T.MAX_ROUNDS_DEFAULT}", "-", "ASSUMPTION", "policy"),
    "Idle model": ("exp decay of Werner weight, averaged over exponential gaps", "-", "ASSUMPTION",
                   "Dephasing T2 used as depolarizing decay (floor F=0.25 not 0.5); one factor per pair."),
    "Multiplexing k (sweep)": ("1,2,5,10,20,50,100", "slots", "HYPOTHETICAL",
                               "Γ_eff = k·Γmult·85 Hz (earliest-of-k arrivals, querp_sim/multiplexing.py); "
                               "k=1 is the locked point; power/cryostat/memory-slot cost not modeled."),
    "Gamma multiplier (sweep)": ("0.5,1,2,4", "x", "HYPOTHETICAL", "Scenario rate multiplier on locked Γ; equivalent to scaling k."),
    "T2 values (sweep)": ("0.17,1.8 | 3.6 | 10,100", "ms", "LITERATURE | LOCKED ASSUMPTION | HYPOTHETICAL",
                          "0.17 ms Hahn echo (Rosenthal PRX 13 031022); 1.8 ms XY8+256 pi (Beukers 2024); "
                          "3.6 ms is locked and exceeds literature; 10/100 ms are what-ifs."),
    "TPP lock gain (sweep)": (1.0, "x", "TUNED (neutral)", "Sweep uses neutral 1.0, not the 1.08 CLI default."),
    "Distance / fiber loss": ("not modeled", "-", "MISSING", "No eta, km or dB/km; PLOB bound untestable."),
    "Useful thresholds": (f"R>={B.USEFUL_RATE_HZ} Hz, F>={B.USEFUL_F}", "-", "ASSUMPTION", "reporting policy"),
}

BANNER = (
    "MODEL OUTPUT UNDER STATED ASSUMPTIONS - NOT MEASURED. None of the inputs is MEASURED for this "
    "hardware. The 'Trinity' factors (T2 x2.4, success x1.18, TPP gain 1.08, per-round depolarizing "
    "residual 0.01) are hypothetical scenario parameters with no demonstrated physical mechanism. "
    "Rates are per elementary link with NO distance or fiber loss modeled. "
    "TPP runs with --purify-idle ideal are an optimistic upper bound (no memory decoherence), not a prediction."
)


def format_assumptions() -> str:
    lines = [BANNER, "", "Input registry (label | value unit | note):"]
    for k, (v, u, lab, note) in ASSUMPTIONS.items():
        val = f"{v:.6g}" if isinstance(v, float) else str(v)
        lines.append(f"  [{lab}] {k} = {val} {u}  -- {note}")
    return "\n".join(lines)
