"""
Graphical outputs for statistical analysis of merged_inner / subsets.
Run these cells after your data-loading notebook (assumes merged_inner,
subsets, malaria_df, life_df, cholera_df, air_df, outcomes already exist
in the namespace).
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["figure.dpi"] = 110

OUTCOME_COLS = {
    "malaria": "malaria_per_100k",
    "cholera": "cholera_per_100k",
    "air_pollution": "pm25_exposure",   # subsets["air_pollution"] = air_df, uses pm25_exposure
    "life_expectancy": "life_expectancy",
}
DRIVER_COLS = ["co2_per_capita", "gdp_per_capita"]


# ---------------------------------------------------------------------
# 1. Correlation heatmap
# ---------------------------------------------------------------------
def plot_correlation_heatmap(df, cols=None, title="Correlation matrix"):
    if cols is None:
        cols = [
            "malaria_per_100k", "cholera_per_100k",
            "air_pollution_deaths_per_100k", "life_expectancy",
            "co2_per_capita", "gdp_per_capita", "population",
        ]
    cols = [c for c in cols if c in df.columns]
    corr = df[cols].corr(numeric_only=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
        vmin=-1, vmax=1, square=True, linewidths=0.5, ax=ax,
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title(title)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------
# 2. Scatter + regression: driver (CO2 / GDP) vs each health outcome
# ---------------------------------------------------------------------
def plot_driver_vs_outcome(df, driver, outcome, log_x=False, log_y=False,
                            hue=None, title=None):
    fig, ax = plt.subplots(figsize=(7, 5))
    plot_df = df.dropna(subset=[driver, outcome]).copy()

    if log_x:
        plot_df = plot_df[plot_df[driver] > 0]
    if log_y:
        plot_df = plot_df[plot_df[outcome] > 0]

    sns.regplot(
        data=plot_df, x=driver, y=outcome, ax=ax,
        scatter_kws={"alpha": 0.4, "s": 25, "edgecolor": "none"},
        line_kws={"color": "crimson"},
    )
    if hue:
        sns.scatterplot(
            data=plot_df, x=driver, y=outcome, hue=hue, ax=ax,
            alpha=0.6, s=25, legend="brief",
        )

    if log_x:
        ax.set_xscale("log")
    if log_y:
        ax.set_yscale("log")

    r = plot_df[driver].corr(plot_df[outcome])
    ax.set_title(title or f"{outcome} vs {driver}  (r = {r:.2f})")
    fig.tight_layout()
    return fig


def plot_all_driver_outcome_pairs(subsets, outcome_cols=OUTCOME_COLS,
                                   drivers=DRIVER_COLS):
    figs = {}
    for name, col in outcome_cols.items():
        df = subsets.get(name)
        if df is None or df.empty:
            continue
        for driver in drivers:
            if driver not in df.columns:
                continue
            log_y = name not in ("life_expectancy", "air_pollution")
            fig = plot_driver_vs_outcome(
                df, driver, col, log_x=True, log_y=log_y,
                title=f"{name}: {col} vs {driver}",
            )
            figs[f"{name}_{driver}"] = fig
    return figs


# ---------------------------------------------------------------------
# 3. Distribution by group (income group / region) - box + violin
# ---------------------------------------------------------------------
def plot_outcome_by_group(df, outcome, group_col="IncomeGroup",
                           kind="box", log_y=False, order=None):
    fig, ax = plt.subplots(figsize=(8, 5))
    plot_df = df.dropna(subset=[outcome, group_col])

    if kind == "box":
        sns.boxplot(data=plot_df, x=group_col, y=outcome, ax=ax, order=order)
    else:
        sns.violinplot(data=plot_df, x=group_col, y=outcome, ax=ax,
                        order=order, cut=0)

    if log_y:
        ax.set_yscale("log")
    ax.set_title(f"{outcome} by {group_col}")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return fig


def plot_all_outcomes_by_group(subsets, outcome_cols=OUTCOME_COLS,
                                group_col="IncomeGroup"):
    figs = {}
    for name, col in outcome_cols.items():
        df = subsets.get(name)
        if df is None or df.empty or group_col not in df.columns:
            continue
        log_y = name not in ("life_expectancy", "air_pollution")
        figs[name] = plot_outcome_by_group(df, col, group_col, log_y=log_y)
    return figs


# ---------------------------------------------------------------------
# 4. Trends over time
# ---------------------------------------------------------------------
def plot_trend_over_time(df, outcome, group_col=None, agg="mean"):
    fig, ax = plt.subplots(figsize=(9, 5))
    plot_df = df.dropna(subset=[outcome, "year"])

    if group_col and group_col in plot_df.columns:
        trend = (
            plot_df.groupby(["year", group_col])[outcome]
            .agg(agg).reset_index()
        )
        sns.lineplot(data=trend, x="year", y=outcome, hue=group_col,
                     marker="o", ax=ax)
    else:
        trend = plot_df.groupby("year")[outcome].agg(agg).reset_index()
        sns.lineplot(data=trend, x="year", y=outcome, marker="o", ax=ax)

    ax.set_title(f"{agg.capitalize()} {outcome} over time"
                 + (f" by {group_col}" if group_col else ""))
    fig.tight_layout()
    return fig


def plot_all_trends(subsets, outcome_cols=OUTCOME_COLS, group_col="Region"):
    figs = {}
    for name, col in outcome_cols.items():
        df = subsets.get(name)
        if df is None or df.empty:
            continue
        figs[name] = plot_trend_over_time(df, col, group_col=group_col)
    return figs


# ---------------------------------------------------------------------
# 5. PM2.5 exposure vs CO2 (alternative air-pollution measure)
# ---------------------------------------------------------------------
def plot_pm25_vs_co2(air_df, driver="co2_per_capita",
                      outcome="pm25_exposure", hue="IncomeGroup"):
    return plot_driver_vs_outcome(
        air_df, driver, outcome, log_x=True, log_y=False, hue=hue,
        title=f"{outcome} vs {driver}",
    )


# ---------------------------------------------------------------------
# 6. Pairplot for a quick multi-variable overview
# ---------------------------------------------------------------------
def plot_pairplot(df, cols, hue=None, title=None):
    g = sns.pairplot(
        df.dropna(subset=cols), vars=cols, hue=hue,
        plot_kws={"alpha": 0.4, "s": 20},
        diag_kind="kde",
    )
    if title:
        g.fig.suptitle(title, y=1.02)
    return g


# ---------------------------------------------------------------------
# Example usage (uncomment in your notebook after loading data)
# ---------------------------------------------------------------------
# plot_correlation_heatmap(merged_inner)
# plot_all_driver_outcome_pairs(subsets)
# plot_all_outcomes_by_group(subsets, group_col="IncomeGroup")
# plot_all_trends(subsets, group_col="Region")
# plot_pm25_vs_co2(air_df)
# plot_pairplot(
#     merged_inner,
#     cols=["co2_per_capita", "gdp_per_capita", "life_expectancy", "malaria_per_100k"],
#     hue="IncomeGroup",
# )
# plt.show()