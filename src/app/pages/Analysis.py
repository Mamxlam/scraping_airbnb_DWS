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

# *** Data Loading ***
@st.cache_data  # Caching to improve load times
def load_airbnb_data():
    return pd.read_csv('../../data/listing_data_postproc_TOKEEP.csv', index_col=0)

def corr_matrix(df):
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
                    title="Correlation Matrix", 
                    color_continuous_scale=reversed_color_scale  # Apply the reversed colormap
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

    cluster_range = st.sidebar.slider("Cluster Range", 1, 11)
    kmeans = KMeans(n_clusters=cluster_range, random_state=42, n_init='auto')  # Set n_clusters to 4
    kmeans.fit(data_scaled)

    # Add a new column named 'cluster' to the DataFrame
    df['cluster'] = kmeans.labels_

    # Cluster visualization
    fig = px.scatter_3d(df, x=columns[0], y=columns[1], z=columns[2], color='cluster', title='Cluster Visualization')
    # Display the plot in Streamlit
    st.plotly_chart(fig) 



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

    fig.update_layout(xaxis={'categoryorder': 'total descending'})  # Ensure correct order 

    st.plotly_chart(fig) 

    # Plotly Bar Chart
    fig = px.bar(df_viz_bot, x='Title', y='Weighted Score', color='Weighted Score', 
                color_continuous_scale='YlOrRd_r', orientation='v',
                title='Bottom Rated Stays')

    fig.update_layout(xaxis={'categoryorder': 'total descending'})  # Ensure correct order 

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

# Select box to choose columns
selected_columns = st.multiselect('Select columns to display:', df.columns)

# Filter DataFrame based on selected columns
if selected_columns:
    st.write('Filtered DataFrame:')
    st.write(df[selected_columns])
    corr_matrix(df[selected_columns])
else:
    selected_columns = ['Price', 'Visitors', 'Beds', 'Bedrooms']
    st.write(df)
    corr_matrix(df[selected_columns])

# Select box to choose columns
features = st.multiselect('Select at least 3 columns for clustering (first 3 will be shown in plot):', df.columns)
if len(features) >= 3:
    clustering(df[features])
else:
    features = ['Price', 'Visitors', 'Beds', 'Bedrooms']
    clustering(df[features])


bot_top_rated_stays(df)
