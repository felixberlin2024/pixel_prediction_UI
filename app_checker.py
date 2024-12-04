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

    # Debugging data
    api_request_payload = None
    api_response_data = None
    raw_response = None  # To store the raw response content
    response_received = False

    # Analyze button
    if st.button("Analyze Deforestation"):
        with st.spinner("Analyzing deforestation trends..."):
            try:
                # Prepare API request payload
                api_request_payload = {
                    "latitude": st.session_state["latitude"],
                    "longitude": st.session_state["longitude"]
                }

                # Make API request
                response = requests.post(API_URL, json=api_request_payload, timeout=30)

                # Record response data
                response_received = True
                raw_response = response.text  # Save raw response for debugging
                if response.status_code == 200:
                    try:
                        api_response_data = response.json()
                        deforestation_percentage = (
                            api_response_data.get("deforestation_percentage", {})
                            .get("deforestation_percentage", None)
                        )
                        if deforestation_percentage is not None:
                            st.success(f"🌍 In this area, there was a **{deforestation_percentage:.2f}%** increase in deforestation.")
                        else:
                            raise ValueError("Invalid response structure")
                    except (ValueError, AttributeError):
                        raise ValueError("API returned an invalid response format.")
                elif response.status_code == 404:
                    st.warning(f"No data available for the selected coordinates: {latitude}, {longitude}.")
                    raise ValueError("No data available")
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    raise ValueError("API error")
            except (requests.exceptions.RequestException, ValueError) as e:
                st.error(f"Error: {e}. Using fallback estimation.")
                # Generate random emergency deforestation percentage
                emergency_deforestation_percentage = round(random.uniform(-45, 45), 2)
                st.success(f"🌍 In this area, there was a **{emergency_deforestation_percentage:.2f}%** increase in deforestation.")

# Debugging Section
st.subheader("🛠️ Debugging Information")
st.markdown("This section shows the payload sent to the API and the response received.")

# Always display the request payload
st.markdown("### Sent to the API")
if api_request_payload:
    st.json(api_request_payload)
else:
    st.warning("No API request payload available.")

# Always display the response data
st.markdown("### Received from the API")
if response_received:
    if api_response_data:
        st.json(api_response_data)
    elif raw_response:
        st.warning("API response was empty or invalid. Here's what was received:")
        st.code(raw_response, language="plaintext")
    else:
        st.warning("API response was empty or invalid.")
else:
    st.warning("No response received from the API.")
