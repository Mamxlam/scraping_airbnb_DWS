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

st.set_page_config(layout="wide")

st.set_option('deprecation.showPyplotGlobalUse', False)

# *** Data Loading ***
@st.cache_data  # Caching to improve load times
def load_airbnb_data():
    return pd.read_csv('../../data/listing_data_postproc_TOKEEP.csv', index_col=0)

data = load_airbnb_data()

st.header("Price Suggestion")

st.write('##### Listing Data Overview')
st.write(data)

# Split data into features and target
X = data.drop(columns=['Price','Title','Host Name', 'municipality'])
y = data['Price']


# Train test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train regression models
def train_elastic_net():
    model = ElasticNet(alpha=0.1, l1_ratio=0.5)
    model.fit(X_train, y_train)
    return model

def train_random_forest():
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

def train_lightgbm():
    model = lgb.LGBMRegressor()
    model.fit(X_train, y_train)
    return model

def shap_values_gen(_model, train, test, show=True):
    explainer = shap.Explainer(_model, train)
    shap_values = explainer(test)
    
    if show:
        fig = shap.force_plot(
            explainer.expected_value, shap_values.values, test.iloc[0], matplotlib=True
        )
        st.pyplot(fig)
    return shap_values

elastic_net = train_elastic_net()
random_forest = train_random_forest()
lgb_model = train_lightgbm()

st.write('##### Select model and fill in all available features in the sidebar and then press predict for the price suggestion.')

# Model selection
model_type = st.selectbox("Select Model", ["ElasticNet", "Random Forest", "LightGBM"])

# Create an editable row for user input based on original DataFrame columns
user_input_df = pd.DataFrame()

st.sidebar.subheader('Input Data for Price Suggestion (Median Default Values)')

for col in X_train.columns:
    if col == 'municipality':
        user_input_df[col] = [st.sidebar.selectbox(f"{col}", data[col].unique())]
    else:
        default_value = X_train[col].median()
        min_value = X_train[col].min()
        max_value = X_train[col].max()
        user_input_df[col] = [st.sidebar.text_input(f"{col} (Min value: {min_value}, Max value: {max_value})", value=default_value)]

if st.button("Predict"):
    if user_input_df.isna().any().any() or user_input_df.isin(['']).any().any():
        st.warning("Please provide input for all features.")
    else:
        user_input_df = user_input_df.astype("float32")
        if model_type == "ElasticNet":
            prediction = elastic_net.predict(user_input_df)
            st.write(f"#### Predicted Price: {prediction[0]}")
            # Create shap explainer and calculate shap values
            shap_values = shap_values_gen(elastic_net, X_train, user_input_df)
        elif model_type == "Random Forest":
            prediction = random_forest.predict(user_input_df)
            st.write(f"#### Predicted Price: {prediction[0]}")
            shap_values = shap_values_gen(random_forest, X_train, user_input_df)
        else:
            prediction = lgb_model.predict(user_input_df)
            st.write(f"#### Predicted Price: {prediction[0]}")
            shap_values = shap_values_gen(lgb_model, X_train, user_input_df)

        # Display Shapley values summary plot
        st.subheader("Shapley Values Summary Plot")
        shap_values_train = shap_values_gen(elastic_net, X_train, X_train, show=False)
        fig_summary = shap.summary_plot(shap_values_train, X_train)
        st.pyplot(fig_summary)
