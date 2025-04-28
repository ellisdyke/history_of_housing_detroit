import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import geopandas as gpd
import requests
import io

st.set_page_config(layout="wide")
st.title("DLBA Sales and Re-Occupancy in Detroit (2014–2024) with HOLC Redlining Overlay")

@st.cache_data
def load_data():
    # Load DLBA-owned properties
    dlba_raw = pd.read_csv("DLBA_Owned_Properties_-7235192583433363849.csv", dtype={'Parcel Number': str})
    dlba_raw['Parcel Number'] = dlba_raw['Parcel Number'].str.replace(r'\.', '', regex=True)
    dlba = dlba_raw.dropna(subset=['Longitude', 'Latitude'])
    dlba_owned = pd.DataFrame({
        'x': dlba['Longitude'],
        'y': dlba['Latitude'],
    })

    # Load DLBA sales (from Google Drive link)
    url = "https://drive.google.com/uc?export=download&id=1Wg_R89wbJtmNWt2okMoljNZijQcZmeC7"
    sales_raw = pd.read_csv(url, dtype={'Parcel Number': str})
    sales_raw['Parcel Number'] = sales_raw['Parcel Number'].str.replace(r'\.', '', regex=True)
    sales_raw['Sale Date'] = pd.to_datetime(sales_raw['Sale Date'], errors='coerce')
    sales = sales_raw.dropna(subset=['Sale Date', 'x', 'y'])
    sales = sales[sales['Sale Date'].dt.year.between(2014, 2024)]
    sales['Year'] = sales['Sale Date'].dt.year.astype(str)

    # Load Certificate of Occupancy
    coo_raw = pd.read_csv("CertificateOfOccupancy_4256029621510488921.csv", dtype={'Parcel ID': str})
    coo_raw['Parcel ID'] = coo_raw['Parcel ID'].str.replace(r'\.', '', regex=True)
    coo_raw['Status Date'] = pd.to_datetime(coo_raw['Status Date'], errors='coerce')
    coo = coo_raw.dropna(subset=['Status Date', 'Longitude', 'Latitude'])
    coo = coo[coo['Status Date'].dt.year.between(2014, 2024)]
    coo['Year'] = coo['Status Date'].dt.year.astype(str)

    return dlba_owned, sales, coo

@st.cache_data
def load_holc_data():
    # Fetch HOLC Redlining data
    url = "https://services.arcgis.com/jIL9msH9OI208GCb/arcgis/rest/services/HOLC_Neighborhood_Redlining/FeatureServer/0/query"
    params = {
        'where': "ST='MI'",
        'outFields': '*',
        'f': 'geojson'
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        gdf = gpd.read_file(io.StringIO(response.text))
        detroit_gdf = gdf[gdf['city'] == 'Detroit']
        return detroit_gdf
    else:
        return None

# Load all data
dlba_owned, sales, coo = load_data()
detroit_gdf = load_holc_data()

# Setup years and frames
years = [str(y) for y in range(2014, 2025)]
frames = []

for year in years:
    sales_subset = sales[sales['Year'] == year]
    coo_persistent = coo[coo['Status Date'].dt.year.astype(str) <= year]

    frame = go.Frame(
        name=year,
        data=[
            go.Scattermapbox(
                lat=sales_subset['y'],
                lon=sales_subset['x'],
                mode='markers',
                marker=dict(size=5, color='orange', opacity=0.3),
                name='DLBA Sale'
            ),
            go.Scattermapbox(
                lat=coo_persistent['Latitude'],
                lon=coo_persistent['Longitude'],
                mode='markers',
                marker=dict(size=5, color='green', opacity=0.7),
                name='Occupied (CofO)'
            )
        ]
    )
    frames.append(frame)

# Base data layers
data_layers = [
    go.Scattermapbox(
        lat=[], lon=[], mode='markers',
        marker=dict(size=5, color='orange', opacity=0.3),
        name='DLBA Sale'
    ),
    go.Scattermapbox(
        lat=[], lon=[], mode='markers',
        marker=dict(size=9, color='green', opacity=1),
        name='Occupied (CofO)'
    ),
    go.Scattermapbox(
        lat=dlba_owned['y'],
        lon=dlba_owned['x'],
        mode='markers',
        marker=dict(size=3, color='gray', opacity=0.08),
        name='Still DLBA-Owned',
        hoverinfo='skip',
        showlegend=False
    )
]

# Add HOLC polygons if available
if detroit_gdf is not None:
    holc_color_map = {
        'A': ('#00A86B', 1),
        'B': ('#0067A5', 2),
        'C': ('#FFBF00', 3),
        'D': ('#F04923', 4)
    }
    grade_legend_included = set()

    for _, row in detroit_gdf.iterrows():
        if row.geometry.geom_type == "Polygon":
            coords = list(row.geometry.exterior.coords)
            grade = row['HOLC_grade']
            fillcolor, rank = holc_color_map.get(grade, ('#000000', 100))
            fillcolor_rgba = f"rgba{tuple(int(fillcolor.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}"

            data_layers.append(
                go.Scattermapbox(
                    lon=[point[0] for point in coords],
                    lat=[point[1] for point in coords],
                    mode='lines',
                    fill='toself',
                    fillcolor=fillcolor_rgba,
                    line=dict(width=0),
                    name=f"HOLC Area - Grade {grade}",
                    showlegend=(grade not in grade_legend_included),
                    legendrank=rank,
                    hoverinfo='skip'
                )
            )
            grade_legend_included.add(grade)

# Create final figure
fig = go.Figure(
    data=data_layers,
    layout=go.Layout(
        title="DLBA Sales and Re-Occupancy in Detroit (2014–2024) with HOLC Overlay",
        mapbox_style="carto-positron",
        mapbox_zoom=10,
        mapbox_center={"lat": 42.36, "lon": -83.1},
        height=700,
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 800, "redraw": True}, "fromcurrent": True}],
                 "label": "▶️ Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0}, "mode": "immediate", "transition": {"duration": 0}}], "label": "⏹️ Pause", "method": "animate"}
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 75},
            "showactive": True,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }],
        sliders=[{
            "steps": [ {
                "args": [[year], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                "label": year,
                "method": "animate"
            } for year in years],
            "transition": {"duration": 300},
            "x": 0.1,
            "len": 0.9,
            "xanchor": "left",
            "y": 0,
            "yanchor": "top"
        }]
    ),
    frames=frames
)

st.plotly_chart(fig, use_container_width=True)
