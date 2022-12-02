import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import time
import gspread
import matplotlib.pyplot as plt

sa = gspread.service_account("service_account.json")
sh = sa.open("verbraeuche_wg")
strom = sh.worksheet("Strom")
strom = pd.DataFrame(strom.get_all_records())

st.set_page_config(
    page_title="Strom",
    page_icon="",
    menu_items={}
)

rgb_background = "#0f1116"


avg_strom = []

for i in range(len(strom["Strom"])):
	current_avg = (strom["Strom"][:i].sum()/i)
	avg_strom.append(current_avg)

strom["Average"] = avg_strom

strom["Datum"] = pd.to_datetime(strom["Datum"], format = "%d.%m.%Y", errors = "coerce")
strom_months = strom.groupby(strom.Datum.dt.month)["Strom"].sum()
strom_months = pd.DataFrame(strom_months)


jetzt = strom["Datum"][len(strom["Datum"])-1]
one_month_ago = jetzt - timedelta(days = 30)

strom_last_month = strom[strom["Datum"] > one_month_ago]

index_list = strom_last_month.index

verbrauch_last_month = strom["Strom"][index_list[-1]] - strom["Strom"][index_list[0]]

costs_last_month =  round(((20.16333333 + verbrauch_last_month *0.1596 * 10) / 100),2)

costs_last_month_pp = round(costs_last_month / 3,2)

month_lst= pd.date_range('2022-04-01', periods = len(strom_months) , freq='1M')-pd.offsets.MonthBegin(1)

month_lst = [date_obj.strftime('%m.%y') for date_obj in month_lst]

strom_months["Month"] = month_lst

###

st.title("Stromverbrauch")

st.subheader(f"In den letzten 30 Tagen haben wir für {costs_last_month}€ Strom verbraucht.")
st.write(f"Das sind {costs_last_month_pp}€ pro Person.")
st.write("")
st.write("Zählerstände der letzten 30 Tage:")
st.write(strom_last_month[["Datum", "Strom"]])

fig, ax = plt.subplots()
ax.plot(strom["Datum"], strom["Strom"])
ax.plot(strom["Datum"], strom["Average"], c = "r")


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
st.write("Stromverbräuche pro Monat:")

st.bar_chart(strom_months["Strom"])

st.write("Hallo Tim :D")
