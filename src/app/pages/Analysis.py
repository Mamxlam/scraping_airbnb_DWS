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
import pydeck as pdk
import folium 
from streamlit_folium import folium_static

st.set_page_config(layout="wide")

# Calculate figure width and height dynamically based on window width
WIN_WIDTH = st.sidebar.number_input('Enter window width', value=800)
FIG_WIDTH = 0.9 * WIN_WIDTH  # 90% of window width or maximum of 800 pixels
FIG_HEIGHT = 0.4 * FIG_WIDTH  # Maintain aspect ratio

# *** Data Loading ***
@st.cache_data  # Caching to improve load times
def load_airbnb_data():
    return pd.read_csv('../../data/listing_data_postproc_TOKEEP.csv', index_col=0)

def corr_matrix(df, title="Correlation Matrix"):
    # 1. Select the relevant columns
    corr_data = df.select_dtypes(exclude=['object'])

    # 2. Calculate the correlation matrix
    corr_matrix = corr_data.corr()

    # 3. Plot the correlation matrix using Seaborn
    # sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')  # 'coolwarm' for a visually appealing colormap
    # plt.title('Correlation Matrix: Visitors vs. Price')
    # plt.show()

    color_scale = px.colors.diverging.RdBu  # Start with a diverging colormap

    # Reverse the colors so red represents positive correlations
    reversed_color_scale = color_scale[::-1]

    # 3. Create the heatmap with Plotly
    fig = px.imshow(corr_matrix,
                    text_auto=True,  # Display correlation values in the cells
                    aspect="auto",  # Adjust aspect ratio for readability
                    title=title, 
                    color_continuous_scale=reversed_color_scale  # Apply the reversed colormap
                )
    
    # Update layout to adjust figure size
    fig.update_layout(
        width=FIG_WIDTH,  # Set width of the figure
        height=FIG_HEIGHT  # Set height of the figure
    )
    st.plotly_chart(fig) 

def clustering(df):
    # Assuming your DataFrame is in 'df'

    data = df

    columns = df.columns

    # Standardize the features
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    # Elbow Method
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, random_state=42, n_init='auto') 
        kmeans.fit(data_scaled)
        wcss.append(kmeans.inertia_)

    # plt.plot(range(1, 11), wcss)
    # plt.title('Elbow Method')
    # plt.xlabel('Number of Clusters')
    # plt.ylabel('WCSS')
    # plt.show()

    cluster_range = st.slider("Clusters Number:", 1, 11)
    kmeans = KMeans(n_clusters=cluster_range, random_state=42, n_init='auto')  # Set n_clusters to 4
    kmeans.fit(data_scaled)

    # Add a new column named 'cluster' to the DataFrame
    df['cluster'] = kmeans.labels_

    # Cluster visualization
    fig = px.scatter_3d(df, x=columns[0], y=columns[1], z=columns[2], color='cluster', title='Cluster Visualization')
    fig.update_layout(
        width=FIG_WIDTH,  # Set width of the figure
        height=FIG_HEIGHT  # Set height of the figure
    )
    # Display the plot in Streamlit
    st.plotly_chart(fig) 

    return df['cluster']



# Calculate the weighted score
def calculate_weighted_score(row):
    # penalizes more the houses that have less reviews.
    prior_weight = 3  # Adjust as needed
    weighted_score = (row['Review Index'] * row['Number of reviews']) / (row['Number of reviews'] + prior_weight)
    return weighted_score


def bot_top_rated_stays(df):
    df['Weighted Score'] = df.apply(calculate_weighted_score, axis=1)

    # Sort the DataFrame by weighted score (descending)
    df = df.sort_values(by='Weighted Score', ascending=False)

    # Get top and bottom 10
    top_10_stays = df.head(10)
    bottom_10_stays = df.tail(10)

    # Combine for visualization
    df_viz_top = top_10_stays[['Title', 'Weighted Score']].drop_duplicates()
    df_viz_bot = bottom_10_stays[['Title', 'Weighted Score']].drop_duplicates()

    # Plotly Bar Chart
    fig = px.bar(df_viz_top, x='Title', y='Weighted Score', color='Weighted Score', 
                color_continuous_scale='YlGn', orientation='v',
                title='Top Rated Stays')

    fig.update_layout(xaxis={'categoryorder': 'total descending'},# Ensure correct order 
                      width=FIG_WIDTH,  # Set width of the figure
                      height=FIG_HEIGHT  # Set height of the figure
                    )  

    st.plotly_chart(fig) 

    # Plotly Bar Chart
    fig = px.bar(df_viz_bot, x='Title', y='Weighted Score', color='Weighted Score', 
                color_continuous_scale='YlOrRd_r', orientation='v',
                title='Bottom Rated Stays')

    fig.update_layout(xaxis={'categoryorder': 'total descending'},# Ensure correct order 
                      width=FIG_WIDTH,  # Set width of the figure
                      height=FIG_HEIGHT  # Set height of the figure
                      )  

    st.plotly_chart(fig) 



data = load_airbnb_data()

st.header("Analysis")

df = data

nanExists = df.select_dtypes(exclude=['object']).isnull().values.any()

if nanExists:
    # Use processor class 
    processor = Preprocessor()

    # Identify missing value columns
    miscols = processor.miscols_ident(df)

    # Perform prediction on those columns to impute the NaN values
    df = processor.impute_predictor(df,miscols)


st.write('##### Assign cluster number to derive type of properties.')

# Select box to choose columns
features = st.multiselect('Select at least 3 columns for clustering (first 3 will be shown in plot):', df.columns)
if len(features) >= 3:
    clusters = clustering(df[features])
else:
    features = ['Price', 'Visitors', 'Beds', 'Bedrooms']
    clusters = clustering(df[features])



