"""
LOCKED QuERP Node baseline v0.3b (24 Aug 2026) — default operating point.

Do not silently change these values. Scenario overrides live in scenarios.py
and must be labeled as extensions only.

STATUS: every value below is an ASSUMPTION of the v0.3b design sketch, none is
MEASURED for this hardware (see assumptions.py for per-input labels/sources).
Notably: locked Γ = 85 Hz is ~2.39× larger than ATTEMPT_RATE × P_SUCC
(5000 × 0.0071 = 35.5 Hz) with no documented origin, and T2 = 3.6 ms exceeds
published SnV⁻ values (170 µs Hahn echo; ~1.7–1.8 ms with 256-pulse XY8).
"""

from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Power (QBEH) — locked
# ---------------------------------------------------------------------------
RF_DENSITY_UW_CM2 = 60.0  # µW/cm²
N_CELLS = 100
CELL_AREA_CM2 = 9.0  # cm²
ETA_E2E = 0.62  # end-to-end RF→DC conversion efficiency (best-case literature range)
# DC harvest: 60e-6 W/cm² * 100 * 9.0 * 0.62 = 0.03348 W ≈ 33.5 mW
P_DC_MW = RF_DENSITY_UW_CM2 * 1e-3 * N_CELLS * CELL_AREA_CM2 * ETA_E2E  # mW
P_ELECTRONICS_MW = 12.0  # mW electronics + control
# Power margin = P_DC - P_electronics ≈ +21.5 mW
POWER_MARGIN_MW = P_DC_MW - P_ELECTRONICS_MW

# ---------------------------------------------------------------------------
# Quantum (SnV⁻ + Trinity Protocol conservative mapping) — locked
# ---------------------------------------------------------------------------
T2_S = 3.60e-3  # Effective T2 = 3.60 ms
P_SUCC = 0.0071  # Effective optical success probability
GAMMA_HZ = 85.0  # Adjacent-link entanglement generation rate Γ
F_LINK = 0.887  # Estimated elementary-link fidelity F

# Attempt rate used only for the Without-Trinity comparison mapping
ATTEMPT_RATE_HZ = 5000.0

# Per-node pass thresholds (baseline Pass when all hold)
THRESH_POWER_MARGIN_MW = 0.0  # margin must be > 0
THRESH_GAMMA_HZ = 80.0  # Γ ≥ 80 Hz
THRESH_F = 0.88  # F ≥ 0.88

# End-to-end "useful" reporting thresholds (simulation policy, not locked HW)
USEFUL_RATE_HZ = 1.0  # e2e rate considered useful if ≥ 1 Hz
USEFUL_F = 0.88  # same fidelity floor as node threshold


@dataclass(frozen=True)
class NodeParams:
    """Per-node operating point (locked defaults or scenario override)."""

    name: str
    t2_s: float
    p_succ: float
    gamma_hz: float
    f_link: float
    rf_density_uw_cm2: float
    p_electronics_mw: float
    eta_e2e: float = ETA_E2E
    n_cells: int = N_CELLS
    cell_area_cm2: float = CELL_AREA_CM2
    attempt_rate_hz: float = ATTEMPT_RATE_HZ

    @property
    def p_dc_mw(self) -> float:
        return (
            self.rf_density_uw_cm2
            * 1e-3
            * self.n_cells
            * self.cell_area_cm2
            * self.eta_e2e
        )

    @property
    def power_margin_mw(self) -> float:
        return self.p_dc_mw - self.p_electronics_mw

    @property
    def energy_autonomous(self) -> bool:
        return self.power_margin_mw > THRESH_POWER_MARGIN_MW

    @property
    def node_pass(self) -> bool:
        return (
            self.energy_autonomous
            and self.gamma_hz >= THRESH_GAMMA_HZ
            and self.f_link >= THRESH_F
        )


def locked_v03b() -> NodeParams:
    """Return the locked v0.3b default operating point."""
    return NodeParams(
        name="nominal_v0.3b",
        t2_s=T2_S,
        p_succ=P_SUCC,
        gamma_hz=GAMMA_HZ,
        f_link=F_LINK,
        rf_density_uw_cm2=RF_DENSITY_UW_CM2,
        p_electronics_mw=P_ELECTRONICS_MW,
    )


def assert_locked_power_identity() -> None:
    """Sanity: locked harvest identity → ~33.5 mW DC, ~+21.5 mW margin."""
    assert abs(P_DC_MW - 33.5) < 0.05, f"P_DC={P_DC_MW}"
    assert abs(POWER_MARGIN_MW - 21.5) < 0.05, f"margin={POWER_MARGIN_MW}"
