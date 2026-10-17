"""Run with:  python tests/test_sanity.py   (or pytest)."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from dataclasses import replace
from querp_sim import baseline as B
from querp_sim.assumptions import ASSUMPTIONS
from querp_sim.repeater import PurifyConfig, simulate_chain
from querp_sim.trinity_purification import bbpssw_analytical
from querp_sim.werner import fidelity_to_werner, mean_idle_factor, werner_to_fidelity


def test_locked_values_unchanged():
    assert (B.T2_S, B.P_SUCC, B.GAMMA_HZ, B.F_LINK) == (3.60e-3, 0.0071, 85.0, 0.887)
    assert ASSUMPTIONS["Gamma (locked)"][0] == B.GAMMA_HZ
    assert ASSUMPTIONS["T2"][0] == B.T2_S
    assert abs(B.P_DC_MW - 33.48) < 1e-9 and abs(B.POWER_MARGIN_MW - 21.48) < 1e-9


def test_n2_no_tpp_is_85hz_0p887():
    r = simulate_chain(B.locked_v03b(), 2)
    assert abs(r.rate_hz - 85.0) < 1e-9 and abs(r.fidelity - 0.887) < 1e-12


def test_n3_zero_idle_analytic():
    # Huge T2 => no decoherence; ideal swap of two F=0.887 Werner links.
    p = replace(B.locked_v03b(), t2_s=1e12)
    r = simulate_chain(p, 3)
    w = fidelity_to_werner(0.887)
    assert abs(r.fidelity - werner_to_fidelity(w * w)) < 1e-6
    assert abs(r.fidelity - 0.7910) < 5e-4


def test_idle_factor_exponential_average():
    assert abs(mean_idle_factor(1.0, 1.0) - 0.5) < 1e-12
    tau, t2 = 1 / 85.0, 3.6e-3
    assert abs(mean_idle_factor(tau, t2) - 1 / (1 + tau / t2)) < 1e-12
    # Monte-Carlo cross-check
    import random
    random.seed(1)
    n = 200000
    mc = sum(math.exp(-random.expovariate(1 / tau) / t2) for _ in range(n)) / n
    assert abs(mc - mean_idle_factor(tau, t2)) < 3e-3
    # truncated version vs MC
    tc = 1.0 * t2
    vals = []
    while len(vals) < 100000:
        d = random.expovariate(1 / tau)
        if d <= tc:
            vals.append(math.exp(-d / t2))
    assert abs(sum(vals) / len(vals) - mean_idle_factor(tau, t2, tc)) < 3e-3


def test_bbpssw_values():
    f, p = bbpssw_analytical(0.887)
    assert abs(f - 0.9158) < 1e-3 and 0 < p <= 1
    assert abs(bbpssw_analytical(0.5)[0] - 0.5) < 1e-12  # fixed point


def test_bounds_over_sweep():
    for tpp in (None, PurifyConfig(enabled=True), PurifyConfig(enabled=True, idle_mode="ideal")):
        for n in range(2, 18):
            r = simulate_chain(B.locked_v03b(), n, purify=tpp)
            assert 0.25 - 1e-9 <= r.fidelity <= 1 + 1e-9
            assert r.rate_hz <= B.GAMMA_HZ * (1 + 1e-9)


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); print("PASS", k)
