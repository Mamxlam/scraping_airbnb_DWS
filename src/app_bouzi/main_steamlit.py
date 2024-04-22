import streamlit as st
import pandas as pd
import numpy as np
import plotly
# from pyscripts.mongo_functionality import mongo_connect


#Load the data from mongo

# my_colleciton=mongo_connect() #Is there all ok with AUTH VPN

# streamlit run C:\Users\Nikolas\PycharmProjects\Master_Projects\scraping_airbnb_DWS\src\main_steamlit.py
st.page_link("./pages/statistics.py",label='Statistics',icon='📊')

st.page_link("./pages/analytics.py",label='Analytics',icon='📈')

st.page_link('./pages/predictions.py',label='Predictions',icon='🔮')