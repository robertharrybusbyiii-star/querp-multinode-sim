# Cheapest combos reaching N (F≥0.88, R≥1 Hz) — MODEL OUTPUT, NOT MEASURED

idle-mode for purified runs: `full`. Cost order: smallest k, then shortest T2, then smallest Γ multiplier, then purification off<link<swap<both, then cutoff (rows differing only by cutoff are collapsed; the cutoff column shows the cheapest = 'none' when it passes). T2 0.17 / 1.8 ms are published SnV⁻ values; 3.6 ms is the locked assumption; 10 / 100 ms and every k>1 are HYPOTHETICAL. Γ_eff = k·Γmult·85 Hz.

## N = 3

### A. Pure multiplexing (Γmult = 1, locked per-slot Γ = 85 Hz): 53 passing grid configs

| rank | k | Γmult | T2 (ms) | cutoff | purify | Γ_eff (Hz) | Γ_eff·T2 | F | R (Hz) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 1 | 10 | none | swap | 1700 | 17 | 0.9498 | 1.029 |
| 2 | 20 | 1 | 100 | none | swap | 1700 | 170 | 0.9563 | 1.257 |
| 3 | 50 | 1 | 1.8 | none | swap | 4250 | 7.65 | 0.9390 | 1.96 |
| 4 | 50 | 1 | 3.6 | none | swap | 4250 | 15.3 | 0.9489 | 2.509 |
| 5 | 50 | 1 | 10 | none | swap | 4250 | 42.5 | 0.9543 | 2.94 |

Cheapest per T2 at N=3 (Γmult = 1):

| T2 (ms) | cheapest passing config | Γ_eff·T2 | F | R (Hz) |
|---|---|---|---|---|
| 0.17 | k=100, Γmult=1, T2=0.17 ms, cutoff=0.5×T2, purify=swap | 1.45 | 0.9190 | 1.368 |
| 1.8 | k=50, Γmult=1, T2=1.8 ms, cutoff=none, purify=swap | 7.65 | 0.9390 | 1.96 |
| 3.6 | k=50, Γmult=1, T2=3.6 ms, cutoff=none, purify=swap | 15.3 | 0.9489 | 2.509 |
| 10 | k=20, Γmult=1, T2=10 ms, cutoff=none, purify=swap | 17 | 0.9498 | 1.029 |
| 100 | k=20, Γmult=1, T2=100 ms, cutoff=none, purify=swap | 170 | 0.9563 | 1.257 |

### B. Any Γmult ∈ {0.5, 1, 2, 4} (286 passing grid configs; Γmult is just another rate multiplier, only k·Γmult matters)

| rank | k | Γmult | T2 (ms) | cutoff | purify | Γ_eff (Hz) | Γ_eff·T2 | F | R (Hz) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 4 | 10 | none | swap | 1700 | 17 | 0.9498 | 1.029 |
| 2 | 5 | 4 | 100 | none | swap | 1700 | 170 | 0.9563 | 1.257 |
| 3 | 10 | 4 | 1.8 | none | swap | 3400 | 6.12 | 0.9333 | 1.387 |

Without purification: 0 passing grid configurations.

## N = 5

### A. Pure multiplexing (Γmult = 1, locked per-slot Γ = 85 Hz): 0 passing grid configs

**No configuration in the grid passes.** (See `sweep_required_gamma.md` for the Γ_eff the model would need beyond the grid.)

### B. Any Γmult ∈ {0.5, 1, 2, 4} (0 passing grid configs; Γmult is just another rate multiplier, only k·Γmult matters)

**No configuration in the grid passes.**

Without purification: 0 passing grid configurations.

## N = 9

### A. Pure multiplexing (Γmult = 1, locked per-slot Γ = 85 Hz): 0 passing grid configs

**No configuration in the grid passes.** (See `sweep_required_gamma.md` for the Γ_eff the model would need beyond the grid.)

### B. Any Γmult ∈ {0.5, 1, 2, 4} (0 passing grid configs; Γmult is just another rate multiplier, only k·Γmult matters)

**No configuration in the grid passes.**

Without purification: 0 passing grid configurations.

## N = 17

### A. Pure multiplexing (Γmult = 1, locked per-slot Γ = 85 Hz): 0 passing grid configs

**No configuration in the grid passes.** (See `sweep_required_gamma.md` for the Γ_eff the model would need beyond the grid.)

### B. Any Γmult ∈ {0.5, 1, 2, 4} (0 passing grid configs; Γmult is just another rate multiplier, only k·Γmult matters)

**No configuration in the grid passes.**

Without purification: 0 passing grid configurations.

