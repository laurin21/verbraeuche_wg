import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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

rgb_background = "#0f1116"


avg_gas = []

for i in range(len(gas["Gas"])):
	current_avg = (gas["Gas"][:i].sum()/i)
	avg_gas.append(current_avg)

gas["Average"] = avg_gas

gas["Datum"] = pd.to_datetime(gas["Datum"], format = "%d.%m.%Y", errors = "coerce")
gas_months = gas.groupby(gas.Datum.dt.month)["Gas"].sum()
gas_months = pd.DataFrame(gas_months)


jetzt = gas["Datum"][len(gas["Datum"])-1]
one_month_ago = jetzt - timedelta(days = 30)

gas_last_month = gas[gas["Datum"] > one_month_ago]

index_list = gas_last_month.index

verbrauch_last_month = gas["Gas"][index_list[-1]] - gas["Gas"][index_list[0]]

costs_last_month =  round(((20.16333333 + verbrauch_last_month *0.1596 * 10) / 100),2)

costs_last_month_pp = round(costs_last_month / 3,2)

month_lst= pd.date_range('2022-04-01', periods = len(gas_months) , freq='1M')-pd.offsets.MonthBegin(1)

month_lst = [date_obj.strftime('%m.%y') for date_obj in month_lst]

gas_months["Month"] = month_lst

###

st.title("Gasverbrauch")

st.subheader(f"In den letzten 30 Tagen haben wir für {costs_last_month}€ Gas verbraucht.")
st.write(f"Das sind {costs_last_month_pp}€ pro Person.")
st.write("")

fig, ax = plt.subplots()
ax.plot(gas["Datum"], gas["Gas"])
ax.plot(gas["Datum"], gas["Average"], c = "r")


ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')
ax.tick_params(axis = "both", colors = "white")
ax.set_xticklabels(labels = gas_months["Month"], rotation=90)
fig.patch.set_facecolor(rgb_background)
ax.set_facecolor(rgb_background)

st.pyplot(fig)

st.write("")
st.markdown("---")
st.write("")
st.write("Gasverbräuche pro Monat:")

st.bar_chart(gas_months["Gas"])


st.write("Zählerstände der letzten 30 Tage:")
st.write(gas_last_month[["Datum", "Gas"]])

st.write("Hallo Tim :D")
