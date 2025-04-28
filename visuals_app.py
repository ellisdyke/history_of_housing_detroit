import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import warnings

# Suppress warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")

st.title("Mapping Detroit’s Housing Inequities (1940–2010)")

@st.cache_data
def load_data():
    # Load CSVs
    forties = pd.read_csv('1940.csv')
    fifties = pd.read_csv('1950.csv')
    sixties = pd.read_csv('1960.csv')
    seventies = pd.read_csv('1970.csv')
    eighties = pd.read_csv('1980.csv')
    nineties = pd.read_csv('1990.csv')
    twothousands = pd.read_csv('2000.csv')
    twentytens = pd.read_csv('2010.csv')

    # Add Year column
    forties['Year'] = 1940
    fifties['Year'] = 1950
    sixties['Year'] = 1960
    seventies['Year'] = 1970
    eighties['Year'] = 1980
    nineties['Year'] = 1990
    twothousands['Year'] = 2000
    twentytens['Year'] = 2010

    # Renaming dictionaries
    rename_dict_forties = {
        'Total Pop': 'Total_Population',
        'White Pop': 'White_Population',
        'Black Pop': 'Black_Population',
        'Owner Occupied': 'Owner_Occupied',
        'OO White': 'OO_White',
        'OO Black': 'OO_Black',
        'Median Value': 'Median_Housing_Value',
        'In City of Detroit?': 'In_City',
        'Year': 'Year'
    }
    rename_dict_fifties = {
        'Total Pop': 'Total_Population',
        'White': 'White_Population',
        'Black': 'Black_Population',
        'Owner Occupied': 'Owner_Occupied',
        'White Owner Occupied': 'OO_White',
        'Nonwhite Owner Occupied': 'OO_Black',
        'Median House Value': 'Median_Housing_Value',
        'In City?': 'In_City',
        'Year': 'Year'
    }
    rename_dict_sixties = {
        'Total Pop': 'Total_Population',
        'White Pop': 'White_Population',
        'Nonwite Pop': 'Black_Population',
        '# Owner Occupied': 'Owner_Occupied',
        'White OO': 'OO_White',
        'Nonwhite OO': 'OO_Black',
        'med.val': 'Median_Housing_Value',
        'City of Detroit?': 'In_City',
        'Year': 'Year'
    }
    rename_dict_seventies = {
        'Total_Population': 'Total_Population',
        'White_Population': 'White_Population',
        'Black_Population': 'Black_Population',
        'Count_Owner_Occupied_units': 'Owner_Occupied',
        'Median_Housing_Value': 'Median_Housing_Value',
        'Count_Black_OO_units': 'OO_Black',
        'In city of Detroit?': 'In_City',
        'Year': 'Year'
    }
    rename_dict_eighties = {
        'Total_Population': 'Total_Population',
        'Total_Pop_White': 'White_Population',
        'Total_Pop_Black': 'Black_Population',
        'Owner_Occupied_Housing_Units': 'Owner_Occupied',
        'Owner occupied >> White': 'OO_White',
        'Owner occupied >> Black': 'OO_Black',
        'Median value': 'Median_Housing_Value',
        'In city of Detroit?': 'In_City',
        'Year': 'Year'
    }
    rename_dict_nineties = {
        'Persons': 'Total_Population',
        'Persons: White': 'White_Population',
        'Persons: Black': 'Black_Population',
        'Occupied housing units: Owner occupied': 'Owner_Occupied',
        'Owner occupied >> White': 'OO_White',
        'Owner occupied >> Black': 'OO_Black',
        'Median Value for Specified owner-occupied housing units': 'Median_Housing_Value',
        'In city of Detroit?': 'In_City',
        'Year': 'Year'
    }
    rename_dict_twothousands = {
        'Total Population': 'Total_Population',
        'White Alone': 'White_Population',
        'Black or African American Alone': 'Black_Population',
        'Occupied Housing Units: Owner Occupied': 'Owner_Occupied',
        'Owner occupied >> White': 'OO_White',
        'Owner occupied >> Black': 'OO_Black',
        'Owner-occupied housing units: Median value': 'Median_Housing_Value',
        'In city of Detroit?': 'In_City',
        'Year': 'Year'
    }
    rename_dict_twentytens = {
        'Total Population:': 'Total_Population',
        'Total Population: White Alone': 'White_Population',
        'Total Population: Black or African American Alone': 'Black_Population',
        'Occupied Housing Units: Owner Occupied': 'Owner_Occupied',
        'Owner occupied >> Black': 'OO_Black',
        'Median Value': 'Median_Housing_Value',
        'In city of Detroit?': 'In_City',
        'Year': 'Year'
    }

    # Rename
    forties.rename(columns=rename_dict_forties, inplace=True)
    fifties.rename(columns=rename_dict_fifties, inplace=True)
    sixties.rename(columns=rename_dict_sixties, inplace=True)
    seventies.rename(columns=rename_dict_seventies, inplace=True)
    eighties.rename(columns=rename_dict_eighties, inplace=True)
    nineties.rename(columns=rename_dict_nineties, inplace=True)
    twothousands.rename(columns=rename_dict_twothousands, inplace=True)
    twentytens.rename(columns=rename_dict_twentytens, inplace=True)

    # Combine
    dfs = [forties, fifties, sixties, seventies, eighties, nineties, twothousands, twentytens]
    columns_to_keep = [
        'Total_Population', 'White_Population', 'Black_Population',
        'Owner_Occupied', 'OO_White', 'OO_Black', 'Median_Housing_Value',
        'In_City', 'Year'
    ]
    combined_df = pd.concat([df[[col for col in columns_to_keep if col in df.columns]] for df in dfs], ignore_index=True)

    for col in ['Median_Housing_Value', 'Total_Population', 'White_Population', 'Black_Population', 'Owner_Occupied', 'OO_White', 'OO_Black']:
        if col in combined_df.columns:
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

    if 'In_City' in combined_df.columns:
        combined_df['In_City'] = combined_df['In_City'].astype(str)
        combined_df = combined_df[combined_df['In_City'].isin(['Yes', 'No'])]

    return combined_df

