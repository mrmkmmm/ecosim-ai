import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from textwrap import dedent
from datetime import date

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
    background: linear-gradient(180deg, #EFFAF3 0%, #F5FAF6 45%, #F2F8FA 100%);
    color: #18372A;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.1rem;
    padding-bottom: 2.5rem;
}

/* Top bar with badges */
.topbar {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 14px;
    margin-bottom: 26px;
    padding: 26px 20px 22px 20px;
    background: linear-gradient(135deg, #E4F7EA 0%, #EAF7F4 55%, #E9F1FC 100%);
    border: 1px solid #DCEEE1;
    border-radius: 22px;
    box-shadow: 0 8px 26px rgba(25, 120, 80, 0.07);
}

.eco-title-row {
    display: flex;
    align-items: baseline;
    justify-content: center;
    gap: 8px;
}

.eco-title {
    font-size: 38px;
    line-height: 1.1;
    font-weight: 800;
    background: linear-gradient(90deg, #0F7A44, #16A085);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}

.eco-subtitle {
    color: #4E6A5D;
    font-size: 15px;
    margin-top: 2px;
}

.badge-row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    justify-content: center;
}

.eco-pill {
    background: #FFFFFF;
    border: 1px solid #E1EAE4;
    border-radius: 12px;
    padding: 9px 16px;
    font-size: 12.5px;
    color: #2A4137;
    box-shadow: 0 3px 10px rgba(25,70,50,0.06);
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 150px;
}

.eco-pill .pill-label {
    font-weight: 700;
    color: #17392C;
    display: block;
    font-size: 13px;
}

.eco-pill .pill-sub {
    color: #7C8C83;
    font-size: 11px;
}

/* Section titles */
.section-title {
    color: #173D2E;
    font-size: 18px;
    font-weight: 800;
    margin: 6px 0 12px 0;
}

/* Metric cards */
.eco-card {
    background: #FFFFFF;
    border: 1px solid #E7EFE9;
    border-radius: 16px;
    padding: 18px;
    min-height: 108px;
    box-shadow: 0 6px 18px rgba(25, 70, 50, 0.06);
    transition: transform 0.15s ease;
}

.eco-card:hover {
    transform: translateY(-2px);
}

.card-icon {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
    margin-bottom: 9px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}

.card-label {
    color: #3A4F45;
    font-size: 13px;
    font-weight: 700;
}

.card-value {
    font-size: 26px;
    font-weight: 800;
    margin-top: 3px;
}

.card-note {
    color: #7C8C83;
    font-size: 11.5px;
    margin-top: 3px;
}

.green-icon  { background: linear-gradient(135deg,#3FCB80,#0E8F4F); color: #fff; }
.leaf-icon   { background: linear-gradient(135deg,#4FCC9A,#12A17E); color: #fff; }
.temp-icon   { background: linear-gradient(135deg,#5B9EE8,#3868C7); color: #fff; }
.co2-icon    { background: linear-gradient(135deg,#A17FE0,#6E4DBF); color: #fff; }

.eco-card:nth-of-type(1) .card-value, .card-value.v-green { color: #0E8F4F; }
.card-value.v-temp { color: #3868C7; }
.card-value.v-co2  { color: #6E4DBF; }

/* Insight panel */
.insight {
    background: linear-gradient(160deg, #EAF9EE 0%, #EFF6F9 100%);
    border: 1px solid #D7ECDD;
    border-radius: 16px;
    padding: 20px;
    height: 100%;
    box-shadow: 0 6px 18px rgba(25,70,50,0.05);
}

.insight h4 {
    color: #177545;
    margin: 0 0 8px 0;
    font-size: 15px;
}

.insight p {
    color: #4C5F55;
    line-height: 1.55;
    font-size: 13px;
    margin: 4px 0;
}

.insight .kt {
    color: #395246;
    font-size: 13px;
    margin: 6px 0;
}

.insight hr {
    border: none;
    border-top: 1px solid #D7ECDD;
    margin: 12px 0;
}

.rec-box {
    background: #FFFFFF;
    border: 1px solid #D7ECDD;
    border-radius: 10px;
    padding: 10px 12px;
    font-size: 12.5px;
    color: #4C5F55;
}

/* Plain white card (before/after, impact summary) */
.plain-card {
    background: #FFFFFF;
    border: 1px solid #E4EDE8;
    border-radius: 16px;
    padding: 18px;
    height: 100%;
}

.plain-card h4 {
    margin: 0 0 12px 0;
    font-size: 15px;
    color: #17392C;
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
    font-weight: 700;
}

div[data-testid="stSidebar"] .stButton:nth-of-type(1) > button {
    border: 1px solid #249B5A;
    background: #249B5A;
    color: white;
}
div[data-testid="stSidebar"] .stButton:nth-of-type(1) > button:hover {
    background: #1C824A;
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
CANOPY_PER_TREE = 0.00002

WATER_MULTIPLIER = {"Low": 0.75, "Medium": 1.0, "High": 1.2}
STRATEGY_MULTIPLIER = {
    "Clustered Planting": 1.10,
    "Dispersed Planting": 0.90,
    "Along Roads / Corridors": 1.0,
}

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


def run_ecosim(trees, area, water="Medium", strategy="Clustered Planting"):
    survival_rate = 0.65 * WATER_MULTIPLIER.get(water, 1.0)
    survival_rate = min(survival_rate, 0.95)
    surviving = int(trees * survival_rate)

    mult = STRATEGY_MULTIPLIER.get(strategy, 1.0)
    added_canopy = min(surviving * CANOPY_PER_TREE * mult, area)
    canopy_increase = (added_canopy / area) * 100 if area else 0
    cooling = estimate_cooling(canopy_increase)
    temp_after = BASE_TEMP - cooling
    green_after = BASE_GREEN + canopy_increase
    co2_low, co2_high = calculate_co2(surviving)
    co2_mid = (co2_low + co2_high) / 2

    return {
        "trees": trees,
        "surviving": surviving,
        "survival_rate": survival_rate,
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
        "co2_mid": co2_mid,
    }


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 🌱 Simulation Controls")

trees = st.sidebar.slider("🌳 Trees to Plant", 10_000, 2_000_000, 500_000, 10_000)
area = st.sidebar.slider("📍 Intervention Area (km²)", 10, 500, 100, 10)
water = st.sidebar.selectbox("💧 Water Availability", ["Low", "Medium", "High"], index=1)
strategy = st.sidebar.selectbox(
    "🗺️ Planting Strategy",
    ["Clustered Planting", "Dispersed Planting", "Along Roads / Corridors"],
    index=0,
)
scenario_name = st.sidebar.text_input("📝 Scenario Name", "My Scenario 1")

run_col, reset_col = st.sidebar.columns(2)
run_clicked = run_col.button("▶ Run Simulation")
reset_clicked = reset_col.button("↺ Reset")

if reset_clicked:
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    dedent("""
    🌱 **EcoSim AI** uses environmental modelling to estimate the impact
    of urban tree planting on Karachi's climate. Results are estimates,
    not guaranteed forecasts.
    """)
)

result = run_ecosim(trees, area, water, strategy)

# =========================================================
# TOP BAR
# =========================================================
today_str = date.today().strftime("%-d %b %Y") if hasattr(date, "strftime") else str(date.today())
weekday_str = date.today().strftime("%A")

st.markdown(dedent(f"""
<div class="topbar">
    <div>
        <div class="eco-title-row">
            <span style="font-size:26px;">🌱</span>
            <span class="eco-title">EcoSim AI</span>
        </div>
        <div class="eco-subtitle">Simulate. Analyze. Act for a Cooler, Greener Karachi.</div>
    </div>
    <div class="badge-row">
        <div class="eco-pill">📅 <span><span class="pill-label">{today_str}</span><span class="pill-sub">{weekday_str}</span></span></div>
        <div class="eco-pill">📍 <span><span class="pill-label">Karachi, Pakistan</span><span class="pill-sub">24.9° N, 67.0° E</span></span></div>
        <div class="eco-pill">🌡️ <span><span class="pill-label">{BASE_TEMP:.2f} °C</span><span class="pill-sub">Baseline Temp.</span></span></div>
    </div>
</div>
"""), unsafe_allow_html=True)

# =========================================================
# KPI CARDS
# =========================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(dedent(f"""
    <div class="eco-card">
        <div class="card-icon green-icon">🌳</div>
        <div class="card-label">Trees Surviving</div>
        <div class="card-value v-green">{result["surviving"]:,}</div>
        <div class="card-note">{result["survival_rate"]*100:.0f}% Survival Rate</div>
    </div>
    """), unsafe_allow_html=True)

with c2:
    st.markdown(dedent(f"""
    <div class="eco-card">
        <div class="card-icon leaf-icon">🌿</div>
        <div class="card-label">Green Cover</div>
        <div class="card-value v-green">{result["green_after"]:.2f}%</div>
        <div class="card-note">From {result["green_before"]:.1f}%</div>
    </div>
    """), unsafe_allow_html=True)

with c3:
    st.markdown(dedent(f"""
    <div class="eco-card">
        <div class="card-icon temp-icon">🌡️</div>
        <div class="card-label">Temperature Reduction</div>
        <div class="card-value v-temp">-{result["cooling"]:.2f} °C</div>
        <div class="card-note">From {result["temp_before"]:.2f} °C</div>
    </div>
    """), unsafe_allow_html=True)

with c4:
    cars_eq = int(result["co2_mid"] / 4.6) if result["co2_mid"] else 0
    st.markdown(dedent(f"""
    <div class="eco-card">
        <div class="card-icon co2-icon">☁️</div>
        <div class="card-label">CO₂ Removed (Annual)</div>
        <div class="card-value v-co2">{result["co2_mid"]:,.0f} tCO₂e</div>
        <div class="card-note">Equivalent to {cars_eq:,} cars off road</div>
    </div>
    """), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# CHART + MAP + AI INSIGHTS
# =========================================================
left, mid, right = st.columns([0.9, 1.35, 0.75])

with left:
    st.markdown('<div class="section-title">Impact Over Time</div>', unsafe_allow_html=True)

    years = [0, 5, 10, 15, 20]
    temps = [
        result["temp_before"] - result["cooling"] * f
        for f in [0, 0.25, 0.50, 0.75, 1.0]
    ]
    green = [
        result["green_before"] + result["canopy_increase"] * f
        for f in [0, 0.25, 0.50, 0.75, 1.0]
    ]
    co2_series = [
        result["co2_mid"] * f
        for f in [0, 0.25, 0.50, 0.75, 1.0]
    ]

    fig, ax1 = plt.subplots(figsize=(5.6, 4.2))
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("axes", 1.18))

    l1, = ax1.plot(years, green, marker="o", color="#22A15A", linewidth=2.2, label="Green Cover (%)")
    l2, = ax1.plot(years, temps, marker="o", color="#3E8BEF", linewidth=2.2, label="Temperature (°C)")
    l3, = ax3.plot(years, co2_series, marker="o", color="#8B5FDB", linewidth=2.2, label="CO₂ Removed (t)")

    ax1.set_xlabel("Years", fontsize=9)
    ax1.set_ylabel("Green Cover (%) / Temperature (°C)", fontsize=8.5)
    ax3.set_ylabel("CO₂ Removed (t)", fontsize=8.5, color="#8B5FDB")
    ax1.tick_params(labelsize=8)
    ax3.tick_params(labelsize=8, colors="#8B5FDB")
    ax1.grid(alpha=0.15)
    ax1.set_xticks(years)
    ax1.set_xticklabels(["0 (Now)", "5 Years", "10 Years", "15 Years", "20 Years"], fontsize=7.5)

    lines = [l1, l2, l3]
    ax1.legend(lines, [l.get_label() for l in lines], loc="upper center",
               bbox_to_anchor=(0.5, 1.18), ncol=3, fontsize=7.5, frameon=False)

    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with mid:
    st.markdown('<div class="section-title">Karachi Map (Satellite View)</div>', unsafe_allow_html=True)

    karachi_map = folium.Map(location=[24.86, 67.01], zoom_start=10, tiles=None)

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

    folium.TileLayer("OpenStreetMap", name="🗺️ Street Map").add_to(karachi_map)

    radius = max(1500, min(12000, (area ** 0.5) * 1000))

    folium.Circle(
        location=[24.86, 67.01],
        radius=radius,
        popup=f"Intervention Zone: {area} km²",
        tooltip="🌱 Proposed Intervention Zone",
        color="#249B5A",
        fill=True,
        fill_color="#63C174",
        fill_opacity=0.35,
        weight=2,
    ).add_to(karachi_map)

    folium.Marker(
        [24.86, 67.01],
        tooltip="Karachi — EcoSim AI",
        icon=folium.Icon(color="green", icon="leaf"),
    ).add_to(karachi_map)

    folium.LayerControl().add_to(karachi_map)

    st_folium(karachi_map, width=None, height=470)
    st.caption("🟩 Intervention Area   ⬛ Urban Area   🟦 Water Bodies")

with right:
    st.markdown('<div class="section-title">✨ AI Insights</div>', unsafe_allow_html=True)

    if result["cooling"] >= 1.2:
        assessment = "Your scenario shows a strong cooling effect with substantial improvement in green cover over the next 10–20 years."
    elif result["cooling"] >= 0.6:
        assessment = "Your scenario shows a moderate cooling effect with noticeable improvement in green cover over the next 10–20 years."
    else:
        assessment = "This scenario has a smaller estimated impact. Try increasing trees planted or the intervention area."

    st.markdown(dedent(f"""
    <div class="insight">
        <p>{assessment}</p>
        <hr>
        <h4>Key Takeaways</h4>
        <div class="kt">✅ Temperature could reduce by <b>{result["cooling"]:.2f} °C</b> in the long term.</div>
        <div class="kt">✅ Green cover will increase by <b>{result["canopy_increase"]:.2f}%</b>.</div>
        <div class="kt">✅ <b>{result["co2_mid"]:,.0f} tonnes</b> of CO₂ could be removed annually.</div>
        <hr>
        <h4>Recommendation</h4>
        <div class="rec-box">Increasing the intervention area to {area+50}–{area+100} km² could maximize cooling benefits.</div>
    </div>
    """), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# BEFORE VS AFTER / IMPACT SUMMARY / PROJECTED IMPACT
# =========================================================
b1, b2, b3 = st.columns(3)

with b1:
    st.markdown('<div class="section-title">Before vs After (20 Years)</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    labels = ["Temperature (°C)", "Green Cover (%)", "CO₂ Removed (t/yr)"]
    before_vals = [result["temp_before"], result["green_before"], 0]
    after_vals = [result["temp_after"], result["green_after"], result["co2_mid"]]
    y = range(len(labels))
    ax.barh([i + 0.18 for i in y], before_vals, height=0.32, color="#C9D3CD", label="Before")
    ax.barh([i - 0.18 for i in y], after_vals, height=0.32, color="#22A15A", label="After")
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.legend(fontsize=8, frameon=False)
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with b2:
    st.markdown('<div class="section-title">Impact Summary</div>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    with s1:
        st.markdown(dedent(f"""
        <div class="eco-card" style="margin-bottom:10px;">
            <div class="card-icon temp-icon">🌡️</div>
            <div class="card-value" style="font-size:20px;">-{result["cooling"]:.2f} °C</div>
            <div class="card-note">Temperature Reduction</div>
        </div>
        <div class="eco-card">
            <div class="card-icon co2-icon">☁️</div>
            <div class="card-value" style="font-size:20px;">{result["co2_mid"]:,.0f} tCO₂e</div>
            <div class="card-note">CO₂ Removed (Annual)</div>
        </div>
        """), unsafe_allow_html=True)
    with s2:
        st.markdown(dedent(f"""
        <div class="eco-card" style="margin-bottom:10px;">
            <div class="card-icon leaf-icon">🌿</div>
            <div class="card-value" style="font-size:20px;">+{result["canopy_increase"]:.2f}%</div>
            <div class="card-note">Green Cover Increase</div>
        </div>
        <div class="eco-card">
            <div class="card-icon green-icon">🌳</div>
            <div class="card-value" style="font-size:20px;">{result["surviving"]:,}</div>
            <div class="card-note">Trees Surviving</div>
        </div>
        """), unsafe_allow_html=True)

with b3:
    st.markdown('<div class="section-title">Projected Impact (20 Years)</div>', unsafe_allow_html=True)
    st.markdown(dedent(f"""
    <div class="plain-card">
        <p style="color:#4C5F55; font-size:13px; line-height:1.6;">
        Your planted trees will continue to grow and create a lasting
        positive impact on Karachi's
        climate, air quality, and biodiversity.
        </p>
    </div>
    """), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# QUICK COMPARISON
# =========================================================
st.markdown('<div class="section-title">🌳 Quick Scenario Comparison</div>', unsafe_allow_html=True)

scenario_rows = []
for number in [100_000, 250_000, 500_000, 1_000_000]:
    x = run_ecosim(number, area, water, strategy)
    scenario_rows.append({
        "Trees Planted": f"{number:,}",
        "Surviving": f'{x["surviving"]:,}',
        "Cooling": f'{x["cooling"]:.2f}°C',
        "CO₂ Removal (mid)": f'{x["co2_mid"]:,.0f} t/year',
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
    <b>Made by Mukarram & Minhaj </b> 💚
</div>
"""), unsafe_allow_html=True)
