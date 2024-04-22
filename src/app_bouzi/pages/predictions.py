'''
In this page you have to train your model
1) a select box where you can choose a model (XGBOOST,SVR ELASTIC NET)
2) sidebars will be adjusted based on you model (SVR, ELASTIC NET IS KNOWN)
3) the results will provide a table for precision recall and f1 score (MACRO AND MICRO CHECK WHICH IS FOR INBALANCED DATA) of our model
#Model is goind to use default parameters (WE DO NOT HAVE TIME FOR THIS)!!!
4)Based on the inputs you have provid (SEE video pyconUs 2023) to get some ideas the model will estimate the price
'''
import streamlit as st
import pandas as pd
import numpy as np
import sklearn

from sklearn.linear_model import ElasticNetCV # A linea model
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.metrics import root_mean_squared_error,mean_absolute_percentage_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from copy import deepcopy

# A tree based model
# The user can have the option to select a range of parameters --> it is not requested
# The input of the model must alwasy be the same

#RMSE and MAPE

data_Df = pd.read_csv('./src/pages//air_bnb.csv',index_col=False)
data_Df.drop(columns= ['Unnamed: 0','_id','title','host_name','search_region', 'n_prop','page','coordinates','off_region','num_characteristics','bathrooms'],inplace=True) #TODO THINK A WAY TO HANDLE THE oof_region -->one hot encode
data_Df['total_reviews']=data_Df['total_reviews'].astype(str).str.replace(',','.')
data_Df['total_rating']=data_Df['total_rating'].astype(str).str.replace(',','.')
data_Df['total_rating'] = pd.to_numeric(data_Df['total_rating'],errors='coerce')
data_Df['total_reviews'] = pd.to_numeric(data_Df['total_reviews'],errors='coerce')
st.header(F'PRICE PREDICTION')
algorithm_list = ["ElasticNET","Random Forest","XGBOOST"]
# print('Starttt!!!!')
list_of_ordinal_columns = ['New', 'superhost', 'guest_favorite' ,'fast_wifi','telework', 'fast_wifi', 'arr_exp', 'location', 'check_in', 'exp_host','pets', 'com', 'cancel', 'parking', 'studio']
for co in list_of_ordinal_columns:
    data_Df[co] = data_Df[co].astype(int)
# print('endddddd!!!')
# print(data_Df.to_string())
# model_name = st.sidebar.selectbox(f'Choose you algorithm',algorithm_list,index=2)

if 'visibility' not in st.session_state:
    st.session_state.visibility = 'visible'
    st.session_state.disabled = False

col1,col2 = st.columns(2)

i_model_name = st.selectbox(f'Choose you algorithm',algorithm_list,index=2)
# st.subheader('Please fill the coresponding input fields.')

test_sample_from_user = {'New':[0], 'superhost':[0], 'guest_favorite':[0], 'total_rating':[0], 'total_reviews':[0],
       'd_aristotelous':[0], 'd_subway':[0], 'd_buses':[0], 'telework':[0], 'fast_wifi':[0],
       'arr_exp':[0], 'location':[0], 'check_in':[0], 'exp_host':[0], 'pets':[0], 'com':[0], 'cancel':[0],
       'parking':[0], 'beds':[0], 'visitors':[0], 'baths':[0], 'bedrooms':[0], 'studio':[0] }
#TODO THE ALGORITHM WILL BE TRAINED IN ALL DATA BUT THESE ARE THE SELECTED FEATURES FROM THE USER
with col1: # The true false values #Make them zeros and one
    i_want_check_in = st.toggle('Check-In')
    i_want_cancel = st.toggle('Cancellation')
    i_want_location = st.toggle('Beautiful view')
    i_want_pets = st.toggle('Pets')
    i_want_workplace = st.toggle('Workplace for professionals and remote workers')
    i_want_parking = st.toggle('Available parking')
    i_want_wifi_speed = st.toggle('Wifi speed > 200 Mbps')
    i_want_arr_exp = st.toggle('Arrival experience')
    i_want_comu_host = st.toggle('Cooperative host') # With excelent communication skills
    i_want_exp_host = st.toggle('Experienced host')
    i_want_superhost = st.toggle("Superhost")
    i_want_guest_favorite = st.toggle("Guest Favorite")
    i_want_new = st.toggle("New room at airbnb")
    i_want_a_studio = st.toggle("Studio")
