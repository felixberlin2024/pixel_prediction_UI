import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

# Set page configuration
st.set_page_config(page_title="Deforestation Analysis Tool", page_icon="🌳", layout="wide")

# Define API endpoint
API_URL = "http://127.0.0.1:8000/deforestation/"

# Header
st.title("🌳 Deforestation Analysis Tool")
st.markdown("Analyze deforestation trends in the Amazon region by selecting coordinates within the defined area of interest.")

# **Placeholder Section: About the Tool**
st.subheader("🌱 About This Tool")
st.markdown(
    """
    This tool allows you to analyze deforestation trends in the Amazon region. By selecting coordinates within a defined area of interest,
    you can access data on the percentage increase in deforestation in specific locations. The Amazon rainforest plays a critical role
    in regulating the Earth's climate, preserving biodiversity, and supporting indigenous communities. Understanding deforestation patterns
    is crucial for developing effective conservation strategies and mitigating the impacts of climate change.
    """
)

# Sidebar for input
st.sidebar.title("📍 Location Selection")
st.sidebar.info("Use the sliders to select a location within the defined area of interest.")

# Define allowed ranges
LATITUDE_RANGE = (-4.39, -3.33)
LONGITUDE_RANGE = (-55.2, -54.48)  # Corrected longitude range

# Initialize session state
if "latitude" not in st.session_state:
    st.session_state["latitude"] = -3.85
if "longitude" not in st.session_state:
    st.session_state["longitude"] = -54.84

# Sliders
latitude = st.sidebar.slider(
    "Latitude",
    LATITUDE_RANGE[0],
    LATITUDE_RANGE[1],
    value=st.session_state["latitude"],
    step=0.01,
    key="latitude_slider"
)
longitude = st.sidebar.slider(
    "Longitude",
    LONGITUDE_RANGE[0],
    LONGITUDE_RANGE[1],
    value=st.session_state["longitude"],
    step=0.01,
    key="longitude_slider"
)

# Update session state
st.session_state["latitude"] = latitude
st.session_state["longitude"] = longitude

# Layout: Map and Analysis side-by-side
col1, col2 = st.columns([2, 1])  # Adjust column width ratios as needed

# Map in the first column
with col1:
    # Initial map setup
    initial_center = [(-4.39 + -3.33) / 2, (-55.2 + -54.48) / 2]
    initial_zoom = 9

    m = folium.Map(location=initial_center, zoom_start=initial_zoom)

    # Draw area of interest
    folium.Rectangle(
        bounds=[[-4.39, -55.2], [-3.33, -54.48]],
        color="blue",
        fill=True,
        fill_opacity=0.1,
        tooltip="Area of Interest"
    ).add_to(m)

    # Marker for selected location
    folium.Marker(
        [st.session_state["latitude"], st.session_state["longitude"]],
        tooltip=f"Latitude: {st.session_state['latitude']}, Longitude: {st.session_state['longitude']}"
    ).add_to(m)

    # Display map
    st_folium(m, height=500, width=700)

# Analysis in the second column
with col2:
    st.subheader("📊 Deforestation Analysis")
    st.markdown(
        f"""
        **Selected Coordinates**:
        - **Latitude**: `{st.session_state['latitude']}`
        - **Longitude**: `{st.session_state['longitude']}`
        """
    )

    try:
        with st.spinner("Analyzing deforestation trends in this area..."):
            # Call API
            response = requests.get(API_URL, params={
                "lat": st.session_state["latitude"],
                "lon": st.session_state["longitude"]
            })

            if response.status_code == 200:
                data = response.json()
                deforestation_percentage = data.get("deforestation_percentage", "Unknown")
                st.success(f"🌍 In this area, there was a **{deforestation_percentage}%** increase in deforestation.")
            else:
                st.error(f"Failed to retrieve analysis data. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error communicating with the API: {e}")
