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
    # Load each decade
    forties = pd.read_csv('1940.csv')
    fifties = pd.read_csv('1950.csv')
    sixties = pd.read_csv('1960.csv')
    seventies = pd.read_csv('1970.csv')
    eighties = pd.read_csv('1980.csv')
    nineties = pd.read_csv('1990.csv')
    twothousands = pd.read_csv('2000.csv')
    twentytens = pd.read_csv('2010.csv')

    forties['Year'] = 1940
    fifties['Year'] = 1950
    sixties['Year'] = 1960
    seventies['Year'] = 1970
    eighties['Year'] = 1980
    nineties['Year'] = 1990
    twothousands['Year'] = 2000
    twentytens['Year'] = 2010

    rename_dicts = {
        1940: {'Total Pop': 'Total_Population', 'White Pop': 'White_Population', 'Black Pop': 'Black_Population', 'Owner Occupied': 'Owner_Occupied', 'OO White': 'OO_White', 'OO Black': 'OO_Black', 'Median Value': 'Median_Housing_Value', 'In City of Detroit?': 'In_City', 'Year': 'Year'},
        1950: {'Total Pop': 'Total_Population', 'White': 'White_Population', 'Black': 'Black_Population', 'Owner Occupied': 'Owner_Occupied', 'White Owner Occupied': 'OO_White', 'Nonwhite Owner Occupied': 'OO_Black', 'Median House Value': 'Median_Housing_Value', 'In City?': 'In_City', 'Year': 'Year'},
        1960: {'Total Pop': 'Total_Population', 'White Pop': 'White_Population', 'Nonwite Pop': 'Black_Population', '# Owner Occupied': 'Owner_Occupied', 'White OO': 'OO_White', 'Nonwhite OO': 'OO_Black', 'med.val': 'Median_Housing_Value', 'City of Detroit?': 'In_City', 'Year': 'Year'},
        1970: {'Total_Population': 'Total_Population', 'White_Population': 'White_Population', 'Black_Population': 'Black_Population', 'Count_Owner_Occupied_units': 'Owner_Occupied', 'Median_Housing_Value': 'Median_Housing_Value', 'Count_Black_OO_units': 'OO_Black', 'In city of Detroit?': 'In_City', 'Year': 'Year'},
        1980: {'Total_Population': 'Total_Population', 'Total_Pop_White': 'White_Population', 'Total_Pop_Black': 'Black_Population', 'Owner_Occupied_Housing_Units': 'Owner_Occupied', 'Owner occupied >> White': 'OO_White', 'Owner occupied >> Black': 'OO_Black', 'Median value': 'Median_Housing_Value', 'In city of Detroit?': 'In_City', 'Year': 'Year'},
        1990: {'Persons': 'Total_Population', 'Persons: White': 'White_Population', 'Persons: Black': 'Black_Population', 'Occupied housing units: Owner occupied': 'Owner_Occupied', 'Owner occupied >> White': 'OO_White', 'Owner occupied >> Black': 'OO_Black', 'Median Value for Specified owner-occupied housing units': 'Median_Housing_Value', 'In city of Detroit?': 'In_City', 'Year': 'Year'},
        2000: {'Total Population': 'Total_Population', 'White Alone': 'White_Population', 'Black or African American Alone': 'Black_Population', 'Occupied Housing Units: Owner Occupied': 'Owner_Occupied', 'Owner occupied >> White': 'OO_White', 'Owner occupied >> Black': 'OO_Black', 'Owner-occupied housing units: Median value': 'Median_Housing_Value', 'In city of Detroit?': 'In_City', 'Year': 'Year'},
        2010: {'Total Population:': 'Total_Population', 'Total Population: White Alone': 'White_Population', 'Total Population: Black or African American Alone': 'Black_Population', 'Occupied Housing Units: Owner Occupied': 'Owner_Occupied', 'Owner occupied >> Black': 'OO_Black', 'Median Value': 'Median_Housing_Value', 'In city of Detroit?': 'In_City', 'Year': 'Year'}
    }

    decades = [forties, fifties, sixties, seventies, eighties, nineties, twothousands, twentytens]
    years = [1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010]

    for df, year in zip(decades, years):
        df.rename(columns=rename_dicts[year], inplace=True)

    columns_to_keep = [
        'Total_Population', 'White_Population', 'Black_Population',
        'Owner_Occupied', 'OO_White', 'OO_Black',
        'Median_Housing_Value', 'In_City', 'Year'
    ]

    combined_df = pd.concat([df[columns_to_keep] for df in decades], ignore_index=True)

    return combined_df

# Load cleaned data
combined_df = load_data()

# Now your visuals start here
# (put your population trends / proportions / ownership visualizations below as you had before)

