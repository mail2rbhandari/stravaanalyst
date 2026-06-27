import streamlit as st
import os
import pandas as pd
import plotly.express as px

os.environ["SILENCE_TOKEN_WARNINGS"] = "true"

st.set_page_config(page_title="EnduraAnalyst", layout="wide")
st.title("🏃‍♂️ EnduraAnalyst")

st.sidebar.header("Strava Login")
st.sidebar.info("Sidebar should appear here")

st.info("If you see this, the app is running. Add more features once stable.")
