# Import Python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import json

# App title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Get user input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get available fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_df = my_dataframe.to_pandas()
fruit_options = fruit_df['FRUIT_NAME'].tolist()

# Multiselect ingredient picker
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

# When user selects ingredients and clicks button
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

# New section: Smoothiefroot API - Nutrition Info
st.header("🍉 Nutrition Info for Watermelon")

smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

try:
    fruit_data = smoothiefroot_response.json()
    # If it's a single object, wrap in list to display in dataframe
    if isinstance(fruit_data, dict):
        fruit_data = [fruit_data]
    st.dataframe(data=fruit_data, use_container_width=True)

except json.JSONDecodeError:
    st.error("❌ Could not load nutrition info. The API returned an error or invalid data.")
    st.code(smoothiefroot_response.text[:1000], language="html")
