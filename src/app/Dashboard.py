import streamlit as st
import pandas as pd
import numpy as np
import re
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
from plotly import graph_objects as go
from plotly.graph_objects import Figure

from sys import path
from os import getcwd
import os
path.append(os.path.join(getcwd(),"..","..","src"))
from pyscripts.Preprocessor import Preprocessor



# *** App Title ***
st.title("Airbnb Listings Analysis")

# *** Data Loading ***
@st.cache_data  # Caching to improve load times
def load_airbnb_data():
    return pd.read_csv('../../data/listing_data_postproc_TOKEEP.csv', index_col=0)

data = load_airbnb_data()

# *** Sidebar for User Input ***
st.sidebar.header("Filters and Options")

# Price Range Slider
price_range = st.sidebar.slider("Price Range", 
                                int(data.Price.min()), 
                                int(data.Price.max()),
                                (int(data.Price.min()), int(data.Price.max() * 0.75)))

# Visitors Slider
visitors_range = st.sidebar.slider("Visitors Range", 
                                   int(data.Visitors.min()), 
                                   int(data.Visitors.max()),
                                   (int(data.Visitors.min()), int(data.Visitors.max() * 0.75)))



# Create a multiselect widget on the sidebar for selecting municipalities
selected_regions = st.sidebar.multiselect(
    'Select regions',
    data['municipality'].unique()  # List of unique regions from the DataFrame
)

if not selected_regions:
    selected_regions = data['municipality'].unique()

# *** Filtered Data ***
filtered_data = data[
    (data['municipality'].isin(selected_regions)) &
    (data.Price >= price_range[0]) & 
    (data.Price <= price_range[1]) &
    (data.Visitors >= visitors_range[0]) &
    (data.Visitors <= visitors_range[1])
]

# *** Main App Sections ***
st.header("Dashboard")

# Add space between sections
st.markdown("---")

# *** Price Distribution (Using Plotly) ***
st.subheader("Price Distribution")
fig_price = px.histogram(filtered_data, x="Price", nbins=30, title="Price Distribution")
st.plotly_chart(fig_price)

# Add space between sections
st.markdown("---")

# *** Price Distribution (Using Plotly) ***
st.subheader("Visitors Distribution")
fig_price = px.histogram(filtered_data, x="Visitors", nbins=30, title="Visitors Distribution")
st.plotly_chart(fig_price)

# Add space between sections
st.markdown("---")

# *** Visitors vs. Price (Using Plotly) ***
st.subheader("Visitors vs. Price")
fig_visitors = px.scatter(filtered_data, x="Visitors", y="Price", title="Visitors vs. Price")
st.plotly_chart(fig_visitors)

# Add space between sections
st.markdown("---")

# ... (Add more plots: e.g., Beds vs. Price, Review Index vs. Price, etc.)


# *** Summary Statistics ***
st.subheader("Summary Statistics")

# Price Summary
st.write("### Price Summary")
st.write(filtered_data['Price'].describe().to_frame().transpose())

# Visitors Summary
st.write("### Visitors Summary")
st.write(filtered_data['Visitors'].describe().to_frame().transpose())

# Bedrooms Count
st.write("### Bedrooms Count")
bedrooms_count = filtered_data['Bedrooms'].value_counts().reset_index()
bedrooms_count.columns = ['Bedrooms', 'Count']
st.write(bedrooms_count)