st.markdown("---")

st.write('##### According to cluster types and desired data, plot your own correlation matrices.')

df['clusters'] = clusters

# Select box to choose columns
selected_columns = st.multiselect('Select columns to plot correlation matrix:', df.columns)

# Create a multiselect widget on the sidebar for selecting municipalities
selected_clusters = st.multiselect(
    'Cluster type of properties to consider in correlation matrix (All clusters when none selected): ',
    df['clusters'].unique()  # List of unique regions from the DataFrame
)

if not selected_clusters:
    selected_clusters = df['clusters'].unique()

if selected_columns:
    st.write('Filtered DataFrame:')
    st.write(df[selected_columns])
    corr_matrix(df[selected_columns].loc[(data['clusters'].isin(selected_clusters))])
else:
    selected_columns = ['Price', 'Visitors', 'Beds', 'Bedrooms']
    st.write(df)
    corr_matrix(df[selected_columns].loc[(data['clusters'].isin(selected_clusters))])


st.markdown("---")

st.write('##### Review Top and Worst Rated Listings with penalization of low number of reviews.')

bot_top_rated_stays(df)

st.markdown("---")


st.write('##### Review most common characteristics of all available listings.')

# Calculate the counts for each characteristic
char_counts = df.filter(regex='char_*').sum().sort_values(ascending=False)

# Define color scale for countplot
color_scale = px.colors.diverging.RdYlGn[::-1]  # Reverse the color scale


# Plot the countplot
fig1 = px.bar(
    x=char_counts.index,
    y=char_counts.values,
    color=char_counts.values,
    color_continuous_scale=color_scale,
    labels={'x': 'Characteristic', 'y': 'Count'},
    title='Countplot of Characteristics',
    color_continuous_midpoint=char_counts.values.mean()  # midpoint for the color scale
)

fig1.update_layout(
        width=FIG_WIDTH,  # Set width of the figure
        height=FIG_HEIGHT  # Set height of the figure
    )

st.plotly_chart(fig1)



corr_matrix(df.filter(regex=r'(char_*|Review)'), title="Corellation of Characteristics and Ratings")










































































# ============================================================================================================
# MAP EXPERIMENTATION



# # Create a PyDeck scatter plot
# view = pdk.ViewState(latitude=data['Latitude'].mean(),
#                     longitude=data['Longitude'].mean(),
#                     zoom=11,
#                     pitch=50)

# scatter_layer = pdk.Layer(
#     'HexagonLayer',
#     data=data,
#     get_position='[Longitude, Latitude]',
#     radius=40,
#     elevation_scale=4,
#     elevation_range=[0, 1000],
#     pickable=True,
#     extruded=True
# )

# tooltip = {
#     "html": "<b>Name:</b>{elevationValue}<br/><b>Info:</b> {Info}",
#     "style": {
#         "backgroundColor": "steelblue",
#         "color": "white"
#     }
# }

# scatter_plot = pdk.Deck(
#     layers=[scatter_layer],
#     initial_view_state=view,
#     tooltip=tooltip
# )

# # Show the PyDeck plot
# st.pydeck_chart(scatter_plot)

# # Add an interactive widget to capture the selected data point
# selected_point_index = st.session_state.get('selected_point_index', None)

# print(selected_point_index)

# if selected_point_index is not None:
#     st.write("Selected Point Info:")
#     st.write(data[selected_point_index])

# # Capture the selected data point using the 'on_click' event
# if scatter_plot.deck_widget:
#     scatter_plot.deck_widget.on_click(
#         lambda x, y, feature_index: st.session_state.update(selected_point_index=feature_index)
# )


# Create a PyDeck scatter plot
view = pdk.ViewState(latitude=data['Latitude'].mean(),
                    longitude=data['Longitude'].mean(),
                    zoom=11,
                    pitch=50)

scatter_layer = pdk.Layer(
    'HexagonLayer',
    data=data,
    get_position='[Longitude, Latitude]',
    get_elevation='Price',
    radius=40,
    elevation_scale=4,
    elevation_range=[0, 1000],
    pickable=True,
    extruded=True
)

tooltip = {
    "html": "<b>{Longitude}</b> meters away from an MRT station, costs <b>{Latitude}</b> NTD/sqm",
    "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
}

scatter_plot = pdk.Deck(
    layers=scatter_layer,
    initial_view_state=view,
    tooltip=tooltip
)

# Show the PyDeck plot
st.pydeck_chart(scatter_plot)

# def plot_map(data):
#     # Center the map on a reasonable starting location 
#     center_lat = data['Latitude'].mean()
#     center_lon = data['Longitude'].mean()

#     # Create the Folium map object
#     map = folium.Map(location=[center_lat, center_lon], zoom_start=12)

#     # Columns you want to display in the popup
#     display_columns = [
#         'Price', 'Title', 'Visitors', 'Bedrooms', 'Guest Favorite', 'Superhost', 
#         'Number of Reviews'
#     ]

#     # Iterate through your data to add markers with popups
#     for _, row in data.iterrows():
#         html = f""""""

#         # Add more information based on the display_columns list 
#         for col in display_columns:
#             if col in data.columns:
#                 html += f"<b>{col}:</b> {row[col]}<br>"

#         iframe = folium.IFrame(html=html, width=250, height=150)
#         popup = folium.Popup(iframe, max_width=250)

#         folium.Marker(
#             location=[row['Latitude'], row['Longitude']],
#             popup=popup,
#             icon=folium.Icon(color='red', icon='info-sign')  # Customize color if needed
#         ).add_to(map)


#     # Streamlit display
#     st.title("Interactive Property Map")
#     folium_static(map)

# plot_map(data)