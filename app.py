import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import base64

# OpenStreetMap API URL
OSM_API_URL = "https://overpass-api.de/api/interpreter"


streamlit_style = """
			<style>
			@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100&display=swap');

			html, body, [class*="css"]  {
			font-family: 'Roboto', sans-serif;
            font-size: 18px;
			}
			</style>
			"""
st.markdown(streamlit_style, unsafe_allow_html=True)

@st.cache
def get_fuel_stations(city):
    # Construct Overpass API query to retrieve fuel stations in the specified city
    query = f"""
    [out:json];
    area[name="{city}"];
    node(area)["amenity"="fuel"];
    out center;
    """
    # Send request to Overpass API
    response = requests.get(OSM_API_URL, params={"data": query})
    if response.status_code != 200:
        st.error("Failed to get data from the server. Please try again later.")
        return pd.DataFrame()
    
    # Parse response JSON
    data = response.json()

    # Extract relevant information from the response and store in a DataFrame
    stations = []
    for element in data["elements"]:
        name = element["tags"].get("name", "Unknown")
        latitude = element["lat"]
        longitude = element["lon"]

        stations.append({
            "Name": name,
            "Latitude": latitude,
            "Longitude": longitude,
        })

    return pd.DataFrame(stations)

def get_image_base64(image_path):
    # Convert image to base64 encoding
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

logo_image_path = "logo.png"
logo_image_base64 = get_image_base64(logo_image_path)


st.markdown(f'<p align="center"><img src="data:image/png;base64,{logo_image_base64}" width="350"></p>', unsafe_allow_html=True)


st.markdown('''
Witaj na interaktywnej mapie stacji paliw w Polsce! 💼 

Ta aplikacja umożliwia wyszukiwanie stacji paliw w dowolnym mieście w Polsce. Możesz również przeszukiwać stacje paliw na podstawie dostawcy paliwa. 

Zachęcamy do eksploracji!
''')


city = st.text_input("Podaj miasto:", placeholder="Enter city name here...")

if city:
    with st.spinner('Fetching data...'):
        df = get_fuel_stations(city)
    if df.empty:
        st.error("Nie znaleziono stacji paliw w podanym mieście.")
    else:
        search_term = st.text_input("Wyszukaj dostawców paliw:")
        
        # Filter the DataFrame based on the search term
        filtered_df = df[df["Name"].str.contains(search_term, case=False)]

        # Create the map using Mapbox
        fig = go.Figure()

        # Add scattermapbox trace for the fuel station locations
        fig.add_trace(go.Scattermapbox(
            lat=filtered_df["Latitude"],
            lon=filtered_df["Longitude"],
            mode="markers",
            marker=dict(
                size=10,
                color="red",
                symbol="circle"
            ),
            text=filtered_df["Name"],
            hoverinfo="text"
        ))

        # Set the layout for the map
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=filtered_df["Latitude"].mean(), lon=filtered_df["Longitude"].mean()),
                zoom=10
            )
        )

        
        st.plotly_chart(fig)

        # Show the filtered DataFrame as a table
        st.table(filtered_df[["Name"]])