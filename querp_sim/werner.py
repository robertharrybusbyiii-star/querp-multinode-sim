"""
Werner / depolarizing channel helpers for entanglement swapping.

A Werner state with fidelity F (overlap with |Φ+⟩) is equivalent to:
    ρ = w |Φ+⟩⟨Φ+| + (1−w) I/4
with
    F = (1 + 3w) / 4    ⟺    w = (4F − 1) / 3

Assumptions (documented):
- Elementary links are Werner states with fidelity F_link.
- Idle decoherence during waiting multiplies the Werner parameter:
  w(t) = w(0) * exp(−t / T2).  MODELING CHOICE (not a derived result): T2 is a
  spin *dephasing* time but is used here as a *depolarizing* decay of w, so the
  plateau is F = 0.25 (pure dephasing of a Bell pair would floor at F = 0.5).
  One factor is applied per idling pair (not per memory qubit); a two-qubit
  pair would see exp(−2t/T2).  Both are open modeling questions.
- The waiting time is random (exponential), so the *average* decay factor is
  E[exp(−Δ/T2)] = 1/(1 + τ/T2) for Δ ~ Exp(mean τ), NOT exp(−τ/T2).  See
  ``mean_idle_factor`` (used by repeater.py since the AEON review fix).
- Ideal Bell-measurement entanglement swap of two Werner states with
  parameters w_a, w_b yields w_out = w_a * w_b (standard composition).
- An optional η_swap ∈ (0,1] multiplies w_out to model residual swap noise.
"""

from __future__ import annotations

import math


def fidelity_to_werner(f: float) -> float:
    """Convert Bell fidelity F to Werner weight w = (4F−1)/3."""
    return (4.0 * f - 1.0) / 3.0


def werner_to_fidelity(w: float) -> float:
    """Convert Werner weight w to Bell fidelity F = (1+3w)/4."""
    return (1.0 + 3.0 * w) / 4.0


def decohere_werner(w: float, t_s: float, t2_s: float) -> float:
    """Apply idle decoherence: w → w * exp(−t/T2)."""
    if t2_s <= 0.0:
        return 0.0
    if t_s <= 0.0:
        return w
    return w * math.exp(-t_s / t2_s)


def mean_idle_factor(tau_s: float, t2_s: float, t_cut_s: float | None = None) -> float:
    """
    E[exp(−Δ/T2)] for an idle gap Δ ~ Exp(mean τ), optionally truncated at t_cut.

    No cutoff:  1 / (1 + τ/T2)                         (exact for exponential Δ)
    Cutoff:     E[e^{−Δ/T2} | Δ ≤ t_cut]
              = [a/(a+b)] (1 − e^{−(a+b) t_cut}) / (1 − e^{−a t_cut}),
                a = 1/τ, b = 1/T2.
    Replaces the earlier exp(−E[Δ]/T2), which underestimates the surviving
    coherence (Jensen's inequality) when Γ·T2 ≲ 1.
    """
    if t2_s <= 0.0:
        return 0.0
    if tau_s <= 0.0:
        return 1.0
    a = 1.0 / tau_s
    b = 1.0 / t2_s
    if t_cut_s is None:
        return a / (a + b)
    if t_cut_s <= 0.0:
        return 1.0
    num = (a / (a + b)) * (-math.expm1(-(a + b) * t_cut_s))
    den = -math.expm1(-a * t_cut_s)
    return num / den


def decohere_werner_factor(w: float, factor: float) -> float:
    """Apply a precomputed (averaged) idle-decay factor to the Werner weight."""
    return w * factor


def swap_werner(w_a: float, w_b: float, eta_swap: float = 1.0) -> float:
    """
    Ideal Werner swap composition with optional residual noise factor.

    w_out = η_swap * w_a * w_b
    """
    return eta_swap * w_a * w_b
