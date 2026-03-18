# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 15:54:02 2026

@author: Makarand Kulkarni
"""

import streamlit as st
import plotly.express as px
import os
from core.data_loader import load_data
from core.metrics import compute_metrics,get_timeseries
from core.metrics import state_summary
from core.portfolio import district_cluster

def get_chart(df,xaxis,yaxis,colort="variable",title="",plot_type="line"):
    colors = ["#2ca02c", "#d62728"]  # customize here
    
    match plot_type:
        case "line":
            fig = px.line(
                df,
                x=xaxis,
                y=yaxis,
                color=colort,
                markers=True,
                title=title
            )
        case "bar":
            fig = px.bar(
                df,
                x=xaxis,
                y=yaxis,
                #color="variable",
                color_discrete_sequence=colors,
                title=title,
                barmode="group"
                
            )
        case _:
            # This is the 'default' case if no match is found
            st.error("Unknown plot type!")
    return fig

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(layout="wide")

#st.title("PMFBY Underwriting Analytics Tool")
st.title("Analysis of Insurance data available in PMFBY portal")

# =========================
# LOAD DATA
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
state_file = os.path.join(BASE_DIR, "data", "states_master.csv")
district_file = os.path.join(BASE_DIR, "data", "districts_master.csv")

state_df, district_df = load_data(state_file, district_file)

state_df = compute_metrics(state_df)
district_df = compute_metrics(district_df)

# =========================
# GLOBAL FILTERS
# =========================

#st.subheader("Filters")

st.sidebar.header("Filters")

years = st.sidebar.multiselect(
    "Year",
    sorted(state_df["Year"].unique()),
    default=sorted(state_df["Year"].unique())
)

season = st.sidebar.selectbox(
    "Season",
    state_df["Season"].unique()
)

scheme = st.sidebar.selectbox(
    "Scheme",
    sorted(state_df["Scheme"].unique())
)

tab1, tab2, tab3 = st.tabs([
    "📊 State Analysis",
    "📍 District Analysis",
    "🧩 Cluster Builder"
])


# Filter dataset
state_filtered = state_df[
    (state_df["Year"].isin(years)) &
    (state_df["Season"] == season) &
    (state_df["Scheme"] == scheme)
]


# =========================
# STATE SUMMARY
# =========================
with tab1:
    st.subheader("State wise score summary")
    
    summary = state_summary(state_filtered)
    
    st.dataframe(summary)
    
    # =========================
    # STATE ANALYSIS
    # =========================
    
    st.subheader("State Analysis")
    
    selected_states = st.sidebar.selectbox(#st.multiselect(
        "Select state",
        summary.index.tolist()
    )
    if not isinstance(selected_states, list):
        selected_states = [selected_states]
    #st.write(selected_states)
    
    if selected_states:
    
        #trend2 = state_timeseries(state_filtered, selected_states)
        trend=get_timeseries(state_filtered, selections=selected_states, groups="State/UT")
        st.write(trend.head(10))
        fig_br_rate=get_chart(trend,xaxis="Year",yaxis=["Rate","BR"],
                              plot_type="bar",title="Yeary BR and avg premium Rates")
        
        
        fig_premium=get_chart(trend,xaxis="Year",yaxis="Total_Premium",
                         colort="State/UT",title="Total Premium (lac rs)")
        fig_claims=get_chart(trend,xaxis="Year",yaxis=["Total_Premium","Claims"],
                         colort="State/UT",title="Claims (lac rs)",plot_type="bar")
        col_left, col_right = st.columns(2)
        with col_left:
            st.plotly_chart(fig_br_rate, use_container_width=True)
        with col_right:
            st.plotly_chart(fig_claims, use_container_width=True)
       

# =========================
# DISTRICT SUMMARY
# =========================
with tab2:
    district_filtered = district_df[
        (district_df["Year"].isin(years)) &
        (district_df["Season"] == season) &
        (district_df["Scheme"] == scheme) &
        (district_df["State/UT"]==selected_states[0])
    ]
    
    
    st.subheader("District wise summary")
    
    district_summary = (
        district_filtered
        .groupby(["State/UT", "District Name"])
        .agg({
            "Total_Premium":"sum",
            "Claims":"sum"
        })
    )
    
    district_summary["BR"] = (
        district_summary["Claims"] /
        district_summary["Total_Premium"]
    )
    
    st.dataframe(district_summary)

# =========================
# DISTRICT CLUSTER BUILDER
# =========================
district_list = district_filtered["District Name"].unique()

selected_districts = st.sidebar.multiselect(
    "Select districts to form cluster",
    district_list
)

with tab3:
    st.subheader("District Cluster Builder")
    
    if selected_districts:
    
        cluster = district_cluster(
            district_filtered,
            selected_districts
        )
        cluster_dt=district_filtered[district_filtered["District Name"].isin(selected_districts)]
        
        #st.write("cluster_dt")
        #st.write(cluster_dt.head(10))
        cluster_sumary=compute_metrics(cluster_dt)
        #st.write(cluster_sumary.head(10))
        st.subheader("Cluster Summary")

        col1, col2, col3, col4 = st.columns(4)
    
        col1.metric("Premium", round(cluster["premium"],2))
        col2.metric("Claims", round(cluster["claims"],2))
        col3.metric("Burn Rate", round(cluster["br"],3))
        col4.metric("Avg Rate", round(cluster["rate"],4))
        
        clust_trend=cluster["yearly"]
            
        
        fig_premium_clust=get_chart(clust_trend,xaxis="Year",
                                    yaxis=["Total_Premium","Claims"],
                         title="Premium and claims (lac rs)",plot_type="bar")
        fig_BR_clust=get_chart(clust_trend,xaxis="Year",
                                    yaxis=["RATE","BR"],
                         title="Premium rate and Burn rate (lac rs)",plot_type="bar")
        col_left, col_right = st.columns(2)
        with col_left:
            st.plotly_chart(fig_premium_clust, use_container_width=True)
        with col_right:
            st.plotly_chart(fig_BR_clust, use_container_width=True)
        st.subheader("Cluster_info")            
        st.write(clust_trend)

