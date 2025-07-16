# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Get user input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get available fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_df = my_dataframe.to_pandas()
fruit_options = fruit_df['FRUIT_NAME'].tolist()

# Multiselect ingredient picker
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

# When user selects ingredients
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders(ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!", icon="✅")

# Pick one fruit to see its nutrition info
fruit_chosen = st.selectbox("🍓 Pick a fruit to see its nutrition info:", fruit_options)

if fruit_chosen:
    try:
        api_url = f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        st.dataframe(data, use_container_width=True)
    except Exception:
        st.error("❌ Could not load nutrition info. The API returned an error or invalid data.")
