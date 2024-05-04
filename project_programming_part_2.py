# -*- coding: utf-8 -*-
"""Project_programming part 2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kKrfCrKxHyqMavFwvF2K3SD_cqae0XDh
"""

import pandas as pd
import sqlite3
from pathlib import Path
import numpy as np
from PIL import Image
import streamlit as st
import seaborn as sns
sns.set(style='ticks', color_codes=True)
import matplotlib.pyplot as plt


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

# Get access to Yearly EC contribution
def get_yearly(selected_country):
    conn = sqlite3.connect('ecsel_database.db')
    query1 = f"""
    SELECT projectID, year
    FROM projects
    """
    query2 = """
    SELECT projectID, ecContribution, country
    FROM participants
    WHERE country = '{selected_country}' 
    """
    df1 = pd.read_sql_query(query1, conn)
    df2 = pd.read_sql_query(query2, conn)
    
    # Merge dataframes on the projectID column
    contr_plot = pd.merge(df1, df2, on='projectID', how='inner')
    conn.close()
    return   sns.barplot(x=contr_plot.year,y=contr_plot.ecContribution)
    plt.xticks(rotation=0)
    
    #return contr_plot


# This would be the main programme

def main():
    # Print logo
    image = Image.open('Logo-KDT-JU.webp') # Load the image from disk
    st.image(image)

    # Print title
    st.title('Partner search tool')

    # Using this function you can access the table of countries in order to retrieve the necessary acronyms from the dictionary.
    countries_df = get_countries_df()
    country_acronyms = dict(zip(countries_df['Country'], countries_df['Acronym']))
    countries = list(country_acronyms.keys())

    # Dropdown menu to select country
    selected_country = st.selectbox('Select Country', countries)

    # It gives you directly access to the acronym of the country selected and it prints it
    selected_country_acronym = country_acronyms[selected_country]
    st.write(f"You selected: {selected_country_acronym} - {selected_country}")

    # Generate and display Yearly EC contribution of the selected country   
    st.subheader("Yearly EC contribution (€) in " + selected_country)
    plot = get_yearly(selected_country_acronym)
    print(plot)
    #plot = pd.DataFrame(plot)
   # st.bar_chart(plot.set_index('year'))
    
    # Generate and display participants dataframe of the selected country
    participants_df = get_participants_df(selected_country_acronym)
    st.subheader("Participants DataFrame:")
    st.write(participants_df)

    # Generate and display project coordinators dataframe of the selected country
    coordinators_df = get_coordinators_df(selected_country_acronym)
    st.subheader("Project Coordinators DataFrame:")
    st.write(coordinators_df)

    # Download buttons for generated dataframes
    @st.cache # IMPORTANT: Cache the conversion to prevent computation on every rerun
    def convert_df(df):
        return participants_df.to_csv().encode('utf-8')
        return coordinators_df.to_csv().encode('utf-8')
   # st.download_button(label="mycsv",data=convert_df(participants_df), file_name='d.csv', mime='text/csv',)
    st.download_button(label="Download Participants Data", data=convert_df(participants_df), file_name='participants_data.csv', mime='text/csv')
    st.download_button(label="Download Coordinators Data", data=convert_df(coordinators_df), file_name='coordinators_data.csv', mime='text/csv')

#This code checks if the script is being run directly by the Python interpreter, rather than being imported as a module into another script
if __name__ == "__main__":
    main()
