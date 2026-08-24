
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------------
# EcoSim AI — Karachi Climate Simulation Lab
# Final Streamlit prototype
# ---------------------------------------------------------

st.set_page_config(
    page_title="EcoSim AI — Karachi Climate Simulation",
    page_icon="🌍",
    layout="wide"
)

# -----------------------------
# Baseline project data
# -----------------------------
BASE_TEMP = 41.75
BASE_GREEN = 0.155
KARACHI_AREA = 5841.13

BUILDINGS = 128285
PARKS = 1148
PARK_AREA = 9.04
WATER_BODIES = 279
WATER_AREA = 252.32

# -----------------------------
# Simulation assumptions
# -----------------------------
SURVIVAL_RATE = 0.80
CANOPY_PER_SURVIVING_TREE_KM2 = 0.00002

# Research-informed prototype cooling relationship:
# 0–10 percentage points canopy increase -> up to 0.8°C
# 10–20 -> additional 0.3°C
# 20–30 -> additional 0.4°C
# Above 30 -> capped at 1.5°C
def estimate_cooling(canopy_increase):
    if canopy_increase <= 0:
        return 0.0
    if canopy_increase <= 10:
        return 0.8 * (canopy_increase / 10)
    if canopy_increase <= 20:
        return 0.8 + 0.3 * ((canopy_increase - 10) / 10)
    if canopy_increase <= 30:
        return 1.1 + 0.4 * ((canopy_increase - 20) / 10)
    return 1.5

def calculate_co2_range(surviving_trees):
    low = surviving_trees * 10 / 1000
    high = surviving_trees * 25 / 1000
    return low, high

def run_ecosim(trees_planted, intervention_area):
    surviving = int(trees_planted * SURVIVAL_RATE)

    added_canopy = surviving * CANOPY_PER_SURVIVING_TREE_KM2

    # Cap canopy at the intervention-zone area
    added_canopy = min(added_canopy, intervention_area)

    canopy_increase = (added_canopy / intervention_area) * 100

    cooling = estimate_cooling(canopy_increase)
    estimated_temp = BASE_TEMP - cooling

    co2_low, co2_high = calculate_co2_range(surviving)

    return {
        "trees_planted": trees_planted,
        "surviving": surviving,
        "intervention_area": intervention_area,
        "added_canopy": added_canopy,
        "canopy_increase": canopy_increase,
        "green_before": BASE_GREEN,
        "green_after": BASE_GREEN + canopy_increase,
        "temp_before": BASE_TEMP,
        "cooling": cooling,
        "temp_after": estimated_temp,
        "co2_low": co2_low,
        "co2_high": co2_high,
    }

# -----------------------------
# Header
# -----------------------------
st.title("🌍 EcoSim AI")
st.subheader("Karachi Climate Simulation Lab")
st.write(
    "Explore how urban tree-planting interventions could affect green cover, "
    "urban temperature and annual CO₂ removal."
)

st.info(
    "⚠️ These are scenario-based estimates from a prototype model. "
    "They are not direct measurements or guaranteed future temperatures."
)

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("🌳 Intervention Settings")

trees = st.sidebar.slider(
    "Trees to Plant",
    min_value=10_000,
    max_value=2_000_000,
    value=500_000,
    step=10_000
)

area = st.sidebar.slider(
    "Planting Zone (km²)",
    min_value=10,
    max_value=500,
    value=100,
    step=10
)

result = run_ecosim(trees, area)

# -----------------------------
# Key metrics
# -----------------------------
st.markdown("## 📊 Simulation Results")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "🌳 Surviving Trees",
    f"{result['surviving']:,}",
    f"{SURVIVAL_RATE*100:.0f}% survival"
)

c2.metric(
    "🌿 Green Cover",
    f"{result['green_after']:.3f}%",
    f"+{result['canopy_increase']:.3f} percentage points"
)

c3.metric(
    "🌡️ Estimated Temperature",
    f"{result['temp_after']:.2f}°C",
    f"-{result['cooling']:.2f}°C"
)

c4.metric(
    "🌍 CO₂ Removal",
    f"{result['co2_low']:,.0f}–{result['co2_high']:,.0f}",
    "tons/year"
)

# -----------------------------
# Detailed results
# -----------------------------
st.markdown("### 🌱 Intervention Details")

details = pd.DataFrame({
    "Indicator": [
        "Trees Planted",
        "Estimated Surviving Trees",
        "Planting Zone",
        "Added Canopy",
        "Canopy Increase in Zone",
        "Baseline Temperature",
        "Estimated Cooling",
        "Estimated Temperature",
        "CO₂ Removal — Low",
        "CO₂ Removal — High"
    ],
    "Value": [
        f"{result['trees_planted']:,}",
        f"{result['surviving']:,}",
        f"{result['intervention_area']:.0f} km²",
        f"{result['added_canopy']:.2f} km²",
        f"{result['canopy_increase']:.2f} percentage points",
        f"{result['temp_before']:.2f}°C",
        f"{result['cooling']:.2f}°C",
        f"{result['temp_after']:.2f}°C",
        f"{result['co2_low']:,.0f} tons/year",
        f"{result['co2_high']:,.0f} tons/year"
    ]
})

