# Netflix Interactive EDA Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE CONFIG
st.set_page_config(
    page_title="Netflix Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# LOAD DATA
@st.cache_data
def load_data():
    net = pd.read_csv("netflix_clean.csv")
    return net

net = load_data()

# CSS ANIMATIONS
# SIDEBAR STYLING & ANIMATION
st.markdown("""
    <style>
    /* Sidebar background gradient */
    [data-testid="stSidebar"] {
        background: #000000;
        color: white;
        animation: slideIn 0.6s ease-out;
    }

    /* Force multiselect chip colors */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #3F1154 !important;
        border-radius: 6px !important;
    }

    /* Chip text */
    .stMultiSelect [data-baseweb="tag"] span {
        color: white !important;
        font-weight: 500;
    }

    /* Close icon */
    .stMultiSelect [data-baseweb="tag"] svg {
        fill: white !important;
    }

    /* Sidebar slide-in animation */
    @keyframes slideIn {
        0% {transform: translateX(-100%); opacity: 0;}
        100% {transform: translateX(0); opacity: 1;}
    }

    /* Sidebar header */
    .sidebar-header {
        font-size: 24px;
        font-weight: bold;
        color: white;
        margin-bottom: 10px;
        animation: fadeIn 1s ease-in-out;
    }

    /* Sidebar labels */
    label {
        font-weight: 600;
        color: #e5e5e5 !important;
    }

    /* Inputs hover effect */
    .stMultiSelect, .stSlider, .stTextInput {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stMultiSelect:hover, .stSlider:hover, .stTextInput:hover {
        transform: scale(1.01);
        box-shadow: 0px 0px 8px rgba(229, 9, 20, 0.6);
    }

    /* Divider animation */
    .sidebar-divider {
        height: 2px;
        background: linear-gradient(90deg, #E50914, transparent);
        margin: 15px 0;
        animation: growWidth 1s ease-in-out;
    }
    @keyframes growWidth {
        from {width: 0;}
        to {width: 100%;}
    }

    /* Fade-in keyframes */
    @keyframes fadeIn {
        0% {opacity: 0; transform: translateY(-10px);}
        100% {opacity: 1; transform: translateY(0);}
    }

    /* KPI Cards hover effect */
    [data-testid="stMetric"] {
        background-color: #1f1f1f;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    [data-testid="stMetric"]:hover {
        transform: scale(1.05);
        box-shadow: 0px 4px 20px rgba(229, 9, 20, 0.5);
        border-color: rgba(229, 9, 20, 0.8);
    }

    /* Main dashboard background gradient */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #000000, #1c1c1c, #3F1154);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.markdown("<div class='sidebar-header'>🔍 Filters</div>", unsafe_allow_html=True)

type_filter = st.sidebar.multiselect(
    "Select Type:",
    options=net["type"].unique(),
    default=net["type"].unique()
)
st.sidebar.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

year_range = st.sidebar.slider(
    "Select Year Added:",
    int(net["year_added"].min()),
    int(net["year_added"].max()),
    (int(net["year_added"].min()), int(net["year_added"].max()))
)
st.sidebar.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

genre_filter = st.sidebar.multiselect(
    "Select Genre:",
    options=net["main_genre"].unique(),
    default=net["main_genre"].unique()
)
# DATA FILTERING
net_filtered = net[
    (net["type"].isin(type_filter)) &
    (net["year_added"] >= year_range[0]) &
    (net["year_added"] <= year_range[1]) &
    (net["main_genre"].isin(genre_filter))
]

# HEADER
st.markdown("<h1 class='fade-in'>🎬 Netflix EDA Dashboard</h1>", unsafe_allow_html=True)

# KPI CARDS
col1, col2, col3 = st.columns(3)
col1.metric("Total Titles", len(net_filtered))
col2.metric("Movies", len(net_filtered[net_filtered["type"] == "Movie"]))
col3.metric("TV Shows", len(net_filtered[net_filtered["type"] == "TV Show"]))

st.markdown("---")

# COUNT OF MOVIES VS TV SHOWS
st.subheader("📊 Count of Movies vs TV Shows")
count_df = net_filtered["type"].value_counts()
count_fig = px.bar(
    x=count_df.index,
    y=count_df.values,
    title="Count of Movies vs TV Shows",
    template="plotly_white"
)
count_fig.update_layout(showlegend=False)
st.plotly_chart(count_fig, use_container_width=True, key="chart1")

# TOP 10 GENRES
st.subheader("🎭 Top 10 Genres")
top_genres = net_filtered["main_genre"].value_counts().head(10).reset_index()
top_genres.columns = ["Genre", "Count"]
genre_fig = px.bar(
    top_genres,
    x="Count", y="Genre",
    orientation="h",
    color="Genre",
    color_discrete_sequence=px.colors.sequential.Viridis
)
genre_fig.update_layout(showlegend=False, template="plotly_white")
st.plotly_chart(genre_fig, use_container_width=True, key="chart2")

# YEARLY TREND (Animated)
st.subheader("📈 Yearly Releases Trend (Animated)")
yearly_counts = net_filtered.groupby(["year_added", "type"]).size().reset_index(name="Count")
yearly_counts = yearly_counts.sort_values(by="year_added")  # Ensure proper animation sequence

trend_fig = px.bar(
    yearly_counts,
    x="type", y="Count",
    color="type",
    animation_frame="year_added",
    range_y=[0, yearly_counts["Count"].max() + 10],
    template="plotly_white",
    title="Number of Releases Over the Years"
)

# Animation speed tweak
trend_fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 800
trend_fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500

st.plotly_chart(trend_fig, use_container_width=True, key="chart3")

# SEARCH BAR
st.subheader("🔎 Search Titles")
search_query = st.text_input("Search for a Movie/Show:")
if search_query:
    search_results = net_filtered[net_filtered["title"].str.contains(search_query, case=False, na=False)]
    st.write(f"Found {len(search_results)} results")
    st.dataframe(search_results)

# DOWNLOAD
csv = net_filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇ Download Filtered Data",
    data=csv,
    file_name="netflix_filtered.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("Netflix EDA Dashboard - Made by Atharwa")
