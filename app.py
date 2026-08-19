import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="EcoSim AI | Karachi Climate Simulator",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM UI
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #F7FAF8;
    color: #17352A;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* ================= HEADER ================= */

.hero {
    background: linear-gradient(
        135deg,
        #E7F5EC 0%,
        #F4FAF6 55%,
        #EAF4F7 100%
    );

    border: 1px solid #D5E9DC;
    border-radius: 22px;

    padding: 28px 32px;
    margin-bottom: 22px;

    box-shadow: 0 8px 25px rgba(30, 80, 55, 0.06);
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: #123D2C;
    margin-bottom: 2px;
}

.hero-subtitle {
    color: #557267;
    font-size: 16px;
}

.hero-badge {
    display: inline-block;
    background: #D8F1DF;
    color: #187344;
    padding: 6px 13px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 10px;
}

/* ================= CARDS ================= */

.card {
    background: #FFFFFF;
    border: 1px solid #DFEAE3;
    border-radius: 17px;
    padding: 20px;
    box-shadow: 0 5px 20px rgba(25, 70, 50, 0.05);
    height: 100%;
}

.metric-label {
    color: #708279;
    font-size: 13px;
    font-weight: 600;
}

.metric-value {
    color: #176B42;
    font-size: 28px;
    font-weight: 800;
    margin-top: 6px;
}

.metric-small {
    color: #71857B;
    font-size: 12px;
    margin-top: 4px;
}

/* ================= SECTION ================= */

.section-title {
    color: #173D2E;
    font-size: 22px;
    font-weight: 750;
    margin-top: 25px;
    margin-bottom: 12px;
}

/* ================= INSIGHTS ================= */

.insight-card {
    background: #F0F8F2;
    border: 1px solid #D7ECDD;
    border-radius: 17px;
    padding: 22px;
}

.insight-title {
    color: #176B42;
    font-size: 18px;
    font-weight: 750;
}

.insight-text {
    color: #50665C;
    line-height: 1.65;
    font-size: 14px;
}

/* ================= INFO ================= */

.info-box {
    background: #EEF7FA;
    border: 1px solid #D6E9EF;
    border-radius: 13px;
    padding: 13px 17px;
    color: #41606A;
    font-size: 13px;
}

/* ================= SIDEBAR ================= */

section[data-testid="stSidebar"] {
    background: #F1F7F3;
    border-right: 1px solid #DCE9E0;
}

section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #176B42 !important;
}

section[data-testid="stSidebar"] label {
    color: #345448 !important;
    font-weight: 600 !important;
}

/* ================= BUTTON ================= */

.stButton > button {
    width: 100%;
    border-radius: 11px;
    border: none;
    background: #249B5A;
    color: white;
    font-weight: 700;
    padding: 0.65rem 1rem;
}

.stButton > button:hover {
    background: #1C824A;
}

/* ================= FOOTER ================= */

.footer {
    text-align: center;
    color: #7B8C84;
    font-size: 12px;
    padding: 25px 0 10px 0;
}

