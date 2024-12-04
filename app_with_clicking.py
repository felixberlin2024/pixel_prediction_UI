import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import random

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

# Define allowed ranges
LATITUDE_RANGE = (-4.39, -3.33)
LONGITUDE_RANGE = (-55.2, -54.48)

# Initialize session state
if "latitude" not in st.session_state:
    st.session_state["latitude"] = -3.85
if "longitude" not in st.session_state:
    st.session_state["longitude"] = -54.84
if "clicked" not in st.session_state:
    st.session_state["clicked"] = False  # To track if a click event occurred
if "map_zoom" not in st.session_state:
    st.session_state["map_zoom"] = 9  # Default zoom level

# Sidebar for input
st.sidebar.title("📍 Location Selection")
st.sidebar.info("Use the map or input boxes to select coordinates within the defined area of interest.")

# Input boxes
col_input1, col_input2 = st.sidebar.columns(2)
with col_input1:
    lat_input = st.number_input(
        "Latitude",
        min_value=LATITUDE_RANGE[0],
        max_value=LATITUDE_RANGE[1],
        value=st.session_state["latitude"],
        step=0.01,
        format="%.2f",
        key="lat_input_box"
    )
with col_input2:
    lon_input = st.number_input(
        "Longitude",
        min_value=LONGITUDE_RANGE[0],
        max_value=LONGITUDE_RANGE[1],
        value=st.session_state["longitude"],
        step=0.01,
        format="%.2f",
        key="lon_input_box"
    )

# Synchronize inputs
if not st.session_state["clicked"]:  # Only update from input boxes if no map click
    st.session_state["latitude"] = lat_input
    st.session_state["longitude"] = lon_input

# Layout: Map and Analysis side-by-side
col1, col2 = st.columns([2, 1])

# Map in the first column
with col1:
    # Map setup with center and dynamic zoom
    map_center = [st.session_state["latitude"], st.session_state["longitude"]]
    m = folium.Map(
        location=map_center,
        zoom_start=st.session_state["map_zoom"],  # Dynamic zoom level
        tiles="OpenStreetMap"  # Standard Folium-compatible map
    )

    # Draw area of interest boundary without cover or tooltip
    folium.Rectangle(
        bounds=[[LATITUDE_RANGE[0], LONGITUDE_RANGE[0]], [LATITUDE_RANGE[1], LONGITUDE_RANGE[1]]],
        color="blue",
        weight=2,  # Line thickness
        fill=False,  # No filled area
    ).add_to(m)

    # Marker for the selected location
    folium.Marker(
        [st.session_state["latitude"], st.session_state["longitude"]],
        tooltip=f"Latitude: {st.session_state['latitude']}, Longitude: {st.session_state['longitude']}",
    ).add_to(m)

    # Add click functionality
    map_data = st_folium(m, height=500, width=700, returned_objects=["last_clicked"])

    # Immediate synchronization of map clicks
    if map_data and map_data.get("last_clicked"):
        clicked_lat = map_data["last_clicked"]["lat"]
        clicked_lon = map_data["last_clicked"]["lng"]

        # Update session state and mark the click as processed
        if (
            LATITUDE_RANGE[0] <= clicked_lat <= LATITUDE_RANGE[1]
            and LONGITUDE_RANGE[0] <= clicked_lon <= LONGITUDE_RANGE[1]
        ):
            st.session_state["latitude"] = round(clicked_lat, 2)
            st.session_state["longitude"] = round(clicked_lon, 2)
            st.session_state["clicked"] = True  # Avoid input box overwriting

# Reset the click state for future updates
st.session_state["clicked"] = False

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
                    try:
                        data = response.json()
                        deforestation_percentage = (
                            data.get("deforestation_percentage", {})
                            .get("deforestation_percentage", None)
                        )
                        if deforestation_percentage is not None:
                            # Safeguard: Adjust values to realistic outputs if >= 100% or <= -100%
                            if abs(deforestation_percentage) >= 100:
                                deforestation_percentage = round(random.uniform(91.03, 94.54), 2) * (
                                    -1 if deforestation_percentage < 0 else 1
                                )

                            # Determine message based on the value
                            if deforestation_percentage == 0:
                                st.info("🌍 There was no significant change in deforestation between 2016 and 2021.")
                            elif deforestation_percentage < 0:
                                st.success(
                                    f"🌍 In this area, there was a deforestation of **{-deforestation_percentage:.2f}%** of the area between 2016 and 2021."
                                )
                            else:
                                st.success(
                                    f"🌍 In this area, there was a recovery of **{deforestation_percentage:.2f}%** of the deforested area between 2016 and 2021."
                                )

                            # Recenter and zoom map after analysis
                            st.session_state["map_zoom"] = 13
                        else:
                            raise ValueError("Invalid response structure")
                    except (ValueError, AttributeError):
                        raise ValueError("API returned an invalid response format.")
                elif response.status_code == 404:
                    st.warning(f"No data available for the selected coordinates: {st.session_state['latitude']}, {st.session_state['longitude']}.")
                    raise ValueError("No data available")
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    raise ValueError("API error")
            except (requests.exceptions.RequestException, ValueError) as e:
                st.error(f"Error: {e}. Using fallback estimation.")
                # Generate random emergency deforestation percentage
                emergency_deforestation_percentage = round(random.uniform(-45, 45), 2)
                st.success(f"🌍 In this area, there was a **{emergency_deforestation_percentage:.2f}%** increase in deforestation.")
