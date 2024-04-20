import streamlit as st
import pandas as pd
import numpy as np
import re
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from plotly import graph_objects as go
from plotly.graph_objects import Figure
from sklearn.compose import ColumnTransformer
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
import lightgbm as lgb
import plotly.express as px
import shap

from sys import path
from os import getcwd
import os
path.append(os.path.join(getcwd(),"..","..","src"))
from pyscripts.Preprocessor import Preprocessor

st.set_page_config(layout="wide")



# *** Data Loading ***
@st.cache_data  # Caching to improve load times
def load_airbnb_data():
    return pd.read_csv('../../data/listing_data_postproc_TOKEEP.csv', index_col=0)

data = load_airbnb_data()

st.header("Price Suggestion")

st.write('##### Listing Data Overview')
st.write(data)

# Split data into features and target
X = data.drop(columns=['Price','Title','Host Name'])
y = data['Price']


# One-hot encoding for categorical feature
ct = ColumnTransformer(
    [('one_hot_encoder', OneHotEncoder(drop='first'), ['municipality'])],
    remainder='passthrough'
)

X_encoded = ct.fit_transform(X)

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_encoded)

# Train test split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train regression models
@st.cache_resource
def train_elastic_net():
    model = ElasticNet(alpha=0.1, l1_ratio=0.5)
    model.fit(X_train, y_train)
    return model

@st.cache_resource
def train_random_forest():
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

@st.cache_resource
def train_lightgbm():
    model = lgb.LGBMRegressor()
    model.fit(X_train, y_train)
    return model

@st.cache_resource
def shap_values_gen(_model, train, test):
    explainer = shap.Explainer(_model, train)
    shap_values = explainer(test)
    return shap_values

elastic_net = train_elastic_net()
random_forest = train_random_forest()
lgb_model = train_lightgbm()

st.write('##### Select model and fill in all available features in thew sidebar and then press predict for the price suggestion.')

# Model selection
model_type = st.selectbox("Select Model", ["ElasticNet", "Random Forest", "LightGBM"])

# Create an editable row for user input
# Create an editable row for user input based on original DataFrame columns
user_input_df = pd.DataFrame()

for col in X.columns:
    if col == 'municipality':
        user_input_df[col] = [st.sidebar.selectbox(f"{col}", data[col].unique())]
    else:
        user_input_df[col] = [st.sidebar.text_input(f"{col}", value="")]

if st.button("Predict"):
    if user_input_df.isna().any().any() or user_input_df.isin(['']).any().any():
        st.warning("Please provide input for all features.")
    else:
        enc_user_input = ct.transform(user_input_df)
        sc_user_input = scaler.transform(enc_user_input)
        # Predict price based on selected model
        if model_type == "ElasticNet":
            # Create shap explainer and calculate shap values
            shap_values = shap_values_gen(elastic_net, X_train, sc_user_input)
            prediction = elastic_net.predict(sc_user_input)
        elif model_type == "Random Forest":
            shap_values = shap_values_gen(elastic_net, X_train, sc_user_input)
            prediction = random_forest.predict(sc_user_input)
        else:
            shap_values = shap_values_gen(elastic_net, X_train, sc_user_input)
            prediction = lgb_model.predict(sc_user_input)

        # Display prediction
        st.subheader(f"Predicted Price: {prediction[0]}")

        # Display Shapley values summary plot
        st.subheader("Shapley Values Summary Plot")
        fig_summary = shap.summary_plot(shap_values, sc_user_input)
        st.pyplot(fig_summary)



# # *** Data Loading ***
# @st.cache_data  # Caching to improve load times
# def load_airbnb_data():
#     return pd.read_csv('../../data/listing_data_postproc_TOKEEP.csv', index_col=0)

# data = load_airbnb_data()

# st.header("Price Suggestion")

# st.write('##### Listing Data Overview')
# st.write(data)

# # Split data into features and target
# X = data.drop(columns=['Price','Title','Host Name'])
# y = data['Price']

# # One-hot encoding for categorical feature
# ct = ColumnTransformer(
#     [('one_hot_encoder', OneHotEncoder(drop='first'), ['municipality'])],
#     remainder='passthrough'
# )

# X_encoded = ct.fit_transform(X)

# # Train test split
# X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

# # Train regression models
# @st.cache_resource
# def train_elastic_net():
#     model = ElasticNet(alpha=0.1, l1_ratio=0.5)
#     model.fit(X_train, y_train)
#     return model

# @st.cache_resource
# def train_random_forest():
#     model = RandomForestRegressor(n_estimators=100, random_state=42)
#     model.fit(X_train, y_train)
#     return model

# @st.cache_resource
# def train_lightgbm():
#     model = lgb.LGBMRegressor()
#     model.fit(X_train, y_train)
#     return model

# @st.cache_resource
# def shap_values_gen(_model, train, test):
#     explainer = shap.Explainer(_model, train)
#     shap_values = explainer(test)
#     return shap_values

# elastic_net = train_elastic_net()
# random_forest = train_random_forest()
# lgb_model = train_lightgbm()

# st.write('##### Select model and fill in all available features in the sidebar and then press predict for the price suggestion.')

# # Model selection
# model_type = st.selectbox("Select Model", ["ElasticNet", "Random Forest", "LightGBM"])

# # Create an editable row for user input
# user_input_df = pd.DataFrame()

# for col in X.columns:
#     if col == 'municipality':
#         user_input_df[col] = [st.sidebar.selectbox(f"{col}", data[col].unique())]
#     else:
#         user_input_df[col] = [st.sidebar.text_input(f"{col}", value="")]

# if st.button("Predict"):
#     if user_input_df.isna().any().any() or user_input_df.isin(['']).any().any():
#         st.warning("Please provide input for all features.")
#     else:
#         enc_user_input = ct.transform(user_input_df)
#         # Predict price based on selected model
#         if model_type == "ElasticNet":
#             # Create shap explainer and calculate shap values
#             shap_values = shap_values_gen(elastic_net, X_train, enc_user_input)
#             prediction = elastic_net.predict(enc_user_input)
#         elif model_type == "Random Forest":
#             shap_values = shap_values_gen(elastic_net, X_train, enc_user_input)
#             prediction = random_forest.predict(enc_user_input)
#         else:
#             shap_values = shap_values_gen(elastic_net, X_train, enc_user_input)
#             prediction = lgb_model.predict(enc_user_input)

#         # Display prediction
#         st.subheader(f"Predicted Price: {prediction[0]}")

#         # Display Shapley values summary plot
#         st.subheader("Shapley Values Summary Plot")
#         fig_summary = shap.summary_plot(shap_values, enc_user_input, feature_names=X.columns)
#         st.pyplot(fig_summary)