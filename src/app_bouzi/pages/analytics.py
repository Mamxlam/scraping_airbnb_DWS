'''
IN this page you are gonna have



0) using collection create a data structure to utilize the collections most_common()
1) selectbox that you will choose an attributes
2) define the type of the building (type is defined by beds, baths, rooms, guests)  --> maybe we should do it exactly like Marios
3) Based on the cluster number and the type of building a coorelation matrix with price must be produced
4)Individual top rated/worst stays based on i)Marios metric ii) chat gpt metric *** iii)multiplication of the number of ratings and the rating iteself normalized to 1/10
 #### Φτιάξε ένα δικό σου cluster ώστε να μπορείς να παίξεις!! εκεπαίδευσε ένα  k-medoids και για κάθε cluster φτιάξε ένα διάγραμμα σε 2d (k) το οποίο να



5) Provide a map that will be show with a scatter plot that show title, number, overall rating and total review number
'''

# streamlit run C:\Users\Nikolas\PycharmProjects\Master_Projects\scraping_airbnb_DWS\src\main_steamlit.py
print('new run')
import streamlit as st
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objects as go
from streamlit_folium import st_folium
import folium as fo
from sklearn.preprocessing import MaxAbsScaler,StandardScaler
from sklearn.cluster import KMeans
import random
import plotly.express as px

# from src.pyscripts.store_data_in_mongo import mongo_connect

# @st.cache_data # ONLY THE before functions
st.header('Analytics page')

data_Df = pd.read_csv('./src/pages/air_bnb.csv',index_col=False)
data_Df['off_region'] = data_Df['off_region'].replace('AMPELOKIPOI-MENEMENI','MENEMENI/AMPELOKIPOI')
data_Df['off_region'] = data_Df['off_region'].replace('Ampelokipoi-Menemeni','Menemeni/Ampelokipoi')
# print('Starttttt')
data_Df = data_Df.drop_duplicates(subset=['title'])

regions = list(data_Df['off_region'].unique())

#--------------------------------------------------- This should go to a function to utilize the side bars
select_region_analysis = st.sidebar.multiselect('Please choose regions',regions,[regions[1],regions[4]])

examined_df = data_Df.loc[data_Df['off_region'].isin(select_region_analysis)]
examined_df.drop(columns =['Unnamed: 0'],inplace =True)
# print(examined_df.do)
st.subheader(f'Available rooms {len(examined_df)}')

# correlation matrix type (beds,bath,room,visitor)  --> implement a cluster algorithm with j-medoids  of the property and price

#TODO I must IMPLMENT A FORMULA THAT PRODUCRED THE TOP RATED BASED ON a combination of numer of rating and the rating itself


#Import collection to identify the most common characteristics (which characteristics are showed more frequently) and plot a correlation matrix


WIN_WIDTH = st.sidebar.number_input('Enter window width (height is 40% of width)', value=1200)
FIG_WIDTH = 0.9 * WIN_WIDTH  # 90% of window width or maximum of 800 pixels
FIG_HEIGHT = 0.4 * FIG_WIDTH  # Maintain aspect ratio
#Create a custer
st.subheader('Create a clusted based on the proerty type defi')

#--------------------------------------------------------------------- MARIOS CODE
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


def calculate_weighted_score(row):
  # penalizes more the houses that have less reviews.
  # row['total_reviews']
  prior_weight = 3  # Adjust as needed
  weighted_score = (float(row['total_rating'].replace(',','.')) * float(row['total_reviews'])) / (float(row['total_reviews'] + prior_weight))
  return weighted_score