# ---------------------------------------------------------
# 1. Population Trends (First visual)

st.header("Population Trends Over Time by Race and Location")
combined_data_long = aggregated_df.melt(id_vars=['Year', 'In_City'],
                                        value_vars=['Total_Population', 'White_Population', 'Black_Population'],
                                        var_name='Population_Type', value_name='Population')

vline_selection = alt.selection_point(on='mousemove', nearest=True, fields=['Year'], empty='none')

base_chart = alt.Chart(combined_data_long).encode(
    x='Year:O',
    y=alt.Y('Population:Q', scale=alt.Scale(domain=[0, 3500000])),
    color='Population_Type:N',
    strokeDash=alt.StrokeDash('In_City:N'),
    tooltip=['Year:O', 'Population_Type:N', 'In_City:N', 'Population:Q']
)

line_chart = base_chart.mark_line(point=True).encode(
    opacity=alt.condition(vline_selection, alt.value(1), alt.value(0.2))
).add_params(vline_selection)

st.altair_chart(line_chart, use_container_width=True)

# ---------------------------------------------------------
# 2. Proportion of Black and White Populations

st.header("Proportion of Black and White Populations Over Time by Location")
viz_data = combined_data_long.copy()
viz_data['Population_Type'] = viz_data['Population_Type'].astype('category')
viz_data['In_City'] = viz_data['In_City'].replace({'No': 'In the Suburbs', 'Yes': 'In the City of Detroit'})

filtered_data = viz_data[viz_data['Population_Type'].isin(['White_Population', 'Black_Population', 'Total_Population'])]

pivot_data = filtered_data.pivot_table(index=['Year', 'In_City'],
                                       columns='Population_Type',
                                       values='Population',
                                       aggfunc='sum').reset_index()

pivot_data['White_Proportion'] = pivot_data['White_Population'] / pivot_data['Total_Population']
pivot_data['Black_Proportion'] = pivot_data['Black_Population'] / pivot_data['Total_Population']

proportions_long = pivot_data.melt(id_vars=['Year', 'In_City'],
                                   value_vars=['White_Proportion', 'Black_Proportion'],
                                   var_name='Population_Type',
                                   value_name='Proportion')

bar_chart = alt.Chart(proportions_long).mark_bar().encode(
    x='Year:O',
    y='Proportion:Q',
    color='Population_Type:N',
    tooltip=['Year', 'Population_Type', alt.Tooltip('Proportion:Q', format='.2%')]
)

st.altair_chart(bar_chart, use_container_width=True)

# ---------------------------------------------------------
# 3. Homeownership Trends

st.header("Demographics and Homeownership by Race in Detroit")
df_city = aggregated_df[aggregated_df['In_City'] == 'Yes'].copy()
df_city['White_Homeownership_Rate'] = df_city['OO_White'] / df_city['Owner_Occupied']
df_city['Black_Homeownership_Rate'] = df_city['OO_Black'] / df_city['Owner_Occupied']

melted_homeownership = df_city[['Year', 'White_Homeownership_Rate', 'Black_Homeownership_Rate']].melt(
    id_vars=['Year'], var_name='Metric', value_name='Rate'
)

home_chart = alt.Chart(melted_homeownership).mark_line(point=True).encode(
    x='Year:O',
    y=alt.Y('Rate:Q', axis=alt.Axis(format='%')),
    color='Metric:N',
    tooltip=['Year', 'Metric', alt.Tooltip('Rate:Q', format='.2%')]
)

st.altair_chart(home_chart, use_container_width=True)

# ---------------------------------------------------------
# 4. Housing Values by Black Population %

st.header("Trends in Median Home Values by Black Population Proportion")
housing_data = result_df[result_df['In_City'] == 'Yes'].copy()
housing_data['Black_Pop_Proportion'] = housing_data['Black_Population'] / housing_data['Total_Population']

bins = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]
labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
housing_data['Black_Pop_Percentage_Bracket'] = pd.cut(housing_data['Black_Pop_Proportion'], bins=bins, labels=labels)

percentage_selection = alt.selection_point(fields=['Black_Pop_Percentage_Bracket'],
                                            bind=alt.binding_select(options=labels, name='Select Black %: '))

scatter_chart = alt.Chart(housing_data).mark_circle(size=100, opacity=0.7, stroke='black').encode(
    x='Year:O',
    y=alt.Y('Median_Housing_Value_Inflation_Adjusted_2024:Q', axis=alt.Axis(format='$,.0f')),
    color='Total_Population:Q',
    tooltip=['Year', 'Total_Population', 'Black_Pop_Proportion', 'Median_Housing_Value_Inflation_Adjusted_2024']
).add_params(percentage_selection).transform_filter(percentage_selection)

st.altair_chart(scatter_chart, use_container_width=True)
