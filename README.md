# Assessment of Opportunities and Challenges Associated with Coal-Mine Waste Rock in Quang Ninh

This repository hosts the calculation workbooks, cost-estimation data, and stochastic simulation source code for the manuscript:

> **Nguyen Phi Hung¹, Nguyen Cam Ngoc²*, Pham Kien Trung²**  
> ¹ *Hanoi University of Mining and Geology, Hanoi, Vietnam*  
> ² *Vietnam Department of Geology and Minerals, Central Branch, Da Nang, Vietnam*  
> \*Corresponding Author: Nguyen Cam Ngoc (`camngoc.ng99@gmail.com`)

---

## 📌 Overview

Coal-mine waste rock in the Quang Ninh basin presents both a substantial storage and environmental liability and an alternative source of construction material. This research establishes:
1. **A Quantitative Techno-Economic Assessment (TEA)** for external unbound fill supply (**Route S1**) delivered via 27-tonne dump trucks.
2. **A Financial Break-Even Analysis** identifying the critical haulage distance threshold ($d_F^*$) and cost tolerance margin.
3. **A 100,000-Iteration Monte Carlo Simulation** (NumPy PCG64, seed `20261003`) evaluating joint parametric uncertainty across multiple haulage distances (3.0 km, 5.0 km, and 7.5 km).
4. **A Qualitative Operational Appraisal** for in-mine hydraulic backfilling (**Route S2**) utilizing published local experimental evidence.

---

## 📂 Repository Structure

```text
├── README.md                          # Repository documentation and reproduction guide
├── LICENSE                            # MIT Open-Source License
├── requirements.txt                   # Required Python libraries
├── data/
│   ├── model_parameters.csv           # Baseline cost norms and simulation parameter ranges (Tables 2 & 3)
│   └── simulation_summary_results.csv # Summary statistics, percentiles, and thresholds (Tables 4, 5 & 6)
├── scripts/
│   ├── s1_deterministic_model.py      # Deterministic DCF model, break-even distance, and headroom solver
│   └── s1_monte_carlo_simulation.py   # Stochastic simulation (100k draws, copula dependencies, CDF export)
├── figures/
│   ├── Figure_1_analytical_framework.svg  # High-resolution vector diagram of the analytical framework
│   └── Figure_2_cdf_FNPV_simulation.svg   # Cumulative distribution functions of simulated FNPV
└── workbook/
    └── S1_cashflow_model.xlsx         # 10-year discounted cash flow workbook and sensitivity tables
