import streamlit as st
from api import classes
import mysql.connector
import pandas as pd
from streamlit_option_menu import option_menu
from api import artifacts_details

# ✅ DEFINE API KEY HERE
API_KEY = "1bd39d42-57ba-4902-99cf-5b8672d7c372"


# PAGE CONFIG
st.set_page_config(layout="wide")

# DATABASE CONNECTION
conn = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    user="3gxYKPf9j9ttPYR.root",
    password="WOua2m1REYeMO0BQ",
    database="artifacts",
    port=4000
)
cursor = conn.cursor()

# TITLE
st.markdown(
    "<h1 style='text-align:center;'>🎨🏛️ Harvard’s Artifacts Collection</h1>",
    unsafe_allow_html=True
)

# INPUT
classification = st.text_input("Enter a classification (Coins, Paintings, etc)")
button = st.button("Collect data")

# OPTION MENU
menu = option_menu(
    None,
    ["Select Your Choice", "Migrate to SQL", "SQL Queries"],
    orientation="horizontal"
)

# MIGRATE TO SQL
if menu == "Migrate to SQL":

    cursor.execute("SELECT DISTINCT classification FROM metadata")
    classes_list = [i[0] for i in cursor.fetchall()]

    st.subheader("Insert the collected data")

    if st.button("Insert"):
        if classification.strip() == "":
            st.error("Please enter a classification first")

        elif classification in classes_list:
            st.error("Classification already exists! Try a different one.")

        else:
            records = classes(API_KEY, classification)
            meta, med, col = artifacts_details(records)
            insert_values(meta, med, col)

            st.success("Data inserted successfully")

            st.divider()

            # SHOW TABLES
            for table in ["metadata", "media", "colors"]:
                st.subheader(table.capitalize())
                cursor.execute(f"SELECT * FROM {table}")
                df = pd.DataFrame(
                    cursor.fetchall(),
                    columns=[i[0] for i in cursor.description]
                )
                st.dataframe(df)

# SQL QUERIES
elif menu == "SQL Queries":

    st.subheader("SQL Queries")

    SQL_QUERIES = {
        "1. German – 20th Century":
            "SELECT * FROM metadata WHERE culture='German' AND century='20th century';",

        "2. Unique Cultures":
            "SELECT DISTINCT culture FROM metadata;",

        "3. Archaic Period":
            "SELECT * FROM metadata WHERE period LIKE '%Archaic%';",

        "4. Latest Accession":
            "SELECT title, accessionyear FROM metadata ORDER BY accessionyear DESC;",

        "5. Artifacts per Department":
            "SELECT department, COUNT(*) AS total FROM metadata GROUP BY department;"
        "6. Imagecount > 1" 
            "SELECT * FROM media WHERE imagecount > 1;",

         "7. Average Rank":
            "SELECT AVG(`rank`) AS avg_rank FROM media;",

        "8. Artifacts (1500–1600)":
            "SELECT * FROM media WHERE databegin BETWEEN 1500 AND 1600;",

        "9. No Media Files":
           "SELECT * FROM media WHERE mediacount = 0;",

        "10. Colorcount > Mediacount":
            "SELECT * FROM media WHERE colorcount > mediacount;",

        "11. Distinct Hues":
            "SELECT DISTINCT hue FROM colors;",

        "12. Top 5 Colors":
            "SELECT color, COUNT(*) AS freq FROM colors GROUP BY color ORDER BY freq DESC LIMIT 5;",

        "13. Avg Color Percent":
             "SELECT AVG(CAST(percent AS DECIMAL(5,2))) AS avg_percent FROM colors;",

        "14. Colors for Artifact 130808":
             "SELECT * FROM colors WHERE objectid = 130808;",

       "15. Total Colors Count":
            "SELECT COUNT(*) AS total_colors FROM colors;",

      "16. Titles + Hues":
           "SELECT m.title, c.hue FROM metadata m JOIN colors c ON m.id = c.objectid;",

      "17. Title + Culture + Rank":
           """SELECT m.title, m.culture, md.rank
           FROM metadata m
           JOIN media md ON m.id = md.objectid
           WHERE m.period IS NOT NULL;""",

      "18. Top 10 Grey Artifacts":
           """SELECT m.title, md.rank
           FROM metadata m
           JOIN media md ON m.id = md.objectid
           JOIN colors c ON m.id = c.objectid
           WHERE c.hue = 'Grey'
           ORDER BY md.rank ASC
           LIMIT 10;""",

      "19. Avg Media per Classification":
           """SELECT m.classification, AVG(md.mediacount) AS avg_media
           FROM metadata m
           JOIN media md ON m.id = md.objectid
           GROUP BY m.classification;""",
 
      "20. Count per Culture":
          "SELECT culture, COUNT(*) AS total FROM metadata GROUP BY culture;",
  
      "21. All Artifact Titles":
          "SELECT title FROM metadata;",

      "22. Unique Colors":
          "SELECT DISTINCT color FROM colors;",

      "23. Artifacts per Department (Repeat)":
          "SELECT department, COUNT(*) AS total FROM metadata GROUP BY department;",

      "24. Highest Media Count":
           """SELECT m.title, md.mediacount
           FROM metadata m
           JOIN media md ON m.id = md.objectid
           ORDER BY md.mediacount DESC
           LIMIT 10;""",

      "25. Full Joined Dataset":
           """SELECT *
           FROM metadata m
           JOIN media md ON m.id = md.objectid
           LEFT JOIN colors c ON m.id = c.objectid;"""
    }

    query_name = st.selectbox(
        "Select a query",
        list(SQL_QUERIES.keys())
    )

    if st.button("Run Query"):
        query = SQL_QUERIES[query_name]
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [i[0] for i in cursor.description]

        df = pd.DataFrame(result, columns=columns)
        st.dataframe(df)

# DEFAULT SCREEN
else:
    st.info(" Please select an option from the menu")
