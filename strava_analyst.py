import streamlit as st
import os
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from stravalib.client import Client
import numpy as np
from sklearn.linear_model import LinearRegression
from folium.plugins import HeatMap

os.environ["SILENCE_TOKEN_WARNINGS"] = "true"

st.set_page_config(page_title="EnduraAnalyst", layout="wide")
st.title("🏃‍♂️ EnduraAnalyst Pro")
st.markdown("### Serious Endurance Athlete Analytics")

# Sidebar login (keep your existing login code here)...

if "token" in st.session_state:
    client = Client(access_token=st.session_state.token['access_token'])
    st.success("✅ Connected")
    
    activities = list(client.get_activities(limit=50))
    df = pd.DataFrame([{
        'id': a.id,
        'name': a.name,
        'sport_type': str(a.sport_type),
        'distance_km': a.distance / 1000,
        'start_date': a.start_date.date(),
    } for a in activities])
    
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Trends", "🗺️ Routes", "🔥 Heatmap"])
    
    with tab1:
        st.metric("Total Distance", f"{df['distance_km'].sum():.1f} km")
        fig = px.bar(df, x='start_date', y='distance_km', color='sport_type')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Performance Prediction")
        # ... prediction code ...
    
    with tab3:
        st.subheader("Your Routes")
        activity_id = st.selectbox("Select Activity", df['id'])
        try:
            stream = client.get_activity_streams(activity_id, types=['latlng'])
            if 'latlng' in stream:
                points = stream['latlng'].data
                m = folium.Map(location=points[0], zoom_start=13)
                folium.PolyLine(points, color="red", weight=3, opacity=1).add_to(m)
                st_folium(m, width=700)
        except:
            st.info("Select activity for route")
    
    with tab4:
        st.subheader("Activity Heatmap")
        m = folium.Map(location=[30.3, 78.0], zoom_start=8)
        # Simple heatmap from activities (expand with all points)
        HeatMap([[30.3, 78.0]], radius=20).add_to(m)  # Replace with real data
        st_folium(m, width=700)
