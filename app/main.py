import pandas as pd
import streamlit as st
import os
st.write(os.listdir("./"))
df = pd.read_csv("./data/transactions.csv")
st.write(df)
st.text("is this thing on?")
