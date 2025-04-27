# Detroit Housing and DLBA Trends (1940–2024)

This repository contains two Streamlit apps exploring housing and demographic trends in Detroit:

1. **DLBA Sales and Re-Occupancy in Detroit (2014–2024)**  
   Visualizes property sales from the Detroit Land Bank Authority (DLBA), current DLBA-owned properties, and occupancy certificates issued between 2014 and 2024.

2. **Census Trends in Detroit (1940–2010)**  
   Explores historical changes in population demographics, homeownership rates, and housing values from U.S. Census data.

---

## Features

### DLBA Sales and Occupancy Visualizations
- Animated map of yearly DLBA sales
- Visualization of properties that received a Certificate of Occupancy
- Contextual layering of properties still owned by the DLBA

### Detroit Census Trends Visualizations
- Population trends over time by race and location
- Racial composition changes (Black and White populations over decades)
- Homeownership trends for Black and White residents
- Housing value trends by Black population percentage in different census tracts

---

## Files Required

### For DLBA Visualizations
- `app.py` (Streamlit app for DLBA visualizations)
- `DLBA_Owned_Properties_-7235192583433363849.csv`
- `Property_Sales_Detroit_-4801866508954663892.csv`
- `CertificateOfOccupancy_4256029621510488921.csv`

### For Detroit Census Visualizations
- `census_app.py` (Streamlit app for Census visualizations)
- `1940.csv`
- `1950.csv`
- `1960.csv`
- `1970.csv`
- `1980.csv`
- `1990.csv`
- `2000.csv`
- `2010.csv`

---

## Running the Apps

Install dependencies:

```bash
pip install -r requirements.txt


## Deployment

This app can be deployed on [Streamlit Cloud](https://streamlit.io/cloud) by connecting this repo and selecting `app.py` as the main file.

