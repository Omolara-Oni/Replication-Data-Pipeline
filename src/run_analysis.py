

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Replication of Fair (1996) Presidential Vote Model
Extended through 2024
Prepared by: Omolara Oni
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import contextlib

log_file = open("fair1_model_output.log", "w")
redirect = contextlib.redirect_stdout(log_file)
redirect.__enter__()




elections_df = pd.read_csv("FAIR election data.csv")
elections_df = elections_df.loc[:, ~elections_df.columns.str.contains("Unnamed")]

print("Loaded original election data:")
print(elections_df.head())

#LOAD FRED DATA (GDP, POPULATION, DEFLATOR)

gdp = pd.read_csv("GDPC1.csv")
pop = pd.read_csv("B230RC0Q173SBEA.csv")
deflator = pd.read_csv("GDPDEF.csv")

gdp.rename(columns={'observation_date':'date','GDPC1':'real_gdp'}, inplace=True)
pop.rename(columns={'observation_date':'date','B230RC0Q173SBEA':'population'}, inplace=True)
deflator.rename(columns={'observation_date':'date','GDPDEF':'deflator'}, inplace=True)

macro = gdp.merge(pop, on="date").merge(deflator, on="date")
macro["date"] = pd.to_datetime(macro["date"])
macro = macro.sort_values("date").reset_index(drop=True)

macro["year"] = macro["date"].dt.year
macro["quarter"] = macro["date"].dt.quarter

#  REAL PER-CAPITA GDP AND FAIR QUARTERLY GROWTH q

macro["real_pc_gdp"] = macro["real_gdp"] / macro["population"]

macro["q"] = ((macro["real_pc_gdp"] / macro["real_pc_gdp"].shift(1))**4 - 1) * 100

# FUNCTIONS FOR FAIR VARIABLES (g3, p15, n)

def calc_g3(year):
    q3 = macro[(macro["year"]==year) & (macro["quarter"]==3)].index[0]
    Y_end = macro.loc[q3, "real_pc_gdp"]
    Y_start = macro.loc[q3-3, "real_pc_gdp"]
    return ((Y_end / Y_start)**(4/3) - 1) * 100

def calc_p15(year):
    q3 = macro[(macro["year"]==year) & (macro["quarter"]==3)].index[0]
    P_end = macro.loc[q3, "deflator"]
    P_start = macro.loc[q3-15, "deflator"]
    return abs(((P_end / P_start)**(4/15) - 1) * 100)

def calc_n(year):
    start_year = year - 4
    q1 = macro[(macro["year"]==start_year) & (macro["quarter"]==1)].index[0]
    return (macro.loc[q1:q1+14, "q"] > 2.9).sum()

#  EXTENSION YEARS (1996–2024)

extension_years = [1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024]

rows = []
for yr in extension_years:
    rows.append({
        "year": yr,
