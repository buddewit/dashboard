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
fd3 = pd.read_csv("fd2.csv", delimiter=";")

# Convert to datetime
fd3["Started"] = pd.to_datetime(fd3["Started"], errors="coerce", dayfirst=True)
fd3["Ended"] = pd.to_datetime(fd3["Ended"], errors="coerce", dayfirst=True)

fd3["Started_ts"] = fd3["Started"].map(pd.Timestamp.timestamp)
fd3["Ended_ts"] = fd3["Ended"].map(pd.Timestamp.timestamp)

# -------------------------
# Slider for date range
# -------------------------
# Convert dates to integers (timestamps) for slider
fd3["Started_ts"] = fd3["Started"].map(pd.Timestamp.timestamp)
fd3["Ended_ts"] = fd3["Ended"].map(pd.Timestamp.timestamp)

min_ts = pd.to_datetime(fd3["Started_ts"].min())
max_ts = pd.to_datetime(fd3["Ended_ts"].max())

range_ts = st.slider(
    "Select Started–Ended range",
    min_value=min_ts,
    max_value=max_ts,
    value=(min_ts, max_ts),
    step=86400  # 1 day in seconds
)

# Convert back to datetime
start_range = pd.to_datetime(range_ts[0], unit="s")
end_range = pd.to_datetime(range_ts[1], unit="s")

# Filter DataFrame
filtered_df = fd3[(fd3["Started"] >= start_range) & (fd3["Ended"] <= end_range)]

st.write(f"Showing {len(filtered_df)} rows in range: {start_range.date()} to {end_range.date()}")

# -------------------------
# Pivot table & heatmap
# -------------------------
# Make Maandjaar ordered
months = ["jan-24", "feb-24", "mrt-24", "apr-24", "mei-24", "jun-24",
          "jul-24", "aug-24", "sep-24", "okt-24", "nov-24", "dec-24"]
filtered_df["Maandjaar"] = pd.Categorical(filtered_df["Maandjaar"], categories=months, ordered=True)

flights = filtered_df.pivot_table(
    index="bucket",
    columns="Maandjaar",
    values="Started",
    aggfunc="count"
)

fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
sns.heatmap(flights, annot=True, fmt="d", linewidths=.5, cmap="YlGnBu", ax=ax)
st.pyplot(fig)




