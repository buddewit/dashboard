import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

sns.set_theme()

# -------------------------
# 1️⃣ Load your CSV (from repo or uploaded)
# -------------------------
fd3 = pd.read_csv('fd2.csv', delimiter=';')

# Optional: clean numeric column
fd3["Started"] = fd3["Started"].astype(str).str.replace(",", ".")
fd3["Started"] = pd.to_numeric(fd3["Started"], errors="coerce").fillna(0)

# Make Maandjaar ordered
months = ["jan-24", "feb-24", "mrt-24", "apr-24", "mei-24", "jun-24",
          "jul-24", "aug-24", "sep-24", "okt-24", "nov-24", "dec-24"]
fd3["Maandjaar"] = pd.Categorical(fd3["Maandjaar"], categories=months, ordered=True)

# -------------------------
# 2️⃣ Filter by Started–Ended range
# -------------------------
st.title("Started Heatmap Dashboard")

# Ensure numeric
fd3["Started"] = pd.to_numeric(fd3["Started"], errors="coerce").fillna(0)
fd3["Ended"] = pd.to_numeric(fd3["Ended"], errors="coerce").fillna(0)

# Slider
min_value = int(fd3["Started"].min())
max_value = int(fd3["Ended"].max())
range_values = st.slider(
    "Select Started–Ended range",
    min_value=min_value,
    max_value=max_value,
    value=(min_value, max_value)
)

# Filter based on slider
filtered_df = fd3[(fd3["Started"] >= range_values[0]) & (fd3["Ended"] <= range_values[1])]
st.write(f"Showing {len(filtered_df)} rows in selected range: {range_values}")

# -------------------------
# 3️⃣ Pivot table & heatmap
# -------------------------
flights = filtered_df.pivot_table(
    index="bucket",
    columns="Maandjaar",
    values="Started",
    aggfunc="count"
)

fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
sns.heatmap(flights, annot=True, fmt="d", linewidths=.5, cmap="YlGnBu", ax=ax)
st.pyplot(fig)
