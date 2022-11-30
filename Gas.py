import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
import time
import gspread
import matplotlib.pyplot as plt

sa = gspread.service_account("service_account.json")
sh = sa.open("verbraeuche_wg")
gas = sh.worksheet("Gas")
gas = pd.DataFrame(gas.get_all_records())

st.set_page_config(
    page_title="Gas",
    page_icon="",
    menu_items={}
)


avg_gas = []

for i in range(len(gas["Gas"])):
	current_avg = (gas["Gas"][:i].sum()/i)
	avg_gas.append(current_avg)

gas["Average"] = avg_gas

gas["Datum"] = pd.to_datetime(gas["Datum"], format = "%d.%m.%Y", errors = "coerce")
gas_months = gas.groupby(gas.Datum.dt.month)["Gas"].sum()

st.write(gas_months)

start_date = datetime.datetime.now() - datetime.timedelta(30)

st.title("Gasverbrauch")
fig, ax = plt.subplots()
ax.plot(gas["Datum"], gas["Gas"])
ax.plot(gas["Datum"], gas["Average"], c = "r")
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.tick_params(right = False ,
                labelbottom = False, bottom = False)
st.pyplot(fig)
