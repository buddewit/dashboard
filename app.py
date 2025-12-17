import streamlit as st

# Set the title
st.title('Hello Streamlit!')

# Add a header
st.header('Welcome to my first Streamlit app')

# Add a subheader
st.subheader('This is a subheader')

# Add text
st.text('This is a simple text.')

# Add a markdown
st.markdown('### This is a markdown')

# Add a button
if st.button('Click me'):
    st.write('Button clicked!')

# Add a slider
value = st.slider('Select a value', 0, 100, 50)
st.write(f'Slider value: {value}')

range_values = st.slider(
    "Select a range",
    min_value=0,
    max_value=100,
    value=(20, 80)  # <-- tuple sets the two handles
)

st.write("Selected range:", range_values)

# Add an input box
name = st.text_input('Enter your name')
if name:
    st.write(f'Hello, {name}!')

