import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import time
import gspread
import matplotlib.pyplot as plt

#####################
###### CONFIGS ######
#####################

st.set_page_config(
    page_title="Engerieverbauch",
    page_icon="",
    menu_items={}
)

rgb_background = "#0f1116"


###################
###### TITEL ######
###################

st.title(f"Energieverbräuche")


##########################
###### IMPORT DATEN ######
##########################

sa = gspread.service_account("service_account.json")
sh = sa.open("verbraeuche_wg")

gas = sh.worksheet("Gas")
gas = pd.DataFrame(gas.get_all_records())
gas["Datum"] = pd.to_datetime(gas["Datum"], format = "%d.%m.%Y", errors = "coerce")
g_prices = sh.worksheet("Gas Abschlag")
g_prices = pd.DataFrame(g_prices.get_all_records())
g_prices["Datum"] = pd.to_datetime(g_prices["Datum"], format = "%d.%m.%Y", errors = "coerce")
g_months = gas.groupby(gas.Datum.dt.month)["Gas"].sum()
g_months = pd.DataFrame(g_months)
month_lst= pd.date_range('2022-04-01', periods = len(g_months) , freq='1M')-pd.offsets.MonthBegin(1)
month_lst = [date_obj.strftime('%m.%y') for date_obj in month_lst]
g_months["Month"] = month_lst

strom = sh.worksheet("Strom")
strom = pd.DataFrame(strom.get_all_records())
strom["Datum"] = pd.to_datetime(strom["Datum"], format = "%d.%m.%Y", errors = "coerce")
s_prices = sh.worksheet("Strom Abschlag")
s_prices = pd.DataFrame(s_prices.get_all_records())
s_prices["Datum"] = pd.to_datetime(s_prices["Datum"], format = "%d.%m.%Y", errors = "coerce")
s_months = strom.groupby(strom.Datum.dt.month)["Strom"].sum()
s_months = pd.DataFrame(s_months)
month_lst= pd.date_range('2022-04-01', periods = len(s_months) , freq='1M')-pd.offsets.MonthBegin(1)
month_lst = [date_obj.strftime('%m.%y') for date_obj in month_lst]
s_months["Month"] = month_lst



#######################################
###### VERBRAUCH LETZTEN 30 TAGE ######
#######################################

g_jetzt = gas["Datum"][len(gas["Datum"])-1]
g_one_month_ago = g_jetzt - timedelta(days = 30)
g_lm = (gas[gas["Datum"] > g_one_month_ago]).reset_index()
g_first_lm = g_lm["Datum"][0]
g_first_date = gas["Datum"][0]
g_duration = (g_jetzt-g_first_lm).days
g_consumption_lm = g_lm["Gas"][len(g_lm)-1] - g_lm["Gas"][0]
g_consumption_lm = g_consumption_lm / g_duration * 30
g_costs_lm =  round(((20.16333333 + g_consumption_lm *0.1596 * 10) / 100),2)
g_costs_lm_pp = round(g_costs_lm / 3,2)

s_jetzt = strom["Datum"][len(strom["Datum"])-1]
s_one_month_ago = s_jetzt - timedelta(days = 30)
s_lm = (strom[strom["Datum"] > s_one_month_ago]).reset_index()
s_first_lm = s_lm["Datum"][0]
s_first_date = strom["Datum"][0]
s_duration = (s_jetzt-s_first_lm).days
s_consumption_lm = s_lm["Strom"][len(s_lm)-1] - s_lm["Strom"][0]
s_consumption_lm = s_consumption_lm / s_duration * 30
s_costs_lm =  round(((8.85 + s_consumption_lm * 0.3985) / 100),2)
s_costs_lm_pp = round(s_costs_lm / 3,2)

st.markdown("---")
st.subheader(f"Verbräuche letzten 30 Tage.")

st.write(f"Gaskosten letzte 30 Tage: {g_costs_lm}€")
st.write(f"Das sind {g_costs_lm_pp}€ pro Person.")
st.write("")
st.write(f"Stromkosten letzte 30 Tage: {s_costs_lm}€")
st.write(f"Das sind {s_costs_lm_pp}€ pro Person.")
st.write("")
st.markdown("---")
st.write("")


####################################
###### DURCHSCHNITTSVERBRAUCH ######
####################################

st.subheader("Verbrauch und Durchschnitt")

carrier = st.radio(
    "Energieversorger auswählen:",
    ('Gas', 'Strom'), key = "1")

if carrier == "Gas":
	energy = gas
	energy_str = carrier
	energy_months = g_months
elif carrier == "Strom":
	energy = strom
	energy_str = carrier
	energy_months = s_months

avg_energy = []
for i in range(len(energy[energy_str])):
	current_avg = (energy[energy_str][:i].sum()/i)
	avg_energy.append(current_avg)
energy["Average"] = avg_energy

fig, ax = plt.subplots(figsize = (9,9))
ax.plot(energy["Datum"], energy[energy_str])
ax.plot(energy["Datum"], energy["Average"], c = "r")
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')
ax.tick_params(axis = "both", colors = "white")
ax.set_xticklabels(labels = energy_months["Month"], rotation=90)
fig.patch.set_facecolor(rgb_background)
ax.set_facecolor(rgb_background)
st.pyplot(fig)

st.write("")
st.markdown("---")
st.write("")


#####################################
###### KOSTEM SEIT START ######
#####################################