def bot_top_rated_stays(df):
    df['Weighted Score'] = df.apply(calculate_weighted_score, axis=1)

    # Sort the DataFrame by weighted score (descending)
    df = df.sort_values(by='Weighted Score', ascending=False)

    # Get top and bottom 10
    top_10_stays = df.head(10)
    bottom_10_stays = df.tail(10)
    print(df.columns)
    # Combine for visualization
    df_viz_top = top_10_stays[['Title', 'Weighted Score']].drop_duplicates()
    df_viz_bot = bottom_10_stays[['Title', 'Weighted Score']].drop_duplicates()

    # Plotly Bar Chart
    fig = px.bar(df_viz_top, x='Title', y='Weighted Score', color='Weighted Score',
                 color_continuous_scale='YlGn', orientation='v',
                 title='Top Rated Stays')

    fig.update_layout(xaxis={'categoryorder': 'total descending'},  # Ensure correct order
                      width=FIG_WIDTH,  # Set width of the figure
                      height=FIG_HEIGHT  # Set height of the figure
                      )

    st.plotly_chart(fig)

    # Plotly Bar Chart
    fig = px.bar(df_viz_bot, x='Title', y='Weighted Score', color='Weighted Score',
                 color_continuous_scale='YlOrRd_r', orientation='v',
                 title='Bottom Rated Stays')

    fig.update_layout(xaxis={'categoryorder': 'total descending'},  # Ensure correct order
                      width=FIG_WIDTH,  # Set width of the figure
                      height=FIG_HEIGHT  # Set height of the figure
                      )

    st.plotly_chart(fig)

    st.header("Analysis")

df = data_Df
df_copy =df.copy()

# nanExists = df.select_dtypes(exclude=['object']).isnull().values.any()

# if nanExists:
#   # Use processor class
#   processor = Preprocessor()
#
#   # Identify missing value columns
#   miscols = processor.miscols_ident(df)
#
#   # Perform prediction on those columns to impute the NaN values
#   df = processor.impute_predictor(df, miscols)

st.write('##### Assign cluster number to derive type of properties.')

# Select box to choose columns
print('hereeee')
print(len(df))

df =df.drop(columns=['Unnamed: 0','Unnamed: 0', '_id', 'title', 'n_prop', 'page','num_characteristics'])
features = st.multiselect('Select at least 3 columns for clustering (first 3 will be shown in plot):', df.columns,['final_price_per_night', 'visitors', 'beds', 'bedrooms'])
if len(features) >= 3:
  clusters = clustering(df[features])
else:
  features = ['final_price_per_night', 'visitors', 'beds', 'bedrooms']
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
# print('---------------------------------------------------------------- CHECK THIS OUT -------------------------------------------------------')
# print(selected_clusters)
if not selected_clusters:
  selected_clusters = df['clusters'].unique()

if selected_columns:
  st.write('Filtered DataFrame:')#TODO INFORM MARIOS ABOUT THAT
  st.write(df[selected_columns])
  corr_matrix(df[selected_columns].loc[(df['clusters'].isin(selected_clusters))])
else:
  selected_columns = ['final_price_per_night', 'visitors', 'beds', 'bedrooms']
  st.write(df)
  corr_matrix(df[selected_columns].loc[(df['clusters'].isin(selected_clusters))])

st.markdown("---")

st.write('##### Review Top and Worst Rated Listings with penalization of low number of reviews.')
# print('before rated stays',len(df))
df['Title'] = df_copy['title']
bot_top_rated_stays(df)

st.markdown("---")

st.write('##### Review most common characteristics of all available listings.')

# Calculate the counts for each characteristic
# print(df.columns)
char_counts = df.loc[:,['superhost', 'guest_favorite','telework',
       'fast_wifi', 'arr_exp', 'location', 'check_in', 'exp_host', 'pets',
       'com', 'cancel', 'parking']].sum().sort_values(ascending=False)
# char_counts = df.filter(regex='char_*').sum().sort_values(ascending=False)

# Define color scale for countplot
color_scale = px.colors.diverging.RdYlGn[::-1]  # Reverse the color scale
# print('char_count------------------------------------------------------------')
# print(type(char_counts))
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

st.markdown("---")

  #----------------------------------------------------------------- END OF MARIOS CODE -----------------------------------------------#

#Create a scatterplot map
st.subheader('ROOMS MAP LOCATION')

