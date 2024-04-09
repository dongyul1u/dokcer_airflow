import streamlit as st
import requests
import pandas as pd



# Streamlit UI
st.title("Welcome to our application")
st.header("Big Data Project - Team03")
st.subheader('Snowflake SQL Executor')



# FastAPI's URL
FASTAPI_URL = 'http://fastapi2:8075/query/'

# input SQL 
# sql_query = st.text_area("SQL Query", height=300)
sql_query = """
select * from PDF_DATA.PUBLIC.PDF_CONTENTS;
"""

# execute button
if st.button('Run Query'):
    with st.spinner("Loading"):
        response = requests.post(FASTAPI_URL, json={"sql": sql_query})
        try:
            if response.status_code == 200:
                data = response.json()["data"]
                df = pd.DataFrame(data)
                df.columns = ['content id','doc id','level','year','topic','section title','paragraph text']
                st.dataframe(df)
        except Exception as e:
                st.error("Failed to fetch data: {e}")