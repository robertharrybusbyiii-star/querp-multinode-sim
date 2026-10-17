"""
Trinity Purification Protocol (TPP) — SEPARATE from noise-damping Trinity.

===========================================================================
STATUS: MODEL OUTPUT, NOT MEASURED. The two "Trinity" knobs below
(``trinity_lock_gain`` = 1.08 and ``depolarizing_residual`` = 0.01) are TUNED
scenario parameters with NO source and NO demonstrated physical mechanism.
A phase lock cannot raise a herald probability above the value fixed by the
state and the operation; the lock gain is a hypothetical what-if only.
===========================================================================
IMPORTANT SEPARATION
---------------------------------------------------------------------------
The locked v0.3b baseline already embeds a **noise-damping Trinity** mapping
into the node operating point (Γ=85 Hz, T2=3.60 ms, p_succ=0.0071, F=0.887).
Those coherence / rate multipliers MUST NOT be altered by this module.

This file implements a **distinct** protocol — the Trinity Purification
Protocol (TPP) — i.e. bilateral entanglement purification of Werner states
with two hypothetical overlays:

  1. ``trinity_lock_gain``: multiplies herald success probability (TUNED), and
  2. ``depolarizing_residual`` ε: a per-round unitless depolarizing shrink of
     the Werner weight (TUNED).

without silently changing locked Γ, T2, or F_link.

===========================================================================
Analytical BBPSSW (twirled each round) on identical Werner states
---------------------------------------------------------------------------
Werner fidelity F ↔ weight w::

    F = (1 + 3w) / 4
    w = (4F − 1) / 3

Two identical copies with fidelity F are consumed. BBPSSW recurrence
(Bennett et al., PRL 76, 722 (1996))::

    p_BBPSSW = F² + (2/3) F (1−F) + (5/9) (1−F)²
    F_out    = [ F² + (1/9)(1−F)² ] / p_BBPSSW

The output is re-twirled to a Werner state after EVERY round, so this is
BBPSSW, NOT DEJMPS. Single-round values coincide for Werner inputs, but
*iterated* DEJMPS (which keeps the Bell-diagonal structure) converges faster
(AEON's quick calc from F=0.887: iterated DEJMPS 0.916→0.985→0.999 vs this
model's twirled BBPSSW with ε=0.01: 0.909→0.927→0.941→0.951), so the pair counts / fidelities here are conservative on
that axis. Fixed point of the recurrence is F = 0.5.
Local gates and measurements are assumed ideal (strong assumption).

TPP overlays (TUNED, no source)::

    p_success = min(1, p_BBPSSW · trinity_lock_gain)   # default gain 1.08
    F_out     = min(1, F_BBPSSW · trinity_fidelity_gain)
    w_out    ← w_out · (1 − ε)   # ε = depolarizing_residual, default 0.01

ε is applied EVERY round (it compounds). It is a per-round unitless shrink of
w — not an angle in radians/degrees and not a one-time floor. It does cap the
reachable F (e.g. target 0.99 is unreachable at ε = 0.01; max ≈ 0.97).

Yield cost (raw input pairs per successful purified output)::

    pairs_consumed = 2 / p_success

``purify_to_target`` iterates rounds until F ≥ F_target or ``max_rounds``.
Total pairs = product of per-round costs (geometric compounding).

Time cost at elementary-link generation rate Γ::

    t_purified = pairs_total / Γ
    R_purified = Γ / pairs_total

NOT MODELED: storage decoherence while a pair waits for its partner copy
(≈ 1/Γ ≈ 3.3·T2 at locked values), classical communication time.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .werner import fidelity_to_werner, werner_to_fidelity


# ---------------------------------------------------------------------------
# Conservative TPP defaults (documented; tunable via CLI)
# ---------------------------------------------------------------------------
# TUNED, NO SOURCE, no demonstrated mechanism. Hypothetical what-if on herald
# success probability. 1.0 = neutral (analytical BBPSSW value).
# Range explored in the design brief: 1.0–1.15.
TRINITY_LOCK_GAIN_DEFAULT = 1.08

# Multiplier on analytical post-selection fidelity. Default 1.0 = stay on
# the analytical BBPSSW curve (no silent F inflation). TUNED (neutral).
TRINITY_FIDELITY_GAIN_DEFAULT = 1.0

# After EACH purification round, shrink Werner weight by (1 − ε). Unitless
# per-round depolarizing residual (compounds across rounds); NOT a one-time
# floor and NOT a phase angle. TUNED, no source. 0 = ideal local operations.
DEPOLARIZING_RESIDUAL_DEFAULT = 0.01
RESIDUAL_PHASE_ERROR_DEFAULT = DEPOLARIZING_RESIDUAL_DEFAULT  # deprecated alias

# Default e2e / link purification fidelity target.
PURIFY_TARGET_DEFAULT = 0.95

# Safety cap on recurrence rounds.
MAX_ROUNDS_DEFAULT = 8


@dataclass(frozen=True)
class PurifyOnceResult:
    """One bilateral purification round on identical Werner copies."""

    w_in: float
    f_in: float
    w_out: float
    f_out: float
    p_success_bbpssw: float
    p_success: float  # after Trinity lock gain (capped at 1)
    yield_cost: float  # input pairs per successful output (= 2 / p_success)
    trinity_lock_gain: float
    trinity_fidelity_gain: float
    depolarizing_residual: float


@dataclass(frozen=True)
class PurifyToTargetResult:
    """Iterated purification until F ≥ target (or max_rounds)."""

    w_in: float
    f_in: float
    w_out: float
    f_out: float
    f_target: float
    rounds: int
    pairs_consumed: float  # total raw input pairs per purified output
    reached_target: bool
    per_round: tuple[PurifyOnceResult, ...]


def bbpssw_analytical(f: float) -> tuple[float, float]:
    """
    BBPSSW recurrence (twirled to Werner each round; NOT DEJMPS) on two identical Werner
    states.

    Returns
    -------
    f_out : float
        Post-selection fidelity (analytical, no Trinity overlay).
    p_success : float
        Analytical bilateral success probability.
    """
    if f <= 0.25:
        # No entanglement; purification cannot help
        return f, 1.0
    # Clamp numerical noise above 1
    f = min(f, 1.0)
    one_m = 1.0 - f
    p = f * f + (2.0 / 3.0) * f * one_m + (5.0 / 9.0) * one_m * one_m
    if p <= 0.0:
        return 0.25, 0.0
    f_out = (f * f + (1.0 / 9.0) * one_m * one_m) / p
    return f_out, p


def purify_once(
    w: float,
    *,
    trinity_lock_gain: float = TRINITY_LOCK_GAIN_DEFAULT,
    trinity_fidelity_gain: float = TRINITY_FIDELITY_GAIN_DEFAULT,
    depolarizing_residual: float = RESIDUAL_PHASE_ERROR_DEFAULT,
) -> PurifyOnceResult:
    """
    One TPP round: two Werner copies → one higher-F copy on success.

    Trinity overlays (SEPARATE from noise-damping Trinity multipliers):
      - ``trinity_lock_gain`` multiplies analytical p_success (capped at 1)
      - ``trinity_fidelity_gain`` multiplies analytical F_out (capped at 1)
      - ``depolarizing_residual`` shrinks output Werner weight each round: w ← w(1−ε)
    """
    if trinity_lock_gain < 1.0:
        raise ValueError("trinity_lock_gain must be ≥ 1.0 (1.0 = no TPP lock boost)")
    if trinity_fidelity_gain < 1.0:
        raise ValueError("trinity_fidelity_gain must be ≥ 1.0")
    if not (0.0 <= depolarizing_residual < 1.0):
        raise ValueError("depolarizing_residual must be in [0, 1)")

    f_in = werner_to_fidelity(w)
    f_bbpssw, p_bbpssw = bbpssw_analytical(f_in)

    p_success = min(1.0, p_bbpssw * trinity_lock_gain)
    f_out = min(1.0, f_bbpssw * trinity_fidelity_gain)
    # Per-round unitless depolarizing residual on the Werner weight (TUNED)
    w_out = fidelity_to_werner(f_out) * (1.0 - depolarizing_residual)
    # Keep physical: Werner weight in [-1/3, 1] but for mixed states ≥ 0
    w_out = max(0.0, min(1.0, w_out))
    f_out = werner_to_fidelity(w_out)

    if p_success <= 0.0:
        yield_cost = float("inf")
    else:
        yield_cost = 2.0 / p_success

    return PurifyOnceResult(
        w_in=w,
        f_in=f_in,
        w_out=w_out,
        f_out=f_out,
        p_success_bbpssw=p_bbpssw,
        p_success=p_success,
        yield_cost=yield_cost,
        trinity_lock_gain=trinity_lock_gain,
        trinity_fidelity_gain=trinity_fidelity_gain,
        depolarizing_residual=depolarizing_residual,
    )


def purify_to_target(
    w: float,
    f_target: float = PURIFY_TARGET_DEFAULT,
    max_rounds: int = MAX_ROUNDS_DEFAULT,
    *,
    trinity_lock_gain: float = TRINITY_LOCK_GAIN_DEFAULT,
    trinity_fidelity_gain: float = TRINITY_FIDELITY_GAIN_DEFAULT,
    depolarizing_residual: float = RESIDUAL_PHASE_ERROR_DEFAULT,
    skip_if_above_target: bool = True,
) -> PurifyToTargetResult:
    """
    Iterate ``purify_once`` until F ≥ f_target or ``max_rounds``.

    If ``skip_if_above_target`` and F_in ≥ f_target, returns immediately
    with pairs_consumed = 1.0 (no extra pairs; identity pass-through).

    ``pairs_consumed`` is the expected number of *input* copies of the
    starting state required per successful output (product of per-round
    yield costs). Time at rate Γ: t = pairs_consumed / Γ.
    """
    f_in = werner_to_fidelity(w)
    if skip_if_above_target and f_in >= f_target:
        return PurifyToTargetResult(
            w_in=w,
            f_in=f_in,
            w_out=w,
            f_out=f_in,
            f_target=f_target,
            rounds=0,
            pairs_consumed=1.0,
            reached_target=True,
            per_round=(),
        )

    rounds: list[PurifyOnceResult] = []
    pairs = 1.0
    w_cur = w
    for _ in range(max_rounds):
        if werner_to_fidelity(w_cur) >= f_target:
            break
        # Need improvement: if already at the BBPSSW fixed point (F=0.5), stop
        f_try, _ = bbpssw_analytical(werner_to_fidelity(w_cur))
        if f_try <= werner_to_fidelity(w_cur) + 1e-15:
            # Cannot improve further (F ≤ 0.5 fixed point of BBPSSW is 0.5)
            break
        once = purify_once(
            w_cur,
            trinity_lock_gain=trinity_lock_gain,
            trinity_fidelity_gain=trinity_fidelity_gain,
            depolarizing_residual=depolarizing_residual,
        )
        if once.yield_cost == float("inf") or (
            once.w_out <= w_cur and once.f_out <= once.f_in
        ):
            # Pathological / no progress
            rounds.append(once)
            pairs *= once.yield_cost if once.yield_cost != float("inf") else float("inf")
            w_cur = once.w_out
            break
        rounds.append(once)
        pairs *= once.yield_cost
        w_cur = once.w_out

    f_out = werner_to_fidelity(w_cur)
    return PurifyToTargetResult(
        w_in=w,
        f_in=f_in,
        w_out=w_cur,
        f_out=f_out,
        f_target=f_target,
        rounds=len(rounds),
        pairs_consumed=pairs,
        reached_target=f_out >= f_target - 1e-12,
        per_round=tuple(rounds),
    )


def pairs_to_rate(gamma_hz: float, pairs_consumed: float) -> float:
    """Effective rate of purified pairs given raw generation rate Γ."""
    if pairs_consumed <= 0.0 or pairs_consumed == float("inf"):
        return 0.0
    return gamma_hz / pairs_consumed


def time_cost_s(gamma_hz: float, pairs_consumed: float) -> float:
    """Mean wall-clock time to obtain one purified pair."""
    if gamma_hz <= 0.0:
        return float("inf")
    if pairs_consumed == float("inf"):
        return float("inf")
    return pairs_consumed / gamma_hz


def describe_tpp_defaults() -> str:
    """Human-readable summary of TPP defaults (all TUNED, not measured)."""
    return (
        f"TPP defaults (TUNED, no source): trinity_lock_gain={TRINITY_LOCK_GAIN_DEFAULT}, "
        f"trinity_fidelity_gain={TRINITY_FIDELITY_GAIN_DEFAULT}, "
        f"depolarizing_residual(per-round)={DEPOLARIZING_RESIDUAL_DEFAULT}, "
        f"purify_target={PURIFY_TARGET_DEFAULT}, "
        f"max_rounds={MAX_ROUNDS_DEFAULT}"
    )


# Backward-compatible alias (old, mislabeled name).
dejmps_analytical = bbpssw_analytical
