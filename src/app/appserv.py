import streamlit as st
import pandas as pd

st.title("Hello World!!")

df = pd.read_csv('../data/listing_data_postproc_20240408_231819.csv', index_col=0)