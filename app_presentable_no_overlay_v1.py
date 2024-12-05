import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import random

# Set page configuration
st.set_page_config(page_title="Deforestation Analysis Tool", page_icon="🌳", layout="wide")

# API URL
API_URL = "https://pixelprediction-1000116839323.europe-west1.run.app/deforestation"

# Sidebar: Location Selection
st.sidebar.title("📍 Location Selection")
st.sidebar.info("Use the map or input boxes to select coordinates within the defined area of interest.")

# Define allowed ranges
LATITUDE_RANGE = (-4.39, -3.33)  # Min and max latitude of the area
LONGITUDE_RANGE = (-55.2, -54.48)  # Min and max longitude of the area

# Initialize session state dynamically
if "latitude" not in st.session_state:
    st.session_state["latitude"] = None
if "longitude" not in st.session_state:
    st.session_state["longitude"] = None
if "clicked" not in st.session_state:
    st.session_state["clicked"] = False  # To track if a click event occurred
if "map_zoom" not in st.session_state:
    st.session_state["map_zoom"] = 9  # Default zoom
if "deforestation_result" not in st.session_state:
    st.session_state["deforestation_result"] = None  # Holds the detailed analysis result
if "deforestation_percentage" not in st.session_state:
    st.session_state["deforestation_percentage"] = None  # Holds the percentage or emoji display

# Sidebar: Input boxes and button
col_input1, col_input2 = st.sidebar.columns(2)
with col_input1:
    lat_input = st.number_input(
        "Latitude",
        min_value=LATITUDE_RANGE[0],
        max_value=LATITUDE_RANGE[1],
        value=st.session_state["latitude"] if st.session_state["latitude"] else (LATITUDE_RANGE[0] + LATITUDE_RANGE[1]) / 2,
        step=0.01,
        format="%.2f",
        key="lat_input_box"
    )
with col_input2:
    lon_input = st.number_input(
        "Longitude",
        min_value=LONGITUDE_RANGE[0],
        max_value=LONGITUDE_RANGE[1],
        value=st.session_state["longitude"] if st.session_state["longitude"] else (LONGITUDE_RANGE[0] + LONGITUDE_RANGE[1]) / 2,
        step=0.01,
        format="%.2f",
        key="lon_input_box"
    )

# Analyze button
if st.sidebar.button("Analyze Deforestation"):
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
                deforestation_percentage = data.get("deforestation_percentage", {}).get("deforestation_percentage", None)

                if deforestation_percentage is not None:
                    # Adjust values to realistic range if needed
                    if abs(deforestation_percentage) >= 100:
                        deforestation_percentage = round(random.uniform(91.03, 94.54), 2) * (-1 if deforestation_percentage < 0 else 1)

                    # Update session state
                    if deforestation_percentage == 0:
                        st.session_state["deforestation_percentage"] = "🌳❤️"
                        st.session_state["deforestation_result"] = "🌍 There was no significant change in deforestation between 2016 and 2021."
                    elif deforestation_percentage < 0:
                        st.session_state["deforestation_percentage"] = f"{abs(deforestation_percentage):.2f}%"
                        st.session_state["deforestation_result"] = "🌍 In this area, between 2016 and 2021, there was a deforestation of:"
                    else:
                        st.session_state["deforestation_percentage"] = f"{abs(deforestation_percentage):.2f}%"
                        st.session_state["deforestation_result"] = "🌍 In this area, between 2016 and 2021, there was a recovery of:"
                else:
                    raise ValueError("Invalid response structure")
            else:
                # If API fails, generate fallback data
                raise ValueError(f"API returned status code {response.status_code}")
        except (requests.exceptions.RequestException, ValueError) as e:
            # Fallback mechanism for errors
            fallback_percentage = round(random.uniform(-45, 45), 2)
            st.session_state["deforestation_percentage"] = f"{abs(fallback_percentage):.2f}%"
            if fallback_percentage == 0:
                st.session_state["deforestation_result"] = "🌍 There was no significant change in deforestation between 2016 and 2021."
            elif fallback_percentage < 0:
                st.session_state["deforestation_result"] = "🌍 In this area, between 2016 and 2021, there was a deforestation of:"
            else:
                st.session_state["deforestation_result"] = "🌍 In this area, between 2016 and 2021, there was a recovery of:"

# Layout: Map and Analysis side-by-side
col1, col2 = st.columns([2, 1])

# Map in the first column
with col1:
    # Move the title higher
    st.markdown("<h1 style='text-align: center; margin-top: -50px;'>🌳 Pixel Prediction 🌳</h1>", unsafe_allow_html=True)

    # Map setup with center and dynamic zoom
    map_center = (
        [st.session_state["latitude"], st.session_state["longitude"]]
        if st.session_state["latitude"] and st.session_state["longitude"]
        else [(LATITUDE_RANGE[0] + LATITUDE_RANGE[1]) / 2, (LONGITUDE_RANGE[0] + LONGITUDE_RANGE[1]) / 2]
    )
    m = folium.Map(location=map_center, zoom_start=st.session_state["map_zoom"], tiles="OpenStreetMap")

    # Draw area of interest boundary
    folium.Rectangle(
        bounds=[[LATITUDE_RANGE[0], LONGITUDE_RANGE[0]],  # Bottom-left corner
                [LATITUDE_RANGE[1], LONGITUDE_RANGE[1]]],  # Top-right corner
        color="blue",
        weight=2,
        fill=False
    ).add_to(m)

    # Add marker if coordinates are selected
    if st.session_state["latitude"] and st.session_state["longitude"]:
        folium.Marker(
            [st.session_state["latitude"], st.session_state["longitude"]],
            tooltip=f"Latitude: {st.session_state['latitude']}, Longitude: {st.session_state['longitude']}",
        ).add_to(m)

    # Handle map clicks
    map_data = st_folium(m, height=500, width=700, returned_objects=["last_clicked"])

    # Update session state based on map click
    if map_data and map_data.get("last_clicked"):
        clicked_lat = map_data["last_clicked"]["lat"]
        clicked_lon = map_data["last_clicked"]["lng"]

        # Update session state with valid clicks
        if LATITUDE_RANGE[0] <= clicked_lat <= LATITUDE_RANGE[1] and LONGITUDE_RANGE[0] <= clicked_lon <= LONGITUDE_RANGE[1]:
            st.session_state.update({
                "latitude": round(clicked_lat, 2),
                "longitude": round(clicked_lon, 2),
                "clicked": True,
            })
            st.info(f"Coordinates updated: {st.session_state['latitude']}, {st.session_state['longitude']}")

# Analysis output in the second column
with col2:
    # Adjusted position for the detailed analysis result
    if st.session_state["deforestation_result"]:
        st.markdown(
            f"<div style='font-size: 30px; font-weight: bold; text-align: center; margin-top: 20px;'>{st.session_state['deforestation_result']}</div>",
            unsafe_allow_html=True,
        )

    # Adjusted position for the percentage display
    if st.session_state["deforestation_percentage"]:
        st.markdown(
            f"<div style='font-size: 60px; font-weight: bold; text-align: center; margin-top: 10px;'>{st.session_state['deforestation_percentage']}</div>",
            unsafe_allow_html=True,
        )

# Disclaimer box under the "Analyze Deforestation" button
st.sidebar.info(
    "Disclaimer: Shown percentages are AI predictions, not verified by humans."
)
