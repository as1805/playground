import streamlit as st
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import gspread
from google.oauth2.service_account import Credentials

# Function to calculate distance using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Function to fetch data from Google Sheets
def fetch_google_sheet(sheet_url, credentials_file):
    # Set up the Google Sheets API connection
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(credentials_file, scopes=scope)
    gc = gspread.authorize(credentials)
    
    # Open the Google Sheet by URL
    sheet = gc.open_by_url(sheet_url)
    worksheet = sheet.sheet1  # Assume data is in the first sheet
    data = worksheet.get_all_records()
    
    return pd.DataFrame(data)

# Streamlit UI
st.title("Distance Calculator from Google Sheets")

# Input: Google Sheet URL and Reference Location
sheet_url = st.text_input("Enter Google Sheet URL:")
credentials_file = "path/to/your/credentials.json"  # Replace with your service account JSON file
reference_city = st.text_input("Reference City:", value="Atlanta")
reference_lat = st.number_input("Reference Latitude:", value=33.7490)
reference_lon = st.number_input("Reference Longitude:", value=-84.3880)

if sheet_url and credentials_file:
    try:
        # Fetch data from Google Sheets
        data = fetch_google_sheet(sheet_url, credentials_file)

        # Ensure the data contains Latitude and Longitude columns
        if not {"Latitude", "Longitude", "City"}.issubset(data.columns):
            st.error("The Google Sheet must have 'City', 'Latitude', and 'Longitude' columns.")
        else:
            # Calculate distances
            data["Distance (km)"] = data.apply(
                lambda row: haversine(reference_lat, reference_lon, row["Latitude"], row["Longitude"]),
                axis=1
            )

            # Display results
            st.success(f"Data fetched successfully from {sheet_url}!")
            st.dataframe(data)

            # Optionally allow user to download results
            csv = data.to_csv(index=False)
            st.download_button(label="Download Results as CSV", data=csv, file_name="distances.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
