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


st.title("Hello World!!")

df = pd.read_csv('../../data/listing_data_postproc_20240408_231819.csv', index_col=0)

nanExists = df.isnull().values.any()

if nanExists:
    # Use processor class 
    processor = Preprocessor()

    # Identify missing value columns
    miscols = processor.miscols_ident(df)

    # Perform prediction on those columns to impute the NaN values
    df = processor.impute_predictor(df,miscols)



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
                title="Correlation Matrix: Visitors vs. Price", 
                color_continuous_scale=reversed_color_scale  # Apply the reversed colormap
               )

st.plotly_chart(fig) 


# Assuming your DataFrame is in 'df'
features = ['Price', 'Visitors', 'Beds', 'Bedrooms']  # Choose your specific columns
data = df[features]

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

kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')  # Set n_clusters to 4
kmeans.fit(data_scaled)

# Add a new column named 'cluster' to the DataFrame
df['cluster'] = kmeans.labels_

# Cluster visualization
fig = px.scatter_3d(df, x='Price', y='Visitors', z='Beds', color='cluster', title='Cluster Visualization')
# Display the plot in Streamlit
st.plotly_chart(fig) 





# Calculate the weighted score
def calculate_weighted_score(row):
    # penalizes more the houses that have less reviews.
    prior_weight = 3  # Adjust as needed
    weighted_score = (row['Review Index'] * row['Number of reviews']) / (row['Number of reviews'] + prior_weight)
    return weighted_score

df['weighted_score'] = df.apply(calculate_weighted_score, axis=1)

st.write(df.head())

# Sort the DataFrame by weighted score (descending)
df = df.sort_values(by='weighted_score', ascending=False)

# Get top and bottom 10
top_10_stays = df.head(10)
bottom_10_stays = df.tail(10)

# Combine for visualization
df_viz = pd.concat([top_10_stays[['Title', 'weighted_score']], bottom_10_stays[['Title', 'weighted_score']]]).drop_duplicates()

# Plotly Bar Chart
fig = px.bar(df_viz, x='Title', y='weighted_score', color='weighted_score', 
             color_continuous_scale='RdYlGn', orientation='v',
             title='Top and Bottom Rated Stays')

fig.update_layout(xaxis={'categoryorder': 'total descending'})  # Ensure correct order 


st.plotly_chart(fig) 