# Load data
df = load_data()

# Inflation Adjustment
cpi_data = {
    1940: 14.0, 1950: 24.1, 1960: 29.6, 1970: 38.8,
    1980: 82.4, 1990: 130.7, 2000: 172.2, 2010: 218.1,
    2020: 258.8, 2024: 314.2
}
def adjust_for_inflation(df, year_col, value_col, cpi_data, target_year):
    cpi_target = cpi_data[target_year]
    df[f'{value_col}_Inflation_Adjusted_{target_year}'] = df.apply(
        lambda row: row[value_col] * cpi_target / cpi_data.get(row[year_col], np.nan)
        if row[year_col] in cpi_data else np.nan,
        axis=1
    )
    return df
df = adjust_for_inflation(df, 'Year', 'Median_Housing_Value', cpi_data, 2024)

# --- Visuals ---

st.header("Population Trends Over Time by Race and Location")
aggregated_df = df.groupby(['Year', 'In_City']).agg({
    'Total_Population': 'sum',
    'White_Population': 'sum',
    'Black_Population': 'sum',
    'Owner_Occupied': 'sum',
    'OO_White': 'sum',
    'OO_Black': 'sum'
}).reset_index()

combined_data_long = aggregated_df.melt(
    id_vars=['Year', 'In_City'],
    value_vars=['Total_Population', 'White_Population', 'Black_Population'],
    var_name='Population_Type',
    value_name='Population'
)

population_chart = alt.Chart(combined_data_long).mark_line(point=True).encode(
    x=alt.X('Year:O'),
    y=alt.Y('Population:Q', scale=alt.Scale(domain=[0, 3500000])),
    color='Population_Type:N',
    strokeDash='In_City:N',
    tooltip=['Year:O', 'Population_Type:N', 'In_City:N', 'Population:Q']
).properties(width=700, height=400)
st.altair_chart(population_chart, use_container_width=True)

# Homeownership chart
st.header("Demographics and Homeownership by Race in Detroit")
df_city = aggregated_df[aggregated_df['In_City'] == 'Yes'].copy()
df_city['White_Homeownership_Rate'] = df_city['OO_White'] / df_city['Owner_Occupied']
df_city['Black_Homeownership_Rate'] = df_city['OO_Black'] / df_city['Owner_Occupied']

homeownership_data = df_city.melt(
    id_vars='Year',
    value_vars=['White_Homeownership_Rate', 'Black_Homeownership_Rate'],
    var_name='Race',
    value_name='Rate'
)

homeownership_chart = alt.Chart(homeownership_data).mark_line(point=True).encode(
    x=alt.X('Year:O'),
    y=alt.Y('Rate:Q', axis=alt.Axis(format='%')),
    color='Race:N',
    tooltip=['Year:O', 'Race:N', alt.Tooltip('Rate:Q', format='.2%')]
).properties(width=700, height=400)
st.altair_chart(homeownership_chart, use_container_width=True)

# Housing values chart
st.header("Housing Values by Black Population Bracket")
housing_data = df[df['In_City'] == 'Yes'].copy()
housing_data['Black_Pop_Proportion'] = housing_data['Black_Population'] / housing_data['Total_Population']

bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
housing_data['Black_Pop_Percentage_Bracket'] = pd.cut(
    housing_data['Black_Pop_Proportion'], bins=bins, labels=labels, include_lowest=True
)

percentage_selector = alt.binding_select(
    options=labels,
    name='Select Black Population % Bracket: '
)
percentage_selection = alt.selection_point(
    fields=['Black_Pop_Percentage_Bracket'],
    bind=percentage_selector
)

scatter_chart = alt.Chart(housing_data).mark_circle(size=100, opacity=0.7).encode(
    x='Year:O',
    y=alt.Y('Median_Housing_Value_Inflation_Adjusted_2024:Q', axis=alt.Axis(format='$,.0f')),
    color='Total_Population:Q',
    tooltip=['Year:O', 'Total_Population:Q', 'Black_Pop_Proportion:Q', 'Median_Housing_Value_Inflation_Adjusted_2024:Q']
).transform_filter(
    percentage_selection
).add_params(
    percentage_selection
).properties(width=700, height=450)
st.altair_chart(scatter_chart, use_container_width=True)
