# Climate, Wealth & Health: A Cross-National Analysis

A data science project investigating whether a country's CO2 emissions are associated with its public health outcomes, and, critically, whether that relationship survives once population size and national wealth are properly accounted for.

## Key finding

The health outcome with the least obvious physical connection to CO2 emissions, malaria, showed the strongest, most consistent relationship in the entire analysis, surviving every statistical test we applied. The outcome with the most obvious physical connection, air pollution, since burning fossil fuels produces both CO2 and particulate matter, showed the weakest and least consistent relationship, even reversing direction depending on income group. This suggests the climate-health relationship runs primarily through broader development pathways (infrastructure, healthcare access, vector control) rather than direct physical exposure.

## Project structure

```
├── data/
│   ├── raw/            # Original downloaded CSVs (WHO, World Bank, PM2.5, country metadata)
│   └── processed/      # Merged/cleaned datasets and verified statistical result exports
├── notebook/
│   └── final_loaded_datasets.ipynb  # Full analysis: data merging, cleaning, statistics, visualization
├── figures/            # Final chart images used in the write-up and presentation
├── src/                # Reusable analysis/visualization scripts
└── README.md
```

## Data sources

| Source | Variables | Coverage |
|---|---|---|
| WHO Global Health Observatory API | Malaria cases, cholera cases, life expectancy at birth | Varies by indicator (see Data Notes) |
| World Bank | CO2 emissions, population, GDP per capita, PM2.5 exposure | 1990–2023 (varies by indicator) |
| World Bank metadata | Region, income group classification | Static, per-country |

Indicator codes were resolved by querying WHO's own indicator registry by name rather than hardcoding remembered codes, since several codes have changed or been deprecated over time.

## Methodology

1. **Merge** — health, climate, and economic data joined on country code and year
2. **Normalize** — case counts converted to per-100,000 population rates; CO2 converted to per-capita, to remove the confound of country size
3. **Stratify** — every relationship tested separately within each World Bank income group, to check whether a pattern holds across similarly-wealthy countries or is only an artifact of comparing rich to poor
4. **Test over time** — a within-country panel regression compares each country only to its own past, removing cross-country wealth differences entirely
5. **Control for wealth directly** — GDP-controlled OLS regression, with Variance Inflation Factor diagnostics to check whether CO2 and GDP are too collinear to separate reliably

Because almost no country-year had all four health outcomes present simultaneously, each outcome (malaria, cholera, air pollution, life expectancy) was analyzed as an independent subset rather than one combined table.

## Results summary

| Outcome | Pooled correlation | Holds across income tiers? | Within-country panel | Reliability |
|---|---|---|---|---|
| Malaria | −0.74 | Yes, in every tier | −0.46, p<0.001 | **Strong, consistent** |
| Life expectancy | +0.74 | Weakens substantially at higher income | +0.18, p<0.001 (small effect) | **Real but modest — mostly wealth-mediated** |
| Air pollution (PM2.5) | −0.24 | No — sign flips by income group | +0.02, not significant | **Weak, inconsistent** |
| Cholera | −0.70 | No — mostly non-significant when split | Not testable (insufficient years) | **Unreliable — treated as illustrative only** |

All figures reflect the final, corrected dataset described in Data Notes below.

## Data notes and corrections

This project went through several rounds of data-quality correction; documenting them here rather than hiding them, since they materially shaped the final methodology:

- **Cholera indicator**: The original WHO code (`WHS3_40`) was a discontinued legacy series ending in 2016 with sparse coverage. Replaced with the actively maintained `CHOLERA_0000000001`.
- **Air pollution indicator**: The original WHO indicator (`AIR_41`, air pollution attributable deaths) turned out to only have a single year of data (2021) per country — a modeled estimate, not an annual series. Replaced with World Bank PM2.5 exposure data (1990–2023), which supports genuine time-series analysis.
- **Population data bug**: A file-loading error caused the population column to be populated from the CO2 emissions file instead, silently corrupting all per-capita calculations until caught via a routine sanity check on value ranges.
- **Excluded countries**: Eight countries/territories (Nauru, four U.S. territories, Tuvalu, Marshall Islands, Micronesia) reported implausible or literally-zero CO2 per capita, likely due to how small economies' emissions are attributed in international reporting. These were excluded, and all statistical tests were re-run to confirm the exclusion didn't materially change core findings.
- **Non-country codes**: World Bank data includes regional and income-group aggregates (e.g., "World," "Arab World") that were filtered out using an authoritative ISO3 country list.

## Limitations

- All relationships are **correlational**, not causal.
- All data is **country-level (ecological)**, not individual-level — associations at the national scale do not necessarily hold for any specific individual within that country (the ecological fallacy).
- The cholera analysis is based on a narrow 2011–2016 window dominated by a single event (Haiti's post-earthquake epidemic) and shows severe multicollinearity between CO2 and GDP (VIF = 7.6) — treated as a supporting illustration, not a robust finding.
- Malaria case counts represent *episodes*, not unique individuals; in high-transmission regions, the same person can be reinfected multiple times per year.

## How to run

1. Open `notebook/final_loaded_datasets.ipynb` in Jupyter or Google Colab
2. Ensure raw data files from `data/raw/` are available in the working directory
3. Install dependencies: `pip install -r requirements.txt`
4. Run all cells in order — later cells depend on variables and merged datasets built earlier in the notebook

## Requirements

See `requirements.txt`. Core dependencies: `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`, `pycountry`, `requests`.

## Contributors

*Saniya Shaikh*
*Riddhi Bagkar*
*Adrita Dasgupta*
