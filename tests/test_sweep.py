"""Tests for multiplexing + sweep. Run: python tests/test_sweep.py (or pytest)."""
import csv, math, os, random, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import sweep as S
from querp_sim import baseline as B
from querp_sim.multiplexing import effective_gamma, multiplexed_params
from querp_sim.repeater import simulate_chain
from querp_sim.werner import mean_idle_factor


def test_locked_baseline_untouched_and_identity():
    p = multiplexed_params(B.locked_v03b(), 1)
    assert p.gamma_hz == B.GAMMA_HZ and p.t2_s == B.T2_S and p.f_link == B.F_LINK
    multiplexed_params(B.locked_v03b(), 100, 4.0, t2_s=0.1)
    assert (B.T2_S, B.P_SUCC, B.GAMMA_HZ, B.F_LINK) == (3.60e-3, 0.0071, 85.0, 0.887)
    assert B.locked_v03b().gamma_hz == 85.0


def test_effective_gamma_and_validation():
    assert effective_gamma(85.0, 10) == 850.0
    assert effective_gamma(85.0, 5, 2.0) == 850.0
    for bad in ((85.0, 0), (85.0, 1.5), (85.0, 2, 0.0)):
        try:
            effective_gamma(*bad)
        except ValueError:
            continue
        raise AssertionError(f"expected ValueError for {bad}")


def test_earliest_of_k_monte_carlo():
    # min of k Exp(Γ) has mean 1/(kΓ); gap of two independent mins is Exp(mean 1/(kΓ)),
    # so E[exp(-gap/T2)] = mean_idle_factor(1/(kΓ), T2).
    random.seed(7)
    g, k, t2, n = 85.0, 5, 3.6e-3, 120000
    mins = [min(random.expovariate(g) for _ in range(k)) for _ in range(n)]
    assert abs(sum(mins) / n - 1 / (k * g)) / (1 / (k * g)) < 0.02
    mins2 = [min(random.expovariate(g) for _ in range(k)) for _ in range(n)]
    mc = sum(math.exp(-abs(a - b) / t2) for a, b in zip(mins, mins2)) / n
    assert abs(mc - mean_idle_factor(1 / (k * g), t2)) < 5e-3


def test_n2_rate_scales_with_k():
    for k in (1, 5, 100):
        r = simulate_chain(multiplexed_params(B.locked_v03b(), k), 2)
        assert abs(r.rate_hz - 85.0 * k) < 1e-9 and abs(r.fidelity - 0.887) < 1e-12


def test_monotone_in_k_without_purification():
    base = B.locked_v03b()
    for n in (3, 4, 5, 9):
        prev_f = prev_r = 0.0
        for k in S.K_VALUES:
            r = simulate_chain(multiplexed_params(base, k), n)
            assert r.fidelity >= prev_f - 1e-12 and r.rate_hz >= prev_r - 1e-12
            prev_f, prev_r = r.fidelity, r.rate_hz
        # swap bound: F can never reach 0.88 for N>=3 without purification
        assert prev_f < 0.88


def test_quick_sweep_structure_bounds_and_csv():
    rows = S.run_sweep(ks=(1, 10), t2s=S.T2_VALUES[2:4], gmults=(1.0,), cutoffs=(None, 1.0),
                       n_range=(2, 3, 4))
    assert len(rows) == 2 * 2 * 1 * 2 * len(S.PURIFY_MODES) * 3
    for r in rows:
        assert 0.25 - 1e-9 <= r["fidelity"] <= 1 + 1e-9
        assert r["rate_hz"] <= r["gamma_eff_hz"] * (1 + 1e-9)
        assert abs(r["gamma_eff_t2"] - r["gamma_eff_hz"] * r["t2_ms"] * 1e-3) < 1e-9 * max(1, r["gamma_eff_t2"])
    locked = [r for r in rows if (r["k"], r["t2_ms"], r["purify"], r["n_nodes"], r["cutoff_t2_mult"])
              == (1, 3.6, "off", 2, "none")]
    assert len(locked) == 1 and abs(locked[0]["rate_hz"] - 85.0) < 1e-9 and locked[0]["useful"] == 1
    assert all(r["useful"] == 0 for r in rows if r["purify"] == "off" and r["n_nodes"] >= 3)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "x.csv")
        S.write_csv(rows, p)
        back = list(csv.DictReader(open(p)))
        assert len(back) == len(rows) and list(back[0].keys()) == S.COLUMNS


def test_max_useful_n_and_ranking_order():
    rows = S.run_sweep(ks=(1, 20, 50), t2s=S.T2_VALUES[2:3], gmults=(1.0,), cutoffs=(None,),
                       purify_modes=("off", "swap"), n_range=(2, 3))
    best = S.max_useful_n(rows)
    assert best[(1, 1.0, 3.6, "none", "off")] == 2
    top, total = S.ranked_for_target(rows, 3, gamma_mult=1.0)
    assert total >= 1 and all(r["useful"] and r["n_nodes"] == 3 for r in top)
    assert [S.cheapness(r) for r in top] == sorted(S.cheapness(r) for r in top)
    assert S.ranked_for_target(rows, 9)[1] == 0


def test_required_gamma_eff_n3_and_unreachable():
    res = S.required_gamma_eff(3, 100e-3, "swap")
    assert res is not None and res[1] >= 1.0 and res[2] >= 0.88
    assert S.required_gamma_eff(3, 100e-3, "link", g_hi=1e4) is not None  # link-purify passes N=3 at modest Γ_eff
    try:
        S.purify_config("bogus", "raw")
    except ValueError:
        pass
    else:
        raise AssertionError


def test_plots_smoke():
    rows = S.run_sweep(ks=(1, 10), t2s=S.T2_VALUES[2:4], gmults=(1.0,), cutoffs=(None,), n_range=(2, 3))
    with tempfile.TemporaryDirectory() as d:
        S.ART = d
        paths = S.make_plots(rows)
        S.ART = os.path.join(os.path.dirname(os.path.abspath(S.__file__)), "artifacts")
        assert len(paths) == 3 and all(os.path.getsize(p) > 5000 for p in paths)


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); print("PASS", k)
