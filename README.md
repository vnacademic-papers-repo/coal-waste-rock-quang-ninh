# Supplementary materials: S1 financial scenario model

This repository contains the inputs, calculation code, outputs, and figures supporting the manuscript *Assessment of Opportunities and Challenges Associated with Coal-Mine Waste Rock in Quang Ninh*.

## Contents

- `assumptions.json` — model inputs, fixed assumptions, parameter ranges, and scope limitations.
- `s1_risk.py` — deterministic cash-flow, break-even, Monte Carlo, convergence, and sensitivity calculations.
- `results.json` — reported numerical outputs, including model checks.
- `s1_draws_seed20261003.npz` — the 100,000 simulated input draws and the corresponding FNPV values for the three haul distances (3, 5, and 7.5 km) in the main independent-triangular configuration.
- `Figure_1_two_outlets.svg` — conceptual diagram of the external S1 and internal S2 routes.
- `Figure_2_FNPV_CDF.svg` — cumulative distributions for S1 at the three assumed haul distances.
- `requirements.txt` — NumPy version used for the reported run.

## Reproducing the analysis

Use Python 3.11 or later, install the dependency, and run the script from this directory:

```bash
python -m pip install -r requirements.txt
python s1_risk.py
```

The script writes updated `assumptions.json`, `results.json`, and `s1_draws_seed20261003.npz` files in the same directory. The main run uses NumPy's PCG64 generator, seed `20261003`, and 100,000 draws. The script includes checks for the annuity calculation, break-even roots, mass balance under the equal-density assumption, continuity of the transport tariff, and consistency of ex-gate and delivered-price formulations.

## Scope and interpretation

The case study is associated with Mong Duong Mine, and the manuscript identifies site-context information as recorded there. The supplementary package does not contain raw mine logs; the underlying record source, date, and measurement protocol should be cited or documented by the authors before public release. Financial results are model calculations, not observed project outcomes. The Monte Carlo distributions and bounds are analyst-selected uncertainty scenarios, not empirical frequency distributions and not fitted to observed data or elicited from experts. In particular, the delivered price is a scenario value, the equal-density base case is unverified, and several costs are estimates or assumptions as itemized in `assumptions.json`. Simulation shares must not be interpreted as empirical probabilities of project loss. The model reports FNPV only; it does not estimate ENPV or a social benefit–cost ratio because counterfactual dump-management costs and environmental externalities have not been measured. The S2 route is discussed qualitatively and is not costed in this model.