st.dataframe(details, use_container_width=True, hide_index=True)

# -----------------------------
# Graphs
# -----------------------------
st.markdown("## 📈 Visual Analysis")

tab1, tab2, tab3 = st.tabs(
    ["🌡️ Temperature", "🌿 Green Cover", "🌍 CO₂"]
)

with tab1:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(
        ["Before", "After"],
        [result["temp_before"], result["temp_after"]]
    )
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("Estimated Temperature Impact")
    st.pyplot(fig)
    plt.close(fig)

with tab2:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(
        ["Before", "After"],
        [result["green_before"], result["green_after"]]
    )
    ax.set_ylabel("Green Cover (%)")
    ax.set_title("Estimated Green Cover Impact")
    st.pyplot(fig)
    plt.close(fig)

with tab3:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(
        ["Low Estimate", "High Estimate"],
        [result["co2_low"], result["co2_high"]]
    )
    ax.set_ylabel("CO₂ Removal (tons/year)")
    ax.set_title("Estimated Annual CO₂ Removal")
    st.pyplot(fig)
    plt.close(fig)

# -----------------------------
# Scenario comparison
# -----------------------------
st.markdown("## 🌳 Tree-Planting Scenarios")

scenario_trees = [100_000, 250_000, 500_000, 1_000_000]
scenario_rows = []

for n in scenario_trees:
    r = run_ecosim(n, area)
    scenario_rows.append({
        "Trees Planted": n,
        "Surviving Trees": r["surviving"],
        "Added Canopy (km²)": round(r["added_canopy"], 2),
        "Cooling (°C)": round(r["cooling"], 2),
        "Temperature (°C)": round(r["temp_after"], 2),
        "CO₂ Low (tons/year)": round(r["co2_low"]),
        "CO₂ High (tons/year)": round(r["co2_high"])
    })

scenario_df = pd.DataFrame(scenario_rows)
st.dataframe(scenario_df, use_container_width=True, hide_index=True)

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(
    scenario_df["Trees Planted"],
    scenario_df["Cooling (°C)"],
    marker="o"
)
ax.set_xlabel("Trees Planted")
ax.set_ylabel("Estimated Cooling (°C)")
ax.set_title("Tree Planting vs Estimated Cooling")
ax.grid(True)
st.pyplot(fig)
plt.close(fig)

# -----------------------------
# Karachi map
# -----------------------------
st.markdown("## 🗺️ Karachi Intervention Map")

st.write(
    "The map shows Karachi and the selected intervention zone. "
    "Use the layer control to switch between the standard map and satellite imagery."
)

m = folium.Map(
    location=[24.86, 67.01],
    zoom_start=10,
    tiles="OpenStreetMap"
)

# Satellite imagery basemap
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
          "World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri World Imagery",
    name="🛰️ Satellite Imagery",
    overlay=False,
    control=True
).add_to(m)

# Intervention zone (illustrative)
radius_m = max(1500, min(12_000, (area ** 0.5) * 1000))

folium.Circle(
    location=[24.86, 67.01],
    radius=radius_m,
    popup=f"Illustrative intervention zone: {area} km²",
    tooltip="EcoSim AI Intervention Zone",
    fill=True,
    fill_opacity=0.20
).add_to(m)

folium.Marker(
    [24.86, 67.01],
    popup="EcoSim AI — Karachi",
    tooltip="Karachi"
).add_to(m)

folium.LayerControl().add_to(m)

st_folium(m, width=None, height=550)

# -----------------------------
# Project information
# -----------------------------
st.markdown("## 🏙️ Karachi Baseline Data")

baseline = pd.DataFrame({
    "Indicator": [
        "Karachi Area",
        "Buildings",
        "Parks",
        "Park Area",
        "Water Bodies",
        "Water Area",
        "Current Park Cover"
    ],
    "Value": [
        f"{KARACHI_AREA:,.2f} km²",
        f"{BUILDINGS:,}",
        f"{PARKS:,}",
        f"{PARK_AREA:.2f} km²",
        f"{WATER_BODIES:,}",
        f"{WATER_AREA:.2f} km²",
        f"{BASE_GREEN:.3f}%"
    ]
})

st.dataframe(baseline, use_container_width=True, hide_index=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption(
    "EcoSim AI — Karachi Climate Simulation Lab | "
    "SDG 11: Sustainable Cities and Communities | "
    "Related SDG 13: Climate Action"
)
