# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 16:54:16 2026

@author: Makarand Kulkarni
"""

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