.footer strong {
    color: #176B42;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# BASELINE DATA
# =========================================================

BASE_TEMP = 41.75
BASE_GREEN = 0.155

KARACHI_AREA = 5841.13
BUILDINGS = 128285
PARKS = 1148
PARK_AREA = 9.04
WATER_BODIES = 279
WATER_AREA = 252.32

# =========================================================
# MODEL PARAMETERS
# =========================================================

SURVIVAL_RATE = 0.80
CANOPY_PER_TREE = 0.00002


# =========================================================
# COOLING MODEL
# =========================================================

def estimate_cooling(canopy_increase):

    if canopy_increase <= 0:
        return 0

    elif canopy_increase <= 10:
        return 0.8 * (canopy_increase / 10)

    elif canopy_increase <= 20:
        return 0.8 + (
            0.3 * ((canopy_increase - 10) / 10)
        )

    elif canopy_increase <= 30:
        return 1.1 + (
            0.4 * ((canopy_increase - 20) / 10)
        )

    else:
        return 1.5


# =========================================================
# CO2 MODEL
# =========================================================

def calculate_co2_range(trees):

    low_rate = 10
    high_rate = 25

    low = trees * low_rate / 1000
    high = trees * high_rate / 1000

    return low, high


# =========================================================
# ECOSIM ENGINE
# =========================================================

def run_ecosim(trees_planted, intervention_area):

    surviving_trees = int(
        trees_planted * SURVIVAL_RATE
    )

    added_canopy = (
        surviving_trees * CANOPY_PER_TREE
    )

    added_canopy = min(
        added_canopy,
        intervention_area
    )

    canopy_increase = (
        added_canopy /
        intervention_area
    ) * 100

    cooling = estimate_cooling(
        canopy_increase
    )

    predicted_temperature = (
        BASE_TEMP - cooling
    )

    new_green_cover = (
        BASE_GREEN + canopy_increase
    )

    co2_low, co2_high = calculate_co2_range(
        surviving_trees
    )

    return {
        "trees_planted": trees_planted,
        "surviving_trees": surviving_trees,
        "intervention_area": intervention_area,
        "added_canopy": added_canopy,
        "canopy_increase": canopy_increase,
        "green_before": BASE_GREEN,
        "green_after": new_green_cover,
        "temperature_before": BASE_TEMP,
        "temperature_after": predicted_temperature,
        "cooling": cooling,
        "co2_low": co2_low,
        "co2_high": co2_high
    }


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">

    <div class="hero-badge">
        🌱 CLIMATE SIMULATION • KARACHI
    </div>

    <div class="hero-title">
        EcoSim AI
    </div>

    <div class="hero-subtitle">
        Explore how urban tree planting could create a cooler,
        greener and more sustainable Karachi.
    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("## 🌱 Simulation Controls")

st.sidebar.caption(
    "Create a tree-planting scenario and explore its estimated impact."
)

st.sidebar.markdown("---")

trees = st.sidebar.slider(
    "🌳 Trees to Plant",
    min_value=10_000,
    max_value=2_000_000,
    value=500_000,
    step=10_000
)

area = st.sidebar.slider(
    "📍 Intervention Area (km²)",
    min_value=10,
    max_value=500,
    value=100,
    step=10
)

st.sidebar.markdown("---")

st.sidebar.markdown("### Model Assumptions")

st.sidebar.caption("🌳 Estimated tree survival: 80%")
st.sidebar.caption("🌿 Canopy generation: 0.00002 km²/tree")
st.sidebar.caption("🌡️ Cooling: scenario-based")
st.sidebar.caption("🌍 CO₂ removal: 10–25 kg/tree/year")

st.sidebar.markdown("---")

st.sidebar.success(
    "Tip: Try different tree counts and intervention areas "
    "to compare scenarios."
)


# =========================================================
# RUN MODEL
# =========================================================

result = run_ecosim(
    trees,
    area
)


# =========================================================
# DISCLAIMER
# =========================================================

st.markdown("""
<div class="info-box">

⚠️ <b>Scenario Estimate:</b>
EcoSim AI provides an exploratory model based on defined assumptions.
The results are estimates and should not be interpreted as guaranteed
future measurements.

</div>
""", unsafe_allow_html=True)


# =========================================================
# KPI CARDS
# =========================================================

st.markdown(
    '<div class="section-title">📊 Simulation Results</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(f"""
    <div class="card">

        <div class="metric-label">
            🌳 TREES SURVIVING
        </div>

        <div class="metric-value">
            {result["surviving_trees"]:,}
        </div>

        <div class="metric-small">
            Estimated survival rate: 80%
        </div>

    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown(f"""
    <div class="card">

        <div class="metric-label">
            🌿 GREEN COVER
        </div>

        <div class="metric-value">
            {result["green_after"]:.2f}%
        </div>

        <div class="metric-small">
            +{result["canopy_increase"]:.2f} percentage points
        </div>

    </div>
    """, unsafe_allow_html=True)


with col3:

    st.markdown(f"""
    <div class="card">

        <div class="metric-label">
            🌡️ TEMPERATURE
        </div>

        <div class="metric-value">
            {result["temperature_after"]:.2f}°C
        </div>

        <div class="metric-small">
            ↓ {result["cooling"]:.2f}°C estimated cooling
        </div>

    </div>
    """, unsafe_allow_html=True)


with col4:

    st.markdown(f"""
    <div class="card">

        <div class="metric-label">
            🌍 CO₂ REMOVAL
        </div>

        <div class="metric-value">
            {result["co2_low"]:,.0f}–{result["co2_high"]:,.0f}
        </div>

        <div class="metric-small">
            tonnes / year
        </div>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# MAIN VISUAL AREA
# =========================================================

left, right = st.columns([1.15, 1])


# =========================================================
# GRAPH
# =========================================================

with left:

    st.markdown(
        '<div class="section-title">📈 Climate Impact</div>',
        unsafe_allow_html=True
    )

    fig, ax = plt.subplots(figsize=(8, 4.2))

    years = [0, 5, 10, 15, 20]

    temperature_values = [
        result["temperature_before"],
        result["temperature_before"] - result["cooling"] * 0.25,
        result["temperature_before"] - result["cooling"] * 0.50,
        result["temperature_before"] - result["cooling"] * 0.75,
        result["temperature_after"]
    ]

    green_values = [
        result["green_before"],
        result["green_before"] + result["canopy_increase"] * 0.25,
        result["green_before"] + result["canopy_increase"] * 0.50,
        result["green_before"] + result["canopy_increase"] * 0.75,
        result["green_after"]
    ]

    ax.plot(
        years,
        temperature_values,
        marker="o",
        linewidth=2.5,
        label="Temperature (°C)"
    )

    ax.plot(
        years,
        green_values,
        marker="o",
        linewidth=2.5,
        label="Green Cover (%)"
    )

    ax.set_xlabel("Years")
    ax.set_title("Projected Environmental Change")
    ax.grid(alpha=0.15)
    ax.legend()

    st.pyplot(fig, use_container_width=True)

    plt.close(fig)


# =========================================================
# AI INSIGHTS
# =========================================================

with right:

    st.markdown(
        '<div class="section-title">🤖 AI Insights</div>',
        unsafe_allow_html=True
    )

    if result["cooling"] >= 1.2:

        assessment = (
            "This scenario shows a strong potential cooling effect "
            "with meaningful improvement in urban green cover."
        )

    elif result["cooling"] >= 0.6:

        assessment = (
            "This scenario shows a moderate cooling effect and "
            "a noticeable improvement in green cover."
        )

    else:

        assessment = (
            "This scenario produces a smaller environmental effect. "
            "Increasing tree coverage could improve the impact."
        )

    st.markdown(f"""
    <div class="insight-card">

        <div class="insight-title">
            Scenario Assessment
        </div>

        <p class="insight-text">
            {assessment}
        </p>

        <hr>

        <b>Key Takeaways</b>

        <p class="insight-text">
            🌡️ Estimated cooling:
            <b>{result["cooling"]:.2f}°C</b>
            <br><br>

            🌿 Green cover increase:
            <b>{result["canopy_increase"]:.2f}%</b>
            <br><br>

            🌍 Annual CO₂ removal:
            <b>{result["co2_low"]:,.0f}–{result["co2_high"]:,.0f} tonnes</b>
        </p>

        <hr>

        <b>Recommendation</b>

        <p class="insight-text">
            Consider testing a larger intervention area or higher
            tree count and compare the resulting environmental impact.
        </p>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SATELLITE MAP
# =========================================================

st.markdown(
    '<div class="section-title">🛰️ Karachi Intervention Map</div>',
    unsafe_allow_html=True
)

st.caption(
    "Explore Karachi using satellite imagery and view the estimated intervention zone."
)

karachi_map = folium.Map(
    location=[24.86, 67.01],
    zoom_start=10,
    tiles="OpenStreetMap"
)


# Satellite imagery

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/"
        "ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/"
        "{z}/{y}/{x}"
    ),
    attr="Esri World Imagery",
    name="🛰️ Satellite",
    overlay=False,
    control=True
).add_to(karachi_map)


# Intervention radius

radius = max(
    1500,
    min(
        12000,
        (area ** 0.5) * 1000
    )
)


folium.Circle(
    location=[24.86, 67.01],
    radius=radius,
    popup=f"EcoSim AI intervention zone: {area} km²",
    tooltip="🌱 Proposed Intervention Zone",
    color="#36A866",
    fill=True,
    fill_color="#36A866",
    fill_opacity=0.20
).add_to(karachi_map)


# Karachi marker

folium.Marker(
    [24.86, 67.01],
    popup="🌍 EcoSim AI — Karachi",
    tooltip="Karachi"
).add_to(karachi_map)


folium.LayerControl().add_to(karachi_map)


st_folium(
    karachi_map,
    width=None,
    height=500
)


# =========================================================
# BEFORE / AFTER
# =========================================================

st.markdown(
    '<div class="section-title">🔎 Before vs After</div>',
    unsafe_allow_html=True
)

before_col, after_col = st.columns(2)


with before_col:

    st.markdown(f"""
    <div class="card">

        <div class="metric-label">
            CURRENT BASELINE
        </div>

        <h3>🌡️ {result["temperature_before"]:.2f}°C</h3>

        <p>
        🌿 Green Cover: <b>{result["green_before"]:.2f}%</b>
        </p>

        <p>
        🌳 Trees Planned: <b>0</b>
        </p>

    </div>
    """, unsafe_allow_html=True)


with after_col:

    st.markdown(f"""
    <div class="card">

        <div class="metric-label">
            ECO SIMULATION
        </div>

        <h3>🌡️ {result["temperature_after"]:.2f}°C</h3>

        <p>
        🌿 Green Cover: <b>{result["green_after"]:.2f}%</b>
        </p>

        <p>
        🌳 Trees Surviving: <b>{result["surviving_trees"]:,}</b>
        </p>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SIMPLE SCENARIO TABLE
# =========================================================

st.markdown(
    '<div class="section-title">🌳 Quick Scenario Comparison</div>',
    unsafe_allow_html=True
)

scenario_trees = [
    100_000,
    250_000,
    500_000,
    1_000_000
]

scenario_results = []

for number in scenario_trees:

    x = run_ecosim(number, area)

    scenario_results.append({
        "Trees Planted": f"{number:,}",
        "Surviving": f'{x["surviving_trees"]:,}',
        "Cooling": f'{x["cooling"]:.2f}°C',
        "CO₂ Removal": f'{x["co2_low"]:,.0f}–{x["co2_high"]:,.0f} t/yr'
    })


scenario_df = pd.DataFrame(
    scenario_results
)

st.dataframe(
    scenario_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">

    🌱 <strong>EcoSim AI</strong>
    <br>
    Karachi Climate Simulation Lab
    <br><br>

    SDG 11 • Sustainable Cities & Communities
    &nbsp; | &nbsp;
    SDG 13 • Climate Action

    <br><br>

    <strong>Made by Mukarram</strong> 💚

</div>
""", unsafe_allow_html=True)
