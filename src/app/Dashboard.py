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


st.set_page_config(layout="wide")

# Calculate figure width and height dynamically based on window width
WIN_WIDTH = st.sidebar.number_input('Enter window width (height is 40% of width)', value=1200)
FIG_WIDTH = 0.9 * WIN_WIDTH  # 90% of window width or maximum of 800 pixels
FIG_HEIGHT = 0.4 * FIG_WIDTH  # Maintain aspect ratio


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


listings_per_municipality = data['municipality'].value_counts().reset_index()
listings_per_municipality.columns = ['municipality', 'Number of Listings']

# Create a bar chart using Plotly
fig = px.bar(
    listings_per_municipality,
    x='municipality',
    y='Number of Listings',
    labels={'Number of Listings': 'Number of Listings', 'Municipality': 'municipality'},
    title='Number of Available Listings per Municipality'
)

# Update layout to adjust figure size
fig.update_layout(
    width=FIG_WIDTH,  # Set width of the figure
    height=FIG_HEIGHT  # Set height of the figure
)

# Streamlit display
st.subheader("Available Listings per Municipality")
st.plotly_chart(fig)

# Add space between sections
st.markdown("---")

# *** Price Distribution (Using Plotly) ***
st.subheader("Price Distribution")
fig_price = px.histogram(filtered_data, x="Price", nbins=30, title="Price Distribution")
# Update layout to adjust figure size
fig_price.update_layout(
    width=FIG_WIDTH,  # Set width of the figure
    height=FIG_HEIGHT  # Set height of the figure
)
st.plotly_chart(fig_price)

# Add space between sections
st.markdown("---")

# *** Visitors Distribution (Using Plotly) ***
st.subheader("Visitors Distribution")
fig_visitors = px.histogram(filtered_data, x="Visitors", nbins=30, title="Visitors Distribution")
# Update layout to adjust figure size
fig_visitors.update_layout(
    width=FIG_WIDTH,  # Set width of the figure
    height=FIG_HEIGHT  # Set height of the figure
)
st.plotly_chart(fig_visitors)

# Add space between sections
st.markdown("---")

# *** Visitors vs. Price (Using Plotly) ***
st.subheader("Visitors vs. Price")
fig_visitorsvsPrice = px.violin(
    filtered_data, 
    y="Price", 
    x="Visitors", 
    title="Visitors vs. Price", 
    box=True, 
    points="all"
)
fig_visitorsvsPrice.update_layout(
    width=FIG_WIDTH,  # Set width of the figure
    height=FIG_HEIGHT  # Set height of the figure
)
st.plotly_chart(fig_visitorsvsPrice)



# Add space between sections
st.markdown("---")

# *** Visitors Distribution (Using Plotly) ***
st.subheader("Review Index Distribution")
fig = px.histogram(filtered_data, x="Review Index", nbins=10, title="Review Index Distribution")
# Update layout to adjust figure size
fig.update_layout(
    width=FIG_WIDTH,  # Set width of the figure
    height=FIG_HEIGHT  # Set height of the figure
)
st.plotly_chart(fig)



# Add space between sections
st.markdown("---")



# *** Visitors Distribution (Using Plotly) ***
st.subheader("Number of Reviews Distribution")
fig = px.histogram(filtered_data, x="Number of reviews", nbins=30, title="Review Index Distribution")
# Update layout to adjust figure size
fig.update_layout(
    width=FIG_WIDTH,  # Set width of the figure
    height=FIG_HEIGHT  # Set height of the figure
)
st.plotly_chart(fig)



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