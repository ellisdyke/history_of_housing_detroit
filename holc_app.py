
import streamlit as st

# Set page configuration
st.set_page_config(page_title="History of Redlining and Housing Inequality in Detroit", layout="wide")

# Page Title
st.title("History of Redlining and Housing Inequality in Detroit")

# Introduction text
st.markdown("""
For over a century, housing in Detroit has reflected deeply entrenched racial and economic divides.
This project explores how discriminatory policies like redlining, urban renewal, and restrictive covenants
shaped who was allowed to live where — and how those patterns persist today. 
Through interactive data visualizations, we track changes in land use and property ownership
that mirror larger patterns of segregation and inequity.
""")

# Sections overview
st.header("Key Aspects of Detroit's Housing History")

st.markdown("""
- **Population Trends Over Time by Race and Location:** Explore demographic changes in Detroit and its suburbs from 1940 to 2020. 
- **Proportion of Black and White Populations Over Time by Location:** Compare the changing racial makeup across city and suburban regions.
- **Demographics and Homeownership Rates by Race in Detroit:** Uncover persistent disparities in homeownership rates over time.
- **Detroit Land Bank Authority (DLBA) Sales and Re-Occupancy:** Visualize the impact of property sales and re-occupancy initiatives from 2014–2024.
""")

# Visualizer section
st.header("Interactive Visual: Re-Occupancy of DLBA Properties")

st.markdown("""
This interactive visual shows how Detroit's buy-back and sales programs have impacted re-occupancy rates over the past decade.
It features an animated timeline map of Detroit Land Bank Authority (DLBA) properties sold between 2014 and 2024,
highlighting both progress and ongoing challenges in reversing decades of disinvestment.
""")

# Create a launch button
st.markdown("""
<a href="https://historyofhousingdetroit-2kdjxr2appzvpx8y349aqmf.streamlit.app/" target="_blank">
    <button style='padding: 10px 20px; background-color: #0066cc; color: white; border: none; border-radius: 8px; font-size: 16px;'>
        🔗 Launch Interactive Visualizer
    </button>
</a>
""", unsafe_allow_html=True)