map_data_df = data_Df.loc[:,['title','final_price_per_night','d_aristotelous','d_subway','coordinates']]
final_map_data_df = map_data_df.copy()
coordinated_df = map_data_df['coordinates'].str.split(',',expand= True).astype(float)
coordinated_df.columns = ['lat','lon']
final_map_data_df = pd.concat([final_map_data_df,coordinated_df],axis=1)
coords_list = []
latitudes = final_map_data_df['lat'].values
longitudes = final_map_data_df['lon'].values
room_prices = final_map_data_df['final_price_per_night'].values
room_titles = final_map_data_df['title'].values
room_distance_ar = final_map_data_df['d_aristotelous'].values
#
for i in range(len(latitudes)):
    coords_list.append((latitudes[i],longitudes[i]))
# Create the MAPS
my_map= fo.Map(location=(40.66129887375087, 22.91549262058974),zoom_start= 13)
for num in range(len(coords_list)):
    popup_content = f"ID: {num} Title: {room_titles[num]}<br>Price: {room_prices[num]} €/night <br>Distance Aristotelous: {round(room_distance_ar[num])} km"

    fo.Marker(coords_list[num],popup=popup_content).add_to(my_map)
st_folium(my_map,width=900)

#Creaty a ploty radar_graph
st.subheader('Radar graph')

radar_graph_Data = data_Df.loc[:,['total_rating', 'total_reviews' ,'d_aristotelous', 'd_subway', 'd_buses']]
radar_graph_Data['total_rating'] =radar_graph_Data['total_rating'].str.replace(",",".").astype(float)
radar_graph_Data['total_reviews'] =radar_graph_Data['total_reviews'].astype(float)
radar_graph_Data['d_aristotelous'] =radar_graph_Data['d_aristotelous'].astype(float)
radar_graph_Data['d_subway'] =radar_graph_Data['d_subway'].astype(float)
radar_graph_Data['d_buses'] =radar_graph_Data['d_buses'].astype(float)
# radar_graph_Data['n_prop'] =radar_graph_Data['n_prop'].astype(float)
# radar_graph_Data['num_characteristics'] =radar_graph_Data['num_characteristics'].astype(float)


my_scaler = MaxAbsScaler()
scaled_radar_data = pd.DataFrame(my_scaler.fit_transform(radar_graph_Data),columns=radar_graph_Data.columns)
scaled_radar_data['title'] = room_titles
titles_radar = list(scaled_radar_data['title'].unique())
select_titles_analysis = st.multiselect('Please choose wanted',titles_radar,[titles_radar[1],titles_radar[4]])

pre_final_radar_1 = scaled_radar_data.loc[scaled_radar_data['title'].isin(select_titles_analysis)]
# print(len(pre_final_radar_1))
final_map_data_df = pre_final_radar_1.loc[:,['total_rating', 'total_reviews' ,'d_aristotelous', 'd_subway', 'd_buses']]
max_value = round(final_map_data_df.max().max())# The max of the maximum
# print('here we are!!!!')
# print(final_map_data_df)
final_map_data_df['title'] = pre_final_radar_1.loc[final_map_data_df.index,'title']
# print(final_map_data_df)


#Plotly graph
categories = ['total_rating', 'total_reviews' ,'d_aristotelous', 'd_subway', 'd_buses']
radar_fig = go.Figure()

for ind, row in final_map_data_df.iterrows():

  my_color =  f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'
  radar_fig.add_trace(go.Scatterpolar(r=[row['total_rating'],row['total_reviews'],row['d_aristotelous'],row['d_subway'],row['d_buses']],theta = categories,fill='toself',name= row['title'],line=dict(color=my_color)))

radar_fig.update_layout(
  polar=dict(
    radialaxis=dict(
      visible=True,
      range=[0, max_value]
    )),
  showlegend=False
)
st.plotly_chart(radar_fig)

#TODO CREATE A SPYDER GRAPH FOR SOME ATTIBUTES OF THE ROOM (HOWEVER YOU MUST FING THE MAX VALUE GIA KATHE DWMATIO VSTE NA MHN TERMATIZEI)
