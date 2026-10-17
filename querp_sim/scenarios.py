"""
Scenario definitions. Extensions only — do not replace locked v0.3b defaults.

Scenarios:
  1. nominal_v0.3b     — locked baseline
  2. half_rf           — half RF density (30 µW/cm²), same electronics
  3. high_electronics  — locked RF, electronics+control = 24.0 mW
  4. half_rf_high_elec — half RF + 24.0 mW electronics
  5. without_trinity   — T2=1.5 ms, p_succ=0.006, Γ=5000×0.006=30 Hz;
                         F_link kept at locked 0.887 (optical fidelity not
                         remapped; only T2 and rate change — documented)
"""

from __future__ import annotations

from .baseline import (
    ATTEMPT_RATE_HZ,
    F_LINK,
    P_ELECTRONICS_MW,
    P_SUCC,
    RF_DENSITY_UW_CM2,
    T2_S,
    GAMMA_HZ,
    NodeParams,
    locked_v03b,
)


def without_trinity_gamma(attempt_rate_hz: float = ATTEMPT_RATE_HZ, p_succ: float = 0.006) -> float:
    """
    Map Without-Trinity optical success to adjacent-link rate.

    Γ = attempt_rate × p_succ.
    Note: locked v0.3b Γ=85 Hz is NOT equal to 5000×0.0071(=35.5 Hz); the
    locked rate includes Trinity protocol / multiplexing factors beyond raw
    attempt×p. Only the Without-Trinity scenario uses this raw product.
    """
    return attempt_rate_hz * p_succ


def all_scenarios() -> list[NodeParams]:
    half_rf = 0.5 * RF_DENSITY_UW_CM2
    high_elec = 24.0  # mW — scenario override
    return [
        locked_v03b(),
        NodeParams(
            name="half_rf",
            t2_s=T2_S,
            p_succ=P_SUCC,
            gamma_hz=GAMMA_HZ,
            f_link=F_LINK,
            rf_density_uw_cm2=half_rf,
            p_electronics_mw=P_ELECTRONICS_MW,
        ),
        NodeParams(
            name="high_electronics",
            t2_s=T2_S,
            p_succ=P_SUCC,
            gamma_hz=GAMMA_HZ,
            f_link=F_LINK,
            rf_density_uw_cm2=RF_DENSITY_UW_CM2,
            p_electronics_mw=high_elec,
        ),
        NodeParams(
            name="half_rf_high_elec",
            t2_s=T2_S,
            p_succ=P_SUCC,
            gamma_hz=GAMMA_HZ,
            f_link=F_LINK,
            rf_density_uw_cm2=half_rf,
            p_electronics_mw=high_elec,
        ),
        NodeParams(
            name="without_trinity",
            t2_s=1.5e-3,
            p_succ=0.006,
            gamma_hz=without_trinity_gamma(),
            f_link=F_LINK,  # keep locked F; only T2 & Γ remapped
            rf_density_uw_cm2=RF_DENSITY_UW_CM2,
            p_electronics_mw=P_ELECTRONICS_MW,
        ),
    ]
