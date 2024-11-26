# app.py
import streamlit as st
import io
from PIL import Image
import plotly.express as px
import folium
from streamlit_folium import folium_static

# Set page configuration
st.set_page_config(layout="wide", page_title="Pixel Prediction")

# Header
st.title("Pixel Prediction Tool: Deforestation Monitoring")

# Sidebar for additional settings and coordinates input
st.sidebar.title("Settings & Upload")
st.sidebar.info("Upload an image and enter location coordinates to monitor deforestation.")

# Image upload and coordinates input
uploaded_file = st.sidebar.file_uploader("Upload an image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

# Set default coordinates for the Amazon area
latitude = st.sidebar.number_input("Enter Latitude:", min_value=-90.0, max_value=90.0, value=-3.4653)
longitude = st.sidebar.number_input("Enter Longitude:", min_value=-180.0, max_value=180.0, value=-62.2159)

# Display message if no file is uploaded
if uploaded_file is None:
    st.sidebar.warning("Please upload an image to proceed.")

# Main content area
col1, col2 = st.columns([3, 1])

# Main content area (left column)
with col1:
    # Create a placeholder for the image display
    image_placeholder = st.empty()

    if uploaded_file is not None:
        # Read the file and display the image
        image = Image.open(uploaded_file)
        image_placeholder.image(image, caption="Uploaded Image", use_column_width=True)

        # Placeholder for deforestation count (this would be calculated by your ML model)
        deforested_trees = 100  # Placeholder value
        st.write(f"### Estimated Number of Deforested Trees: {deforested_trees}")

        # Example of a bar chart (simulating results)
        fig = px.bar(x=["Forest", "Deforested"], y=[80, 20], labels={'x': 'Land Type', 'y': 'Percentage'})
        st.plotly_chart(fig)

# Measurement tool (right column)
with col2:
    st.subheader("Deforestation in Percentage")

    # Placeholder for deforestation percentage (this would be calculated by your ML model)
    deforestation_percentage = 25  # Placeholder value

    # Create a progress bar to represent the deforestation percentage
    st.progress(deforestation_percentage)
    st.write(f"Deforestation: {deforestation_percentage}%")

# Interactive Map for showing the location of the image
if latitude != 0.0 and longitude != 0.0:
    st.subheader("Image Location on Map")

    # Create map centered around the given coordinates
    map_center = [latitude, longitude]
    m = folium.Map(location=map_center, zoom_start=4)

    # Add a marker for the coordinates
    folium.Marker([latitude, longitude], popup=f"Location: {latitude}, {longitude}").add_to(m)

    # Display the map in Streamlit
    folium_static(m)

# Information note at the bottom
st.info("This is a placeholder. The actual deforestation analysis will be powered by your ML model.")
