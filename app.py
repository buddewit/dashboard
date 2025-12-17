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
# 1️⃣ Load and Prepare Data
# -------------------------
fd3 = pd.read_csv("fd2.csv", delimiter=";")

# Ensure columns are datetime
fd3["Started"] = pd.to_datetime(fd3["Started"], errors="coerce", dayfirst=True)
fd3["Ended"] = pd.to_datetime(fd3["Ended"], errors="coerce", dayfirst=True)

# Drop NaT values to avoid errors in min/max calculation
fd3 = fd3.dropna(subset=["Started", "Ended"])

# -------------------------
# 2️⃣ Slider Logic
# -------------------------
# Get min and max as Timestamp objects directly from the datetime columns
min_date = fd3["Maxgevraagd(w)"].min()
max_date = fd3["Maxgevraagd(w)"].max()

min_date2 = fd3["hour"].min()
max_date2 = fd3["hour"].max()

# Use the datetime objects directly in the slider
range_ts = st.slider(
    "Selecteer minimale tot maximale stroomtoevoer van laadpaal (w)",
    min_value=min_date, #to_pydatetime()
    max_value=max_date, #to_pydatetime() 
    value=(min_date, max_date)
    #format="DD-MM-YYYY"
)
range_ts2 = st.slider(
    "Selecteer tijdstip start laden",
    min_value=int(min_date2),
    max_value=int(max_date2),
    value=(int(min_date2), int(max_date2)),
    step=1,
    format="%d uur"
)


# range_ts is already a tuple of datetime objects, no need to convert with unit="s"
start_range, end_range = range_ts
start_range2, end_range2 = range_ts2

# -------------------------
# 3️⃣ Filter and Pivot
# -------------------------
# Filter DataFrame using the slider values

filtered_df = fd3[
    (fd3["Maxgevraagd(w)"] >= start_range) & 
    (fd3["Maxgevraagd(w)"] <= end_range) & 
    (fd3["hour"] >= start_range2) & 
    (fd3["hour"] <= end_range2)].copy()

st.write(
    f"Showing {len(filtered_df)} rows | "
    f"Wattage: {start_range}–{end_range} | "
    f"Hour: {start_range2}–{end_range2}"
)

# Set Categorical order
months = ["jan-24", "feb-24", "mrt-24", "apr-24", "mei-24", "jun-24",
          "jul-24", "aug-24", "sep-24", "okt-24", "nov-24", "dec-24"]
filtered_df["Maandjaar"] = pd.Categorical(filtered_df["Maandjaar"], categories=months, ordered=True)

# Generate Heatmap
if not filtered_df.empty:
    flights = filtered_df.pivot_table(
        index="bucket",
        columns="Maandjaar",
        values="Started",
        aggfunc="count"
    )

    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
    sns.heatmap(flights, annot=True, fmt=".0f", linewidths=.5, cmap="YlGnBu", ax=ax)
    st.pyplot(fig)
else:
    st.warning("No data found for the selected date range.")

if not filtered_df.empty:

    # Convert types safely
    filtered_df["Started"] = pd.to_datetime(filtered_df["Started"], errors="coerce")
    filtered_df["Verbruikte energie WH accuraat"] = (
        filtered_df["Verbruikte energie WH accuraat"]
        .astype(str)
        .str.replace(",", ".")
        .astype(float)
    )

    # Drop rows with NaNs in key columns
    filtered_df = filtered_df.dropna(subset=["Started", "Bezettingsgraad", "Verbruikte energie WH accuraat"])

    cmap = sns.cubehelix_palette(rot=-.2, as_cmap=True)

    g = sns.relplot(
        data=filtered_df,
        x="Started",
        y="Bezettingsgraad",
        hue="Verbruikte energie WH accuraat",
        size="Verbruikte energie WH accuraat",
        palette=cmap,
        sizes=(10, 200),
        height=6,
        aspect=2
    )

    g.ax.xaxis.grid(True, "minor", linewidth=.25)
    g.ax.yaxis.grid(True, "minor", linewidth=.25)
    g.despine(left=True, bottom=True)
    g.ax.set_ylim(0, 100)
    g.ax.yaxis.set_major_locator(mticker.MultipleLocator(10))

    st.pyplot(g.fig)

else:
    st.warning("No data found for the selected date range.")














