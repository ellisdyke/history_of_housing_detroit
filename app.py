import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import warnings

# Suppress warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")

st.set_page_config(layout="wide")
st.title("Mapping Detroit's Housing Inequities (1940–2010)")

@st.cache_data
def load_data():
    years = [1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010]
    dfs = []
    for year in years:
        df = pd.read_csv(f"{year}.csv")
        df['Year'] = year
        dfs.append(df)

    rename_mappings = { ... }  # Assume the same detailed rename mappings from your original code

    for i, df in enumerate(dfs):
        df.rename(columns=rename_mappings[years[i]], inplace=True)

    combined = pd.concat(dfs, ignore_index=True)
    combined = combined[[col for col in ['Total_Population', 'White_Population', 'Black_Population',
                                          'Owner_Occupied', 'OO_White', 'OO_Black', 'Median_Housing_Value',
                                          'In_City', 'Year'] if col in combined.columns]]

    for col in ['Total_Population', 'White_Population', 'Black_Population', 'Owner_Occupied', 'OO_White', 'OO_Black', 'Median_Housing_Value']:
        combined[col] = pd.to_numeric(combined[col], errors='coerce')

    combined['In_City'] = combined['In_City'].astype(str)
    combined = combined[combined['In_City'].isin(['Yes', 'No'])]

    return combined

# Load data
df = load_data()

# Inflation adjustment
cpi_data = {1940:14.0, 1950:24.1, 1960:29.6, 1970:38.8, 1980:82.4, 1990:130.7, 2000:172.2, 2010:218.1, 2020:258.8, 2024:314.2}

def adjust_for_inflation(df, value_col, year_col, cpi_target=314.2):
    df[f'{value_col}_Inflation_Adjusted_2024'] = df.apply(
        lambda row: row[value_col] * cpi_target / cpi_data.get(row[year_col], np.nan)
        if row[year_col] in cpi_data else np.nan, axis=1)
    return df

result_df = adjust_for_inflation(df.copy(), 'Median_Housing_Value', 'Year')

# ---- Visual 1: Population Trends Over Time by Race and Location ----
st.header("Population Trends Over Time by Race and Location")
agg = df.groupby(['Year', 'In_City']).sum().reset_index()

pop_long = agg.melt(id_vars=['Year', 'In_City'], value_vars=['Total_Population', 'White_Population', 'Black_Population'],
                    var_name='Population_Type', value_name='Population')

population_type_selection = alt.selection_point(fields=['Population_Type'], bind='legend')
in_city_selection = alt.selection_point(fields=['In_City'], bind='legend')
interval_selection = alt.selection_interval(encodings=['x'])
vline_selection = alt.selection_point(on='mousemove', nearest=True, fields=['Year'], empty='none')

base = alt.Chart(pop_long).encode(
    x='Year:O',
    y='Population:Q',
    color='Population_Type:N',
    strokeDash='In_City:N',
    tooltip=['Year', 'Population_Type', 'In_City', 'Population']
)

line = base.mark_line(point=True).encode(
    opacity=alt.condition(vline_selection, alt.value(1), alt.value(0.2))
).transform_filter(
    population_type_selection & in_city_selection
)

vline = base.mark_rule(color='gray').encode(
    opacity=alt.condition(vline_selection, alt.value(1), alt.value(0))
).add_params(vline_selection)

pop_chart = (line + vline).add_params(population_type_selection, in_city_selection, interval_selection)

st.altair_chart(pop_chart.properties(width=800, height=400).interactive(), use_container_width=True)

# ---- Visual 2: Racial Proportion Stacked Bars ----
st.header("Proportion of Black and White Populations Over Time by Location")

viz = pop_long.pivot(index=['Year', 'In_City'], columns='Population_Type', values='Population').reset_index()
viz['White_Proportion'] = viz['White_Population'] / viz['Total_Population']
viz['Black_Proportion'] = viz['Black_Population'] / viz['Total_Population']

prop_long = viz.melt(id_vars=['Year', 'In_City'], value_vars=['White_Proportion', 'Black_Proportion'],
                     var_name='Race', value_name='Proportion')

highlight = alt.selection_point(fields=['Year'], empty='none', clear=False)
population_type_selection2 = alt.selection_point(fields=['Race'], bind='legend')
y_scroll = alt.selection_interval(bind='scales', encodings=['y'])

bars = alt.Chart(prop_long).mark_bar().encode(
    x='Year:O',
    y='Proportion:Q',
    color='Race:N',
    tooltip=['Year', 'Race', alt.Tooltip('Proportion:Q', format='.2%')],
    opacity=alt.condition(population_type_selection2 & highlight, alt.value(0.8), alt.value(0.2))
).add_params(population_type_selection2)

st.altair_chart(bars.add_params(highlight, y_scroll).properties(width=800, height=400), use_container_width=True)

# ---- Visual 3: Demographics and Homeownership ----
st.header("Demographics and Homeownership by Race in Detroit")

detroit = agg[agg['In_City'] == 'Yes'].copy()
detroit['White_Homeownership_Rate'] = detroit['OO_White'] / detroit['Owner_Occupied']
detroit['Black_Homeownership_Rate'] = detroit['OO_Black'] / detroit['Owner_Occupied']

home_long = detroit.melt(id_vars='Year', value_vars=['White_Homeownership_Rate', 'Black_Homeownership_Rate'],
                         var_name='Race', value_name='Rate')

race_dropdown = alt.binding_select(options=[None, 'White_Homeownership_Rate', 'Black_Homeownership_Rate'],
                                   labels=['All', 'White Homeownership', 'Black Homeownership'],
                                   name='Select Race: ')
race_filter = alt.selection_point(fields=['Race'], bind=race_dropdown, empty='all')

home_chart = alt.Chart(home_long).mark_line(point=True).encode(
    x='Year:O',
    y=alt.Y('Rate:Q', axis=alt.Axis(format='%')),
    color='Race:N',
    tooltip=['Year', 'Race', alt.Tooltip('Rate:Q', format='.2%')]
).add_params(race_filter).transform_filter(race_filter)

st.altair_chart(home_chart.properties(width=700, height=400).interactive(), use_container_width=True)

# ---- Visual 4: Median Home Value by Black Population Bracket ----
st.header("Trends in Median Home Values by Black Population Proportion")

city = result_df[result_df['In_City'] == 'Yes'].copy()
city['Black_Pop_Proportion'] = city['Black_Population'] / city['Total_Population']

bins = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]
labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']

city['Bracket'] = pd.cut(city['Black_Pop_Proportion'], bins=bins, labels=labels)

selector = alt.selection_point(fields=['Bracket'], bind=alt.binding_select(options=labels, name='Select Black %: '))

scatter = alt.Chart(city).mark_circle(size=100).encode(
    x='Year:O',
    y=alt.Y('Median_Housing_Value_Inflation_Adjusted_2024:Q', axis=alt.Axis(format='$,.0f')),
    color='Total_Population:Q',
    tooltip=['Year', 'Total_Population', 'Black_Pop_Proportion', 'Median_Housing_Value_Inflation_Adjusted_2024']
).add_params(selector).transform_filter(selector)

st.altair_chart(scatter.properties(width=800, height=450).interactive(), use_container_width=True)
