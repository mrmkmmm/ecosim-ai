import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from textwrap import dedent

# =========================================================
# PAGE
# =========================================================
st.set_page_config(
    page_title="EcoSim AI | Karachi Climate Simulator",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# STYLE
# =========================================================
st.markdown(dedent("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #F7FAF8;
    color: #18372A;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.4rem;
    padding-bottom: 2.5rem;
}

/* Header */
.eco-hero {
    background: linear-gradient(135deg, #E8F7EC 0%, #F6FBF7 62%, #E9F5F5 100%);
    border: 1px solid #D4E9DA;
    border-radius: 22px;
    padding: 28px 32px;
    margin-bottom: 20px;
    box-shadow: 0 7px 24px rgba(35, 90, 60, 0.06);
}

.eco-badge {
    display: inline-block;
    background: #D8F1DF;
    color: #177545;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .7px;
    margin-bottom: 9px;
}

.eco-title {
    font-size: 42px;
    line-height: 1.1;
    font-weight: 800;
    color: #123D2C;
    margin: 0;
}

.eco-subtitle {
    color: #5A7167;
    font-size: 15px;
    margin-top: 7px;
}

/* Section titles */
.section-title {
    color: #173D2E;
    font-size: 21px;
    font-weight: 800;
    margin: 22px 0 11px 0;
}

/* Cards */
.eco-card {
    background: #FFFFFF;
    border: 1px solid #DFEAE3;
    border-radius: 17px;
    padding: 19px;
    min-height: 112px;
    box-shadow: 0 5px 18px rgba(25, 70, 50, 0.045);
}

.card-label {
    color: #71837A;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .3px;
}

.card-value {
    color: #167443;
    font-size: 27px;
    font-weight: 800;
    margin-top: 5px;
}

.card-note {
    color: #71857B;
    font-size: 11px;
    margin-top: 3px;
}

/* Insight */
.insight {
    background: #F0F8F2;
    border: 1px solid #D7ECDD;
    border-radius: 17px;
    padding: 20px;
    min-height: 250px;
}

.insight h3 {
    color: #177545;
    margin-top: 0;
}

.insight p {
    color: #52685E;
    line-height: 1.6;
    font-size: 13px;
}

/* Info */
.info-box {
    background: #EEF7FA;
    border: 1px solid #D6E9EF;
    border-radius: 12px;
    padding: 12px 15px;
    color: #46636C;
    font-size: 12px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #F1F8F3;
    border-right: 1px solid #DCE9E0;
}

section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #177545 !important;
}

section[data-testid="stSidebar"] label {
    color: #355548 !important;
    font-weight: 600 !important;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid #249B5A;
    background: #249B5A;
    color: white;
    font-weight: 700;
}

.stButton > button:hover {
    background: #1C824A;
    border-color: #1C824A;
}

/* Footer */
.eco-footer {
    text-align: center;
    color: #7A8B83;
    font-size: 12px;
    padding: 25px 0 8px 0;
}

.eco-footer b {
    color: #177545;
}
</style>
"""), unsafe_allow_html=True)

# =========================================================
# MODEL
# =========================================================
BASE_TEMP = 41.75
BASE_GREEN = 15.5
SURVIVAL_RATE = 0.80
CANOPY_PER_TREE = 0.00002

KARACHI_AREA = 5841.13
BUILDINGS = 128285
PARKS = 1148
PARK_AREA = 9.04
WATER_BODIES = 279
WATER_AREA = 252.32


def estimate_cooling(canopy_increase):
    if canopy_increase <= 0:
        return 0.0
    if canopy_increase <= 10:
        return 0.8 * canopy_increase / 10
    if canopy_increase <= 20:
        return 0.8 + 0.3 * (canopy_increase - 10) / 10
    if canopy_increase <= 30:
        return 1.1 + 0.4 * (canopy_increase - 20) / 10
    return 1.5


def calculate_co2(trees):
    return trees * 10 / 1000, trees * 25 / 1000


def run_ecosim(trees, area):
    surviving = int(trees * SURVIVAL_RATE)
    added_canopy = min(surviving * CANOPY_PER_TREE, area)
    canopy_increase = (added_canopy / area) * 100 if area else 0
    cooling = estimate_cooling(canopy_increase)
    temp_after = BASE_TEMP - cooling
    green_after = BASE_GREEN + canopy_increase
    co2_low, co2_high = calculate_co2(surviving)

    return {
        "trees": trees,
        "surviving": surviving,
        "area": area,
        "canopy": added_canopy,
        "canopy_increase": canopy_increase,
        "green_before": BASE_GREEN,
        "green_after": green_after,
        "temp_before": BASE_TEMP,
        "temp_after": temp_after,
        "cooling": cooling,
        "co2_low": co2_low,
        "co2_high": co2_high,
    }


# =========================================================
# HEADER
# =========================================================
st.markdown(dedent("""
<div class="eco-hero">
    <div class="eco-badge">🌱 CLIMATE SIMULATION • KARACHI</div>
    <div class="eco-title">EcoSim AI</div>
    <div class="eco-subtitle">
        Simulate how urban tree planting could create a cooler,
        greener and more sustainable Karachi.
    </div>
</div>
"""), unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 🌱 Simulation Controls")
st.sidebar.caption("Create a Karachi tree-planting scenario.")

trees = st.sidebar.slider(
    "🌳 Trees to Plant",
    10_000, 2_000_000, 500_000, 10_000
)

area = st.sidebar.slider(
    "📍 Intervention Area (km²)",
    10, 500, 100, 10
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Model Assumptions")
st.sidebar.caption("🌳 Tree survival: 80%")
st.sidebar.caption("🌿 Canopy: 0.00002 km²/tree")
st.sidebar.caption("🌡️ Cooling: scenario-based")
st.sidebar.caption("🌍 CO₂: 10–25 kg/tree/year")

result = run_ecosim(trees, area)

# =========================================================
# NOTICE
# =========================================================
st.markdown(dedent("""
<div class="info-box">
⚠️ <b>Scenario estimate:</b> EcoSim AI uses defined assumptions to explore
possible environmental outcomes. Results are estimates, not guaranteed forecasts.
</div>
"""), unsafe_allow_html=True)

# =========================================================
# KPI
# =========================================================
st.markdown('<div class="section-title">📊 Simulation Results</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(dedent(f"""
    <div class="eco-card">
        <div class="card-label">🌳 TREES SURVIVING</div>
        <div class="card-value">{result["surviving"]:,}</div>
        <div class="card-note">80% estimated survival</div>
    </div>
    """), unsafe_allow_html=True)

with c2:
    st.markdown(dedent(f"""
    <div class="eco-card">
        <div class="card-label">🌿 GREEN COVER</div>
        <div class="card-value">{result["green_after"]:.2f}%</div>
        <div class="card-note">+{result["canopy_increase"]:.2f} percentage points</div>
    </div>
    """), unsafe_allow_html=True)

with c3:
    st.markdown(dedent(f"""
    <div class="eco-card">
        <div class="card-label">🌡️ TEMPERATURE</div>
        <div class="card-value">{result["temp_after"]:.2f}°C</div>
        <div class="card-note">↓ {result["cooling"]:.2f}°C estimated cooling</div>
    </div>
    """), unsafe_allow_html=True)

with c4:
    st.markdown(dedent(f"""
    <div class="eco-card">
        <div class="card-label">🌍 CO₂ REMOVAL / YEAR</div>
        <div class="card-value">{result["co2_low"]:,.0f}–{result["co2_high"]:,.0f}</div>
        <div class="card-note">estimated tonnes per year</div>
    </div>
    """), unsafe_allow_html=True)

# =========================================================
# GRAPH + AI INSIGHTS
# =========================================================
left, right = st.columns([1.25, 0.75])

with left:
    st.markdown('<div class="section-title">📈 Climate Impact</div>', unsafe_allow_html=True)

    years = [0, 5, 10, 15, 20]
    temps = [
        result["temp_before"],
        result["temp_before"] - result["cooling"] * 0.25,
        result["temp_before"] - result["cooling"] * 0.50,
        result["temp_before"] - result["cooling"] * 0.75,
        result["temp_after"],
    ]
    green = [
        result["green_before"],
        result["green_before"] + result["canopy_increase"] * 0.25,
        result["green_before"] + result["canopy_increase"] * 0.50,
        result["green_before"] + result["canopy_increase"] * 0.75,
        result["green_after"],
    ]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(years, temps, marker="o", linewidth=2.4, label="Temperature (°C)")
    ax.plot(years, green, marker="o", linewidth=2.4, label="Green Cover (%)")
    ax.set_xlabel("Years")
    ax.grid(alpha=0.15)
    ax.legend()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with right:
    st.markdown('<div class="section-title">🤖 AI Insights</div>', unsafe_allow_html=True)

    if result["cooling"] >= 1.2:
        assessment = "This scenario shows a strong potential cooling effect with meaningful improvement in green cover."
    elif result["cooling"] >= 0.6:
        assessment = "This scenario shows a moderate cooling effect with a noticeable improvement in green cover."
    else:
        assessment = "This scenario has a smaller estimated impact. Try increasing trees or intervention area."

    st.markdown(dedent(f"""
    <div class="insight">
        <h3>Scenario Assessment</h3>
        <p>{assessment}</p>
        <hr>
        <p>
        🌡️ Cooling: <b>{result["cooling"]:.2f}°C</b><br><br>
        🌿 Green cover increase: <b>{result["canopy_increase"]:.2f}%</b><br><br>
        🌍 CO₂ removal: <b>{result["co2_low"]:,.0f}–{result["co2_high"]:,.0f} t/year</b>
        </p>
        <hr>
        <p><b>Recommendation:</b> Test different tree counts and intervention
        areas and compare the resulting environmental impact.</p>
    </div>
    """), unsafe_allow_html=True)

# =========================================================
# SATELLITE MAP
# =========================================================
st.markdown('<div class="section-title">🛰️ Karachi Satellite Map</div>', unsafe_allow_html=True)
st.caption("Switch layers using the map control. The green zone represents the selected intervention area.")

karachi_map = folium.Map(
    location=[24.86, 67.01],
    zoom_start=10,
    tiles="OpenStreetMap"
)

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Esri World Imagery",
    name="🛰️ Satellite",
    overlay=False,
    control=True,
).add_to(karachi_map)

radius = max(1500, min(12000, (area ** 0.5) * 1000))

folium.Circle(
    location=[24.86, 67.01],
    radius=radius,
    popup=f"EcoSim AI intervention zone: {area} km²",
    tooltip="🌱 Proposed Intervention Zone",
    color="#249B5A",
    fill=True,
    fill_color="#63C174",
    fill_opacity=0.20,
).add_to(karachi_map)

folium.Marker(
    [24.86, 67.01],
    popup="🌍 EcoSim AI — Karachi",
    tooltip="Karachi",
).add_to(karachi_map)

folium.LayerControl().add_to(karachi_map)

st_folium(karachi_map, width=None, height=500)

# =========================================================
# BEFORE / AFTER
# =========================================================
st.markdown('<div class="section-title">🔎 Before vs After</div>', unsafe_allow_html=True)

b1, b2 = st.columns(2)

with b1:
    st.markdown(dedent(f"""
    <div class="eco-card">
        <div class="card-label">CURRENT BASELINE</div>
        <h3>🌡️ {result["temp_before"]:.2f}°C</h3>
        <p>🌿 Green Cover: <b>{result["green_before"]:.2f}%</b></p>
        <p>🌳 Trees in scenario: <b>0</b></p>
    </div>
    """), unsafe_allow_html=True)

with b2:
    st.markdown(dedent(f"""
    <div class="eco-card">
        <div class="card-label">ECOSIM SCENARIO</div>
        <h3>🌡️ {result["temp_after"]:.2f}°C</h3>
        <p>🌿 Green Cover: <b>{result["green_after"]:.2f}%</b></p>
        <p>🌳 Trees Surviving: <b>{result["surviving"]:,}</b></p>
    </div>
    """), unsafe_allow_html=True)

# =========================================================
# QUICK COMPARISON
# =========================================================
st.markdown('<div class="section-title">🌳 Quick Scenario Comparison</div>', unsafe_allow_html=True)

scenario_rows = []
for number in [100_000, 250_000, 500_000, 1_000_000]:
    x = run_ecosim(number, area)
    scenario_rows.append({
        "Trees Planted": f"{number:,}",
        "Surviving": f'{x["surviving"]:,}',
        "Cooling": f'{x["cooling"]:.2f}°C',
        "CO₂ Removal": f'{x["co2_low"]:,.0f}–{x["co2_high"]:,.0f} t/year',
    })

st.dataframe(pd.DataFrame(scenario_rows), use_container_width=True, hide_index=True)

# =========================================================
# KARACHI BASELINE
# =========================================================
with st.expander("🏙️ Karachi Baseline Data"):
    baseline = pd.DataFrame({
        "Indicator": [
            "City Area", "Buildings", "Parks", "Park Area",
            "Water Bodies", "Water Area", "Current Green Cover"
        ],
        "Value": [
            f"{KARACHI_AREA:,.2f} km²",
            f"{BUILDINGS:,}",
            f"{PARKS:,}",
            f"{PARK_AREA:.2f} km²",
            f"{WATER_BODIES:,}",
            f"{WATER_AREA:.2f} km²",
            f"{BASE_GREEN:.2f}%"
        ]
    })
    st.dataframe(baseline, use_container_width=True, hide_index=True)

# =========================================================
# FOOTER
# =========================================================
st.markdown(dedent("""
<div class="eco-footer">
    🌱 <b>EcoSim AI</b> • Karachi Climate Simulation Lab<br><br>
    SDG 11 • Sustainable Cities & Communities &nbsp; | &nbsp; SDG 13 • Climate Action
    <br><br>
    <b>Made by Mukarram</b> 💚
</div>
"""), unsafe_allow_html=True)

