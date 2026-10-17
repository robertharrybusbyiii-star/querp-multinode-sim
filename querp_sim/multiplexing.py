"""
Multiplexing extension (NEW scenario parameter; locked v0.3b values untouched).

Model
-----
Each node has ``k`` parallel link-attempt slots (memory slots / frequency
channels) per elementary link.  Slot i succeeds after an i.i.d. waiting time
T_i ~ Exp(rate Γ_slot).  A link is "available" as soon as the FIRST slot
succeeds:

    T_link = min(T_1..T_k) ~ Exp(rate k·Γ_slot)        (earliest-of-k arrivals)
    E[T_link] = 1 / (k·Γ_slot)

so the effective elementary-link rate is  Γ_eff = k · Γ_slot.

Idle-wait distribution: at a swap, the partner link is also an earliest-of-k
arrival, T_link' ~ Exp(k·Γ_slot) independent of the first.  By memorylessness
the residual gap |T_link − T_link'| is again Exp(mean 1/Γ_eff), so the existing
idle machinery (1/(1+τ/T2) average, truncated form with cutoff, acceptance
probability 1−exp(−t_cut/τ), nested 3/2·τ recursion) applies unchanged with
Γ → Γ_eff.  Multiplexing therefore only rescales the clock; it adds no new
decoherence channel and Γ_eff·T2 = k·Γ_slot·T2 is the key figure of merit.

Assumptions / caveats (all HYPOTHETICAL scenario parameters, not measured):
  * Slots are independent and identical; no crosstalk, no shared-resource limits.
  * The k−1 later-succeeding slots are simply ignored (conservative: a real
    scheme could pick the freshest of several stored pairs).
  * The locked Γ=85 Hz is taken as the per-slot rate Γ_slot (× optional
    ``gamma_mult`` scenario multiplier).  k=1, gamma_mult=1 is exactly locked v0.3b.
  * Power budget, cryostat load, memory-slot count (≥ 2k per repeater node),
    switching/feed-forward latency and photon-source rate limits are NOT modeled:
    k does not change the power margin here.
"""

from __future__ import annotations

from dataclasses import replace

from .baseline import NodeParams


def effective_gamma(gamma_slot_hz: float, k: int, gamma_mult: float = 1.0) -> float:
    """Γ_eff = k · gamma_mult · Γ_slot (earliest-of-k arrival rate)."""
    if k < 1 or int(k) != k:
        raise ValueError(f"k must be a positive integer, got {k!r}")
    if gamma_mult <= 0.0:
        raise ValueError("gamma_mult must be > 0")
    return k * gamma_mult * gamma_slot_hz


def multiplexed_params(
    params: NodeParams,
    k: int,
    gamma_mult: float = 1.0,
    t2_s: float | None = None,
) -> NodeParams:
    """
    Return a NodeParams copy with Γ → k·gamma_mult·Γ and optional T2 override.
    Does NOT mutate the locked baseline; k=1, gamma_mult=1, t2_s=None is identity
    (apart from the name).
    """
    gamma = effective_gamma(params.gamma_hz, k, gamma_mult)
    tag = f"{params.name}+mux(k={k},gm={gamma_mult:g}"
    kw = dict(gamma_hz=gamma)
    if t2_s is not None:
        if t2_s <= 0.0:
            raise ValueError("t2_s must be > 0")
        kw["t2_s"] = t2_s
        tag += f",T2={t2_s * 1e3:g}ms"
    return replace(params, name=tag + ")", **kw)
