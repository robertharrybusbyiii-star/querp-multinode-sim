"""QBEH power-autonomy checks for QuERP nodes."""

from __future__ import annotations

from .baseline import NodeParams, THRESH_POWER_MARGIN_MW


def power_report(params: NodeParams) -> dict:
    """Return a dict summarizing DC harvest, load, and autonomy."""
    return {
        "rf_density_uw_cm2": params.rf_density_uw_cm2,
        "p_dc_mw": params.p_dc_mw,
        "p_electronics_mw": params.p_electronics_mw,
        "power_margin_mw": params.power_margin_mw,
        "energy_autonomous": params.energy_autonomous,
        "threshold_margin_mw": THRESH_POWER_MARGIN_MW,
    }
