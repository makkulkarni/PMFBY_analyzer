# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 14:27:27 2026

@author: Makarand Kulkarni
"""

import pandas as pd

season_map = {1: "Kharif", 2: "Rabi"}
scheme_map = {4: "PMFBY", 2: "WBCIS"}
def dfmap(df):
    df["Season"] = df["Season"].map(season_map)
    df["Scheme"] = df["Scheme"].map(scheme_map)
    return df


def load_data(state_file, district_file):

    state_df = pd.read_csv(state_file,thousands=",")
    district_df = pd.read_csv(district_file,thousands=",")
    
    state_df=dfmap(state_df)
    district_df=dfmap(district_df)    

    numeric_cols = [
        "Amount In Lac._Farmers Premium",
        "Amount In Lac._State Premium",
        "Amount In Lac._GOI Premium",
        "Claim Paid (In Lac.)_Total Claim Paid",
        "Sum Insured (In Lac.)"
    ]

    for df in [state_df, district_df]:

        for c in numeric_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df["Total Premium"] = (
            df["Amount In Lac._Farmers Premium"]
            + df["Amount In Lac._State Premium"]
            + df["Amount In Lac._GOI Premium"]
        )

        df["Claims"] = df["Claim Paid (In Lac.)_Total Claim Paid"]

        df["SI"] = df["Sum Insured (In Lac.)"]

        df["Rate"] = df["Total Premium"] / df["SI"]

        df["BR"] = df["Claims"] / df["Total Premium"]

    return state_df, district_df