st.subheader(f"Energiekosten seit Einzug")

g_duration_lst = []
for i in range(len(g_prices)-1):
	g_duration = (g_prices["Datum"][i+1] - g_prices["Datum"][i]).days
	g_duration_lst.append(g_duration)
g_last_duration = (gas["Datum"][len(gas["Datum"])-1] - g_prices["Datum"][len(g_prices["Datum"])-1]).days
g_duration_lst.append(g_last_duration)
g_duration_total_d = (g_jetzt-g_first_date).days
g_consumption_total = (gas["Gas"][len(gas)-1] - gas["Gas"][0]) / 100
g_share_lst = []	
for i in range(len(g_prices["Datum"])):
	g_price_share = g_duration_lst[i] / g_duration_total_d
	g_share_lst.append(g_price_share)
g_price_share_lst = []
for i in range(len(g_prices["Datum"])):
	g_price_share = g_share_lst[i] * g_prices["Preis"][i] / 10000
	g_price_share_lst.append(g_price_share)
g_average_price = 0
for i in range(len(g_price_share_lst)):
	g_average_price += g_price_share_lst[i]
g_base_price = 241.96 / 365 * g_duration_total_d
g_average_total = round(((g_base_price + g_consumption_total * g_average_price * 10)),2)
g_duration_total_m = g_duration_total_d / 30
g_average_per_month = round(g_average_total / g_duration_total_m, 2)

s_duration_lst = []
for i in range(len(s_prices)-1):
	s_duration = (s_prices["Datum"][i+1] - s_prices["Datum"][i]).days
	s_duration_lst.append(s_duration)
s_last_duration = (strom["Datum"][len(strom["Datum"])-1] - s_prices["Datum"][len(s_prices["Datum"])-1]).days
s_duration_lst.append(s_last_duration)
s_duration_total_d = (s_jetzt-s_first_date).days
s_consumption_total = (strom["Strom"][len(strom)-1] - strom["Strom"][0]) / 100
s_share_lst = []	
for i in range(len(s_prices["Datum"])):
	s_price_share = s_duration_lst[i] / s_duration_total_d
	s_share_lst.append(s_price_share)
s_price_share_lst = []
for i in range(len(s_prices["Datum"])):
	s_price_share = s_share_lst[i] * s_prices["Preis"][i] / 10000
	s_price_share_lst.append(s_price_share)
s_average_price = 0
for i in range(len(s_price_share_lst)):
	s_average_price += s_price_share_lst[i]
s_base_price = 106.2 / 365 * s_duration_total_d
s_average_total = round(((s_base_price + s_consumption_total * s_average_price)),2)
s_duration_total_m = s_duration_total_d / 30
s_average_per_month = round(s_average_total / s_duration_total_m, 2)

st.write(f"Durchschnitssverbauch Gas: {g_average_per_month}€ pro Monat")
st.write(f"Durchschnittlicher Preis pro Einheit Gas: {round(g_average_price,4)}€")
st.write(f"Gesamtkosten Gas seit Einzug: {g_average_total}€")
st.write(f"Durchschnitssverbauch Strom: {s_average_per_month}€ pro Monat")
st.write(f"Durchschnittlicher Preis pro Einheit Strom: {round(s_average_price,4)}€")
st.write(f"Gesamtkosten Strom seit Einzug: {s_average_total}€")

st.write("")
st.markdown("---")
st.write("")


#################################
###### VERBRAUCH PRO MONAT ######
#################################

st.subheader(f"Verbräuche pro Monat:")

carrier2 = st.radio(
    "Energieversorger auswählen:",
    ('Gas', 'Strom'), key = "2")

if carrier2 == "Gas":
	energy = gas
	energy_str = carrier2
	energy_months = g_months
elif carrier2 == "Strom":
	energy = strom
	energy_str = carrier2
	energy_months = s_months

st.bar_chart(energy_months[energy_str])

st.write("")
st.markdown("---")
st.write("")


##########################################
###### ZÄHLERSTÄNDE LETZTEN 30 TAGE ######
##########################################

st.subheader("Zählerstände der letzten 30 Tage:")

col1, col2 = st.columns(2)

with col1:
	st.markdown("##### Gas")
	st.write(g_lm[["Datum", "Gas"]])

with col2:
	st.markdown("##### Strom")
	st.write(s_lm[["Datum", "Strom"]])

st.write("")
st.markdown("---")
st.write("")


##############################
###### ALLGEMEINE STATS ######
##############################

st.subheader("Allgemeine Stats")

first_october = "2022-10-01"
time_format = "%Y-%m-%d"
first_october = datetime.strptime(first_october, time_format)
today = datetime.now()
days_since_move = (today - energy["Datum"][0]).days
month_since_move = days_since_move / 30
days_since_anna = (today - first_october).days
month_since_anna = days_since_anna / 30

st.write(f"Tage seit Einzug: {days_since_move}")
st.write(f"Monate seit Einzug: {round(month_since_move,1)}")
st.write(f"Tage seit Annas Einzug: {days_since_anna}")
st.write(f"Monate seit Annas Einzug: {round(month_since_anna,1)}")

st.write("")
st.markdown("---")
st.write("")


##############################
###### GANZER DATENSATZ ######
##############################

see_data = st.expander('Ganzer Datensatz')
with see_data:
	st.dataframe(data=energy.reset_index(drop=True))
