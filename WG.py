import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import time
import gspread
import matplotlib.pyplot as plt
from zipfile import ZipFile
from io import BytesIO


#####################
###### CONFIGS ######
#####################

st.set_page_config(
    page_title="Engerieverbäuche",
    page_icon="",
    menu_items={}
)

rgb_background = "#0f1116"

first_october = "2022-10-01"
time_format = "%Y-%m-%d"
first_october = datetime.strptime(first_october, time_format)


###################
###### TITEL ######
###################

st.title(f"Energieverbräuche")
st.markdown("---")

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

st.subheader(f"Verbräuche letzten 30 Tage")

g_jetzt = gas["Datum"][len(gas["Datum"])-1]
g_one_month_ago = g_jetzt - timedelta(days = 30)
g_lm = (gas[gas["Datum"] > g_one_month_ago]).reset_index()
g_first_lm = g_lm["Datum"][0]
g_first_date = gas["Datum"][0]
g_duration = (g_jetzt-g_first_lm).days
g_consumption_lm = g_lm["Gas"][len(g_lm)-1] - g_lm["Gas"][0]
g_consumption_lm = g_consumption_lm / g_duration * 30


g_prices_lm = (g_prices[g_prices["Datum"] > g_one_month_ago]).reset_index()
g_prices_first_lm = g_prices_lm["Datum"][0]

g_duration_lst_lm = []
for i in range(len(g_prices_lm)-1):
	g_duration_lm = (g_prices_lm["Datum"][i+1] - g_prices_lm["Datum"][i]).days
	g_duration_lst_lm.append(g_duration_lm)
g_last_duration_lm = (g_lm["Datum"][len(g_lm["Datum"])-1] - g_prices_lm["Datum"][len(g_prices_lm["Datum"])-1]).days
g_duration_lst_lm.append(g_last_duration_lm)
g_duration_total_d_lm = (g_jetzt-g_first_date).days
g_consumption_total_lm = (g_lm["Gas"][len(g_lm)-1] - g_lm["Gas"][0]) / 100
g_share_lst_lm = []
for i in range(len(g_prices_lm["Datum"])):
	g_price_share_lm = g_duration_lst_lm[i] / 30
	g_share_lst_lm.append(g_price_share_lm)
g_price_share_lst_lm = []
for i in range(len(g_prices_lm["Datum"])):
	g_price_share_lm = g_share_lst_lm[i] * g_prices_lm["Preis"][i] / 10000
	g_price_share_lst_lm.append(g_price_share_lm)
g_price_share_lst_lm = 0
for i in range(len(g_price_share_lst_lm)):
	g_average_price_lm += g_price_share_lst_lm[i]
g_base_price_lm = 20.1633
g_average_total_lm = round(((g_base_price_lm+ g_consumption_total_lm * g_average_price_lm * 10)),2)
g_duration_total_m_lm = g_duration_total_d_lm / 30
g_average_per_month_lm = round(g_average_total_lm / g_duration_total_m_lm, 2)
g_average_per_month_lm_pp = round(g_average_per_month_lm / 3, 2)

st.write(g_prices_lm)
st.write(g_duration_lst_lm)
st.write(g_share_lst_lm)
st.write(g_price_share_lst_lm)
st.write(g_base_price_lm)
st.write()


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

col1, col2 = st.columns(2)

with col1:
	st.metric(label = "Gas", value = f"{g_average_per_month_lm}€")
	st.write(f"Pro Person: {g_average_per_month_lm_pp}")

with col2:
	st.metric(label = "Strom", value =f"{s_costs_lm}€")
	st.write(f"Pro Person: {s_costs_lm_pp}")

st.write("")
st.markdown("---")
st.write("")


########################################
###### VERBRAUCH UND DURCHSCHNITT ######
########################################

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
if carrier == "Gas":
	gas["Average"] = avg_energy
elif carrier == "Strom":
	strom["Average"] = avg_energy

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


###############################
###### KOSTEN SEIT START ######
###############################
tab1, tab2 = st.tabs(["Seit Einzug", "Seit Anna"])
with tab1:
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

	col1, col2 = st.columns(2)

	with col1:
		st.markdown("##### Gas")
		st.write(f"Durchschnitssverbauch: {g_average_per_month}€ pro Monat")
		st.write(f"Durchschnittlicher Preis: {round(g_average_price,4)}€ / kWh")
		st.write(f"Gesamtkosten seit Einzug: {g_average_total}€")

	with col2:
		st.markdown("##### Strom")
		st.write(f"Durchschnitssverbauch: {s_average_per_month}€ pro Monat")
		st.write(f"Durchschnittlicher Preis: {round(s_average_price,4)}€ / kWh")
		st.write(f"Gesamtkosten seit Einzug: {s_average_total}€")

