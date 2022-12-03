import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import time
import gspread
import matplotlib.pyplot as plt

###

st.set_page_config(
    page_title="Energieverbrauch",
    page_icon="",
    menu_items={}
)

energie_str = "Gas"

energieversorger = st.radio(
    "Energieversorger auswählen:",
    ('Gas', 'Strom'))

if energieversorger == 'Gas':
    energie_str = energieversorger
elif energieversorger == "Strom":
	energie_str = energieversorger
else:
    energie_str = energieversorger

st.title(f"{energie_str}verbrauch")

sa = gspread.service_account("service_account.json")
sh = sa.open("verbraeuche_wg")
energie = sh.worksheet(energie_str)
energie = pd.DataFrame(energie.get_all_records())


rgb_background = "#0f1116"

avg_energie = []

for i in range(len(energie[energie_str])):
	current_avg = (energie[energie_str][:i].sum()/i)
	avg_energie.append(current_avg)

energie["Average"] = avg_energie

energie["Datum"] = pd.to_datetime(energie["Datum"], format = "%d.%m.%Y", errors = "coerce")
energie_months = energie.groupby(energie.Datum.dt.month)[energie_str].sum()
energie_months = pd.DataFrame(energie_months)


jetzt = energie["Datum"][len(energie["Datum"])-1]
one_month_ago = jetzt - timedelta(days = 30)

energie_last_month = energie[energie["Datum"] > one_month_ago]

index_list = energie_last_month.index

verbrauch_last_month = energie[energie_str][index_list[-1]] - energie[energie_str][index_list[0]]

costs_last_month =  round(((20.16333333 + verbrauch_last_month *0.1596 * 10) / 100),2)

costs_last_month_pp = round(costs_last_month / 3,2)

month_lst= pd.date_range('2022-04-01', periods = len(energie_months) , freq='1M')-pd.offsets.MonthBegin(1)

month_lst = [date_obj.strftime('%m.%y') for date_obj in month_lst]

energie_months["Month"] = month_lst


st.subheader(f"In den letzten 30 Tagen haben wir für {costs_last_month}€ {energie_str} verbraucht.")
st.write(f"Das sind {costs_last_month_pp}€ pro Person.")
st.write("")

fig, ax = plt.subplots()
ax.plot(energie["Datum"], energie[energie_str])
ax.plot(energie["Datum"], energie["Average"], c = "r")


ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')
ax.tick_params(axis = "both", colors = "white")
ax.set_xticklabels(labels = energie_months["Month"], rotation=90)
fig.patch.set_facecolor(rgb_background)
ax.set_facecolor(rgb_background)

st.pyplot(fig)

st.write("")
st.markdown("---")
st.write("")
st.write(f"{energie_str}verbräuche pro Monat:")

st.bar_chart(energie_months[energie_str])


st.write("Zählerstände der letzten 30 Tage:")
st.write(energie_last_month[["Datum", energie_str]])

st.write("Hallo Tim :D")
