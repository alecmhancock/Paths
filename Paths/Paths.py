import streamlit as st
import requests as rq
import pandas as pd
from datetime import datetime
import pytz
import shapely
from shapely import wkt
from shapely.geometry import Polygon

st.title('Live Storm Data Visualization')

# Tab setup
tab1, tab2 = st.tabs(["Event List", "Map"])

# API callout and modify to dict
apiurl = "https://api.weather.gov/alerts/active/"
response = rq.get(apiurl, headers={"PATHSWX": "ALPHA"})
NwsDict =  response.json()

# var definitions for event totals
total = 0
activeTotal = 0

# User preference vars
descriptions = False
torWar = False
floWar = False
sevtWar = False
spWeather = False
expFilter = False

# Data vars
torCount = 0
floCount = 0
spCount = 0
sevtCount = 0
bar_data = {}
map_data = []
point_list = []

# Reusable Well Known Text (WKT) converter for polygons
def convert_to_wkt(coordinates):
    polygon = Polygon(coordinates)
    wkt = polygon.wkt
    return wkt

# Stripping WKT format to send point back to list
def convert_to_list(wkt_point):
    coordinates = wkt_point.strip('POINT ()').split()
    coordinates = [float(coord) for coord in coordinates]
    return coordinates


# Get time for expiration filtering, convert to ISO format for comparison
dttemp = datetime.now().isoformat()
current_dateTime = datetime.fromisoformat(dttemp)
utc=pytz.UTC
current_dateTime = utc.localize(current_dateTime)


# User preference checkboxes
with st.sidebar:
    if st.checkbox('Show Tornado Warnings'):
        torWar = True
        bar_data.update({"Tornado Warnings":[torCount]})
    if st.checkbox('Show Flood Warnings'):
        floWar = True
        bar_data.update({"Flood Warnings":[floCount]})
    if st.checkbox('Show Severe Thunderstorm Warnings'):
        sevtWar = True
        bar_data.update({"Severe Thunderstorms":[sevtCount]})
    if st.checkbox('Show Special Weather Statements'):
        spWeather = True
        bar_data.update({"Special Weather Statements":[spCount]})
    if st.checkbox('Show Descriptions'):
        descriptions = True
    if st.checkbox('Filter Expired'):
        expFilter = True


# Totals and geometries for all events
for feature in NwsDict["features"]:
    total += 1

    if feature["properties"]["event"] == "Tornado Warning" and feature["geometry"] is not None:
        torCount += 1
        activeTotal += 1
        if torWar == True:
            bar_data.update({"Tornado Warnings":[torCount]})
            coordlist = feature["geometry"]["coordinates"]
            for sublist in coordlist:
                map_data.append(sublist)

    if feature["properties"]["event"] == "Special Weather Statement" and feature["geometry"] is not None:
        spCount += 1
        activeTotal += 1
        if spWeather == True:
            bar_data.update({"Special Weather Statements":[spCount]})
            coordlist = feature["geometry"]["coordinates"]
            for sublist in coordlist:
                map_data.append(sublist)

    if feature["properties"]["event"] == "Flood Warning" and feature["geometry"] is not None:
        floCount += 1
        activeTotal += 1
        if floWar == True:
            bar_data.update({"Flood Warnings":[floCount]})
            coordlist = feature["geometry"]["coordinates"]
            for sublist in coordlist:
                map_data.append(sublist)

    if feature["properties"]["event"] == "Severe Thunderstorm Warning" and feature["geometry"] is not None:
        sevtCount += 1
        activeTotal += 1
        if sevtWar == True:
            bar_data.update({"Severe Thunderstorms":[sevtCount]})
            coordlist = feature["geometry"]["coordinates"]
            for sublist in coordlist:
                map_data.append(sublist)

    if feature["properties"]["status"] == "Test":
        total -= 1


