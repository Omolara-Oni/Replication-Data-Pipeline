

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

# DATA PREPARATION
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
        "g3_new": calc_g3(yr),
        "p15_new": calc_p15(yr),
        "n_new": calc_n(yr),
    })

macro_ext = pd.DataFrame(rows)
print("\nComputed Fair variables for extension:")
print(macro_ext)

#  MERGE EXTENSIONS WITH ORIGINAL DATA

extended_df = elections_df.merge(macro_ext, on="year", how="left")

extended_df["g3"]  = extended_df["g3"].fillna(extended_df["g3_new"])
extended_df["p15"] = extended_df["p15"].fillna(extended_df["p15_new"])
extended_df["n"]   = extended_df["n"].fillna(extended_df["n_new"])

extended_df.drop(columns=["g3_new","p15_new","n_new"], inplace=True)

# Add incumbent values for modern elections
extension_values = {
    1996: {"I": 1, "DPER": 1, "DUR": 1},
    2000: {"I": 1, "DPER": 0, "DUR": 2},
    2004: {"I": -1, "DPER": 1, "DUR": 1},
    2008: {"I": -1, "DPER": 0, "DUR": 2},
    2012: {"I": 1, "DPER": 1, "DUR": 1},
    2016: {"I": 1, "DPER": 0, "DUR": 2},
    2020: {"I": -1, "DPER": 1, "DUR": 1},
    2024: {"I": 1, "DPER": 1, "DUR": 1},
}

for year, vals in extension_values.items():
    extended_df.loc[extended_df["year"] == year, ["I","DPER","DUR"]] = (
        vals["I"], vals["DPER"], vals["DUR"]
    )

# Adjust wartime years
war_years = [1920, 1944, 1948]
extended_df["p15_adj"] = np.where(extended_df["year"].isin(war_years), 0, extended_df["p15"])
extended_df["n_adj"]   = np.where(extended_df["year"].isin(war_years), 0, extended_df["n"])

# RUN FAIR REGRESSIONS FOR TABLE 2 AND TABLE 3

def run_fair_regression(data, mask, label):
    d = data.loc[mask].copy()
    X = d[["I","DPER","g3","p15_adj","n_adj","DUR"]]
    X = sm.add_constant(X)
    y = d["V"]

    model = sm.OLS(y, X).fit()

    print(f"\n======= {label} =======")
    print(model.summary())

    # Create Table 3 predictions
    d["V_hat"] = model.predict(X)
    d["error"] = d["V_hat"] - d["V"]

    print("\nTABLE 3 OUTPUT:")
    print(d[["year","V","V_hat","error"]])

    print("\nRMSE:", np.sqrt((d["error"]**2).mean()))

    return model


mask_1992 = extended_df["year"] <= 1992
mask_1988 = extended_df["year"] <= 1988
mask_1960 = extended_df["year"] <= 1960

model_1992 = run_fair_regression(extended_df, mask_1992, "Regression 1916–1992")
model_1988 = run_fair_regression(extended_df, mask_1988, "Regression 1916–1988")
model_1960 = run_fair_regression(extended_df, mask_1960, "Regression 1916–1960")


# TABLE 4 OUT OF SAMPLE FORECASTS (1996–2024)

forecast = extended_df[extended_df["year"] >= 1996].copy()

X_fore = forecast[["I","DPER","g3","p15_adj","n_adj","DUR"]]
X_fore = sm.add_constant(X_fore)

forecast["V_hat"] = model_1992.predict(X_fore)
forecast["error"] = forecast["V_hat"] - forecast["V"]

print("\n======== TABLE 4 OUT OF SAMPLE FORECASTS (1996–2024) ========")
print(forecast[["year","V","V_hat","error","g3","p15","n","I","DPER","DUR"]])

forecast.to_csv("Fair_Table4_OutOfSample_1996_2024.csv", index=False)



extended_df.to_csv("FAIR_newz_dataset_1916_2024_CORRECT.csv", index=False)

print("\nExport complete. Script finished successfully.")



redirect.__exit__(None, None, None)
log_file.close()


