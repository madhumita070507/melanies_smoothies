# Import python packages

import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App title

st.title(':cup_with_straw: Customize Your Smoothie! :cup_with_straw:')
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input

name_on_order = st.text_input('Name on Smoothie')
st.write('The name on Smoothie is:', name_on_order)

# Connect to Snowflake

cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options including SEARCH_ON column

my_dataframe = session.table('smoothies.public.fruit_options').select(
col('FRUIT_NAME'),
col('SEARCH_ON')
)

# Convert Snowflake dataframe to pandas dataframe

pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients

ingredients_list = st.multiselect(
'Choose up to 5 ingredients:',
pd_df['FRUIT_NAME'],
max_selections=5
)

# If ingredients are selected

if ingredients_list:
   ingredients_string = ''

   for fruit_chosen in ingredients_list:

      ingredients_string += fruit_chosen + ' '

    # Get API search value from SEARCH_ON column
      search_on = pd_df.loc[ pd_df['FRUIT_NAME'] == fruit_chosen,'SEARCH_ON'].iloc[0]

      st.subheader(fruit_chosen + ' Nutrition Information')

    # API call
      smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

      sf_df=st.dataframe( data=smoothiefroot_response.json(),use_container_width=True)

#st.write(ingredients_string)

# Insert order into Snowflake
  my_insert_stmt = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order)VALUES ('{ingredients_string.strip()}', '{name_on_order}')"""

  time_to_insert = st.button('Submit Order')

  if time_to_insert:
      session.sql(my_insert_stmt).collect()
      st.success('Your Smoothie is ordered!', icon="✅")

