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

    rename_mappings = {
        1940: {'Total Pop': 'Total_Population', 'White Pop': 'White_Population', 'Black Pop': 'Black_Population',
               'Owner Occupied': 'Owner_Occupied', 'OO White': 'OO_White', 'OO Black': 'OO_Black',
               'Median Value': 'Median_Housing_Value', 'In City of Detroit?': 'In_City'},
        1950: {'Total Pop': 'Total_Population', 'White': 'White_Population', 'Black': 'Black_Population',
               'Owner Occupied': 'Owner_Occupied', 'White Owner Occupied': 'OO_White',
               'Nonwhite Owner Occupied': 'OO_Black', 'Median House Value': 'Median_Housing_Value',
               'In City?': 'In_City'},
        1960: {'Total Pop': 'Total_Population', 'White Pop': 'White_Population', 'Nonwite Pop': 'Black_Population',
               '# Owner Occupied': 'Owner_Occupied', 'White OO': 'OO_White', 'Nonwhite OO': 'OO_Black',
               'med.val': 'Median_Housing_Value', 'City of Detroit?': 'In_City'},
        1970: {'Total_Population': 'Total_Population', 'White_Population': 'White_Population',
               'Black_Population': 'Black_Population', 'Count_Owner_Occupied_units': 'Owner_Occupied',
               'Median_Housing_Value': 'Median_Housing_Value', 'Count_Black_OO_units': 'OO_Black',
               'In city of Detroit?': 'In_City'},
        1980: {'Total_Population': 'Total_Population', 'Total_Pop_White': 'White_Population',
               'Total_Pop_Black': 'Black_Population', 'Owner_Occupied_Housing_Units': 'Owner_Occupied',
               'Owner occupied >> White': 'OO_White', 'Owner occupied >> Black': 'OO_Black',
               'Median value': 'Median_Housing_Value', 'In city of Detroit?': 'In_City'},
        1990: {'Persons': 'Total_Population', 'Persons: White': 'White_Population', 'Persons: Black': 'Black_Population',
               'Occupied housing units: Owner occupied': 'Owner_Occupied', 'Owner occupied >> White': 'OO_White',
               'Owner occupied >> Black': 'OO_Black',
               'Median Value for Specified owner-occupied housing units': 'Median_Housing_Value',
               'In city of Detroit?': 'In_City'},
        2000: {'Total Population': 'Total_Population', 'White Alone': 'White_Population',
               'Black or African American Alone': 'Black_Population',
               'Occupied Housing Units: Owner Occupied': 'Owner_Occupied',
               'Owner occupied >> White': 'OO_White', 'Owner occupied >> Black': 'OO_Black',
               'Owner-occupied housing units: Median value': 'Median_Housing_Value',
               'In city of Detroit?': 'In_City'},
        2010: {'Total Population:': 'Total_Population', 'Total Population: White Alone': 'White_Population',
               'Total Population: Black or African American Alone': 'Black_Population',
               'Occupied Housing Units: Owner Occupied': 'Owner_Occupied', 'Owner occupied >> Black': 'OO_Black',
               'Median Value': 'Median_Housing_Value', 'In city of Detroit?': 'In_City'}
    }

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

# --- VISUAL 1: Population Trends ---
st.header("Population Trends Over Time by Race and Location")

agg = df.groupby(['Year', 'In_City']).sum().reset_index()
pop_long = agg.melt(id_vars=['Year', 'In_City'], value_vars=['Total_Population', 'White_Population', 'Black_Population'],
                    var_name='Population_Type', value_name='Population')

vline = alt.selection_point(fields=['Year'], nearest=True, on='mouseover')
zoom = alt.selection_interval(encodings=['x'])

base = alt.Chart(pop_long).encode(
    x='Year:O',
    y='Population:Q',
    color='Population_Type:N',
    strokeDash='In_City:N',
    tooltip=['Year', 'Population_Type', 'In_City', 'Population']
)

points = base.mark_point().add_params(vline).encode(
    opacity=alt.condition(vline, alt.value(1), alt.value(0.2))
)

rule = base.mark_rule(color='gray').encode(
    opacity=alt.condition(vline, alt.value(0.5), alt.value(0))
)

