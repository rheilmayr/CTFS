# -*- coding: utf-8 -*-
"""
Script to explore historical deforestation rates in light of CTFS. Prepared
by Robert Heilmayr for emLab blog post. v1
"""
import pandas as pd
import numpy as np
import glob
import os

# =============================================================================
# Identify local path for data directory
# =============================================================================
wdir = os.path.join(os.path.dirname(__file__), 'data/')
files = glob.glob(wdir+'*.xlsx')

# =============================================================================
# Load and aggregate Hansen deforestation data
# Data from: Global Forest Watch
# =============================================================================
data_dict = {}
for file in files:
    country = file[file.rfind('.xlsx')-3:file.rfind('.xlsx')]
    nat_df = pd.read_excel(file, sheet_name = 'Loss (2001-2017) by Subnat1')
    i = [i for i, col in enumerate(nat_df.columns) if \
         col=='TREE COVER LOSS (>30% CANOPY COVER)'][0]
    index = nat_df.iloc[slice(None), 0].iloc[1:]
    nat_df = nat_df.iloc[slice(None), i:i+17]
    nat_df.columns = nat_df.iloc[0].astype(int)
    nat_df = nat_df.drop(0)
    nat_df = nat_df.set_index(index)
    data_dict[country] = nat_df

df = pd.concat(data_dict)

# =============================================================================
# Calculate reference emissions level and crediting baseline
# =============================================================================
# Calculate baseline using 2001-2010 deforestation rates
df['reference'] = df[list(range(2001,2011))].mean(axis = 1) 

# Baseline assuming 10% below in year 1 (~2020), dropping linearly 
# to 0 in year 30 (~2050)
bl_reduction = [0.9, 0.87, 0.84, 0.81, 0.78, 0.75, 0.72]
df['baseline'] = df['reference'] * np.sum(bl_reduction)

# =============================================================================
# Contrast baseline to actual performance
# =============================================================================
df['performance'] = df[list(range(2011,2018))].sum(axis = 1)
df['credits'] = df['baseline'] - df['performance']
credit_df = df.loc[df['credits']>0]
#credit_df = credit_df.loc[['PER', 'COL', 'IDN', 'NGA', 'MEX', 'ECU', 'CIV']]

# Subset to states with non-additional credits
area_credited = credit_df['credits'].sum() # ha
c_credited = area_credited * 150 /1000000 # MMtCe assuming 250 t C / ha - http://www.ipcc.ch/ipccreports/sres/land_use/index.php?idp=151
co2_credited = c_credited * 44/12 # MMtCO2e
credit_value = co2_credited * 14.61 / 1000 # Billion USD

# Calculate share of offsets that might be captured by non-additional credits
cap = [321, 308, 294, 281, 267, 254, 240] # 2021-2027 cap, https://static1.squarespace.com/static/549885d4e4b0ba0bff5dc695/t/5952c7436b4998a9abdce3dc/1498597187813/Hot+air+and+offsets.pdf
offsets = (np.sum(cap)*0.08)*(1-0.08)
redd_share = co2_credited / offsets

# =============================================================================
# Print results
# =============================================================================
print("Total non-additional credits (MMtCO2e): " + str(round(co2_credited, 2)))
print("Total value of credits (USD): " + str(round(credit_value, 2)))
print("Annual non-additional allowances as share of offset cap: " + \
      str(round(redd_share, 2)))