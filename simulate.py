#!/usr/bin/env python3
"""
QuERP multi-node quantum repeater simulation CLI
Grounded in LOCKED QuERP Node baseline v0.3b (24 Aug 2026).

Usage:
  python simulate.py
  python simulate.py --n-max 17 --protocol auto
  python simulate.py --scenarios nominal_v0.3b without_trinity
  python simulate.py --cutoff-t2-mult 1.0
  python simulate.py --trinity-purify --purify-target 0.95 --purify-when both
  python simulate.py --trinity-purify --scenarios nominal_v0.3b without_trinity
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from querp_sim.baseline import (
    USEFUL_F,
    USEFUL_RATE_HZ,
    assert_locked_power_identity,
)
from querp_sim.assumptions import format_assumptions
from querp_sim.power import power_report
from querp_sim.repeater import (
    ETA_SWAP_DEFAULT,
    P_SWAP_DEFAULT,
    PURIFY_WHEN_DEFAULT,
    PurifyConfig,
    simulate_chain,
    sweep_n,
)
from querp_sim.scenarios import all_scenarios
from querp_sim.trinity_purification import (
    PURIFY_TARGET_DEFAULT,
    DEPOLARIZING_RESIDUAL_DEFAULT,
    TRINITY_FIDELITY_GAIN_DEFAULT,
    TRINITY_LOCK_GAIN_DEFAULT,
    describe_tpp_defaults,
)


def _scenario_map():
    return {s.name: s for s in all_scenarios()}


def sanity_check_n2(params, p_swap: float, eta_swap: float) -> None:
    """N=2 must recover Γ and F_link (exact under this model) WITHOUT TPP."""
    r = simulate_chain(params, 2, protocol="auto", p_swap=p_swap, eta_swap=eta_swap)
    ok_rate = abs(r.rate_hz - params.gamma_hz) < 1e-9
    ok_f = abs(r.fidelity - params.f_link) < 1e-12
    print("=== Sanity check (N=2 recovers elementary link, TPP off) ===")
    print(f"  expected Γ={params.gamma_hz:.1f} Hz, F={params.f_link:.3f}")
    print(f"  got      Γ={r.rate_hz:.1f} Hz, F={r.fidelity:.3f}  protocol={r.protocol}")
    if not (ok_rate and ok_f):
        raise SystemExit("SANITY CHECK FAILED: N=2 did not recover locked link")
    print("  PASS")
    print()


def print_power(params) -> None:
    pr = power_report(params)
    print(f"=== Power autonomy ({params.name}) ===")
    print(f"  RF density     : {pr['rf_density_uw_cm2']:.1f} µW/cm²")
    print(f"  DC harvest     : {pr['p_dc_mw']:.2f} mW")
    print(f"  Electronics    : {pr['p_electronics_mw']:.2f} mW")
    print(f"  Power margin   : {pr['power_margin_mw']:+.2f} mW")
    print(f"  Autonomous     : {pr['energy_autonomous']}  (node_pass={params.node_pass})")
    print()


def check_invariants(results, gamma_hz: float, label: str) -> None:
    """Sanity bounds: 0.25 ≤ F ≤ 1 and R ≤ Γ for every point."""
    for r in results:
        assert 0.25 - 1e-9 <= r.fidelity <= 1.0 + 1e-9, (label, r.n_nodes, r.fidelity)
        assert r.rate_hz <= gamma_hz * (1.0 + 1e-9), (label, r.n_nodes, r.rate_hz)


def print_table(results, label: str) -> None:
    print(f"=== End-to-end sweep — {label} ===")
    print(
        f"{'N':>3} {'L':>3} {'protocol':>20} {'R_e2e [Hz]':>12} {'F_e2e':>8} "
        f"{'useful_R':>8} {'useful_F':>8} {'useful':>6}"
    )
    print("-" * 82)
    for r in results:
        print(
            f"{r.n_nodes:3d} {r.n_links:3d} {r.protocol:>20} {r.rate_hz:12.4e} "
            f"{r.fidelity:8.4f} {str(r.useful_rate):>8} {str(r.useful_fidelity):>8} "
            f"{str(r.useful):>6}"
        )
    print()
    f_ok = [r.n_nodes for r in results if r.fidelity >= USEFUL_F]
    f_ok_5 = [r.n_nodes for r in results if r.fidelity >= 0.5]
    r_ok = [r.n_nodes for r in results if r.rate_hz >= USEFUL_RATE_HZ]
    both = [r.n_nodes for r in results if r.useful]
    print("Key findings:")
    print(f"  F_e2e ≥ {USEFUL_F} (node floor): N ∈ {f_ok if f_ok else '∅'}")
    print(f"  F_e2e ≥ 0.5 (above classical): N ∈ {f_ok_5 if f_ok_5 else '∅'}")
    print(f"  R_e2e ≥ {USEFUL_RATE_HZ} Hz: N ∈ {r_ok if r_ok else '∅'}")
    print(f"  both (F≥{USEFUL_F} & R≥{USEFUL_RATE_HZ}): N ∈ {both if both else '∅'}")
    if f_ok:
        print(f"  max N with F≥{USEFUL_F}: {max(f_ok)}")
    if f_ok_5:
        print(f"  max N with F≥0.5: {max(f_ok_5)}")
    if both:
        print(f"  max N with both node-floor thresholds: {max(both)}")
    else:
        print("  max N with both node-floor thresholds: none")
    print()


def plot_results(
    scenario_results: dict,
    out_dir: str,
    useful_f: float = USEFUL_F,
    useful_r: float = USEFUL_RATE_HZ,
) -> tuple[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    rate_path = os.path.join(out_dir, "rate_vs_N.png")
    fid_path = os.path.join(out_dir, "fidelity_vs_N.png")

    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    for name, results in scenario_results.items():
        ns = [r.n_nodes for r in results]
        rates = [max(r.rate_hz, 1e-30) for r in results]
        ax.semilogy(ns, rates, marker="o", label=name)
    ax.axhline(useful_r, color="gray", ls="--", lw=1, label=f"useful R={useful_r} Hz")
    ax.set_xlabel("Number of QuERP nodes N")
    ax.set_ylabel("End-to-end entanglement rate [Hz]")
    ax.set_title("QuERP repeater — rate vs N\nMODEL OUTPUT, NOT MEASURED (assumption-based; no fiber loss)", fontsize=9)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=7, loc="best")
    all_n = sorted({r.n_nodes for rs in scenario_results.values() for r in rs})
    ax.set_xticks(all_n)
    fig.tight_layout()
    fig.savefig(rate_path, dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    for name, results in scenario_results.items():
        ns = [r.n_nodes for r in results]
        fids = [r.fidelity for r in results]
        ax.plot(ns, fids, marker="o", label=name)
    ax.axhline(useful_f, color="gray", ls="--", lw=1, label=f"useful F={useful_f}")
    ax.axhline(0.5, color="lightgray", ls=":", lw=1, label="F=0.5")
    ax.set_xlabel("Number of QuERP nodes N")
    ax.set_ylabel("End-to-end entanglement fidelity")
    ax.set_title("QuERP repeater — fidelity vs N\nMODEL OUTPUT, NOT MEASURED (assumption-based; no fiber loss)", fontsize=9)
    ax.set_ylim(0.20, 1.0)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, loc="best")
    ax.set_xticks(all_n)
    fig.tight_layout()
    fig.savefig(fid_path, dpi=150)
    plt.close(fig)

    return rate_path, fid_path


def write_csv(path: str, results) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            "N,L,protocol,rate_hz,fidelity,werner_w,mean_time_s,cutoff_s,"
            "purify_enabled,purify_when,purify_target,purify_rounds_link,"
            "pairs_per_e2e,useful\n"
        )
        for r in results:
            cut = "" if r.cutoff_s is None else f"{r.cutoff_s:.8e}"
            pwhen = "" if r.purify_when is None else r.purify_when
            ptar = "" if r.purify_target is None else f"{r.purify_target:.6f}"
            pairs = "" if r.pairs_per_e2e is None else f"{r.pairs_per_e2e:.8e}"
            f.write(
                f"{r.n_nodes},{r.n_links},{r.protocol},{r.rate_hz:.8e},"
                f"{r.fidelity:.8f},{r.werner_w:.8e},{r.mean_time_s:.8e},"
                f"{cut},{int(r.purify_enabled)},{pwhen},{ptar},"
                f"{r.purify_rounds_link},{pairs},{int(r.useful)}\n"
            )


def build_purify_config(args) -> PurifyConfig | None:
    """Build PurifyConfig from CLI; None means TPP disabled."""
    if not args.trinity_purify:
        return None
    return PurifyConfig(
        enabled=True,
        f_target=args.purify_target,
        when=args.purify_when,
        trinity_lock_gain=args.trinity_purify_gain,
        trinity_fidelity_gain=args.trinity_fidelity_gain,
        depolarizing_residual=args.depolarizing_residual,
        max_rounds=args.purify_max_rounds,
        skip_if_above_target=not args.force_purify,
        idle_mode=args.purify_idle,
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="QuERP multi-node repeater sim (LOCKED baseline v0.3b)"
    )
    parser.add_argument("--n-min", type=int, default=2)
    parser.add_argument("--n-max", type=int, default=17)
    parser.add_argument(
        "--protocol",
        choices=["auto", "nested", "sequential"],
        default="auto",
        help="auto: nested when L=2^n else sequential",
    )
    parser.add_argument("--p-swap", type=float, default=P_SWAP_DEFAULT)
    parser.add_argument("--eta-swap", type=float, default=ETA_SWAP_DEFAULT)
    parser.add_argument(
        "--cutoff-t2-mult",
        type=float,
        default=None,
        help="If set (e.g. 1.0), also sweep a temporal-cutoff protocol "
        "with t_cut = mult * T2 (extension; trades rate for fidelity)",
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=None,
        help="Subset of scenario names (default: all)",
    )
    parser.add_argument(
        "--artifacts",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts"),
    )
    parser.add_argument("--primary", default="nominal_v0.3b")

    # --- Trinity Purification Protocol (SEPARATE from noise-damping Trinity) ---
    tpp = parser.add_argument_group(
        "Trinity Purification Protocol (TPP)",
        "SEPARATE from the locked v0.3b noise-damping Trinity multipliers "
        "already baked into Γ/T2/p_succ. Does not change locked HW numbers.",
    )
    tpp.add_argument(
        "--trinity-purify",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enable Trinity Purification Protocol (BBPSSW, twirled each round, + TUNED Trinity lock gain). "
        "Default: off. Use --no-trinity-purify to force off.",
    )
    tpp.add_argument(
        "--purify-target",
        type=float,
        default=PURIFY_TARGET_DEFAULT,
        help=f"Fidelity target for TPP rounds (default {PURIFY_TARGET_DEFAULT})",
    )
    tpp.add_argument(
        "--purify-when",
        choices=["link", "swap", "both"],
        default=PURIFY_WHEN_DEFAULT,
        help="When to purify: elementary links, after each swap level, or both "
        f"(default {PURIFY_WHEN_DEFAULT})",
    )
    tpp.add_argument(
        "--trinity-purify-gain",
        type=float,
        default=TRINITY_LOCK_GAIN_DEFAULT,
        help="TPP Trinity lock gain on BBPSSW success probability (TUNED, no source, no demonstrated mechanism) "
        f"(default {TRINITY_LOCK_GAIN_DEFAULT}; suggested 1.0–1.15). "
        "NOT the noise-damping Trinity coherence multiplier.",
    )
    tpp.add_argument(
        "--trinity-fidelity-gain",
        type=float,
        default=TRINITY_FIDELITY_GAIN_DEFAULT,
        help="Optional multiplier on analytical BBPSSW post-selection fidelity "
        f"(default {TRINITY_FIDELITY_GAIN_DEFAULT} = analytical curve)",
    )
    tpp.add_argument(
        "--depolarizing-residual",
        "--residual-phase-error",  # deprecated alias (old, misleading name)
        dest="depolarizing_residual",
        type=float,
        default=DEPOLARIZING_RESIDUAL_DEFAULT,
        help="Per-ROUND unitless depolarizing residual: output Werner weight is "
        "multiplied by (1−ε) after EVERY purification round (compounds; not a "
        "one-time floor, not a phase angle). TUNED, no source "
        f"(default {DEPOLARIZING_RESIDUAL_DEFAULT}). --residual-phase-error is a deprecated alias.",
    )
    tpp.add_argument(
        "--purify-max-rounds",
        type=int,
        default=8,
        help="Max BBPSSW recurrence rounds per purify_to_target call",
    )
    tpp.add_argument(
        "--force-purify",
        action="store_true",
        help="Purify even when F already ≥ target (default: skip if above target)",
    )
    tpp.add_argument(
        "--purify-idle",
        choices=["ideal", "raw", "full"],
        default="raw",
        help="Swap-idle decoherence under TPP (rate always pays pair cost). "
        "raw=memory decoherence ON, pre-tax τ (DEFAULT); "
        "full=decoherence ON, idle uses rate τ (harsh); "
        "ideal=NO memory decoherence: OPTIMISTIC UPPER BOUND, not a prediction "
        "and not like-for-like with the no-TPP baseline.",
    )
    tpp.add_argument(
        "--compare-tpp",
        action="store_true",
        default=False,
        help="Also sweep the same scenarios WITH TPP (if --trinity-purify off) "
        "or WITHOUT TPP (if --trinity-purify on), and write "
        "summary_with_trinity_purify.csv for the primary+TPP curve.",
    )

    args = parser.parse_args(argv)

    assert_locked_power_identity()
    smap = _scenario_map()
    names = args.scenarios if args.scenarios else list(smap.keys())
    for n in names:
        if n not in smap:
            raise SystemExit(f"Unknown scenario {n!r}. Choose from {list(smap)}")

    primary = smap[args.primary] if args.primary in smap and args.primary in names else smap[names[0]]
    if "nominal_v0.3b" in names:
        primary = smap["nominal_v0.3b"]

    purify_cfg = build_purify_config(args)

    print("QuERP multi-node simulation — LOCKED baseline v0.3b (24 Aug 2026)")
    print()
    print(format_assumptions())
    print()
    print(f"Protocol={args.protocol}, p_swap={args.p_swap}, η_swap={args.eta_swap}")
    print(f"N = {args.n_min} .. {args.n_max}")
    print(f"Γ·T2 (nominal) = {primary.gamma_hz * primary.t2_s:.3f}  "
          f"(≪1 ⇒ idle decoherence dominates without cutoff/multiplexing)")
    print()
    print("Noise-damping Trinity (locked into Γ/T2/p_succ): UNCHANGED")
    if purify_cfg is not None:
        print(f"Trinity Purification Protocol (TPP): ON  "
              f"target={purify_cfg.f_target}, when={purify_cfg.when}, "
              f"lock_gain={purify_cfg.trinity_lock_gain}, "
              f"F_gain={purify_cfg.trinity_fidelity_gain}, "
              f"depol_residual/round={purify_cfg.depolarizing_residual}, "
              f"idle={purify_cfg.idle_mode}")
    else:
        print("Trinity Purification Protocol (TPP): OFF")
        print(f"  ({describe_tpp_defaults()})")
    print()

    # Always sanity-check N=2 WITHOUT purify (locked recovery)
    sanity_check_n2(primary, args.p_swap, args.eta_swap)

    print("=== Locked quantum (primary scenario) ===")
    print(f"  T2      = {primary.t2_s*1e3:.2f} ms")
    print(f"  p_succ  = {primary.p_succ}")
    print(f"  Γ       = {primary.gamma_hz:.1f} Hz")
    print(f"  F_link  = {primary.f_link:.3f}")
    print()

    scenario_results = {}
    for name in names:
        params = smap[name]
        print_power(params)
        results = sweep_n(
            params,
            n_min=args.n_min,
            n_max=args.n_max,
            protocol=args.protocol,
            p_swap=args.p_swap,
            eta_swap=args.eta_swap,
            cutoff_s=None,
            purify=None,  # baseline without TPP first
        )
        check_invariants(results, params.gamma_hz, name)
        scenario_results[name] = results
        print_table(results, label=f"scenario={params.name} (no TPP)")

        # Optional cutoff extension curve (same hardware params, no TPP)
        if args.cutoff_t2_mult is not None:
            t_cut = args.cutoff_t2_mult * params.t2_s
            cut_results = sweep_n(
                params,
                n_min=args.n_min,
                n_max=args.n_max,
                protocol=args.protocol,
                p_swap=args.p_swap,
                eta_swap=args.eta_swap,
                cutoff_s=t_cut,
                purify=None,
            )
            cut_label = f"{name}+cutoff({args.cutoff_t2_mult:.2f}·T2)"
            scenario_results[cut_label] = cut_results
            print_table(cut_results, label=cut_label)

        # TPP curves
        run_tpp = purify_cfg is not None or args.compare_tpp
        if run_tpp:
            cfg = purify_cfg or PurifyConfig(
                enabled=True,
                f_target=args.purify_target,
                when=args.purify_when,
                trinity_lock_gain=args.trinity_purify_gain,
                trinity_fidelity_gain=args.trinity_fidelity_gain,
                depolarizing_residual=args.depolarizing_residual,
                max_rounds=args.purify_max_rounds,
                skip_if_above_target=not args.force_purify,
                idle_mode=args.purify_idle,
            )
            tpp_results = sweep_n(
                params,
                n_min=args.n_min,
                n_max=args.n_max,
                protocol=args.protocol,
                p_swap=args.p_swap,
                eta_swap=args.eta_swap,
                cutoff_s=None,
                purify=cfg,
            )
            tpp_label = (
                f"{name}+TPP(target={cfg.f_target},when={cfg.when},"
                f"idle={cfg.idle_mode})"
            )
            if cfg.idle_mode == "ideal":
                print("  !! idle=ideal: NO memory decoherence in TPP curve — "
                      "OPTIMISTIC UPPER BOUND, not a prediction.")
            check_invariants(tpp_results, params.gamma_hz, tpp_label)
            scenario_results[tpp_label] = tpp_results
            print_table(tpp_results, label=tpp_label)

            # Cross: without_trinity hardware + TPP is already covered when
            # without_trinity is in the scenario list and compare/tpp is on.

    rate_path, fid_path = plot_results(scenario_results, args.artifacts)
    print(f"Wrote {rate_path}")
    print(f"Wrote {fid_path}")

    csv_path = os.path.join(args.artifacts, f"summary_{primary.name}.csv")
    write_csv(csv_path, scenario_results[primary.name])
    print(f"Wrote {csv_path}")

    # Always write TPP summary CSV when TPP curves were generated for primary
    tpp_key = None
    for k in scenario_results:
        if k.startswith(f"{primary.name}+TPP"):
            tpp_key = k
            break
    if tpp_key is not None:
        csv_tpp = os.path.join(args.artifacts, "summary_with_trinity_purify.csv")
        write_csv(csv_tpp, scenario_results[tpp_key])
        print(f"Wrote {csv_tpp}")

    if args.cutoff_t2_mult is not None:
        cut_key = f"{primary.name}+cutoff({args.cutoff_t2_mult:.2f}·T2)"
        if cut_key in scenario_results:
            csv_cut = os.path.join(
                args.artifacts, f"summary_{primary.name}_cutoff.csv"
            )
            write_csv(csv_cut, scenario_results[cut_key])
            print(f"Wrote {csv_cut}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
