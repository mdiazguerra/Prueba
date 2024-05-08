# -*- coding: utf-8 -*-
"""P_Gloria.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1I658fFyzLPB4_j2yDV7u6IbsxwU3STkm
"""

import pandas as pd
import sqlite3
from pathlib import Path
import numpy as np
from PIL import Image
import streamlit as st

db_file = 'ecsel_database.db'

#Here, we check whether the database already exists or whether one needs to be created. If it does not exist, create a new one

if not Path(db_file).exists():
    conn = sqlite3.connect(db_file)
    projects.to_sql('projects', conn)
    participants.to_sql('participants', conn)
    countries.to_sql('countries', conn)
    df_plot.to_sql('df_plot', conn)
    conn.close()
else:
    print("Database file already exists. Skipping table creation.")

print("Database creation complete.")


def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://kiutra.com/wp-content/uploads/2021/06/KDT-JU-logo-medium.gif/200/200);
                background-repeat: no-repeat;
                padding-top: 120px;
                background-position: 20px 20px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "My Company Name";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )



# This function is expected to connect to the database and access the countries dataframe.
def get_countries_df():
    conn = sqlite3.connect('ecsel_database.db')
    countries_df = pd.read_sql_query("SELECT * FROM countries", conn)
    conn.close()
    return countries_df

#This function is expected to connect to the database and access the participants' dataframe with certain characteristics.

def get_participants_df(selected_country):
    conn = sqlite3.connect('ecsel_database.db')
    query = f"""
    SELECT shortName, name, activityType, organizationURL, SUM(ecContribution) AS total_grants
    FROM participants
    WHERE country = '{selected_country}'
    GROUP BY shortName, name, activityType, organizationURL
    ORDER BY total_grants DESC
    """
    participants_df = pd.read_sql_query(query, conn)
    conn.close()
    return participants_df


# This function is expected to connect to the database and access the co-ordinator dataframe with certain characteristics.

def get_coordinators_df(selected_country):
    conn = sqlite3.connect('ecsel_database.db')
    query = f"""
    SELECT shortName, name, activityType, projectAcronym
    FROM participants
    WHERE country = '{selected_country}' AND role = 'coordinator'
    ORDER BY shortName ASC
    """
    coordinators_df = pd.read_sql_query(query, conn)
    conn.close()
    return coordinators_df

#def get_yearly_contributions(selected_country):
#    conn = sqlite3.connect(db_file)
 #   query = f"""
  #  SELECT year, SUM(ecContribution)
   # FROM participants
    #WHERE country = '{selected_country}'
   # GROUP BY year
   # """
    #participants_df = pd.read_sql_query(query, conn)
   # conn.close()
   # return participants_df

# This would be the main programme
def main():
    #First of all, the logo is printed
    # Print logo
    #st.image(Image.open('Logo-KDT-JU.webp'), caption='Your Logo Here', use_column_width=True)

    # Call the add_logo function to add the logo and styled sidebar
    add_logo()

    # Using this function you can access the table of countries in order to retrieve the necessary acronyms from the dictionary.
    countries_df = get_countries_df()
    country_acronyms = dict(zip(countries_df['Country'], countries_df['Acronym']))
    countries = list(country_acronyms.keys())

    # Dropdown menu to select country
    selected_country = st.selectbox('Select Country', countries)

    # It gives you directly access to the acronym of the country selected and it prints it
    selected_country_acronym = country_acronyms[selected_country]
    st.write(f"You selected: {selected_country_acronym} - {selected_country}")

    # Plot yearly contributions
    # Connect to the database
    conn = sqlite3.connect('ecsel_database.db')

    # Query the database for yearly contributions for the selected country
    query = f"""
    SELECT year, SUM(ecContribution) AS total_ecContribution
    FROM participants
    WHERE country = '{selected_country}'
    GROUP BY year
    """
    yearly_contributions_df = pd.read_sql_query(query, conn)

    # Close the database connection
    conn.close()

    # Plot yearly contributions
    st.write("Yearly Contributions:")
    st.bar_chart(yearly_contributions_df.set_index('year'))

    #yearly_contributions = get_yearly_contributions(selected_country)
    #st.write("Yearly Contributions:")
    #st.bar_chart(yearly_contributions)


    # Generate and display participants dataframe of the selected country
    participants_df = get_participants_df(selected_country_acronym)
    st.write("Participants DataFrame:")
    st.write(participants_df)


    # Generate and display project coordinators dataframe of the selected country
    coordinators_df = get_coordinators_df(selected_country_acronym)
    st.write("Project Coordinators DataFrame:")
    st.write(coordinators_df)

    # Download buttons for generated dataframes
    st.download_button(label="Download Participants Data", data=participants_df.to_csv(), file_name='participants_data.csv', mime='text/csv')
    st.download_button(label="Download Coordinators Data", data=coordinators_df.to_csv(), file_name='coordinators_data.csv', mime='text/csv')

#This code checks if the script is being run directly by the Python interpreter, rather than being imported as a module into another script
if _name_ == "_main_":
    main()