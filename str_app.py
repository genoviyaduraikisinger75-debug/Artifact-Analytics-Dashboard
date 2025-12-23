import streamlit as st
import mysql.connector
import pandas as pd

# DATABASE CONNECTION

conn = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    user="3gxYKPf9j9ttPYR.root",
    password="WOua2m1REYeMO0BQ",
    database="artifacts",
    port=4000
)

# STREAMLIT PAGE CONFIG

st.set_page_config(page_title="Harvard Artifacts", layout="wide")
st.markdown(
    "<h1 style='text-align:center;'>Harvard’s Artifacts Collection</h1>",
    unsafe_allow_html=True
)

# UI – CLASSIFICATION (UI ONLY)

classification = st.text_input("Enter a classification:") # Coins, Vessels, Paintings
button = st.button("Collect data")

st.markdown("<h1 style='text-align: center; color: black;'> Harvard’s Artifacts Collection</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.button("Select Your Choice", use_container_width=True)
col2.button("Migrate to SQL", use_container_width=True)
col3.button("SQL Queries", use_container_width=True)

st.markdown("---")

# SQL QUERIES (25)

queries = {
    "1. German – 20th Century":
        "SELECT * FROM metadata WHERE culture='German' AND century='20th century';",

    "2. Unique Cultures":
        "SELECT DISTINCT culture FROM metadata;",

    "3. Archaic Period":
        "SELECT * FROM metadata WHERE period LIKE '%Archaic%';",

    "4. Latest Accession":
        "SELECT * FROM metadata ORDER BY accessionyear DESC;",

    "5. Artifacts per Department":
        "SELECT department, COUNT(*) AS total FROM metadata GROUP BY department;",

    "6. Imagecount > 1":
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

# SIDEBAR – SELECT QUERY 

st.sidebar.header("Select SQL Query")
query_name = st.sidebar.selectbox(
    "Choose a query",
    list(queries.keys())
)

# RUN QUERY 

try:
    df = pd.read_sql(queries[query_name], conn)
except Exception as e:
    st.error(f"Query failed: {e}")
    st.stop()

# METRICS

c1, c2, c3 = st.columns(3)
c1.metric("Rows", len(df))
c2.metric("Columns", len(df.columns))
c3.metric("Query No", query_name.split(".")[0])

#TABS
tab1, tab2, tab3 = st.tabs(["📋 Table", "📊 Chart", "🧠 SQL"])

with tab1:
    st.dataframe(df, use_container_width=True)

with tab2:
    numeric_df = df.select_dtypes(include=["int64", "float64"])
    if not numeric_df.empty:
        st.bar_chart(numeric_df.iloc[:, 0])
    else:
        st.info("No numeric data available for visualization.")

with tab3:
    st.code(queries[query_name], language="sql")

# CLOSE CONNECTION

conn.close()
