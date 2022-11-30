import streamlit as st
import pandas as pd
from datetime import datetime
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



avg_strom = []

for i in range(len(strom["Strom"])):
	current_avg = (strom["Strom"][:i].sum()/i)
	avg_strom.append(current_avg)

strom["Average"] = avg_strom



st.title("Stromverbrauch")

fig, ax = plt.subplots()
ax.plot(strom["Datum"], strom["Strom"])
ax.plot(strom["Datum"], strom["Average"], c = "r")
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.tick_params(right = False ,
                labelbottom = False, bottom = False)
st.pyplot(fig)

