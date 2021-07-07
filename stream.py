import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd

"""
# My first app
Here's our first attempt at using data to create a table:
"""

df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

df

chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])

st.line_chart(chart_data)

import scipy

from scipy.ndimage import correlate

st.write(correlate(np.arange(10), [1, 2.5]))

t = st.text_area("Enter multiline text")

st.write(t)

x = st.slider('x')
st.markdown(f'`{x}` squared is `{x * x}` and `42`')


option = st.radio('Select three known variables:',
                  ['initial velocity (u), final velocity (v), acceleration (a)',
                   'initial velocity (u), final velocity (v), time (t)',
                   'initial velocity (u), acceleration (a), time (t)',
                   'final velocity (v),acceleration (a), time (t)'])


map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)


if st.checkbox('Show dataframe'):
    chart_data = pd.DataFrame(
       np.random.randn(20, 3),
       columns=['a', 'b', 'c'])

    chart_data

option = st.selectbox(
    'Which number do you like best?',
     df['first column'])

'You selected: ', option

if str(option) == str(4):
    st.write('hehe')