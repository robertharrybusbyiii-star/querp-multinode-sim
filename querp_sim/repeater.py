"""
Multi-node quantum repeater chain models (Werner + nested / sequential swap).

Chain: N QuERP nodes ⇒ L = N−1 elementary links.

Models
------
1. Nested swapping (exact for L = 2^n):
   - Level-0 links at rate Γ, Werner weight w0 from F_link.
   - At nesting level k, two independent level-(k−1) pairs are generated;
     expected time to have both ready is (3/2) τ_{k−1} (mean of max of two
     i.i.d. exponential waiting times with mean τ_{k−1}).
   - The earlier pair idles for a residual time Δ ~ Exp(mean τ_{k−1}); only
     that ONE arm decoheres (the later-arriving arm is fresh). The averaged
     decay factor is E[e^{−Δ/T2}] = 1/(1+τ_{k−1}/T2) (see werner.mean_idle_factor),
     NOT exp(−τ/T2). (AEON review fixes U5, U6.)
   - Swap: w_k = η_swap * (w * factor) * w; τ_k = (3/2) τ_{k−1} / p_swap.
   - End-to-end rate R = 1/τ_n, fidelity F = (1+3w_n)/4.

2. Sequential left-to-right swapping (any L ≥ 1):
   - Start with link 0 (τ=1/Γ, w=w0).
   - For each additional link: generate next elementary pair (mean 1/Γ);
     the growing remote entanglement idles for mean 1/Γ; decohere; swap
     with the fresh link; swap failure restarts the current swap attempt
     (factor 1/p_swap on that step's generation time).

3. Nested + temporal cutoff (extension, --cutoff-t2-mult):
   - Same nested skeleton, but an elementary (or lower-level) pair is kept
     only if the residual idle |T_a − T_b| ≤ t_cut = m·T2.
   - For two i.i.d. Exp(1/τ) generation times, P(|T_a−T_b| ≤ t_cut) = 1 − e^{−t_cut/τ}.
   - Decay factor is the exact truncated-exponential average
       E[e^{−Δ/T2} | Δ≤t_cut]  (werner.mean_idle_factor with t_cut);
     the conditional mean gap E[Δ | Δ≤t_cut] = τ − t_cut/(e^{t_cut/τ}−1)
     is kept only for reference.
   - Rate is reduced by the acceptance probability at each nesting level.
   - This does NOT change locked Γ/T2/F; it is a protocol extension that
     trades rate for fidelity when Γ·T2 ≲ 1 (v0.3b: Γ·T2 ≈ 0.306).

4. Trinity Purification Protocol (TPP) — SEPARATE from noise-damping Trinity
   ---------------------------------------------------------------------------
   Optional bilateral BBPSSW purification, twirled to a Werner state after every
   round (NOT DEJMPS; see trinity_purification.py).
   Does NOT modify locked Γ/T2/F_link. Charges rate for pairs consumed.
   KNOWN LIMITATION: link-level purification does not charge storage
   decoherence for pairs waiting for their partner copy (see README).

   --purify-when:
     - "link": purify elementary links to --purify-target before nesting/swap
     - "swap": purify after each swap / nesting level
     - "both": link then swap-level
   Default when TPP enabled: "link" (swap-level recurrence is very rate-expensive).

   If F already ≥ target, that stage is skipped (pairs_consumed = 1).
   N=2 without TPP recovers Γ, F_link exactly. With TPP + link purify and
   F_link < target, N=2 rate drops and F rises (documented).

Swap parameters (documented defaults for SnV⁻ matter nodes)
------------------------------------------------------------
- p_swap = 1.0  : deterministic matter-qubit Bell swap (CNOT + measure)
- η_swap = 1.0  : ideal Werner composition (override with --eta-swap <1 for residual gate noise)

N=2 sanity: L=1, no swap ⇒ R=Γ, F=F_link (exact recovery of locked link)
when Trinity Purification is disabled.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .baseline import NodeParams, USEFUL_F, USEFUL_RATE_HZ
from .trinity_purification import (
    MAX_ROUNDS_DEFAULT,
    PURIFY_TARGET_DEFAULT,
    DEPOLARIZING_RESIDUAL_DEFAULT,
    TRINITY_FIDELITY_GAIN_DEFAULT,
    TRINITY_LOCK_GAIN_DEFAULT,
    purify_to_target,
)
from .werner import (
    decohere_werner_factor,
    mean_idle_factor,
    fidelity_to_werner,
    swap_werner,
    werner_to_fidelity,
)


# Documented swap defaults (SnV⁻ matter-node model)
P_SWAP_DEFAULT = 1.0
ETA_SWAP_DEFAULT = 1.0

# Default purify-when when TPP is enabled via CLI
PURIFY_WHEN_DEFAULT = "link"


@dataclass(frozen=True)
class PurifyConfig:
    """Trinity Purification Protocol options (orthogonal to noise-damping Trinity)."""

    enabled: bool = False
    f_target: float = PURIFY_TARGET_DEFAULT
    when: str = PURIFY_WHEN_DEFAULT  # "link" | "swap" | "both"
    trinity_lock_gain: float = TRINITY_LOCK_GAIN_DEFAULT
    trinity_fidelity_gain: float = TRINITY_FIDELITY_GAIN_DEFAULT
    depolarizing_residual: float = DEPOLARIZING_RESIDUAL_DEFAULT  # per-round unitless shrink (TUNED)
    max_rounds: int = MAX_ROUNDS_DEFAULT
    skip_if_above_target: bool = True
    # Idle decoherence policy while TPP is enabled (rate ALWAYS pays pair cost):
    #   "raw"   — DEFAULT. Memory decoherence ON: idle uses pre-purify-tax τ
    #   "full"  — memory decoherence ON, idle uses rate τ (includes purify
    #             pair-cost stretch; harsh)
    #   "ideal" — OPTIMISTIC UPPER BOUND, not a prediction: zero swap-idle
    #             decoherence (Werner composition bound). The no-TPP baseline
    #             has decoherence on, so ideal-vs-baseline is NOT like-for-like.
    idle_mode: str = "raw"

    def __post_init__(self) -> None:
        if self.when not in ("link", "swap", "both"):
            raise ValueError(f"purify when must be link|swap|both, got {self.when!r}")
        if self.idle_mode not in ("ideal", "raw", "full"):
            raise ValueError(f"idle_mode must be ideal|raw|full, got {self.idle_mode!r}")

    @property
    def do_link(self) -> bool:
        return self.enabled and self.when in ("link", "both")

    @property
    def do_swap(self) -> bool:
        return self.enabled and self.when in ("swap", "both")


@dataclass(frozen=True)
class ChainResult:
    n_nodes: int
    n_links: int
    protocol: str  # "elementary" | "sequential" | "nested" | "nested_cutoff" | ...
    rate_hz: float
    fidelity: float
    werner_w: float
    mean_time_s: float
    nesting_level: int | None
    useful_rate: bool
    useful_fidelity: bool
    useful: bool
    cutoff_s: float | None = None
    # TPP accounting (None / defaults when purification disabled)
    purify_enabled: bool = False
    purify_when: str | None = None
    purify_target: float | None = None
    purify_rounds_link: int = 0
    pairs_per_e2e: float | None = None  # raw elementary pairs per e2e output


def _is_power_of_two(x: int) -> bool:
    return x > 0 and (x & (x - 1)) == 0


def _gap_accept_prob(tau: float, t_cut: float) -> float:
    """P(|T1−T2| ≤ t_cut) for T_i ~ Exp(1/τ) i.i.d. = 1 − exp(−t_cut/τ)."""
    if t_cut <= 0.0:
        return 0.0
    return 1.0 - math.exp(-t_cut / tau)


def _mean_idle_given_accept(tau: float, t_cut: float) -> float:
    """
    [Reference only — no longer used for the decay factor; see
    werner.mean_idle_factor.]
    E[|T1−T2| | |T1−T2| ≤ t_cut] for T_i ~ Exp(1/τ).

    The unconditional gap Δ=|T1−T2| is Exp(1/τ)-distributed (rate 1/τ), so
    E[Δ | Δ≤t] = τ − t / (e^{t/τ} − 1).
    """
    if t_cut <= 0.0:
        return 0.0
    x = t_cut / tau
    if x < 1e-9:
        return 0.0
    return tau - t_cut / (math.exp(x) - 1.0)


def _apply_purify(
    w: float,
    cfg: PurifyConfig,
) -> tuple[float, float, int]:
    """
    Run purify_to_target; return (w_out, pairs_consumed, rounds).

    pairs_consumed is relative to one copy of the *input* state at this stage.
    """
    res = purify_to_target(
        w,
        f_target=cfg.f_target,
        max_rounds=cfg.max_rounds,
        trinity_lock_gain=cfg.trinity_lock_gain,
        trinity_fidelity_gain=cfg.trinity_fidelity_gain,
        depolarizing_residual=cfg.depolarizing_residual,
        skip_if_above_target=cfg.skip_if_above_target,
    )
    return res.w_out, res.pairs_consumed, res.rounds


def _finish(
    n_nodes: int,
    L: int,
    protocol: str,
    rate: float,
    w: float,
    tau: float,
    nesting_level: int | None,
    cutoff_s: float | None,
    purify: PurifyConfig | None,
    purify_rounds_link: int = 0,
    pairs_per_e2e: float | None = None,
) -> ChainResult:
    F = werner_to_fidelity(w)
    cfg = purify or PurifyConfig(enabled=False)
    return ChainResult(
        n_nodes=n_nodes,
        n_links=L,
        protocol=protocol,
        rate_hz=rate,
        fidelity=F,
        werner_w=w,
        mean_time_s=tau,
        nesting_level=nesting_level,
        useful_rate=rate >= USEFUL_RATE_HZ,
        useful_fidelity=F >= USEFUL_F,
        useful=(rate >= USEFUL_RATE_HZ and F >= USEFUL_F),
        cutoff_s=cutoff_s,
        purify_enabled=cfg.enabled,
        purify_when=cfg.when if cfg.enabled else None,
        purify_target=cfg.f_target if cfg.enabled else None,
        purify_rounds_link=purify_rounds_link,
        pairs_per_e2e=pairs_per_e2e,
    )


def simulate_elementary(
    params: NodeParams,
    purify: PurifyConfig | None = None,
) -> ChainResult:
    """N=2 / L=1: recover locked adjacent-link operating point (unless TPP link purify)."""
    cfg = purify or PurifyConfig(enabled=False)
    w = fidelity_to_werner(params.f_link)
    tau = 1.0 / params.gamma_hz
    rounds_link = 0
    pairs_e2e = 1.0

    if cfg.do_link:
        w, pairs, rounds_link = _apply_purify(w, cfg)
        tau = tau * pairs
        pairs_e2e = pairs

    rate = 0.0 if tau == float("inf") else 1.0 / tau
    proto = "elementary"
    if cfg.enabled:
        proto = "elementary_tpp"
    return _finish(
        2, 1, proto, rate, w, tau, 0, None, cfg,
        purify_rounds_link=rounds_link,
        pairs_per_e2e=pairs_e2e,
    )


def simulate_nested(
    params: NodeParams,
    n_nodes: int,
    p_swap: float = P_SWAP_DEFAULT,
    eta_swap: float = ETA_SWAP_DEFAULT,
    cutoff_s: float | None = None,
    purify: PurifyConfig | None = None,
) -> ChainResult:
    """
    Nested entanglement swapping for L = N−1 = 2^n elementary links.

    If cutoff_s is set, apply temporal cutoff at each nesting level (extension).
    Optional TPP purification on links and/or after each swap level.

    When TPP is enabled, ``PurifyConfig.idle_mode`` controls swap-idle decoherence
    (rate always pays the purification pair cost):
      raw   — (default) decoherence on; idle clock uses pre-purify-tax τ
      full  — decoherence on; idle clock uses rate τ (pair-cost stretch)
      ideal — zero idle: OPTIMISTIC UPPER BOUND, not a prediction
    """
    cfg = purify or PurifyConfig(enabled=False)
    L = n_nodes - 1
    if L < 1:
        raise ValueError("n_nodes must be ≥ 2")
    if L == 1:
        return simulate_elementary(params, purify=cfg)
    if not _is_power_of_two(L):
        raise ValueError(f"nested protocol requires L=2^n, got L={L}")

    n_level = int(math.log2(L))
    tau_rate = 1.0 / params.gamma_hz
    tau_idle = 1.0 / params.gamma_hz  # coherent / gap clock
    w = fidelity_to_werner(params.f_link)
    rounds_link = 0
    pairs_per_current = 1.0

    # --- Link-level TPP -------------------------------------------------------
    if cfg.do_link:
        w, pairs, rounds_link = _apply_purify(w, cfg)
        tau_rate = tau_rate * pairs
        pairs_per_current *= pairs
        if cfg.idle_mode == "full":
            tau_idle = tau_idle * pairs
        # "raw" and "ideal": leave tau_idle at raw 1/Γ for this stage

    proto = "nested_cutoff" if cutoff_s is not None else "nested"
    if cfg.enabled:
        proto = proto + "_tpp"

    for _k in range(1, n_level + 1):
        if cfg.enabled and cfg.idle_mode == "ideal":
            idle_f = 1.0  # OPTIMISTIC UPPER BOUND: no memory decoherence
            p_acc = 1.0
            # Cutoff still affects rate if requested (gap on idle clock)
            if cutoff_s is not None:
                p_acc = _gap_accept_prob(tau_idle, cutoff_s)
                if p_acc <= 0.0:
                    w = 0.0
                    tau_rate = float("inf")
                    break
        elif cutoff_s is None:
            idle_f = mean_idle_factor(tau_idle, params.t2_s)
            p_acc = 1.0
        else:
            p_acc = _gap_accept_prob(tau_idle, cutoff_s)
            if p_acc <= 0.0:
                w = 0.0
                tau_rate = float("inf")
                break
            idle_f = mean_idle_factor(tau_idle, params.t2_s, cutoff_s)

        # Only the earlier-arriving pair idles; the other arm is fresh.
        w_dec = decohere_werner_factor(w, idle_f)
        w = swap_werner(w_dec, w, eta_swap=eta_swap)
        tau_rate = (1.5 * tau_rate) / (p_swap * p_acc)
        tau_idle = (1.5 * tau_idle) / (p_swap * p_acc)
        pairs_per_current = 2.0 * pairs_per_current / (p_swap * p_acc)

        # --- Swap-level TPP ---------------------------------------------------
        if cfg.do_swap and tau_rate != float("inf"):
            w, pairs_sw, _ = _apply_purify(w, cfg)
            tau_rate = tau_rate * pairs_sw
            pairs_per_current *= pairs_sw
            if cfg.idle_mode == "full":
                tau_idle = tau_idle * pairs_sw
            # raw/ideal: do not stretch idle clock by swap-purify yield

    rate = 0.0 if tau_rate == float("inf") else 1.0 / tau_rate
    return _finish(
        n_nodes, L, proto, rate, w, tau_rate, n_level, cutoff_s, cfg,
        purify_rounds_link=rounds_link,
        pairs_per_e2e=pairs_per_current if pairs_per_current != float("inf") else None,
    )


def simulate_sequential(
    params: NodeParams,
    n_nodes: int,
    p_swap: float = P_SWAP_DEFAULT,
    eta_swap: float = ETA_SWAP_DEFAULT,
    cutoff_s: float | None = None,
    purify: PurifyConfig | None = None,
) -> ChainResult:
    """
    Sequential left-to-right swapping for any L = N−1 ≥ 1.

    Optional cutoff: discard and retry the new-link step if the growing pair
    would idle longer than t_cut (P(T_new ≤ t_cut) = 1−e^{−t_cut/τ_link}).
    Optional TPP on elementary links and/or after each swap.
    See ``simulate_nested`` for ``idle_mode`` semantics under TPP.
    """
    cfg = purify or PurifyConfig(enabled=False)
    L = n_nodes - 1
    if L < 1:
        raise ValueError("n_nodes must be ≥ 2")
    if L == 1:
        return simulate_elementary(params, purify=cfg)

    t_link_raw = 1.0 / params.gamma_hz
    w0_raw = fidelity_to_werner(params.f_link)
    rounds_link = 0
    pairs_link = 1.0

    if cfg.do_link:
        w0, pairs_link, rounds_link = _apply_purify(w0_raw, cfg)
    else:
        w0 = w0_raw

    t_link_rate = t_link_raw * pairs_link
    if cfg.enabled and cfg.idle_mode == "full":
        t_link_idle = t_link_rate
    else:
        # raw / ideal / no-TPP: coherent wait uses raw elementary timescale
        t_link_idle = t_link_raw

    w = w0
    tau = t_link_rate
    pairs_per_e2e = pairs_link
    proto = "sequential_cutoff" if cutoff_s is not None else "sequential"
    if cfg.enabled:
        proto = proto + "_tpp"

    for _ in range(L - 1):
        if cfg.enabled and cfg.idle_mode == "ideal":
            idle_f = 1.0  # OPTIMISTIC UPPER BOUND: no memory decoherence
            p_acc = 1.0
            if cutoff_s is not None:
                p_acc = 1.0 - math.exp(-cutoff_s / t_link_idle)
                if p_acc <= 0.0:
                    w = 0.0
                    tau = float("inf")
                    break
        elif cutoff_s is None:
            idle_f = mean_idle_factor(t_link_idle, params.t2_s)
            p_acc = 1.0
        else:
            p_acc = 1.0 - math.exp(-cutoff_s / t_link_idle)
            if p_acc <= 0.0:
                w = 0.0
                tau = float("inf")
                break
            idle_f = mean_idle_factor(t_link_idle, params.t2_s, cutoff_s)

        # Growing remote pair idles while the fresh link is generated (one arm).
        w_idle = decohere_werner_factor(w, idle_f)
        w_fresh = w0
        w = swap_werner(w_idle, w_fresh, eta_swap=eta_swap)
        tau = tau + t_link_rate / (p_swap * p_acc)
        pairs_per_e2e = pairs_per_e2e + pairs_link / (p_swap * p_acc)

        if cfg.do_swap and tau != float("inf"):
            w, pairs_sw, _ = _apply_purify(w, cfg)
            tau = tau * pairs_sw
            pairs_per_e2e *= pairs_sw
            if cfg.idle_mode == "full":
                t_link_idle = t_link_idle  # growing-pair idle scale unchanged here;
                # sequential fresh-link wait stays on elementary clock

    rate = 0.0 if tau == float("inf") else 1.0 / tau
    return _finish(
        n_nodes, L, proto, rate, w, tau, None, cutoff_s, cfg,
        purify_rounds_link=rounds_link,
        pairs_per_e2e=pairs_per_e2e if pairs_per_e2e != float("inf") else None,
    )


def simulate_chain(
    params: NodeParams,
    n_nodes: int,
    protocol: str = "auto",
    p_swap: float = P_SWAP_DEFAULT,
    eta_swap: float = ETA_SWAP_DEFAULT,
    cutoff_s: float | None = None,
    purify: PurifyConfig | None = None,
) -> ChainResult:
    """
    protocol:
      - "auto": nested when L is a power of two, else sequential
      - "nested": require L=2^n
      - "sequential": always sequential
    """
    L = n_nodes - 1
    kwargs = dict(p_swap=p_swap, eta_swap=eta_swap, cutoff_s=cutoff_s, purify=purify)
    if protocol == "sequential":
        return simulate_sequential(params, n_nodes, **kwargs)
    if protocol == "nested":
        return simulate_nested(params, n_nodes, **kwargs)
    if protocol == "auto":
        if L == 1 or _is_power_of_two(L):
            return simulate_nested(params, n_nodes, **kwargs)
        return simulate_sequential(params, n_nodes, **kwargs)
    raise ValueError(f"unknown protocol {protocol!r}")


def sweep_n(
    params: NodeParams,
    n_min: int = 2,
    n_max: int = 17,
    protocol: str = "auto",
    p_swap: float = P_SWAP_DEFAULT,
    eta_swap: float = ETA_SWAP_DEFAULT,
    cutoff_s: float | None = None,
    purify: PurifyConfig | None = None,
) -> list[ChainResult]:
    """Sweep N from n_min..n_max inclusive."""
    results = []
    for n in range(n_min, n_max + 1):
        results.append(
            simulate_chain(
                params,
                n,
                protocol=protocol,
                p_swap=p_swap,
                eta_swap=eta_swap,
                cutoff_s=cutoff_s,
                purify=purify,
            )
        )
    return results
