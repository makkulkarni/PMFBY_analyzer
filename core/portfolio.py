# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 14:29:46 2026

@author: Makarand Kulkarni
"""

def district_cluster(df, districts):

    cluster = df[df["District Name"].isin(districts)]

    premium = cluster["Total Premium"].sum()
    claims = cluster["Claims"].sum()
    si = cluster["SI"].sum()

    br = claims / premium
    rate = premium / si

    yearly = (
        cluster.groupby("Year")
        .agg({
            "Total_Premium":"sum",
            "Claims":"sum",
            "SI": "sum"
        })
        .reset_index()
    )

    yearly["BR"] = yearly["Claims"] / yearly["Total_Premium"]
    yearly["RATE"] = yearly["Total_Premium"] / yearly["SI"]

    result = {
        "premium": premium,
        "claims": claims,
        "si": si,
        "br": br,
        "rate": rate,
        "yearly": yearly
    }

    return result