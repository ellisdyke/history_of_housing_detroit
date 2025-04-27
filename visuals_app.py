import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import warnings

# Suppress warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")

# --- Title
st.title("Detroit Housing and Population Trends (1940–2010)")
st.markdown("""
Explore changes in Detroit's population, racial demographics, homeownership rates, and housing values over time.
""")

# --- Load Data
@st.cache_data
def load_data():
    # Load directly from the root directory
    forties = pd.read_csv('1940.csv')
    fifties = pd.read_csv('1950.csv')
    sixties = pd.read_csv('1960.csv')
    seventies = pd.read_csv('1970.csv')
    eighties = pd.read_csv('1980.csv')
    nineties = pd.read_csv('1990.csv')
    twothousands = pd.read_csv('2000.csv')
    twentytens = pd.read_csv('2010.csv')

    # Add Year columns
    for df, year in zip(
        [forties, fifties, sixties, seventies, eighties, nineties, twothousands, twentytens],
        [1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010]):
        df['Year'] = year

    dfs = [forties, fifties, sixties, seventies, eighties, nineties, twothousands, twentytens]

    columns_to_keep = [
        'Total_Population', 'White_Population', 'Black_Population',
        'Owner_Occupied', 'OO_White', 'OO_Black', 'Median_Housing_Value',
        'In_City', 'Year'
    ]

    def filter_and_combine_dfs(dfs, columns_to_keep):
        filtered_dfs = []
        for df in dfs:
            present_cols = [col for col in columns_to_keep if col in df.columns]
            filtered_dfs.append(df[present_cols])
        return pd.concat(filtered_dfs, ignore_index=True)

    combined_df = filter_and_combine_dfs(dfs, columns_to_keep)
    combined_df.drop(index=0, inplace=True)
    combined_df.reset_index(drop=True, inplace=True)

    # ✅ FIXED: Only try to convert columns that actually exist
    for col in ['Median_Housing_Value', 'Total_Population', 'White_Population', 'Black_Population', 'Owner_Occupied', 'OO_White', 'OO_Black']:
        if col in combined_df.columns:
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

    combined_df['In_City'] = combined_df['In_City'].astype(str)
    combined_df = combined_df[combined_df['In_City'].isin(['Yes', 'No'])]

    return combined_df

# --- Load and Preprocess
df = load_data()

aggregated_df = df.groupby(['Year', 'In_City']).agg({
    'Total_Population': 'sum',
    'White_Population': 'sum',
    'Black_Population': 'sum',
    'Owner_Occupied': 'sum',
    'OO_White': 'sum',
    'OO_Black': 'sum'
}).reset_index()

# Inflation adjustment
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

result_df = adjust_for_inflation(df.copy(), 'Year', 'Median_Housing_Value', cpi_data, 2024)

# --- Section 1: Population Trends
st.header("Population Trends Over Time by Race and Location")

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
).properties(
    width=700,
    height=400,
    title="Detroit Population Trends by Race and City/Suburbs"
)

st.altair_chart(population_chart, use_container_width=True)

# --- Section 2: Racial Proportions
st.header("Proportion of Black and White Populations Over Time")

viz_data = combined_data_long.copy()
viz_data['In_City'] = viz_data['In_City'].replace({
    'No': 'In the Suburbs',
    'Yes': 'In the City of Detroit'
})

filtered_data = viz_data[viz_data['Population_Type'].isin(
    ['White_Population', 'Black_Population', 'Total_Population']
)]

pivot_data = filtered_data.pivot_table(
    index=['Year', 'In_City'],
    columns='Population_Type',
    values='Population',
    aggfunc='sum',
    observed=False
).reset_index()

pivot_data['White_Proportion'] = pivot_data['White_Population'] / pivot_data['Total_Population']
pivot_data['Black_Proportion'] = pivot_data['Black_Population'] / pivot_data['Total_Population']

proportions_long = pivot_data.melt(
    id_vars=['Year', 'In_City'],
    value_vars=['White_Proportion', 'Black_Proportion'],
    var_name='Population_Type',
    value_name='Proportion'
)

racial_chart = alt.Chart(proportions_long).mark_bar().encode(
    x=alt.X('Year:O'),
    y=alt.Y('Proportion:Q'),
    color='Population_Type:N',
    column='In_City:N',
    tooltip=['Year:O', 'Population_Type:N', alt.Tooltip('Proportion:Q', format='.0%')]
).properties(
    width=150,
    height=300,
    title="Proportion of Black and White Populations Over Time"
)

st.altair_chart(racial_chart, use_container_width=True)

# --- Section 3: Demographics and Homeownership
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
).properties(
    width=700,
    height=400,
    title="Homeownership Rates for Black and White Residents"
)

st.altair_chart(homeownership_chart, use_container_width=True)

# --- Section 4: Housing Values by Black Population
st.header("Housing Values by Black Population Bracket")

housing_data = result_df[result_df['In_City'] == 'Yes'].copy()
housing_data['Black_Pop_Proportion'] = housing_data['Black_Population'] / housing_data['Total_Population']

bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
housing_data['Black_Pop_Percentage_Bracket'] = pd.cut(
    housing_data['Black_Pop_Proportion'],
    bins=bins,
    labels=labels,
    include_lowest=True
)

percentage_selector = alt.binding_select(
    options=labels,
    name='Select Black Population % Bracket: '
)
percentage_selection = alt.selection_point(
    fields=['Black_Pop_Percentage_Bracket'],
    bind=percentage_selector
)

scatter_chart = alt.Chart(housing_data).mark_circle(opacity=0.7, size=100).encode(
    x='Year:O',
    y=alt.Y('Median_Housing_Value_Inflation_Adjusted_2024:Q', axis=alt.Axis(format='$,d')),
    color='Total_Population:Q',
    tooltip=['Year:O', 'Total_Population:Q', 'Black_Pop_Proportion:Q', 'Median_Housing_Value_Inflation_Adjusted_2024:Q']
).transform_filter(
    percentage_selection
).add_params(
    percentage_selection
).properties(
    width=700,
    height=450,
    title="Median Housing Values (Inflation-Adjusted to 2024 Dollars)"
)

st.altair_chart(scatter_chart, use_container_width=True)

# --- Footer
st.markdown("---")
st.markdown("Created with ❤️ by [Your Name] using Streamlit and Altair.")
