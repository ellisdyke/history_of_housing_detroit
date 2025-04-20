# DLBA Sales and Re-Occupancy in Detroit (2014–2024)

This Streamlit app visualizes property sales from the Detroit Land Bank Authority (DLBA), current DLBA-owned properties, and occupancy certificates issued between 2014 and 2024.

## Features

- Animated map of yearly DLBA sales
- Visualization of properties that received a Certificate of Occupancy
- Contextual layering of still DLBA-owned properties

## Files Required

- `app.py` (the Streamlit app)
- `DLBA_Owned_Properties_-7235192583433363849.csv`
- `Property_Sales_Detroit_-4801866508954663892.csv`
- `CertificateOfOccupancy_4256029621510488921.csv`

## Running the App

Install dependencies:

```bash
pip install -r requirements.txt
```

Then run:

```bash
streamlit run app.py
```

## Deployment

This app can be deployed on [Streamlit Cloud](https://streamlit.io/cloud) by connecting this repo and selecting `app.py` as the main file.

