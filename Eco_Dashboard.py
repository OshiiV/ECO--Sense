import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, date

# ── PAGE CONFIGURATION ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Clima Predict - Sensor Lab",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── INITIALIZE SESSION STATE FOR THRESHOLDS ──────────────────────────────────
defaults = {
    "tmp_w": 26, "tmp_d": 30,
    "hum_w": 60, "hum_d": 75,
    "co2_w": 700, "co2_d": 1000,
    "dst_w": 25, "dst_d": 35
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── CSS STYLING ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fira+Code:wght@300;400;500;700&display=swap');

:root {
    --bg:      #05080a;
    --bg1:     #0a1018;
    --bg2:     #0f1922;
    --a1:      #39d9c8;
    --muted:   #93b9d6;
    --border:  #1f3c5b;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: var(--bg); color: #f2fbff;
}

/* FIXED TOP GAP: Increased to 3.5rem to prevent overlap with Streamlit's top bar */
.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 2rem !important;
}

/* Hide the sidebar toggle button completely */
[data-testid="collapsedControl"] { display: none; }

/* KPI CARDS */
.kpi-card {
    background: linear-gradient(145deg, var(--bg1), var(--bg2));
    border: 1px solid var(--border); border-radius: 18px;
    padding: 22px 20px; position: relative; overflow: hidden;
    height: 155px;
    display: flex; flex-direction: column; justify-content: space-between;
}
.kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; }
.kc-teal::before   { background:linear-gradient(90deg,#39d9c8,#5b8cff); }
.kc-indigo::before { background:linear-gradient(90deg,#5b8cff,#a78bfa); }
.kc-amber::before  { background:linear-gradient(90deg,#ffd166,#ff9f43); }
.kc-rose::before   { background:linear-gradient(90deg,#ff5e7e,#ffd166); }

.kpi-header { display: flex; justify-content: space-between; align-items: flex-start; }
.kpi-label { font-family:'Fira Code',monospace; font-size:12px; letter-spacing:2px; text-transform:uppercase; color:#edf6fb; margin-bottom:5px; font-weight: 600;}
.kpi-val   { font-family:'Plus Jakarta Sans',sans-serif; font-size:46px; font-weight:800; line-height:1; color: #f2fbff; }
.kpi-unit  { font-family:'Fira Code',monospace; font-size:14px; color:var(--muted); margin-left:4px; font-weight: 500; }

/* STATUS BADGES FOR KPI CARDS */
.stat-badge {
    font-family: 'Fira Code', monospace; font-size: 10px; font-weight: bold; letter-spacing: 1px;
    padding: 4px 10px; border-radius: 20px; text-transform: uppercase;
}
.sb-low  { background: rgba(57,217,200,0.15); color: #39d9c8; border: 1px solid rgba(57,217,200,0.4); }
.sb-med  { background: rgba(255,209,102,0.15); color: #ffd166; border: 1px solid rgba(255,209,102,0.4); }
.sb-high { background: rgba(255,94,126,0.15); color: #ff5e7e; border: 1px solid rgba(255,94,126,0.4); }

.sh {
    font-family:'Fira Code',monospace; font-size:11px; letter-spacing:4px;
    text-transform:uppercase; color:var(--muted);
    border-left:3px solid var(--a1); padding-left:12px; margin:30px 0 16px;
}

/* ROUNDED HOVER TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px; background: transparent; border: none; padding-bottom: 10px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important; 
    font-size: 14px !important; font-weight: 600 !important;
    color: var(--muted) !important; background: var(--bg1) !important;
    border: 1px solid var(--border) !important;
    border-radius: 30px !important; /* Rounded pills */
    padding: 10px 24px !important;
    transition: all 0.3s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    transform: translateY(-2px);
    border-color: var(--a1) !important;
    color: #fff !important;
    box-shadow: 0 4px 12px rgba(57,217,200,0.15);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #162334, #0a1018) !important;
    border-color: var(--a1) !important; color: var(--a1) !important;
    box-shadow: 0 4px 15px rgba(57,217,200,0.2);
}

/* INSIDE-TAB STATUS BANNER */
.status-banner {
    padding: 15px 20px; border-radius: 12px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; border: 1px solid;
}
.status-low { background: rgba(57, 217, 200, 0.1); border-color: #39d9c8; color: #39d9c8; }
.status-med { background: rgba(255, 209, 102, 0.1); border-color: #ffd166; color: #ffd166; }
.status-high { background: rgba(255, 94, 126, 0.1); border-color: #ff5e7e; color: #ff5e7e; }

[data-testid="stButton"] button { margin-top: 5px; border-radius: 8px !important; }
.tab-desc { font-size: 15px; color: #93b9d6; margin-bottom: 25px; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# ── DATA GENERATION ───────────────────────────────────────────────────────────
TODAY         = date.today()
HIST_DAYS     = 30          
FORECAST_DAYS = 14          
MIN_DATE      = TODAY - timedelta(days=HIST_DAYS)
MAX_DATE      = TODAY + timedelta(days=FORECAST_DAYS)

PARAMS = {
    "temperature": dict(base=23.0, occ_add=1.2, noise=.4,  unit="°C",    color="#39d9c8"),
    "humidity":    dict(base=46.0, occ_add=5.0, noise=3.0, unit="%",     color="#5b8cff"),
    "pressure":    dict(base=1013.2,occ_add=0,  noise=.9,  unit="hPa",   color="#a78bfa"),
    "co2":         dict(base=650,  occ_add=220, noise=28,  unit="ppm",   color="#ffd166"),
    "dust":        dict(base=16,   occ_add=12,  noise=4.0, unit="µg/m³", color="#ff5e7e"),
}

@st.cache_data(ttl=300)
def gen_history():
    np.random.seed(42)
    n = HIST_DAYS * 24 * 4
    rows = []
    for i in range(n):
        ts = datetime.combine(TODAY, datetime.min.time()) - timedelta(days=HIST_DAYS) + timedelta(minutes=i*15)
        occ = 1.0 if 8 <= ts.hour <= 18 and ts.weekday() < 5 else 0.07
        day_i = i / (24*4)
        rows.append({
            "timestamp":   ts,
            "temperature": round(PARAMS["temperature"]["base"] + np.random.normal(0,.4) + occ*1.2 + 0.8*np.sin(2*np.pi*day_i/7), 1),
            "humidity":    round(np.clip(PARAMS["humidity"]["base"] + np.random.normal(0,3) + occ*5 + 2*np.cos(2*np.pi*day_i/14), 20, 95), 1),
            "pressure":    round(1013.2 + np.random.normal(0,.9) + 1.5*np.sin(2*np.pi*day_i/10), 2),
            "co2":         round(PARAMS["co2"]["base"] + (day_i * 1.5) + np.random.normal(0,28) + occ*220),
            "dust":        round(max(0, PARAMS["dust"]["base"] + np.random.normal(0,4) + occ*12 + 2*np.sin(2*np.pi*day_i/5)), 1),
        })
    return pd.DataFrame(rows)

@st.cache_data(ttl=300)
def gen_forecast(days_ahead=14):
    hist = gen_history()
    cutoff = datetime.combine(TODAY, datetime.min.time()) - timedelta(days=14)
    basis  = hist[hist["timestamp"] >= cutoff].copy()
    basis["hour"] = basis["timestamp"].dt.hour
    cols = ["temperature","humidity","pressure","co2","dust"]
    hourly_median = basis.groupby("hour")[cols].median()
    hourly_std    = basis.groupby("hour")[cols].std().fillna(1)
    
    basis["t_idx"] = (basis["timestamp"] - basis["timestamp"].min()).dt.total_seconds() / 3600
    trends = {c: np.polyfit(basis["t_idx"], basis[c], 1)[0] for c in cols}

    rows = []
    for i in range(days_ahead * 24 * 4):
        ts = datetime.combine(TODAY, datetime.min.time()) + timedelta(minutes=i*15)
        h = ts.hour
        row = {"timestamp": ts}
        for c in cols:
            base_val = hourly_median.loc[h, c] + trends[c] * (i * 0.25)
            row[c] = round(float(base_val), 2)
            row[f"{c}_lo"] = round(float(base_val - 1.5 * hourly_std.loc[h, c]), 2)
            row[f"{c}_hi"] = round(float(base_val + 1.5 * hourly_std.loc[h, c]), 2)
        rows.append(row)
    return pd.DataFrame(rows)

def PL(**kw):
    base = dict(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#cbd5e1"), margin=dict(l=14, r=14, t=42, b=14),
        hovermode="x unified", dragmode="zoom",
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showgrid=True, zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showgrid=True, zeroline=False)
    )
    base.update(kw)
    return base

# ── CENTERED HEADER ──────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; margin-top: 0px; margin-bottom: 40px;">
    <div style="font-size: 55px; line-height: 1; margin-bottom: 10px;">🌿</div>
    <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 48px; font-weight: 800; letter-spacing: 2px; line-height: 1.1;">CLIMA PREDICT</div>
    <div style="font-family: 'Fira Code', monospace; font-size: 14px; color: #39d9c8; letter-spacing: 6px; margin-top: 8px;">SENSOR ANALYTICS DASHBOARD</div>
</div>
""", unsafe_allow_html=True)

# ── GLOBAL FILTERS ───────────────────────────────────────────────────────────
c_df1, c_df2, c_spacer, c_refresh = st.columns([1.5, 1.5, 4, 1.5])
with c_df1:
    date_from = st.date_input("From", value=TODAY - timedelta(days=7), min_value=MIN_DATE, max_value=MAX_DATE)
with c_df2:
    date_to = st.date_input("To", value=TODAY + timedelta(days=3), min_value=MIN_DATE, max_value=MAX_DATE)

if date_from > date_to: 
    date_from = date_to - timedelta(days=1)

with c_refresh:
    st.markdown(f'<div style="font-family:Fira Code;font-size:10px;color:#93b9d6;margin-bottom:8px;text-align:right;">LAST SYNC: {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    if st.button("⟳ Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── PREPARE DATA ──────────────────────────────────────────────────────────────
hist_df = gen_history()
fore_df = gen_forecast(FORECAST_DAYS)
s_dt = datetime.combine(date_from, datetime.min.time())
e_dt = datetime.combine(date_to,   datetime.max.time())

df_h = hist_df[(hist_df["timestamp"] >= s_dt) & (hist_df["timestamp"] <= min(e_dt, datetime.combine(TODAY, datetime.max.time())))].copy()
df_f = fore_df[(fore_df["timestamp"] > datetime.combine(TODAY, datetime.min.time())) & (fore_df["timestamp"] <= e_dt)].copy()

actual_cols = ["timestamp","temperature","humidity","pressure","co2","dust"]
df_combined = pd.concat([df_h[actual_cols], df_f[actual_cols] if not df_f.empty else pd.DataFrame(columns=actual_cols)], ignore_index=True).sort_values("timestamp")
df = df_combined.copy() if not df_combined.empty else hist_df.tail(96).copy()
last_reading = df_h.iloc[-1] if not df_h.empty else hist_df.iloc[-1]

# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

def get_status_info(val, warn, danger):
    """Evaluates metrics to return SAFE, MODERATE, or DANGER states for KPI Cards."""
    if val >= danger: return "DANGER", "sb-high"
    if val >= warn: return "MODERATE", "sb-med"
    return "SAFE", "sb-low"

def render_status_banner(val, warn, danger, unit, label):
    """Renders the detailed status banner inside individual tabs."""
    if val >= danger:
        cls, status, icon = "status-high", "DANGER (Critical)", "🚨"
    elif val >= warn:
        cls, status, icon = "status-med", "MODERATE (Warning)", "⚠️"
    else:
        cls, status, icon = "status-low", "SAFE (Stable)", "✅"
    
    st.markdown(f"""
    <div class="status-banner {cls}">
        <div>
            <div style="font-size: 0.8rem; font-family: Fira Code; text-transform: uppercase;">Current {label}</div>
            <div style="font-size: 1.8rem; font-weight: bold;">{val:.1f} <span style="font-size:1rem;">{unit}</span></div>
        </div>
        <div style="text-align:right;">
            <div style="font-size: 1.2rem; font-weight: bold;">{icon} {status}</div>
            <div style="font-size: 0.8rem; opacity: 0.8;">Thresholds: Warn {warn}{unit} | Danger {danger}{unit}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def kpi_cards():
    t_val = df['temperature'].mean()
    h_val = df['humidity'].mean()
    c_val = df['co2'].mean()
    d_val = df['dust'].mean()

    cards = [
        ("kc-teal", "🌡️", "TEMPERATURE", f"{t_val:.1f}", "°C", *get_status_info(t_val, st.session_state.tmp_w, st.session_state.tmp_d)),
        ("kc-indigo", "💧", "HUMIDITY", f"{h_val:.1f}", "%", *get_status_info(h_val, st.session_state.hum_w, st.session_state.hum_d)),
        ("kc-amber", "💨", "CO₂", f"{c_val:.0f}", "ppm", *get_status_info(c_val, st.session_state.co2_w, st.session_state.co2_d)),
        ("kc-rose", "🔴", "DUST PM2.5", f"{d_val:.1f}", "µg/m³", *get_status_info(d_val, st.session_state.dst_w, st.session_state.dst_d)),
    ]
    
    cols = st.columns(len(cards))
    for col_, (cls, icon, lbl, val, unit, s_text, s_cls) in zip(cols, cards):
        with col_:
            st.markdown(f"""
            <div class="kpi-card {cls}">
                <div class="kpi-header">
                    <div class="kpi-label">{icon} {lbl}</div>
                    <div class="stat-badge {s_cls}">{s_text}</div>
                </div>
                <div>
                    <span class="kpi-val">{val}</span><span class="kpi-unit">{unit}</span>
                </div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

def plot_forecast_chart(col_key, color, title, unit, warn_val, danger_val):
    fig = go.Figure()
    
    # Historical Data
    if not df_h.empty:
        dh_s = df_h.sort_values("timestamp")
        fig.add_trace(go.Scatter(
            x=dh_s["timestamp"], y=dh_s[col_key].rolling(4,min_periods=1).mean(), 
            name="Historical", line=dict(color=color,width=2.5), fill="tozeroy", 
            fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},.05)"
        ))
        
    # Forecast Data
    if not df_f.empty:
        dfs = df_f.sort_values("timestamp")
        fig.add_trace(go.Scatter(
            x=pd.concat([dfs["timestamp"],dfs["timestamp"][::-1]]), 
            y=pd.concat([dfs[f"{col_key}_hi"],dfs[f"{col_key}_lo"][::-1]]), 
            fill="toself", fillcolor="rgba(167,139,250,.08)", line=dict(color="rgba(0,0,0,0)"), 
            name="Confidence"
        ))
        fig.add_trace(go.Scatter(
            x=dfs["timestamp"], y=dfs[col_key], name="Forecast", 
            line=dict(color="#a78bfa",width=2,dash="dot")
        ))
    
    # Add Threshold Lines Safely
    if warn_val:
        fig.add_hline(y=warn_val, line_dash="dash", line_color="#ffd166")
        fig.add_annotation(x=0.01, y=warn_val, xref="paper", yref="y", text="Warn", showarrow=False, font=dict(color="#ffd166", size=10), yanchor="bottom")
        
    if danger_val:
        fig.add_hline(y=danger_val, line_dash="dash", line_color="#ff5e7e")
        fig.add_annotation(x=0.01, y=danger_val, xref="paper", yref="y", text="Danger", showarrow=False, font=dict(color="#ff5e7e", size=10), yanchor="bottom")
    
    # Add 'TODAY' Line Safely
    today_dt = datetime.combine(TODAY, datetime.min.time())
    fig.add_vline(x=today_dt, line_dash="dash", line_color="#72d0ff", opacity=0.8)
    fig.add_annotation(x=today_dt, y=1.02, xref="x", yref="paper", text="TODAY", showarrow=False, font=dict(color="#72d0ff", size=10, family="Fira Code"))
    
    fig.update_layout(title=f"{title} Predictive Model", height=340, **PL())
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── MAIN TABS ─────────────────────────────────────────────────────────────────
tab_overview, tab_temp, tab_humid, tab_air, tab_dust, tab_forecast = st.tabs([
    "Summary", "🌡️ Temperature", "💧 Humidity", "💨 Air Quality", "🔴 Dust", " Predictive Lab"
])

# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_overview:
    st.markdown('<div class="tab-desc">A high-level snapshot of current sensor readings, showing the average metrics and their current severity status based on global thresholds.</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sh">Statistical Distribution Summary</div>', unsafe_allow_html=True)
    stat_params = [("temperature","Temp °C"),("humidity","Humid %"), ("co2","CO₂ ppm"),("dust","Dust µg/m³")]
    sc = st.columns(4)
    for col, (k, lbl) in zip(sc, stat_params):
        mn, mx, av = df[k].min(), df[k].max(), df[k].mean()
        with col:
            st.markdown(f"""
            <div style="background:var(--bg1);border:1px solid var(--border); border-radius:14px;padding:14px;text-align:center">
                <div style="font-family:Fira Code;font-size:9px;letter-spacing:2px;color:#93b9d6;margin-bottom:10px">{lbl}</div>
                <div style="display:flex;justify-content:space-around">
                    <div><div style="font-size:18px;font-weight:700;color:#5b8cff">{mn:.1f}</div><div style="font-size:9px;color:#93b9d6;font-weight:600;">MIN</div></div>
                    <div><div style="font-size:18px;font-weight:700;color:#39d9c8">{av:.1f}</div><div style="font-size:9px;color:#93b9d6;font-weight:600;">AVG</div></div>
                    <div><div style="font-size:18px;font-weight:700;color:#ff5e7e">{mx:.1f}</div><div style="font-size:9px;color:#93b9d6;font-weight:600;">MAX</div></div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">Current Environmental Status</div>', unsafe_allow_html=True)
    kpi_cards()

# ══════════════════════════════════════════════════════════════════════════════
# TEMPERATURE TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_temp:
    st.markdown('<div class="tab-desc">Deep dive into temperature analytics. Track historical heat trends against forecasted statistical bands to prevent overheating events.</div>', unsafe_allow_html=True)
    
    with st.expander("⚙️ Adjust Temperature Thresholds"):
        c1, c2 = st.columns(2)
        st.session_state.tmp_w = c1.slider("Warning Level (°C)", 18, 40, st.session_state.tmp_w, 1)
        st.session_state.tmp_d = c2.slider("Danger Level (°C)", 20, 45, st.session_state.tmp_d, 1)

    render_status_banner(last_reading['temperature'], st.session_state.tmp_w, st.session_state.tmp_d, "°C", "Temperature")
    plot_forecast_chart("temperature", "#39d9c8", "Temperature", "°C", st.session_state.tmp_w, st.session_state.tmp_d)

# ══════════════════════════════════════════════════════════════════════════════
# HUMIDITY TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_humid:
    st.markdown('<div class="tab-desc">Monitor moisture levels in the environment. High humidity combined with heat can damage sensitive equipment or promote mold growth.</div>', unsafe_allow_html=True)
    
    with st.expander("⚙️ Adjust Humidity Thresholds"):
        c1, c2 = st.columns(2)
        st.session_state.hum_w = c1.slider("Warning Level (%)", 30, 85, st.session_state.hum_w, 5)
        st.session_state.hum_d = c2.slider("Danger Level (%)", 40, 95, st.session_state.hum_d, 5)

    render_status_banner(last_reading['humidity'], st.session_state.hum_w, st.session_state.hum_d, "%", "Humidity")
    plot_forecast_chart("humidity", "#5b8cff", "Humidity", "%", st.session_state.hum_w, st.session_state.hum_d)

# ══════════════════════════════════════════════════════════════════════════════
# AIR QUALITY TAB (CO2)
# ══════════════════════════════════════════════════════════════════════════════
with tab_air:
    st.markdown('<div class="tab-desc">Analyze carbon dioxide concentrations. Rising CO₂ levels often indicate poor ventilation or high occupancy rates, which can impact cognitive function.</div>', unsafe_allow_html=True)
    
    with st.expander("⚙️ Adjust CO₂ Thresholds"):
        c1, c2 = st.columns(2)
        st.session_state.co2_w = c1.slider("Warning Level (ppm)", 400, 1500, st.session_state.co2_w, 50)
        st.session_state.co2_d = c2.slider("Danger Level (ppm)", 500, 2000, st.session_state.co2_d, 50)

    render_status_banner(last_reading['co2'], st.session_state.co2_w, st.session_state.co2_d, "ppm", "CO₂")
    plot_forecast_chart("co2", "#ffd166", "CO₂", "ppm", st.session_state.co2_w, st.session_state.co2_d)

# ══════════════════════════════════════════════════════════════════════════════
# DUST TAB (PM2.5)
# ══════════════════════════════════════════════════════════════════════════════
with tab_dust:
    st.markdown('<div class="tab-desc">Track fine particulate matter (PM2.5) suspended in the air. High dust concentrations are a primary health hazard for respiration and clean-room environments.</div>', unsafe_allow_html=True)
    
    with st.expander("⚙️ Adjust Dust Thresholds"):
        c1, c2 = st.columns(2)
        st.session_state.dst_w = c1.slider("Warning Level (µg/m³)", 5, 75, st.session_state.dst_w, 5)
        st.session_state.dst_d = c2.slider("Danger Level (µg/m³)", 10, 100, st.session_state.dst_d, 5)

    render_status_banner(last_reading['dust'], st.session_state.dst_w, st.session_state.dst_d, "µg/m³", "Dust PM2.5")
    plot_forecast_chart("dust", "#ff5e7e", "Dust PM2.5", "µg/m³", st.session_state.dst_w, st.session_state.dst_d)

# ══════════════════════════════════════════════════════════════════════════════
# PREDICTIVE LAB TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_forecast:
    st.markdown('<div class="tab-desc">Overlay multiple forecasted environmental metrics simultaneously to identify complex correlations, such as the relationship between heat spikes and air quality degradation.</div>', unsafe_allow_html=True)
    
    st.info("**Tip:** Use the specific parameter tabs (Temperature, Humidity, etc.) for detailed, single-metric forecasting and threshold analysis. This tab provides a holistic overlay of all predicted parameters.")
    
    fore_param = st.multiselect("Select parameters to overlay:", ["temperature", "humidity", "co2", "dust"], default=["temperature", "humidity"])
    
    if fore_param:
        fig_multi = go.Figure()
        dfs = df_f.sort_values("timestamp") if not df_f.empty else pd.DataFrame()
        dh_s = df_h.sort_values("timestamp") if not df_h.empty else pd.DataFrame()
        
        for p in fore_param:
            color = PARAMS[p]["color"]
            if not dh_s.empty:
                fig_multi.add_trace(go.Scatter(x=dh_s["timestamp"], y=dh_s[p].rolling(4,min_periods=1).mean(), name=f"{p.title()} (Hist)", line=dict(color=color,width=2)))
            if not dfs.empty:
                fig_multi.add_trace(go.Scatter(x=dfs["timestamp"], y=dfs[p], name=f"{p.title()} (Fore)", line=dict(color=color,width=2,dash="dot")))
        
        fig_multi.update_layout(height=450, **PL())
        st.plotly_chart(fig_multi, use_container_width=True, config={"displayModeBar": False})