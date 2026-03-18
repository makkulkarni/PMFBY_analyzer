# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 14:28:50 2026

@author: Makarand Kulkarni
"""
import pandas as pd

def state_summary(df):

    summary = (
        df.groupby("State/UT")
        .agg({
            "Total Premium":"sum",
            "Claims":"sum",
            "SI":"sum"
        })
    )

    summary["BR"] = summary["Claims"] / summary["Total Premium"]
    summary["Rate"] = summary["Total Premium"] / summary["SI"]

    return summary

def state_timeseries(df, states):
    """
    Returns yearly metrics for selected states
    """

    filtered = df[df["State/UT"].isin(states)]

    ts = (
        filtered
        .groupby(["State/UT", "Year"])
        .agg({
            "Total_Premium": "sum",
            "Claims": "sum",
            "Sum Insured (In Lac.)": "sum"
        })
        .reset_index()
    )

    ts["BR"] = ts["Claims"] / ts["Total_Premium"]

    ts["Rate"] = (
        ts["Total_Premium"] /
        ts["Sum Insured (In Lac.)"]
    )

    return ts

def get_timeseries(df, selections=None, groups=None):
    """
    Returns yearly metrics for selected groups (e.g., states).
    Handles string or list inputs for groups and selections.
    """

    # --- Normalize inputs ---
    if isinstance(groups, str):
        groups = [groups]
    elif groups is None:
        groups = []

    if isinstance(selections, str):
        selections = [selections]

    # --- Filtering ---
    if groups and selections:
        # Apply filtering across all group columns
        mask = True
        for col in groups:
            mask = mask & df[col].isin(selections)
        filtered = df[mask]
    else:
        filtered = df.copy()

    # --- Grouping ---
    group_cols = groups + ["Year"] if groups else ["Year"]

    ts = (
        filtered
        .groupby(group_cols)
        .agg({
            "Total_Premium": "sum",
            "Claims": "sum",
            "Sum Insured (In Lac.)": "sum"
        })
        .reset_index()
    )

    # --- Metrics ---
    ts["BR"] = ts["Claims"] / ts["Total_Premium"]

    ts["Rate"] = (
        ts["Total_Premium"] /
        ts["Sum Insured (In Lac.)"]
    )

    return ts

def yearly_state_trend(df, states):

    comp = df[df["State/UT"].isin(states)]

    yearly = (
        comp.groupby(["Year","State/UT"])
        .agg({
            "Total Premium":"sum",
            "Claims":"sum"
        })
        .reset_index()
    )

    yearly["BR"] = yearly["Claims"] / yearly["Total Premium"]

    return yearly


def compute_metrics(df):
    df = df.copy()

    # Convert numeric columns
    cols = [
        "Amount In Lac._Farmers Premium",
        "Amount In Lac._State Premium",
        "Amount In Lac._GOI Premium",
        "Sum Insured (In Lac.)",
        "Claim Paid (In Lac.)_Total Claim Paid"
    ]

    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Premium totals
    df["Farmer_Premium"] = df["Amount In Lac._Farmers Premium"]
    df["State_Premium"] = df["Amount In Lac._State Premium"]
    df["Central_Premium"] = df["Amount In Lac._GOI Premium"]

    df["Total_Premium"] = (
        df["Farmer_Premium"]
        + df["State_Premium"]
        + df["Central_Premium"]
    )

    # Claims
    df["Claims"] = df["Claim Paid (In Lac.)_Total Claim Paid"]

    # Burn rate
    df["Burn_Rate"] = df["Claims"] / df["Total_Premium"]

    # Premium rate
    df["Premium_Rate"] = df["Total_Premium"] / df["Sum Insured (In Lac.)"]

    return df




