# Import packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# User input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
try:
    cnx = st.connection("snowflake")  # Make sure secrets.toml is set!
    session = cnx.session()
except Exception as e:
    st.error("❌ Failed to connect to Snowflake.")
    st.exception(e)
    st.stop()

# Get available fruit options from Snowflake
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
    fruit_df = my_dataframe.to_pandas()
    fruit_options = fruit_df['FRUIT_NAME'].tolist()
except Exception as e:
    st.error("❌ Failed to retrieve fruit options from Snowflake.")
    st.exception(e)
    st.stop()

# Ingredient picker
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

# If user picked ingredients
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button('Submit Order'):
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f"✅ Your Smoothie is ordered, {name_on_order}!", icon="✅")
        except Exception as e:
            st.error("❌ Failed to submit order to Snowflake.")
            st.exception(e)

# Call external API for fruit info
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

try:
    fruit_data = smoothiefroot_response.json()
    st.write("🍉 Watermelon Info:", fruit_data)
    st.dataframe(data=fruit_data, use_container_width=True)
except ValueError:
    st.error("❌ Failed to parse response from API (not valid JSON).")
    st.text(smoothiefroot_response.text)