over_rate,number_rev,distance_aristo,distance_subway,distance_buses ,beds  ,visitors ,bedrooms , bathrooms = 0,0,0,0,0,0,0,0,0
with col2:
    min_ov_rate, max_ov_rate = round(data_Df["total_rating"].min(),2), round(data_Df["total_rating"].max(),2)
    min_number_rev, max_number_rev = round(data_Df["total_reviews"].min(),2), round(data_Df["total_reviews"].max(),2)
    min_d_aristo,max_d_aristo = round(data_Df["d_aristotelous"].min(),2), round(data_Df["d_aristotelous"].max(),2)
    min_d_buses,max_d_buses = round(data_Df["d_buses"].min(),2), round(data_Df["d_buses"].max(),2)
    min_d_subway,max_d_subway = round(data_Df["d_subway"].min(),2), round(data_Df["d_subway"].max(),2)
    min_beds,max_beds = round(data_Df['beds'].min(),2),round(data_Df['beds'].max(),2)
    min_bedrooms,max_bedrooms = round(data_Df['bedrooms'].min(),2),round(data_Df['bedrooms'].max(),2)
    min_visitors,max_visitors = round(data_Df['visitors'].min(),2),round(data_Df['visitors'].max(),2)
    min_baths,max_baths = round(data_Df['baths'].min(),2),round(data_Df['baths'].max(),2)
    over_rate= st.number_input(f"Insert overall rating",value=None,placeholder=f"Suggested range ({min_ov_rate},{max_ov_rate})")
    number_rev = st.number_input(f"Insert number of reviews",value=None,placeholder=f"Suggested range ({min_number_rev},{max_number_rev})")
    distance_aristo = st.number_input(f"Insert distance from Aristotelous",value=None,placeholder=f"Suggested range ({min_d_aristo},{max_d_aristo})")
    distance_subway = st.number_input(f"Insert distance from subway",value=None,placeholder=f"Suggested range ({min_d_subway},{max_d_subway})")
    distance_buses = st.number_input(f"Insert distance from buses",value=None,placeholder=f"Suggested range ({min_d_buses},{max_d_buses})")
    beds = st.number_input(f"Insert number of beds",value=None,placeholder=f"Suggested range ({min_beds},{max_beds})")
    visitors = st.number_input(f"Insert number of visitors",value=None,placeholder=f"Suggested range ({min_visitors},{max_beds})")
    bedrooms = st.number_input(f"Insert number of bedrooms",value=None,placeholder=f"Suggested range ({min_bedrooms},{max_bedrooms})")
    bathrooms = st.number_input(f"Insert of bathrooms",value=None,placeholder=f"Suggested range ({min_baths},{max_baths})")
# check_none_list # We have that we cannot produce predictions with None values
if over_rate is None:
    over_rate = 0
if number_rev is None:
    number_rev = 0
if distance_aristo is None:
    distance_aristo = 0
if distance_subway is None:
    distance_subway = 0
if distance_buses is None:
    distance_buses = 0
if beds is None:
    beds=0
if bedrooms is None:
    bedrooms =0
if bathrooms is None:
    bathrooms=0
if visitors is None:
    visitors =0

data_Df_copy = data_Df.copy()
model_to_train = ''
X = data_Df_copy.drop(columns=['final_price_per_night']) # TODO ETSI OPWS THA EKPAIDEYSW TO MODELO ETSI THA PREPEI NA ΚΑΤΑΣΚΕΥΑΣΩ ΜΕ ΤΗΝ ΣΩΣΤΗ ΣΕΙΡΑ ΤΟ ΔΙΑΝΥΣΜΑ ΠΟΥ ΘΑ ΔΩΣΕΙ Ο ΧΡΗΣΤΗΣ
y = data_Df_copy['final_price_per_night']

test_sample_from_user = {'New':[int(i_want_new)], 'superhost':[int(i_want_superhost)], 'guest_favorite':[int(i_want_guest_favorite)],
'total_rating':[over_rate], 'total_reviews':[number_rev], 'd_aristotelous':[distance_aristo], 'd_subway':[distance_subway], 'd_buses':[distance_buses],
'telework':[int(i_want_workplace)], 'fast_wifi':[int(i_want_wifi_speed)], 'arr_exp':[int(i_want_arr_exp)],
'location':[int(i_want_location)], 'check_in':[int(i_want_check_in)], 'exp_host':[int(i_want_exp_host)],
'pets':[int(i_want_pets)], 'com':[int(i_want_comu_host)], 'cancel':[int(i_want_cancel)], 'parking':[int(i_want_parking)],
'beds':[beds], 'visitors':[visitors],  'baths':[bathrooms], 'bedrooms':[bedrooms], 'studio':[int(i_want_a_studio)]}
test_sample_df = pd.DataFrame(data= test_sample_from_user)

x_train,x_test,y_train,y_test = train_test_split(X,y,train_size=0.8,random_state=42)
y_preds = 0
if i_model_name == "ElasticNET":
    model_to_train = ElasticNetCV(cv=5,random_state=0)
    model_to_train.fit(x_train,y_train)
    y_preds=model_to_train.predict(x_test)
elif i_model_name == "XGBOOST":
    model_to_train = XGBRegressor()
    model_to_train.fit(x_train, y_train)
    y_preds=model_to_train.predict(x_test)
elif i_model_name == 'Random Forest':
    model_to_train = RandomForestRegressor()
    model_to_train.fit(x_train, y_train)
    y_preds=model_to_train.predict(x_test)


st.header('Results')

rmse_metric = root_mean_squared_error(y_true=y_test,y_pred=y_preds) # RMSE how much deviation i have from the actual value
mape_metric = mean_absolute_percentage_error(y_true=y_test,y_pred=y_preds)
results_dict ={"RMSE":[round(rmse_metric,2)],"MPE":[round(mape_metric,2)]} # MEAN PERCENTAGE OF ERRORS BETWEEN THE PREDICTED AND ACTUAL
#TODO ΠΡΟΣΠΑΘΗΣΕ ΝΑ ΒΑΛΩ ΚΑΙ ΜΙΑ ΔΙΕΥΚΡΙΝΙΣΗ ΣΑΝ ΠΛΗΡΟΦΟΡΙΑ ΣΧΕΤΙΚΑ ΜΕ ΤΗΝ ΣΗΜΑΣΙΑ ΤΩΝ ΣΦΑΛΜΑΤΩΝ
#TODO YOU CAN INSERT AN RSQUARED METRIC
results_df = pd.DataFrame(data=results_dict,index=["Errors"])
st.subheader("Model's errors")
st.dataframe(results_df)
print(test_sample_df)
st.write(f"According to your input the estimated room price is ... {round(model_to_train.predict(test_sample_df)[0])} euros per night")
#TODO ADD MARIOS COMMENTS HERE



# streamlit run C:\Users\Nikolas\PycharmProjects\Master_Projects\scraping_airbnb_DWS\src\main_steamlit.py