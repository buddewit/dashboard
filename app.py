import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.ticker as mticker
from shapely import wkt
import geopandas as gpd
import gdown 
from datetime import date

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
    option = st.selectbox('Selecteer een weergave', 
                         ['Laadpaalmap', 'Laadpaaldata', 'Elektrische autos'])

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

    st.title("⚡ EV Charging Stations Dashboard")
    
    df_muni = pd.read_csv("df_muni.csv", delimiter=",")
    gdf_points = pd.read_csv("gdf_points.csv", delimiter=",")
    gdf_munis = pd.read_csv("gdf_munis.csv", delimiter=",")
     
    gdf_munis['geometry'] = gdf_munis['geometry'].apply(wkt.loads)
    
    # Convert to GeoDataFrame
    gdf_munis = gpd.GeoDataFrame(gdf_munis, geometry='geometry', crs="EPSG:4326")

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
    
    for _, row in gdf_points.iterrows():
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


##
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

    #y as aanpassen
    ax_scatter.set_ylim(-2, 102)
    
    #y as afstand 
    ax_scatter.set_yticks(range(0, 101, 10))

    ax_scatter.set_title("Bezetting over Tijd")
    ax_scatter.set_ylabel("Bezettingsgraad (%)")
    
    # legenda verplaatsen
    sns.move_legend(ax_scatter, "lower center", bbox_to_anchor=(0.5, -0.3), ncol=4)
    
    st.pyplot(fig_scatter)

elif option == 'Elektrische autos':
    
    #file_id = "18PefqMveefnbdKbincQeW6O8IBbcPSPw"
    #url = f"https://drive.google.com/uc?id={file_id}"
    #output = "elektrischeautos5.csv"
    #gdown.download(url, output, quiet=False)

    @st.cache_data
    def load_data():
        file_id = "18PefqMveefnbdKbincQeW6O8IBbcPSPw"
        url = f"https://drive.google.com/uc?id={file_id}"
        output = "elektrischeautos5.csv"
    
        #if not os.path.exists(output):
        #    gdown.download(url, output, quiet=True)
    
        df_faainal = pd.read_csv(
            output,
            delimiter=',',
            usecols=list(range(15)),
            skip_blank_lines=True
        )
    
        return df_faainal
        
    df_faainal = load_data()

    date_cols = [
    "datum_eerste_tenaamstelling_in_nederland",
    "datum_eerste_toelating",
    "datum_tenaamstelling"
    ]
    
    df_faainal[date_cols] = df_faainal[date_cols].apply(
    pd.to_datetime,
    format="%Y-%m-%d",
    errors="coerce"
    )
###########################################################
#    filtered_df2 = df_faainal[
#        (df_faainal["catalogusprijs"] > 100000) &
#        (df_faainal["maximale_constructiesnelheid"] > 250)
#    ].copy()
#    
#    filtered_df2 = filtered_df2.groupby('handelsbenaming').filter(lambda x: len(x) > 2)
###############################################################

    min_date3 = 10000
    max_date3 = 500000
    
    min_date4 = df_faainal["datum_eerste_toelating"].min().to_pydatetime()
    max_date4 = df_faainal["datum_eerste_toelating"].max().to_pydatetime()

    min_date5 = df_faainal["maximale_constructiesnelheid"].min()
    max_date5 = df_faainal["maximale_constructiesnelheid"].max()

    #min_date6 = df_faainal.groupby('handelsbenaming').filter(lambda x: len(x).min()
    #max_date6 = df_faainal.groupby('handelsbenaming').filter(lambda x: len(x).max()

    # Use the datetime objects directly in the slider
    range_ts3 = st.slider(
        "Selecteer catalogusprijs (€)",
        min_value=min_date3, #to_pydatetime()
        max_value=max_date3, #to_pydatetime() 
        value=(min_date3, max_date3)
        #format="DD-MM-YYYY"
    )

    range_ts4 = st.slider(
        "Datum eerste toelating",
        min_value=(min_date4),
        max_value=(max_date4),
        value=(min_date4, max_date4),
        format="YYYY-MM-DD"
    )

    range_ts5 = st.slider(
        "Maximale snelheid (km/h)",
        min_value=(min_date5),
        max_value=(max_date5),
        value=(min_date5, max_date5)
        #format="YYYY-MM-DD"
    )
     #range_ts6 = st.slider(
     #   "Datum eerste toelating",
     #   min_value=(min_date4),
     #   max_value=(max_date4),
     #   value=(min_date4), (max_date4))
     #   format="YYYY-MM-DD"
     #)

    
    # range_ts is already a tuple of datetime objects, no need to convert with unit="s"
    start_range3, end_range3 = range_ts3
    start_range4, end_range4 = range_ts4
    start_range4 = pd.Timestamp(start_range4)
    end_range4 = pd.Timestamp(end_range4)
    start_range5, end_range5 = range_ts5
    #start_range6, end_range6 = range_ts6
    
    # -------------------------
    # 3️⃣ Filter and Pivot
    # -------------------------
    # Filter DataFrame using the slider values
    
    filtered_df2 = df_faainal[
        (df_faainal["catalogusprijs"] >= start_range3) & 
        (df_faainal["catalogusprijs"] <= end_range3) & 
        (df_faainal["datum_eerste_toelating"] >= start_range4) & 
        (df_faainal["datum_eerste_toelating"] <= end_range4) &
        (df_faainal["maximale_constructiesnelheid"] >= start_range5) & 
        (df_faainal["maximale_constructiesnelheid"] <= end_range5)].copy()
        #(df_faainal["hour"] >= start_range6) & 
        #(df_faainal["hour"] <= end_range6)
        

################################################
#boxplot    
    fig2, ax2 = plt.subplots(figsize=(15, 12))
    sns.boxplot(
        data=filtered_df2,
        x="merk",
        y="maximale_constructiesnelheid"
    )
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig2)


######################################################
#relplot    
    g = sns.relplot(
    x="massa_rijklaar",
    y="maximale_constructiesnelheid",
    hue="klasse_hybride_elektrisch_voertuig",
    size="catalogusprijs",
    sizes=(40, 400),
    alpha=.5,
    palette="muted",
    height=6,
    data=filtered_df2)

    st.pyplot(g.fig)  # ✅ use the figure behind the FacetGrid



##################################################
#heatmap
    
    selected_brand = st.selectbox(
    "Selecteer een automerk",
    filtered_df2["merk"].unique())

    subset2 = filtered_df2[
        (filtered_df2["merk"] == selected_brand)].copy()
    
    sns.set_theme()
    
    subset2 = filtered_df2.groupby('handelsbenaming').filter(lambda x: len(x) > 500)
    
    # Pivot with aggregation
    flights = subset2.pivot_table(
        index="handelsbenaming",
        columns="jaar",
        values="datum_eerste_toelating",
        aggfunc="count"
    )
    
    # Create figure and heatmap
    f, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(flights, annot=True, fmt=".0f", linewidths=.5, cmap="YlGnBu", ax=ax)
    
    # ✅ Show in Streamlit
    st.pyplot(f)
























































































