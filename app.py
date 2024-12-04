import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

# Set page configuration
st.set_page_config(page_title="Deforestation Analysis Tool", page_icon="🌳", layout="wide")

# API URL
API_URL = "https://pixel-prediction-1000116839323.europe-west1.run.app/deforestation"

# Header
st.title("🌳 Deforestation Analysis Tool")
st.markdown("Analyze deforestation trends in the Amazon region by selecting coordinates within the defined area of interest.")

# About Section
st.subheader("🌱 About This Tool")
st.markdown(
    """
    This tool provides insights into deforestation trends in the Amazon rainforest, a critical ecosystem for global climate regulation, biodiversity,
    and the livelihoods of indigenous communities. By selecting coordinates within a defined area of interest, you can access data on deforestation
    percentage changes over time. Understanding these patterns is essential for driving effective conservation strategies and mitigating climate change impacts.
    """
)

# Sidebar for input
st.sidebar.title("📍 Location Selection")
st.sidebar.info("Use the sliders to select a location within the defined area of interest.")

# Define allowed ranges
LATITUDE_RANGE = (-4.39, -3.33)
LONGITUDE_RANGE = (-55.2, -54.48)

# Initialize session state
if "latitude" not in st.session_state:
    st.session_state["latitude"] = -3.85
if "longitude" not in st.session_state:
    st.session_state["longitude"] = -54.84

# Sliders for latitude and longitude
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

# Update session state with slider values
st.session_state["latitude"] = latitude
st.session_state["longitude"] = longitude

# Layout: Map and Analysis side-by-side
col1, col2 = st.columns([2, 1])

# Map in the first column
with col1:
    # Map setup
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

    # Marker for the selected location
    folium.Marker(
        [st.session_state["latitude"], st.session_state["longitude"]],
        tooltip=f"Latitude: {st.session_state['latitude']}, Longitude: {st.session_state['longitude']}"
    ).add_to(m)

    # Display the map
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

    # Analyze button
    if st.button("Analyze Deforestation"):
        with st.spinner("Analyzing deforestation trends..."):
            try:
                # Make API request
                payload = {
                    "latitude": st.session_state["latitude"],
                    "longitude": st.session_state["longitude"]
                }
                response = requests.post(API_URL, json=payload, timeout=30)

                # Handle responses
                if response.status_code == 200:
                    data = response.json()
                    deforestation_percentage = data.get("deforestation_percentage", {}).get("deforestation_percentage", "Unknown")

                    if deforestation_percentage == "Unknown":
                        st.warning("Unexpected API response structure.")
                    elif isinstance(deforestation_percentage, (int, float)):
                        st.success(f"🌍 In this area, there was a **{deforestation_percentage:.2f}%** increase in deforestation.")
                    else:
                        st.warning(f"Deforestation data unavailable: {data.get('message', 'Unknown error')}")

                elif response.status_code == 404:
                    st.warning(f"No data available for the selected coordinates: {latitude}, {longitude}.")

                else:
                    st.error(f"API Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}")

            except requests.exceptions.RequestException as e:
                st.error(f"Error communicating with the API: {e}")
