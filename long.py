import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt

# Set Streamlit page configuration
st.set_page_config(page_title="HRM", initial_sidebar_state="expanded", layout="wide")

# Title and header
st.title("Industrial Human Resource Geo-Visualization")

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv("final_HR.csv")

    # Clean column names (remove extra spaces)
    data.columns = data.columns.str.strip()

    # Check if latitude and longitude columns exist, if not, add them
    if 'latitude' not in data.columns or 'longitude' not in data.columns:
        # Generate random latitudes and longitudes for demonstration
        np.random.seed(42)  # For reproducibility
        data['latitude'] = np.random.uniform(8.0, 37.0, size=len(data))  # Approximate range for India
        data['longitude'] = np.random.uniform(68.0, 97.0, size=len(data))
    return data

# Load the data
data = load_data()

# Sidebar for selecting state and district
unique_states = sorted(data['State'].unique())
selected_state = st.sidebar.selectbox("Select State", unique_states)

filtered_districts = sorted(data[data['State'] == selected_state]['District'].unique())
selected_district = st.sidebar.selectbox("Select District", filtered_districts)

# Display data columns for debugging
if st.sidebar.checkbox("Show Data Columns"):
    st.sidebar.write(data.columns.tolist())

# Display summary of the selected state and district
state_data = data[data['State'] == selected_state]
district_data = data[data['District'] == selected_district]

st.subheader("State and District Information")
st.write(f"State: {selected_state}, District: {selected_district}")

# Display data summary
st.subheader("Data Summary")
st.write(data.describe())

# State-wise Summary Plot
try:
    state_summary = state_data[['main_workers_total_persons', 'main_workers_total_males', 'main_workers_total_females', 'TotalPopulation']].sum()
    fig = px.bar(
        x=state_summary.index,
        y=state_summary.values,
        title=f"{selected_state} - Workers Summary",
        labels={"x": "Worker Type", "y": "Count"},
        color=state_summary.index
    )
    st.plotly_chart(fig)
except KeyError as e:
    st.error(f"Column missing: {str(e)}. Please check your CSV file.")

# Workers Distribution Plot
rural_cols = ['main_workers_rural_persons', 'main_workers_rural_males', 'main_workers_rural_females']
urban_cols = ['main_workers_urban_persons', 'main_workers_urban_males', 'main_workers_urban_females']

rural_data = state_data[rural_cols].sum().values
urban_data = state_data[urban_cols].sum().values

fig, ax = plt.subplots()
ax.bar(['Rural', 'Urban'], [sum(rural_data), sum(urban_data)], color=['#1f77b4', '#ff7f0e'])
ax.set_title(f"{selected_state} - Rural vs Urban Workers")
st.pyplot(fig)

# Geo-Map Visualization
folium_map = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
marker_cluster = MarkerCluster().add_to(folium_map)

for idx, row in state_data.iterrows():
    lat, lon = row['latitude'], row['longitude']
    total_workers = row['main_workers_total_persons']
    popup_text = f"State: {selected_state}<br>District: {row['District']}<br>Total Workers: {total_workers}"
    folium.Marker([lat, lon], popup=popup_text).add_to(marker_cluster)

st_folium(folium_map)