with tab2:
	st.subheader(f"Energiekosten seit Anna")

	a_g_prices = g_prices[g_prices["Datum"] >= first_october]
	a_s_prices = s_prices[s_prices["Datum"] >= first_october]
	a_gas = gas[gas["Datum"] >= first_october]
	a_strom = strom[strom["Datum"] >= first_october]

	a_g_prices.reset_index(inplace = True)
	a_s_prices.reset_index(inplace = True)
	a_gas.reset_index(inplace = True)
	a_strom.reset_index(inplace = True)

	st.write(a_g_prices)
	st.write(a_s_prices)
	st.write(a_gas)
	st.write(a_strom)

	a_g_duration_lst = []
	for i in range(len(a_g_prices)-1):
		a_g_duration = (a_g_prices["Datum"][i+1] - a_g_prices["Datum"][i]).days
		a_g_duration_lst.append(a_g_duration)
	a_g_last_duration = (a_gas["Datum"][len(a_gas["Datum"])-1] - a_g_prices["Datum"][len(a_g_prices["Datum"])-1]).days
	a_g_duration_lst.append(a_g_last_duration)
	a_g_duration_total_d = (g_jetzt-g_first_date).days
	a_g_consumption_total = (a_gas["Gas"][len(a_gas)-1] - a_gas["Gas"][0]) / 100
	a_g_share_lst = []	
	for i in range(len(a_g_prices["Datum"])):
		a_g_price_share = a_g_duration_lst[i] / a_g_duration_total_d
		a_g_share_lst.append(a_g_price_share)
	a_g_price_share_lst = []
	for i in range(len(a_g_prices["Datum"])):
		a_g_price_share = a_g_share_lst[i] * a_g_prices["Preis"][i] / 10000
		a_g_price_share_lst.append(a_g_price_share)
	a_g_average_price = 0
	for i in range(len(a_g_price_share_lst)):
		a_g_average_price += a_g_price_share_lst[i]
	a_g_base_price = 241.96 / 365 * a_g_duration_total_d
	a_g_average_total = round(((a_g_base_price + a_g_consumption_total * a_g_average_price * 10)),2)
	a_g_duration_total_m = a_g_duration_total_d / 30
	a_g_average_per_month = round(a_g_average_total / a_g_duration_total_m, 2)

	a_s_duration_lst = []
	for i in range(len(a_s_prices)-1):
		a_s_duration = (a_s_prices["Datum"][i+1] - a_s_prices["Datum"][i]).days
		a_s_duration_lst.append(a_s_duration)
	a_s_last_duration = (a_strom["Datum"][len(a_strom["Datum"])-1] - a_s_prices["Datum"][len(a_s_prices["Datum"])-1]).days
	a_s_duration_lst.append(a_s_last_duration)
	a_s_duration_total_d = (s_jetzt-s_first_date).days
	a_s_consumption_total = (a_strom["Strom"][len(a_strom)-1] - a_strom["Strom"][0]) / 100
	a_s_share_lst = []	
	for i in range(len(a_s_prices["Datum"])):
		a_s_price_share = a_s_duration_lst[i] / a_s_duration_total_d
		a_s_share_lst.append(a_s_price_share)
	a_s_price_share_lst = []
	for i in range(len(a_s_prices["Datum"])):
		a_s_price_share = a_s_share_lst[i] * a_s_prices["Preis"][i] / 10000
		a_s_price_share_lst.append(a_s_price_share)
	a_s_average_price = 0
	for i in range(len(a_s_price_share_lst)):
		a_s_average_price += a_s_price_share_lst[i]
	a_s_base_price = 106.2 / 365 * a_s_duration_total_d
	a_s_average_total = round(((a_s_base_price + a_s_consumption_total * a_s_average_price)),2)
	a_s_duration_total_m = a_s_duration_total_d / 30
	a_s_average_per_month = round(a_s_average_total / a_s_duration_total_m, 2)

	col1, col2 = st.columns(2)

	with col1:
		st.markdown("##### Gas")
		st.write(f"Durchschnitssverbauch: {a_g_average_per_month}€ pro Monat")
		st.write(f"Durchschnittlicher Preis: {round(a_g_average_price,4)}€ / kWh")
		st.write(f"Gesamtkosten seit Anna: {a_g_average_total}€")

	with col2:
		st.markdown("##### Strom")
		st.write(f"Durchschnitssverbauch: {a_s_average_per_month}€ pro Monat")
		st.write(f"Durchschnittlicher Preis: {round(a_s_average_price,4)}€ / kWh")
		st.write(f"Gesamtkosten seit Anna: {a_s_average_total}€")

st.write("")
st.markdown("---")
st.write("")


#################################
###### VERBRAUCH PRO MONAT ######
#################################

st.subheader(f"Verbräuche pro Monat")

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

st.subheader("Zählerstände der letzten 30 Tage")

col1, col2 = st.columns(2)

with col1:
	st.markdown("##### Gas")
	st.table(g_lm[["Datum", "Gas"]])

with col2:
	st.markdown("##### Strom")
	st.table(s_lm[["Datum", "Strom"]])

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
	col1, col2 = st.columns(2)

	with col1:
		st.markdown("##### Gas")
		st.dataframe(data=gas[["Datum", "Gas"]].reset_index(drop=True))

	with col2:
		st.markdown("##### Strom")
		st.dataframe(data=strom[["Datum", "Strom"]].reset_index(drop=True))

##########################
###### EXPERIMENTAL ######
##########################

st.write("")
st.markdown("---")
st.write("")