# Map logic, polygon centroid finder
for element in map_data:
    elementwkt = convert_to_wkt(element)
    pointload = wkt.loads(elementwkt)
    pointWKT = pointload.centroid.wkt
    point = convert_to_list(pointWKT)
    point_list.append(point)

# Console check, just to make sure things are working right
print(len(point_list))
print(point_list)

with tab2:
    mapDF = pd.DataFrame(point_list, columns=['lon', 'lat'])
    st.map(mapDF)


#df = pd.DataFrame(bar_data)
#st.bar_chart(df)

# Headline and description section

# Tornado Warnings
with tab1:
    if torWar == True:
        st.title('Tornado Warnings')
        for feature in NwsDict["features"]:
            if expFilter == True:
                expiryTime = datetime.fromisoformat(feature["properties"]["expires"])
                if feature["properties"]["event"] == "Tornado Warning" and expiryTime > current_dateTime:
                    st.subheader(feature['properties']['headline'])
                    if descriptions == True:
                        st.subheader('Description:')
                        st.text(feature['properties']['description'])
                        st.divider()
            else:
                if feature["properties"]["event"] == "Tornado Warning":
                    st.subheader(feature['properties']['headline'])
                    if descriptions == True:
                        st.subheader('Description:')
                        st.text(feature['properties']['description'])
                        st.divider()

    # Flood Warnings
    if floWar == True:
        st.title('Flood Warnings')
        for feature in NwsDict["features"]:
            if expFilter == True:
                if "+" in feature["properties"]["expires"]:
                    expiryTime = datetime.fromisoformat(feature["properties"]["expires"])
                if feature["properties"]["event"] == "Flood Warning" and expiryTime > current_dateTime:
                    st.subheader(feature['properties']['headline'])
                    if descriptions == True:
                        st.subheader('Description:')
                        st.text(feature['properties']['description'])
                        st.divider()
            else:
                if feature["properties"]["event"] == "Flood Warning":
                    st.subheader(feature['properties']['headline'])
                    if descriptions == True:
                        st.subheader('Description:')
                        st.text(feature['properties']['description'])
                        st.divider()

    # Special Weather Statements
    if spWeather == True:
        st.title('Special Weather Statements')
        for feature in NwsDict["features"]:
            if expFilter == True:
                expiryTime = datetime.fromisoformat(feature["properties"]["expires"])
                if feature["properties"]["event"] == "Special Weather Statement" and expiryTime > current_dateTime:
                        st.subheader(feature['properties']['headline'])
                        if descriptions == True:
                            st.subheader('Description:')
                            st.text(feature['properties']['description'])
                            st.divider()
            else:
                if feature["properties"]["event"] == "Special Weather Statement":
                    st.subheader(feature['properties']['headline'])
                    if descriptions == True:
                        st.subheader('Description:')
                        st.text(feature['properties']['description'])
                        st.divider()

    #Severe Thunderstorm Warnings
    if sevtWar == True:
        st.title('Severe Thunderstorm Warnings')
        for feature in NwsDict["features"]:
            if expFilter == True:
                expiryTime = datetime.fromisoformat(feature["properties"]["expires"])
                if feature["properties"]["event"] == "Severe Thunderstorm Warning" and expiryTime > current_dateTime:
                    st.subheader(feature['properties']['headline'])
                    if descriptions == True:
                        st.subheader('Description:')
                        st.text(feature['properties']['description'])
            else:
                if feature["properties"]["event"] == "Severe Thunderstorm Warning":
                    st.subheader(feature['properties']['headline'])
                    if descriptions == True:
                        st.subheader('Description:')
                        st.text(feature['properties']['description'])



st.header(f"\nTotal active severe storm events: {activeTotal} out of {total}")

coltor, colflo, colsevt, colsp = st.columns(4)

coltor.metric("Tornado Warnings", torCount)
colflo.metric("Flood Warnings", floCount)
colsevt.metric("Severe T.storm Warnings", sevtCount)
colsp.metric("Special Weather Statements", spCount)