upper = (points + rule).properties(height=400).add_params(zoom).transform_filter(zoom)
lower = base.mark_line(point=True).transform_filter(zoom).properties(height=200)

st.altair_chart(alt.vconcat(upper, lower).resolve_scale(color='shared').interactive(), use_container_width=True)

# --- VISUAL 2: Proportion of Black and White Populations ---
st.header("Proportion of Black and White Populations Over Time by Location")

viz = pop_long.pivot(index=['Year', 'In_City'], columns='Population_Type', values='Population').reset_index()
viz['White_Proportion'] = viz['White_Population'] / viz['Total_Population']
viz['Black_Proportion'] = viz['Black_Population'] / viz['Total_Population']

prop_long = viz.melt(id_vars=['Year', 'In_City'], value_vars=['White_Proportion', 'Black_Proportion'],
                     var_name='Race', value_name='Proportion')

highlight = alt.selection_point(fields=['Year'], empty='none', clear=False)
population_type_selection = alt.selection_point(fields=['Race'], bind='legend')
y_scroll = alt.selection_interval(bind='scales', encodings=['y'])

bars = alt.Chart(prop_long).mark_bar().encode(
    x=alt.X('Year:O', sort='ascending'),
    y='Proportion:Q',
    color='Race:N',
    tooltip=['Year', 'Race', alt.Tooltip('Proportion:Q', format=".2%")],
    opacity=alt.condition(population_type_selection & highlight, alt.value(0.9), alt.value(0.2))
).add_params(population_type_selection, highlight, y_scroll)

st.altair_chart(bars.properties(width=800, height=400), use_container_width=True)

# --- VISUAL 3: Homeownership by Race ---
st.header("Demographics and Homeownership by Race in Detroit")

detroit = agg[agg['In_City'] == 'Yes'].copy()
detroit['White_Homeownership_Rate'] = detroit['OO_White'] / detroit['Owner_Occupied']
detroit['Black_Homeownership_Rate'] = detroit['OO_Black'] / detroit['Owner_Occupied']

home_long = detroit.melt(id_vars='Year', value_vars=['White_Homeownership_Rate', 'Black_Homeownership_Rate'],
                         var_name='Metric', value_name='Rate')

race_dropdown = alt.binding_select(options=['All', 'White_Homeownership_Rate', 'Black_Homeownership_Rate'],
                                   name='Select Race:')
race_selection = alt.selection_point(fields=['Metric'], bind=race_dropdown, empty='all')

hover = alt.selection_point(fields=['Year'], nearest=True, on='mouseover', empty='none')
click = alt.selection_point(fields=['Year'], on='click', toggle=False, empty='none')

home_chart = alt.Chart(home_long).mark_line(point=True).encode(
    x='Year:O',
    y=alt.Y('Rate:Q', axis=alt.Axis(format='%')),
    color='Metric:N',
    tooltip=['Year', 'Metric', alt.Tooltip('Rate:Q', format='.2%')],
    opacity=alt.condition(race_selection, alt.value(1), alt.value(0.2))
).add_params(race_selection, hover, click)

st.altair_chart(home_chart.properties(width=800, height=400).interactive(), use_container_width=True)

# --- VISUAL 4: Home Value by Black Population Bracket ---
st.header("Trends in Median Home Values by Black Population Proportion")

city = result_df[result_df['In_City'] == 'Yes'].copy()
city['Black_Pop_Proportion'] = city['Black_Population'] / city['Total_Population']

bins = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]
labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%',
          '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']

city['Bracket'] = pd.cut(city['Black_Pop_Proportion'], bins=bins, labels=labels)

selector = alt.selection_point(fields=['Bracket'], bind=alt.binding_select(options=labels, name='Select Black %:'))

scatter = alt.Chart(city).mark_circle(size=100).encode(
    x='Year:O',
    y=alt.Y('Median_Housing_Value_Inflation_Adjusted_2024:Q', axis=alt.Axis(format='$,.0f')),
    color='Total_Population:Q',
    tooltip=['Year', 'Total_Population', 'Black_Pop_Proportion', 'Median_Housing_Value_Inflation_Adjusted_2024']
).add_params(selector).transform_filter(selector)

st.altair_chart(scatter.properties(width=800, height=450).interactive(), use_container_width=True)
