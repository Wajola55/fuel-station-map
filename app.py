import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

OSM_API_URL = "https://overpass-api.de/api/interpreter"

def get_fuel_stations(city):
    query = f"""
    [out:json];
    area[name="{city}"];
    node(area)["amenity"="fuel"];
    out center;
    """
    response = requests.get(OSM_API_URL, params={"data": query})
    data = response.json()

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

st.title("Mapa Stacji Paliw")

st.markdown('''
Ta aplikacja pokazuje lokalizację stacji paliw w Polsce.
''')

city = st.text_input("Podaj miasto:")

if city:
    df = get_fuel_stations(city)

    if df.empty:
        st.error("Nie znaleziono stacji paliw w podanym mieście.")
    else:
        # Create the map using Mapbox
        fig = go.Figure()

        # Add scattermapbox trace for the fuel station locations
        fig.add_trace(go.Scattermapbox(
            lat=df["Latitude"],
            lon=df["Longitude"],
            mode="markers",
            marker=dict(
                size=10,
                color="red",
                symbol="circle"
            ),
            text=df["Name"],
            hoverinfo="text"
        ))

        # Set the layout for the map
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=df["Latitude"].mean(), lon=df["Longitude"].mean()),
                zoom=10
            )
        )

        # Display the map
        st.plotly_chart(fig)

        # Display the fuel providers
        st.header("Dostawcy paliwa")
        st.table(df["Name"])










