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

# Add an input box
name = st.text_input('Enter your name')
if name:
    st.write(f'Hello, {name}!')
