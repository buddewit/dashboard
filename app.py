import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.ticker as mticker

st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.title('🏂 US Population Dashboard')
    option = ['Laadpaalmap','Laadpaaldata','Elektrische autos']
    selected_color_theme = st.selectbox('Select a color theme', option)

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

if option == 'Laadpaalmap':
    df_muni = pd.read_csv("df_muni.csv", delimiter=";")
    gpd_points = pd.read_csv("gpd_points.csv", delimiter=";")
    # Page config
    st.set_page_config(page_title="Charging Stations Map", layout="wide")
    
    st.title("⚡ EV Charging Stations Dashboard")
    
    # Assuming you have your dataframes loaded:
    # gdf_munis, df_muni, df3
    
    # Base map
    m = folium.Map(location=[52.1, 5.3], zoom_start=8)
    
    # Choropleth layer
    folium.Choropleth(
        geo_data=gdf_munis,       # full GeoDataFrame with geometry
        data=df_muni,              # your dataset
        columns=['province', 'avg_power'],
        key_on='feature.properties.NAME_2',  # depends on your GeoJSON property
        fill_color='BuPu',
        fill_opacity=0.7,
        line_opacity=0.3,
        legend_name='avg_power'
    ).add_to(m)
    
    # Marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    for _, row in df3.iterrows():
        tooltip = (
            f"Postcode: {row['AddressInfo.Postcode']}<br>"
            f"Town: {row['AddressInfo.Town']}<br>"
            "Click for more"
        )
    
        popup = f"""
        <i>Power KW:</i> <br> <b>{row['Conn_PowerKW']}</b> <br>
        <i>Connection type:</i> <br> <b>{row['Conn_ConnectionType.Title']}</b> <br>
        <i>Current type:</i> <br> <b>{row['Conn_CurrentType.Title']}</b> <br>
        """
    
        folium.CircleMarker(
            location=[row["AddressInfo.Latitude"], row["AddressInfo.Longitude"]],
            radius=4,
            fill=True,
            fill_opacity=0.8,
            tooltip=tooltip,
            popup=popup
        ).add_to(marker_cluster)
    
    # Display the map in Streamlit
    st_folium(m, width=1400, height=600)

elif option == 'Laadpaaldata':
    
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
    flights = filtered_df.pivot_table(
            index="bucket",
            columns="Maandjaar",
            values="Started",
            aggfunc="count"
        )
    
        fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
        sns.heatmap(flights, annot=True, fmt=".0f", linewidths=.5, cmap="YlGnBu", ax=ax)
        st.pyplot(fig)



    # --- CLEANING PHASE ---
    # 1. Work on a fresh copy so we don't mess up your heatmap data
    df_plot = filtered_df.copy()
    
    # 2. Force conversion of everything to numbers (Standardizing commas/strings)
    cols_to_fix = ["Bezettingsgraad", "Verbruikte energie WH accuraat"]
    for col in cols_to_fix:
        df_plot[col] = pd.to_numeric(
            df_plot[col].astype(str).str.replace(",", "."), 
            errors="coerce"
        )
    
    # 3. Ensure date is correct
    df_plot["Started"] = pd.to_datetime(df_plot["Started"], errors="coerce")
    
    # 4. Drop any rows that failed conversion (this is vital for the axis to stay numerical)
    df_plot = df_plot.dropna(subset=["Started", "Bezettingsgraad", "Verbruikte energie WH accuraat"])
    
    # --- PLOTTING PHASE ---
    # Create a brand new figure and axis object
    fig_scatter, ax_scatter = plt.subplots(figsize=(12, 6), dpi=150)
    
    # Set the style to ensure the grid is visible
    sns.set_style("whitegrid")
    
    sns.scatterplot(
        data=df_plot,
        x="Started",
        y="Bezettingsgraad",
        hue="Verbruikte energie WH accuraat",
        size="Verbruikte energie WH accuraat",
        palette="viridis", # Using a standard palette first to ensure it works
        sizes=(20, 200),
        ax=ax_scatter
    )
    
    # --- AXIS ENFORCEMENT ---
    # Explicitly set the limits (0 to 100)
    ax_scatter.set_ylim(-2, 102)
    
    # Explicitly set the ticks (0, 10, 20... 100)
    ax_scatter.set_yticks(range(0, 101, 10))
    
    # Clean up labels
    ax_scatter.set_title("Bezetting over Tijd")
    ax_scatter.set_ylabel("Bezettingsgraad (%)")
    
    # Move the legend outside so it doesn't cover data
    sns.move_legend(ax_scatter, "lower center", bbox_to_anchor=(0.5, -0.3), ncol=4)
    
    st.pyplot(fig_scatter)

elif option == 'Elektrische autos':

# --- RENDER --



























