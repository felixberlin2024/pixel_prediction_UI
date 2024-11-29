import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

# Set page configuration
st.set_page_config(layout="wide", page_title="Deforestation Analysis")

# Header
st.title("Deforestation Analysis Tool")

# Sidebar for displaying clicked coordinates
st.sidebar.title("Selected Coordinates")
st.sidebar.info("Click on the map to select a location. The coordinates will be used to analyze deforestation trends.")

# Initialize state for clicked coordinates
if "clicked_coords" not in st.session_state:
    st.session_state["clicked_coords"] = {"latitude": None, "longitude": None}

# Main content area
st.subheader("Select a Location on the Map")

# Create a Folium map centered at a default location
default_center = [-3.4653, -62.2159]  # Default coordinates
m = folium.Map(location=default_center, zoom_start=4)

# Add an event listener for clicks
map_data = st_folium(m, height=500, returned_objects=["last_clicked"])

# Update session state with the clicked coordinates
if map_data and map_data.get("last_clicked"):
    st.session_state["clicked_coords"] = {
        "latitude": map_data["last_clicked"]["lat"],
        "longitude": map_data["last_clicked"]["lng"]
    }

# Display the selected coordinates and fetch deforestation data
latitude = st.session_state["clicked_coords"]["latitude"]
longitude = st.session_state["clicked_coords"]["longitude"]

if latitude is not None and longitude is not None:
    # Display rounded coordinates
    st.write(f"**Latitude:** {round(latitude, 2)}")
    st.write(f"**Longitude:** {round(longitude, 2)}")

    # Call the FastAPI service with the full-precision coordinates
    st.write("Analyzing deforestation trends in this area...")
    try:
        # Define the API endpoint
        api_url = "http://127.0.0.1:8000/deforestation/" #http://host.docker.internal:8000/predict"




        # Send the GET request to FastAPI
        response = requests.get(api_url, params={"lat": latitude, "lon": longitude})
        st.write(response.status_code)

        # Handle the API response
        if response.status_code == 200:
            # Parse the API response data
            data = response.json()
            deforestation_percentage = data ["deforestation_percentage"]

            # Display the deforestation percentage
            st.success(f"In this area, there was a {deforestation_percentage}% increase in deforestation.")
        else:
            st.error("Failed to retrieve analysis data from the API.")
    except Exception as e:
        st.error(f"Error communicating with the API: {e}")
else:
    st.write("Click on the map to select a location.")
