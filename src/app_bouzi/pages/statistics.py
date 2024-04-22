'''
In this page you are gonna have a select box where you can

0)insert also the general characteristis for example name and number of available rooms
1)see which search region do you infer to, if nothing is given then it will provide general statistics for all region
2) a check box that will allow to select multiple region or an individual

3) there will be histogram for price distribution, a general statistic table from describe describe --> box plot are a good idea?

4) The user will have the opportunity to select to the price reange or the

'''

# streamlit run C:\Users\Nikolas\PycharmProjects\Master_Projects\scraping_airbnb_DWS\src\main_steamlit.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objects as go
# from sto import mongo_connect

# my_collection=mongo_connect()

# data_list=list(my_collection.find())

data_Df = pd.read_csv('./src/pages//air_bnb.csv',index_col=False)
# print(data_Df.columns)
def sidebar_charcteristics():
    '''
    Here we are gonna implement the side characteristics
    '''
    pass

regions = tuple(data_Df['off_region'].unique())

#--------------------------------------------------- This should go to a function to utilize the side bars
selected_region=st.sidebar.selectbox(f'Region statistics',regions,index=2) # other wise use multiselect but returns a numpy array
st.header(F'GENERAL STATISTICS')
examined_df = data_Df.loc[data_Df['off_region']==selected_region]
examined_df.drop(columns =['Unnamed: 0'],inplace =True)
# print(examined_df.columns)



#Range για το final price per night, review_numbers, total rating
final_prices = examined_df['final_price_per_night'].values
sort_final_prices = np.unique(np.sort(final_prices))#final_prices
# print(sort_final_prices)
# print(min(sort_final_prices),max(sort_final_prices))
start_price,end_price = st.sidebar.select_slider('Select the price range',options=sort_final_prices,value=(min(sort_final_prices),max(sort_final_prices)))
# print(start_price,end_price)
# print(len(examined_df))
after_price_df = examined_df.loc[(examined_df['final_price_per_night']>=start_price)&(examined_df['final_price_per_night']<=end_price)]
after_price_df['total_reviews']=after_price_df['total_reviews'].astype(str).str.replace(',','.')
after_price_df['total_rating']=after_price_df['total_rating'].astype(str).str.replace(',','.')
after_price_df['total_rating_float'] = pd.to_numeric(after_price_df['total_rating'],errors='coerce')
after_price_df['total_reviews_float'] = pd.to_numeric(after_price_df['total_reviews'],errors='coerce')

total_reviews = np.unique(np.sort(after_price_df['total_reviews_float'].values))
overall_rating = np.unique(np.sort(after_price_df['total_rating_float'].values))


start_rating,end_rating = st.sidebar.select_slider('Select the total rating',options=overall_rating,value=(min(overall_rating),max(overall_rating)))
after_rating_df = after_price_df.loc[(after_price_df['total_rating_float']>=start_rating)&(after_price_df['total_rating_float']<=end_rating)]

start_reviews,end_reviews = st.sidebar.select_slider('Select the total reviews',options=total_reviews,value=(min(total_reviews),max(total_reviews)))
after_reviews_df = after_rating_df.loc[(after_rating_df['total_reviews_float']>=start_reviews)&(after_rating_df['total_reviews_float']<=end_reviews)]

is_superhost = st.sidebar.checkbox('Superhost')
# print(after_reviews_df.columns)
after_superhost_df,after_guest_favorite_df =pd.DataFrame(),pd.DataFrame()
if is_superhost:
    after_superhost_df = after_reviews_df.loc[after_reviews_df['superhost']==True]
else:
    after_superhost_df =after_reviews_df

is_guest_favorite = st.sidebar.checkbox('Guest Favorite')
if is_guest_favorite:
    after_guest_favorite_df = after_superhost_df.loc[after_reviews_df['guest_favorite']==True]
else:
    after_guest_favorite_df = after_superhost_df

st.subheader(f"{selected_region.upper()} available rooms : {len(after_guest_favorite_df), len(examined_df) , len(after_reviews_df)} ")


parameter=st.selectbox(f'Region statistics',after_guest_favorite_df.columns,index=0)
# st.subheader(f'{selected_region} Bar Chart')
trace_for_mean = go.Bar(x=after_guest_favorite_df['title'],y=after_guest_favorite_df[parameter],marker=dict(color='skyblue'))
layout_for_mean = go.Layout(title = f'Barplot for {parameter}')
fig_mean = go.Figure(data = [trace_for_mean],layout=layout_for_mean)
st.plotly_chart(fig_mean)

st.subheader(f'{selected_region} table')
st.dataframe(after_guest_favorite_df)

st.subheader(f'{selected_region} Box plot')
trace_for_box_plot = go.Box(y=after_guest_favorite_df[parameter],boxmean=True,marker=dict(color='skyblue')) #TODO να μπορείς να το εξηγείς
layout_for_box_plot = go.Layout(title = f'Boxplot for {parameter}')
fig_box_plot = go.Figure(data=[trace_for_box_plot],layout=layout_for_box_plot)
st.plotly_chart(fig_box_plot)

st.subheader(f'{selected_region} statistics')
st.dataframe(after_guest_favorite_df.describe())
