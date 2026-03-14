import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date

st.set_page_config(
    page_title="Eco-Sense — Sensor Lab",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fira+Code:wght@300;400;500;700&display=swap');

:root {
    --bg:      #05080a;
    --bg1:     #0a1018;
    --bg2:     #0f1922;
    --bg3:     #162334;
    --a1:      #39d9c8;
    --a2:      #5b8cff;
    --a3:      #ffd166;
    --a4:      #ff5e7e;
    --a5:      #a78bfa;
    --a6:      #ff9f43;
    --txt:     #f2fbff;
    --muted:   #93b9d6;
    --border:  #1f3c5b;
    --border2: #2a4f76;
}
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: var(--bg); color: var(--txt);
}
html, body, div, span, p, label, h1, h2, h3, h4, h5, h6, a, button {
    color: var(--txt) !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080f18 0%, #050a10 100%);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--txt) !important; }
#MainMenu, footer, header { visibility: hidden; }

.kpi-card {
    background: linear-gradient(145deg, var(--bg1), var(--bg2));
    border: 1px solid var(--border); border-radius: 18px;
    padding: 20px 18px 16px; position: relative; overflow: hidden;
    transition: transform .22s cubic-bezier(.34,1.56,.64,1), box-shadow .22s, border-color .22s;
    height: 150px;
}
.kpi-card:hover {
    transform: translateY(-5px) scale(1.015);
    box-shadow: 0 20px 50px rgba(57,217,200,.08);
    border-color: var(--border2);
}
.kpi-card::after {
    content:''; position:absolute; inset:0;
    background:radial-gradient(ellipse at top right,rgba(57,217,200,.04),transparent 60%);
    pointer-events:none;
}
.kpi-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    border-radius:18px 18px 0 0;
}
.kc-teal::before   { background:linear-gradient(90deg,#39d9c8,#5b8cff); }
.kc-indigo::before { background:linear-gradient(90deg,#5b8cff,#a78bfa); }
.kc-amber::before  { background:linear-gradient(90deg,#ffd166,#ff9f43); }
.kc-rose::before   { background:linear-gradient(90deg,#ff5e7e,#ffd166); }
.kc-violet::before { background:linear-gradient(90deg,#a78bfa,#5b8cff); }
.kc-green::before  { background:linear-gradient(90deg,#39d9c8,#a78bfa); }

.kpi-chip  { font-family:'Fira Code',monospace; font-size:8.5px; letter-spacing:3px;
             text-transform:uppercase; color:#d8eaf2; margin-bottom:3px; }
.kpi-label { font-family:'Fira Code',monospace; font-size:9px; letter-spacing:2.5px;
             text-transform:uppercase; color:#edf6fb; margin-bottom:7px; }
.kpi-val   { font-family:'Plus Jakarta Sans',sans-serif; font-size:36px; font-weight:800; line-height:1; }
.kpi-unit  { font-family:'Fira Code',monospace; font-size:12px; color:var(--muted); margin-left:3px; }
.kpi-delta { font-family:'Fira Code',monospace; font-size:9.5px; margin-top:9px; }
.kpi-icon  { position:absolute; top:14px; right:14px; font-size:26px; opacity:.13; }
.d-up   { color:#39d9c8; }
.d-down { color:#ff5e7e; }

.sh {
    font-family:'Fira Code',monospace; font-size:9.5px; letter-spacing:4px;
    text-transform:uppercase; color:var(--muted);
    border-left:3px solid var(--a1); padding-left:10px; margin:26px 0 14px;
}
/* Forecast section header — purple accent */
.sh-pred {
    font-family:'Fira Code',monospace; font-size:9.5px; letter-spacing:4px;
    text-transform:uppercase; color:var(--muted);
    border-left:3px solid #a78bfa; padding-left:10px; margin:26px 0 14px;
}

.bdg { display:inline-block; padding:3px 10px; border-radius:20px; font-size:9px;
       font-weight:700; letter-spacing:1.5px; text-transform:uppercase;
       font-family:'Fira Code',monospace; }
.bdg-ok   { background:rgba(57,217,200,.1);  color:#39d9c8; border:1px solid rgba(57,217,200,.25); }
.bdg-warn { background:rgba(255,209,102,.1); color:#ffd166; border:1px solid rgba(255,209,102,.25); }
.bdg-bad  { background:rgba(255,94,126,.1);  color:#ff5e7e; border:1px solid rgba(255,94,126,.25); }
.bdg-live { background:rgba(91,140,255,.1);  color:#5b8cff; border:1px solid rgba(91,140,255,.25); }
.bdg-hist { background:rgba(57,217,200,.1);  color:#39d9c8; border:1px solid rgba(57,217,200,.25); }
.bdg-fore { background:rgba(167,139,250,.15);color:#a78bfa; border:1px solid rgba(167,139,250,.3); }

.alrt { border-radius:10px; padding:11px 15px; margin:7px 0; font-size:13px; }
.alrt-warn { background:rgba(255,209,102,.06); border:1px solid rgba(255,209,102,.2); border-left:3px solid #ffd166; }
.alrt-bad  { background:rgba(255,94,126,.06);  border:1px solid rgba(255,94,126,.2);  border-left:3px solid #ff5e7e; }

/* forecast info box */
.fore-info {
    background:rgba(167,139,250,.05); border:1px solid rgba(167,139,250,.2);
    border-left:3px solid #a78bfa; border-radius:10px;
    padding:12px 16px; margin-bottom:16px;
    font-family:'Fira Code',monospace; font-size:10px; color:#4d6e80; letter-spacing:1px;
}

.stTabs [data-baseweb="tab-list"] {
    background:var(--bg1); border-radius:12px 12px 0 0;
    border-bottom:1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    font-family:'Fira Code',monospace !important; font-size:10.5px !important;
    letter-spacing:1.5px !important; color:var(--muted) !important; background:transparent !important;
}
.stTabs [aria-selected="true"] { color:var(--a1) !important; border-bottom:2px solid var(--a1) !important; }

.streamlit-expanderHeader {
    font-family:'Fira Code',monospace !important; font-size:10px !important;
    letter-spacing:2px !important; color:var(--muted) !important;
}
.stSlider > label, .stSelectbox > label, .stRadio > label,
.stToggle > label, .stNumberInput > label, .stMultiSelect > label, .stDateInput > label {
    font-family:'Fira Code',monospace !important; font-size:9.5px !important;
    letter-spacing:2px !important; color:var(--muted) !important; text-transform:uppercase;
}
.stButton > button {
    font-family:'Fira Code',monospace !important; font-size:10px !important;
    letter-spacing:2px !important; background:var(--bg2) !important;
    color:var(--a1) !important; border:1px solid var(--border2) !important; border-radius:10px !important;
}
.stButton > button:hover { background:rgba(57,217,200,.08) !important; border-color:var(--a1) !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
TODAY         = date.today()
HIST_DAYS     = 30          # historical data goes back 30 days
FORECAST_DAYS = 14          # forecasts go up to 14 days ahead
MIN_DATE      = TODAY - timedelta(days=HIST_DAYS)
MAX_DATE      = TODAY + timedelta(days=FORECAST_DAYS)

PARAMS = {
    "temperature": dict(base=23.0, occ_add=1.2, noise=.4,  unit="°C",    label="Temperature", color="#39d9c8", chip="BME280"),
    "humidity":    dict(base=46.0, occ_add=5.0, noise=3.0, unit="%",     label="Humidity",    color="#5b8cff", chip="BME280"),
    "pressure":    dict(base=1013.2,occ_add=0,  noise=.9,  unit="hPa",   label="Pressure",    color="#a78bfa", chip="BME280"),
    "co2":         dict(base=650,  occ_add=220, noise=28,  unit="ppm",   label="CO₂",         color="#ffd166", chip="CCS811"),
    "dust":        dict(base=16,   occ_add=12,  noise=4.0, unit="µg/m³", label="Dust PM2.5",  color="#ff5e7e", chip="GP2Y1010"),
}

# ── Historical data (30 days back) ────────────────────────────────────────────
@st.cache_data(ttl=300)
def gen_history() -> pd.DataFrame:
    np.random.seed(42)
    n = HIST_DAYS * 24 * 4
    rows = []
    for i in range(n):
        ts  = datetime.combine(TODAY, datetime.min.time()) - timedelta(days=HIST_DAYS) + timedelta(minutes=i*15)
        h, wd = ts.hour, ts.weekday()
        occ = 1.0 if 8 <= h <= 18 and wd < 5 else 0.07
        # weekly seasonal drift — slight upward CO2 trend, temp cycles
        day_i = i / (24*4)
        co2_trend = day_i * 1.5
        rows.append({
            "timestamp":   ts,
            "temperature": round(PARAMS["temperature"]["base"] + np.random.normal(0,.4) + occ*1.2
                                 + 0.8*np.sin(2*np.pi*day_i/7), 1),
            "humidity":    round(np.clip(PARAMS["humidity"]["base"] + np.random.normal(0,3) + occ*5
                                         + 2*np.cos(2*np.pi*day_i/14), 20, 95), 1),
            "pressure":    round(1013.2 + np.random.normal(0,.9) + 1.5*np.sin(2*np.pi*day_i/10), 2),
            "co2":         round(PARAMS["co2"]["base"] + co2_trend + np.random.normal(0,28) + occ*220),
            "dust":        round(max(0, PARAMS["dust"]["base"] + np.random.normal(0,4) + occ*12
                                       + 2*np.sin(2*np.pi*day_i/5)), 1),
        })
    return pd.DataFrame(rows)

# ── Forecast engine (simple statistical) ─────────────────────────────────────
@st.cache_data(ttl=300)
def gen_forecast(days_ahead: int = 14) -> pd.DataFrame:
    """
    Uses the last 14 days of history to:
    1. Compute hourly medians (seasonal pattern)
    2. Compute a linear trend per parameter
    3. Project forward with ±1σ confidence intervals
    """
    hist = gen_history()
    # use last 14 days as basis
    cutoff = datetime.combine(TODAY, datetime.min.time()) - timedelta(days=14)
    basis  = hist[hist["timestamp"] >= cutoff].copy()
    basis["hour"] = basis["timestamp"].dt.hour

    cols = ["temperature","humidity","pressure","co2","dust"]
    hourly_median = basis.groupby("hour")[cols].median()
    hourly_std    = basis.groupby("hour")[cols].std().fillna(1)

    # linear trend from basis
    basis["t_idx"] = (basis["timestamp"] - basis["timestamp"].min()).dt.total_seconds() / 3600
    trends = {}
    for c in cols:
        try:
            z = np.polyfit(basis["t_idx"], basis[c], 1)
            trends[c] = z[0]   # slope per hour
        except Exception:
            trends[c] = 0.0

    rows = []
    for i in range(days_ahead * 24 * 4):
        ts  = datetime.combine(TODAY, datetime.min.time()) + timedelta(minutes=i*15)
        h   = ts.hour
        hrs_ahead = i * 0.25
        row = {"timestamp": ts}
        for c in cols:
            base_val = hourly_median.loc[h, c] + trends[c] * hrs_ahead
            sigma    = hourly_std.loc[h, c]
            row[c]         = round(float(base_val), 2)
            row[f"{c}_lo"] = round(float(base_val - 1.5 * sigma), 2)
            row[f"{c}_hi"] = round(float(base_val + 1.5 * sigma), 2)
        rows.append(row)
    return pd.DataFrame(rows)

# ── Plotly base ───────────────────────────────────────────────────────────────
def PL(**kw):
    base = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(3,8,16,0.88)",
        plot_bgcolor="rgba(9,20,35,0.87)",
        font=dict(family="Times New Roman", color="#e5f8ff"),
        margin=dict(l=14, r=14, t=42, b=14),
        hovermode="x unified",
        dragmode="zoom",
        colorway=["#39d9c8", "#5b8cff", "#ffd166", "#ff5e7e", "#a78bfa", "#ff9f43"],
        xaxis=dict(
            gridcolor="#16435a", showgrid=True, zeroline=False,
            linecolor="#4386b3", tickfont=dict(family="Fira Code", size=10, color="#c8efff"),
            color="#d8ecff"
        ),
        yaxis=dict(
            gridcolor="#16435a", showgrid=True, zeroline=False,
            linecolor="#4386b3", tickfont=dict(family="Fira Code", size=10, color="#c8efff"),
            color="#d8ecff"
        ),
        legend=dict(bgcolor="rgba(0,0,0,0.25)", bordercolor="#2184b8",
                    font=dict(family="Fira Code", size=10, color="#d8ecff")),
        title_font=dict(family="Plus Jakarta Sans", size=16, color="#e5f8ff")
    )
    base.update(kw)
    return base

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;
                padding:16px 0 22px;border-bottom:1px solid #162334;margin-bottom:18px">
        <div style="width:46px;height:46px;background:linear-gradient(135deg,#39d9c8,#5b8cff);
                    border-radius:14px;display:flex;align-items:center;justify-content:center;
                    font-size:24px;box-shadow:0 4px 18px rgba(57,217,200,.3)">🌿</div>
        <div>
            <div style="font-family:Plus Jakarta Sans,sans-serif;font-size:18px;font-weight:800;letter-spacing:1px">ECO-SENSE</div>
            <div style="font-family:Fira Code,monospace;font-size:8.5px;color:#1e3a4a;letter-spacing:3px">SENSOR ANALYTICS</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(57,217,200,.06);border:1px solid rgba(57,217,200,.2);
                border-radius:10px;padding:10px 14px;margin-bottom:16px">
        <div style="font-family:Fira Code,monospace;font-size:8px;letter-spacing:3px;color:#1e4a3a;margin-bottom:5px">DEPLOYMENT</div>
    </div>""", unsafe_allow_html=True)

    # ... (Keep your top branding and deployment info) ...

    st.markdown('<div style="font-family:Fira Code,monospace;font-size:8.5px;letter-spacing:3px;color:#39d9c8;margin-bottom:8px">NAVIGATION</div>', unsafe_allow_html=True)
    
    # Using a cleaner list and removing redundant spaces
    pages = ["📊  Overview", "🌡️  Temp & Humidity", "💨  Air Quality", "🔴  Dust", "🚨  Alerts", "🔮  Forecast"]
    
    # We use an empty string for label, but ensure visibility isn't breaking the DOM
    page = st.radio("Navigation", pages, label_visibility="collapsed")

    # Force the sidebar to stay open and visible with this CSS hack
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] {display: none;} /* Hides the default nav if using multipage files */
        [data-testid="stSidebar"] {
            min-width: 300px !important;
            max-width: 300px !important;
        }
        /* Ensure the radio buttons are large enough to click */
        div[data-testid="stRadio"] > div {
            gap: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # ── Date range with FULL range (past + future) ────────────────────────────
    st.markdown('<div style="font-family:Fira Code,monospace;font-size:8.5px;letter-spacing:3px;color:#1e4a3a;margin-bottom:6px">DATE RANGE</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-family:Fira Code,monospace;font-size:8.5px;color:#4d6e80;
                margin-bottom:10px;line-height:1.6">
        <span style="color:#39d9c8">◀</span> History: back to {MIN_DATE.strftime('%d %b %Y')}<br>
        <span style="color:#a78bfa">▶</span> Forecast: up to {MAX_DATE.strftime('%d %b %Y')}
    </div>""", unsafe_allow_html=True)

    cd1, cd2 = st.columns(2)
    with cd1:
        date_from = st.date_input("From", value=TODAY - timedelta(days=7),
                                   min_value=MIN_DATE, max_value=MAX_DATE, key="df")
    with cd2:
        date_to = st.date_input("To", value=TODAY + timedelta(days=3),
                                 min_value=MIN_DATE, max_value=MAX_DATE, key="dt")
    if date_from > date_to:
        date_from = date_to - timedelta(days=1)

    dlabel = f"{date_from.strftime('%d %b')} → {date_to.strftime('%d %b %Y')}"

    # Mode badge
    has_hist = date_from <= TODAY
    has_fore = date_to   > TODAY
    if has_hist and has_fore:
        mode_html = '<span class="bdg bdg-hist">HIST</span> + <span class="bdg bdg-fore">FORECAST</span>'
        mode_label = "History + Forecast"
    elif has_fore:
        mode_html = '<span class="bdg bdg-fore">FORECAST ONLY</span>'
        mode_label = "Forecast"
    else:
        mode_html = '<span class="bdg bdg-hist">HISTORICAL</span>'
        mode_label = "Historical"

    st.markdown(f'<div style="margin-top:6px;font-family:Fira Code,monospace;font-size:9px;color:#39d9c8">📌 {dlabel}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="margin-top:4px">{mode_html}</div>', unsafe_allow_html=True)

    st.markdown("---")

    with st.expander("⚙️  ALERT THRESHOLDS"):
        co2_w = st.slider("CO₂ Warning (ppm)",   400, 1500, 700,  50)
        co2_d = st.slider("CO₂ Danger (ppm)",    500, 2000, 1000, 50)
        tmp_w = st.slider("Temp Warning (°C)",    18,  40,   26,   1)
        dst_w = st.slider("Dust Warning (µg/m³)", 5,   75,   25,   5)
        hum_w = st.slider("Humidity Warning (%)", 30,  85,   60,   5)

    st.markdown("---")

    # Removed sensor node info cards; focus on the core BME280/CCS811/GP2Y1010 metrics only.

    st.markdown("---")
    st.markdown(f'<div style="font-family:Fira Code,monospace;font-size:8.5px;color:#162334;letter-spacing:2px">SYNC · {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    if st.button("⟳  Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Build combined data view ──────────────────────────────────────────────────
hist_df = gen_history()
fore_df = gen_forecast(FORECAST_DAYS)

s_dt = datetime.combine(date_from, datetime.min.time())
e_dt = datetime.combine(date_to,   datetime.max.time())

# Historical slice
df_h = hist_df[(hist_df["timestamp"] >= s_dt) &
               (hist_df["timestamp"] <= min(e_dt, datetime.combine(TODAY, datetime.max.time())))].copy()

# Forecast slice
df_f = fore_df[(fore_df["timestamp"] > datetime.combine(TODAY, datetime.min.time())) &
               (fore_df["timestamp"] <= e_dt)].copy()

# Combined (only actual values, not CI columns)
actual_cols = ["timestamp","temperature","humidity","pressure","co2","dust"]
df_combined = pd.concat([df_h[actual_cols],
                         df_f[actual_cols] if not df_f.empty else pd.DataFrame(columns=actual_cols)],
                         ignore_index=True).sort_values("timestamp")

# Working df = combined
df = df_combined.copy()
if df.empty:
    df = df_h.copy() if not df_h.empty else hist_df.tail(96).copy()

# ── Helpers ───────────────────────────────────────────────────────────────────
def delta(col, dec=1):
    if len(df) < 2:
        return "d-up", "—"
    mid  = df["timestamp"].quantile(.5)
    prev = df[df["timestamp"] <= mid][col].mean()
    curr = df[df["timestamp"] >  mid][col].mean()
    d    = curr - prev
    return ("d-up" if d >= 0 else "d-down"), f"{'↑' if d>=0 else '↓'} {abs(d):.{dec}f}"

def kpi_cards(metrics=None):
    at = df["temperature"].mean()
    ah = df["humidity"].mean()
    ac = df["co2"].mean()
    ad = df["dust"].mean()
    co2_col  = "#39d9c8" if ac < co2_w else "#ffd166" if ac < co2_d else "#ff5e7e"
    dust_col = "#39d9c8" if ad < dst_w else "#ffd166"
    hum_col  = "#5b8cff" if ah < hum_w else "#ffd166"

    all_cards = {
        "temperature": ("kc-teal",   "🌡️","BME280",  "TEMPERATURE",f"{at:.1f}","°C",   "#39d9c8", *delta("temperature")),
        "humidity":    ("kc-indigo", "💧","BME280",  "HUMIDITY",   f"{ah:.1f}","%",    hum_col,   *delta("humidity")),
        "co2":         ("kc-amber",  "💨","CCS811",  "CO₂",        f"{ac:.0f}","ppm",  co2_col,   *delta("co2",0)),
        "dust":        ("kc-rose",   "🔴","GP2Y1010","DUST PM2.5", f"{ad:.1f}","µg/m³",dust_col, *delta("dust")),
    }

    if metrics is None:
        metrics = ["temperature", "humidity", "co2", "dust"]

    cards = [all_cards[m] for m in metrics if m in all_cards]
    cols = st.columns(max(1, len(cards)))
    for col_, card in zip(cols, cards):
        cls, icon, chip, lbl, val, unit, color, dcls, dtxt = card
        with col_:
            st.markdown(f"""
            <div class="kpi-card {cls}">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-chip">{chip}</div>
                <div class="kpi-label">{lbl}</div>
                <div class="kpi-val" style="color:{color}">{val}<span class="kpi-unit">{unit}</span></div>
                <div class="kpi-delta {dcls}">{dtxt}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:18px'></div>", unsafe_allow_html=True)

def heatmap_hour_dow(col, title, colorscale):
    dh = df.copy()
    dh["hour"] = dh["timestamp"].dt.hour
    dh["dow"]  = dh["timestamp"].dt.day_name().str[:3]
    order = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    piv = dh.groupby(["dow","hour"])[col].mean().reset_index()
    piv["dow"] = pd.Categorical(piv["dow"], categories=order, ordered=True)
    piv = piv.sort_values("dow")
    pw  = piv.pivot(index="dow", columns="hour", values=col)
    fig = go.Figure(go.Heatmap(
        z=pw.values, x=pw.columns, y=pw.index,
        colorscale=colorscale,
        text=np.round(pw.values,1), texttemplate="%{text}",
        textfont={"size":9,"family":"Fira Code"}, showscale=True,
        hovertemplate="<b>%{y} %{x}:00</b><br>"+title+": %{z:.1f}<extra></extra>"
    ))
    fig.update_layout(height=220, **PL(), xaxis_title="Hour of Day", title=title)
    return fig

def add_today_line(fig):
    """Add a vertical 'TODAY' marker to any figure."""
    today_dt = datetime.combine(TODAY, datetime.min.time())
    # avoid Plotly internal datetime mean bug with annotation preprocessing
    fig.add_vline(
        x=today_dt,
        line_dash="dash",
        line_color="#72d0ff",
        line_width=2,
        opacity=0.8,
    )
    fig.add_annotation(
        x=today_dt,
        y=1.01,
        xref="x",
        yref="paper",
        text="TODAY",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        bgcolor="rgba(26,53,82,0.8)",
        bordercolor="#72d0ff",
        borderwidth=1,
        font=dict(color="#72d0ff", size=10, family="Fira Code", weight="bold"),
    )
    return fig

def forecast_trace(col, color):
    """Returns (actual_trace, forecast_trace, CI_trace) for a given column."""
    traces = []
    if not df_h.empty:
        d_h = df_h.sort_values("timestamp")
        traces.append(go.Scatter(
            x=d_h["timestamp"], y=d_h[col].rolling(4,min_periods=1).mean(),
            name="Historical", line=dict(color=color, width=2.2),
            fill="tozeroy",
            fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},.05)",
            hovertemplate="<b>%{x|%d %b %H:%M}</b><br>Historical: %{y:.1f}<extra></extra>"
        ))
    if not df_f.empty:
        d_f = df_f.sort_values("timestamp")
        lo_col = f"{col}_lo"
        hi_col = f"{col}_hi"
        # CI band
        traces.append(go.Scatter(
            x=pd.concat([d_f["timestamp"], d_f["timestamp"][::-1]]),
            y=pd.concat([d_f[hi_col], d_f[lo_col][::-1]]),
            fill="toself", fillcolor="rgba(167,139,250,.1)",
            line=dict(color="rgba(0,0,0,0)"),
            name="95% Conf. Interval", showlegend=True,
            hoverinfo="skip"
        ))
        traces.append(go.Scatter(
            x=d_f["timestamp"], y=d_f[col],
            name="Forecast", line=dict(color="#a78bfa", width=2, dash="dot"),
            hovertemplate="<b>%{x|%d %b %H:%M}</b><br>Forecast: %{y:.1f}<extra></extra>"
        ))
    return traces

# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊  Overview":
    ac = df["co2"].mean()
    air_cls = "bdg-ok" if ac < co2_w else "bdg-warn" if ac < co2_d else "bdg-bad"
    air_lbl = "GOOD"  if ac < co2_w else "WARN"  if ac < co2_d else "POOR"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;padding:18px 22px;
                background:var(--bg1);border:1px solid var(--border);
                border-left:4px solid #39d9c8;border-radius:16px;margin-bottom:20px">
        <div style="font-size:34px">🏢</div>
        <div>
            <div style="font-family:Fira Code,monospace;font-size:10px;color:#4d6e80;letter-spacing:2px">
                {dlabel} · {mode_label} · BME280 · CCS811 · GP2Y1010</div>
        </div>
        <div style="margin-left:auto;text-align:right">
            <span class="bdg {air_cls}" style="font-size:11px;padding:5px 14px">AIR {air_lbl}</span>
            <div style="margin-top:5px">{mode_html}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    kpi_cards(["temperature", "humidity", "co2", "dust"])

    # Multi-param overlay with history + forecast
    st.markdown('<div class="sh">Multi-Parameter Trend — History & Forecast</div>', unsafe_allow_html=True)
    param_opts = {
        "🌡️ Temperature (°C)": ("temperature","#39d9c8"),
        "💧 Humidity (%)":     ("humidity",   "#5b8cff"),
        "💨 CO₂ (ppm)":        ("co2",        "#ffd166"),
        "🔴 Dust (µg/m³)":     ("dust",       "#ff5e7e"),
    }
    c_sel, c_tog = st.columns([4, 1])
    with c_sel:
        sel = st.multiselect("Choose parameters (up to 4)",
            list(param_opts.keys()),
            default=["🌡️ Temperature (°C)","💨 CO₂ (ppm)","🔴 Dust (µg/m³)"],
            max_selections=4, key="ov_sel")
    with c_tog:
        smooth_ov = st.toggle("Smooth", value=True, key="ov_sm")

    if sel:
        n = len(sel)
        fig = make_subplots(rows=n, cols=1, shared_xaxes=True, vertical_spacing=.05,
                            subplot_titles=sel)
        for i, s in enumerate(sel):
            k, c = param_opts[s]
            if not df_h.empty:
                dh_s = df_h.sort_values("timestamp")
                yh = dh_s[k].rolling(4,min_periods=1).mean() if smooth_ov else dh_s[k]
                fig.add_trace(go.Scatter(
                    x=dh_s["timestamp"], y=yh,
                    line=dict(color=c,width=2), name="Historical" if i==0 else "",
                    showlegend=(i==0),
                    fill="tozeroy", fillcolor=f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},.04)",
                    hovertemplate=f"<b>%{{x|%d %b %H:%M}}</b><br>{s}: %{{y:.1f}}<extra></extra>"
                ), row=i+1, col=1)
            if not df_f.empty:
                df_s = df_f.sort_values("timestamp")
                yf = df_s[k]
                fig.add_trace(go.Scatter(
                    x=df_s["timestamp"], y=yf,
                    line=dict(color="#a78bfa",width=1.8,dash="dot"),
                    name="Forecast" if i==0 else "", showlegend=(i==0),
                    hovertemplate=f"<b>%{{x|%d %b %H:%M}}</b><br>Forecast: %{{y:.1f}}<extra></extra>"
                ), row=i+1, col=1)
        today_dt = datetime.combine(TODAY, datetime.min.time())
        for r in range(1, n+1):
            fig.add_vline(x=today_dt, line_dash="dot", line_color="#a78bfa",
                          line_width=1, row=r, col=1)
        fig.update_annotations(font=dict(family="Fira Code",size=10,color="#4d6e80"))
        fig.update_layout(height=max(260,n*130), **PL())
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Sparklines — historical only
    if not df_h.empty:
        st.markdown('<div class="sh">Live Sparklines — All Sensors</div>', unsafe_allow_html=True)
        sparks = [("temperature","#39d9c8","Temp °C"),("humidity","#5b8cff","Humid %"),
                  ("dust","#ff5e7e","Dust µg/m³")]
        sp_cols = st.columns(6)
        for col, (k,c,t) in zip(sp_cols, sparks):
            last_n = df_h.sort_values("timestamp").tail(96)
            y = last_n[k].rolling(4,min_periods=1).mean()
            fig_sp = go.Figure(go.Scatter(x=last_n["timestamp"], y=y,
                line=dict(color=c,width=2), fill="tozeroy",
                fillcolor=f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},.07)"))
            fig_sp.update_layout(height=90, title=t, showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,16,24,.55)",
                margin=dict(l=4,r=4,t=22,b=4),
                font=dict(family="Fira Code",size=9,color="#4d6e80"),
                xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False, zeroline=False,
                           tickfont=dict(family="Fira Code",size=8)))
            with col:
                st.plotly_chart(fig_sp, use_container_width=True, config={"displayModeBar": False})

    # Stats
    st.markdown('<div class="sh">Statistical Summary</div>', unsafe_allow_html=True)
    stat_params = [("temperature","Temp °C"),("humidity","Humid %"),
                   ("co2","CO₂ ppm"),("dust","Dust µg/m³")]
    sc = st.columns(6)
    for col, (k, lbl) in zip(sc, stat_params):
        mn, mx, av = df[k].min(), df[k].max(), df[k].mean()
        with col:
            st.markdown(f"""
            <div style="background:var(--bg1);border:1px solid var(--border);
                        border-radius:14px;padding:14px;text-align:center">
                <div style="font-family:Fira Code,monospace;font-size:7.5px;letter-spacing:2px;
                            color:#1e4a3a;margin-bottom:10px">{lbl}</div>
                <div style="display:flex;justify-content:space-around">
                    <div><div style="font-family:Plus Jakarta Sans,sans-serif;font-size:15px;font-weight:700;color:#5b8cff">{mn:.1f}</div>
                         <div style="font-family:Fira Code,monospace;font-size:7px;color:#4d6e80">MIN</div></div>
                    <div><div style="font-family:Plus Jakarta Sans,sans-serif;font-size:15px;font-weight:700;color:#39d9c8">{av:.1f}</div>
                         <div style="font-family:Fira Code,monospace;font-size:7px;color:#4d6e80">AVG</div></div>
                    <div><div style="font-family:Plus Jakarta Sans,sans-serif;font-size:15px;font-weight:700;color:#ff5e7e">{mx:.1f}</div>
                         <div style="font-family:Fira Code,monospace;font-size:7px;color:#4d6e80">MAX</div></div>
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TEMP & HUMIDITY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌡️  Temp & Humidity":
    st.markdown(f'<div class="sh">BME280 — Temperature · Humidity · Pressure · {dlabel}</div>', unsafe_allow_html=True)
    kpi_cards(["temperature", "humidity"])

    tab1, tab2 = st.tabs(["🌡️  TEMPERATURE","💧  HUMIDITY"])

    for tab, col_key, color, title, unit, warn_val in [
        (tab1,"temperature","#39d9c8","Temperature","°C",tmp_w),
        (tab2,"humidity",   "#5b8cff","Humidity",   "%", hum_w),
    ]:
        with tab:
            win = st.select_slider("Smoothing",
                options=["None","15 min","30 min","1 hour"],value="15 min",key=f"win_{col_key}")
            w = {"None":1,"15 min":1,"30 min":2,"1 hour":4}[win]

            fig = go.Figure()
            if not df_h.empty:
                dh_s = df_h.sort_values("timestamp")
                y = dh_s[col_key].rolling(w,min_periods=1).mean()
                fig.add_trace(go.Scatter(x=dh_s["timestamp"], y=y,
                    name="Historical", line=dict(color=color,width=2.5),
                    fill="tozeroy", fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},.05)",
                    hovertemplate=f"<b>%{{x|%d %b %H:%M}}</b><br>{title}: %{{y:.1f}} {unit}<extra></extra>"
                ))
            if not df_f.empty:
                dfs = df_f.sort_values("timestamp")
                fig.add_trace(go.Scatter(
                    x=pd.concat([dfs["timestamp"],dfs["timestamp"][::-1]]),
                    y=pd.concat([dfs[f"{col_key}_hi"],dfs[f"{col_key}_lo"][::-1]]),
                    fill="toself", fillcolor="rgba(167,139,250,.08)",
                    line=dict(color="rgba(0,0,0,0)"), name="Confidence Interval"))
                fig.add_trace(go.Scatter(x=dfs["timestamp"], y=dfs[col_key],
                    name="Forecast", line=dict(color="#a78bfa",width=2,dash="dot"),
                    hovertemplate=f"<b>%{{x|%d %b %H:%M}}</b><br>Forecast: %{{y:.1f}} {unit}<extra></extra>"
                ))
            if warn_val:
                fig.add_hline(y=warn_val, line_dash="dash", line_color="#ffd166",
                              annotation_text=f"Warn {warn_val}{unit}",
                              annotation_font=dict(color="#ffd166",size=10,family="Fira Code"))
            add_today_line(fig)
            fig.update_layout(title=f"{title} ({unit}) — History + Forecast", height=340, **PL())
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            if not df_h.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(heatmap_hour_dow(col_key, f"{title} {unit}",
                        [[0,"#05080a"],[.4,color],[1,"#ff5e7e"]]),
                        use_container_width=True, config={"displayModeBar": False})
                with c2:
                    fig_h = go.Figure(go.Histogram(x=df_h[col_key], nbinsx=40,
                        marker_color=color, opacity=.85,
                        hovertemplate=f"{title}: %{{x:.1f}}<br>Count: %{{y}}<extra></extra>"))
                    fig_h.update_layout(title=f"{title} Distribution (Historical)",
                                         height=220, bargap=.04, **PL())
                    st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# AIR QUALITY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💨  Air Quality":
    st.markdown(f'<div class="sh">CCS811 — CO₂ · {dlabel}</div>', unsafe_allow_html=True)
    kpi_cards(["co2"])

    if not df_h.empty:
        cur_co2  = float(df_h["co2"].iloc[-1])
        co2_col  = "#39d9c8" if cur_co2 < co2_w else "#ffd166" if cur_co2 < co2_d else "#ff5e7e"
        g1, _ = st.columns(2)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=cur_co2,
            delta={"reference":co2_w + (co2_d-co2_w)*.35,"valueformat":".0f",
                   "increasing":{"color":"#ff5e7e"},"decreasing":{"color":"#39d9c8"}},
            title={"text":"CO₂ — Latest Reading","font":{"color":"#4d6e80","size":13,"family":"Plus Jakarta Sans"}},
            number={"suffix":" ppm","font":{"color":co2_col,"size":26,"family":"Plus Jakarta Sans"}},
            gauge={"axis":{"range":[400,2000],"tickcolor":"#162334",
                           "tickfont":{"color":"#4d6e80","size":9,"family":"Fira Code"}},
                   "bar":{"color":co2_col,"thickness":.25},
                   "bgcolor":"#05080a","bordercolor":"#162334","borderwidth":1,
                   "steps":[{"range":[400,1100],"color":"rgba(57,217,200,.06)"},
                             {"range":[1100,1550],"color":"rgba(255,209,102,.06)"},
                             {"range":[1550,2000],"color":"rgba(255,94,126,.06)"}],
                   "threshold":{"line":{"color":co2_col,"width":3},"thickness":.88,"value":cur_co2}}
        ))
        fig_g.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)",
                             font=dict(color="#4d6e80"), margin=dict(l=10,r=10,t=30,b=10))
        with g1:
            st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": False})

    show_raw = st.toggle("Show raw (unsmoothed)", value=False)
    c1, c2 = st.columns(2)
    for col_w, col_key, color, title, unit, warn, danger in [
        (c1,"co2","#ffd166","CO₂","ppm",co2_w,co2_d),
    ]:
        fig = go.Figure()
        if not df_h.empty:
            dh_s = df_h.sort_values("timestamp")
            y = dh_s[col_key] if show_raw else dh_s[col_key].rolling(4,min_periods=1).mean()
            fig.add_trace(go.Scatter(x=dh_s["timestamp"], y=y,
                name="Historical", line=dict(color=color,width=2.2),
                fill="tozeroy", fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},.05)",
                hovertemplate=f"<b>%{{x|%d %b %H:%M}}</b><br>{title}: %{{y:.0f}} {unit}<extra></extra>"
            ))
        if not df_f.empty:
            dfs = df_f.sort_values("timestamp")
            fig.add_trace(go.Scatter(
                x=pd.concat([dfs["timestamp"],dfs["timestamp"][::-1]]),
                y=pd.concat([dfs[f"{col_key}_hi"],dfs[f"{col_key}_lo"][::-1]]),
                fill="toself", fillcolor="rgba(167,139,250,.08)",
                line=dict(color="rgba(0,0,0,0)"), name="Confidence Interval"))
            fig.add_trace(go.Scatter(x=dfs["timestamp"], y=dfs[col_key],
                name="Forecast", line=dict(color="#a78bfa",width=2,dash="dot"),
                hovertemplate=f"Forecast: %{{y:.0f}} {unit}<extra></extra>"
            ))
        fig.add_hline(y=danger, line_dash="dash", line_color="#ff5e7e",
                      annotation_text=f"Danger {danger}",
                      annotation_font=dict(color="#ff5e7e",size=10,family="Fira Code"))
        fig.add_hline(y=warn, line_dash="dash", line_color="#ffd166",
                      annotation_text=f"Warn {warn}",
                      annotation_font=dict(color="#ffd166",size=10,family="Fira Code"))
        add_today_line(fig)
        fig.update_layout(title=f"{title} ({unit}) — History + Forecast", height=310, **PL())
        with col_w:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if not df_h.empty:
        st.plotly_chart(heatmap_hour_dow("co2","CO₂ ppm",
            [[0,"#05080a"],[.4,"#ffd166"],[.7,"#ff9f43"],[1,"#ff5e7e"]]),
            use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# DUST
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔴  Dust":
    st.markdown(f'<div class="sh">GP2Y1010 — Particulate Matter PM2.5 · {dlabel}</div>', unsafe_allow_html=True)
    kpi_cards(["dust"])

    fig = go.Figure()
    if not df_h.empty:
        dh_s = df_h.sort_values("timestamp")
        fig.add_trace(go.Scatter(x=dh_s["timestamp"],
            y=dh_s["dust"].rolling(4,min_periods=1).mean(),
            name="Historical", line=dict(color="#ff5e7e",width=2.5),
            fill="tozeroy", fillcolor="rgba(255,94,126,.05)",
            hovertemplate="<b>%{x|%d %b %H:%M}</b><br>Dust: %{y:.1f} µg/m³<extra></extra>"
        ))
    if not df_f.empty:
        dfs = df_f.sort_values("timestamp")
        fig.add_trace(go.Scatter(
            x=pd.concat([dfs["timestamp"],dfs["timestamp"][::-1]]),
            y=pd.concat([dfs["dust_hi"],dfs["dust_lo"][::-1]]),
            fill="toself", fillcolor="rgba(167,139,250,.08)",
            line=dict(color="rgba(0,0,0,0)"), name="Confidence Interval"))
        fig.add_trace(go.Scatter(x=dfs["timestamp"], y=dfs["dust"],
            name="Forecast", line=dict(color="#a78bfa",width=2,dash="dot"),
            hovertemplate="Forecast: %{y:.1f} µg/m³<extra></extra>"
        ))
    fig.add_hline(y=35,    line_dash="dash", line_color="#ff5e7e",
                  annotation_text="WHO 35 µg/m³",
                  annotation_font=dict(color="#ff5e7e",size=10,family="Fira Code"))
    fig.add_hline(y=dst_w, line_dash="dash", line_color="#ffd166",
                  annotation_text=f"Warn {dst_w} µg/m³",
                  annotation_font=dict(color="#ffd166",size=10,family="Fira Code"))
    add_today_line(fig)
    fig.update_layout(title="PM2.5 Dust (µg/m³) — History + Forecast", height=340, **PL())
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if not df_h.empty:
        c1, c2 = st.columns(2)
        with c1:
            dh2 = df_h.copy(); dh2["hour"] = dh2["timestamp"].dt.hour
            dh_agg = dh2.groupby("hour")["dust"].mean().reset_index()
            fig_bar = go.Figure(go.Bar(x=dh_agg["hour"], y=dh_agg["dust"],
                marker_color="#ff5e7e", marker_line_width=0, opacity=.85,
                hovertemplate="Hour %{x}:00<br>Avg: %{y:.1f} µg/m³<extra></extra>"))
            fig_bar.update_layout(title="Avg Dust by Hour (Historical)",
                                   height=260, **PL(), xaxis_title="Hour", showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        with c2:
            st.plotly_chart(heatmap_hour_dow("dust","Dust µg/m³",
                [[0,"#05080a"],[.5,"#ff9f43"],[1,"#ff5e7e"]]),
                use_container_width=True, config={"displayModeBar": False})
            

# ══════════════════════════════════════════════════════════════════════════════
# FORECAST
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔮  Forecast":
    st.markdown(f'<div class="sh">Forecast Dashboard · {dlabel}</div>', unsafe_allow_html=True)
    kpi_cards(["temperature", "humidity", "co2", "dust"])

    st.markdown('<div class="sh-pred">Forecast parameters</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        fore_param = st.selectbox("Parameter to forecast", [
            "temperature","humidity","co2","dust"
        ], format_func=lambda x: PARAMS[x]["label"], key="fp_fore")
    with c2:
        fore_days = st.slider("Forecast horizon (days)", 1, FORECAST_DAYS, 7, key="fdays_fore")
    with c3:
        hist_window = st.slider("Historical context (days)", 3, HIST_DAYS, 14, key="hwin_fore")

    color = PARAMS[fore_param]["color"]
    unit  = PARAMS[fore_param]["unit"]
    label = PARAMS[fore_param]["label"]

    hist_start = datetime.combine(TODAY - timedelta(days=hist_window), datetime.min.time())
    hist_slice = hist_df[hist_df["timestamp"] >= hist_start].copy()
    fore_end   = datetime.combine(TODAY + timedelta(days=fore_days), datetime.max.time())
    fore_slice = fore_df[fore_df["timestamp"] <= fore_end].copy()

    fig = go.Figure()
    if not hist_slice.empty:
        dh_s = hist_slice.sort_values("timestamp")
        y_h  = dh_s[fore_param].rolling(4,min_periods=1).mean()
        fig.add_trace(go.Scatter(x=dh_s["timestamp"], y=y_h,
            name=f"Historical {label}", line=dict(color=color,width=2.5),
            fill="tozeroy", fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},.07)",
            hovertemplate=f"<b>%{{x|%d %b %H:%M}}</b><br>Historical: %{{y:.1f}} {unit}<extra></extra>"
        ))

    if not fore_slice.empty:
        dfs = fore_slice.sort_values("timestamp")
        fig.add_trace(go.Scatter(
            x=pd.concat([dfs["timestamp"], dfs["timestamp"][::-1]]),
            y=pd.concat([dfs[f"{fore_param}_hi"], dfs[f"{fore_param}_lo"][::-1]]),
            fill="toself", fillcolor="rgba(167,139,250,.12)", line=dict(color="rgba(0,0,0,0)"),
            name="Confidence Band"
        ))
        fig.add_trace(go.Scatter(x=dfs["timestamp"], y=dfs[fore_param],
            name=f"Forecast {label}", line=dict(color="#a78bfa",width=2.8,dash="dash"),
            hovertemplate=f"<b>%{{x|%d %b %H:%M}}</b><br>Forecast: %{{y:.1f}} {unit}<extra></extra>"
        ))

    add_today_line(fig)
    fig.update_layout(title=f"{label} — Forecast ({fore_days}d) + History ({hist_window}d)",
                      height=420, **PL())
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# ALERTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🚨  Alerts":
    st.markdown(f'<div class="sh">Alert System · {dlabel}</div>', unsafe_allow_html=True)
    kpi_cards(["co2", "dust", "temperature", "humidity"])

    TH = {
        "co2":         {"w":co2_w,"d":co2_d,   "u":"ppm",  "l":"CO₂"},
        "temperature": {"w":tmp_w,"d":tmp_w+4, "u":"°C",   "l":"Temperature"},
        "humidity":    {"w":hum_w,"d":hum_w+10,"u":"%",    "l":"Humidity"},
        "dust":        {"w":dst_w,"d":35,       "u":"µg/m³","l":"Dust PM2.5"},
    }

    last = df_h.iloc[-1] if not df_h.empty else df.iloc[-1]
    alerts = []
    for p, th in TH.items():
        v = float(last[p])
        if v >= th["d"]:
            alerts.append({"p":th["l"],"v":v,"u":th["u"],"lv":"danger","thr":th["d"]})
        elif v >= th["w"]:
            alerts.append({"p":th["l"],"v":v,"u":th["u"],"lv":"warn","thr":th["w"]})

    # Forecast alerts — check if any forecasted values breach thresholds
    fore_alerts = []
    if not df_f.empty:
        for p, th in TH.items():
            breach = df_f[df_f[p] >= th["w"]]
            if not breach.empty:
                first_breach = breach.iloc[0]
                days_away = (first_breach["timestamp"] - datetime.combine(TODAY, datetime.min.time())).days
                fore_alerts.append({
                    "p": th["l"], "v": float(first_breach[p]),
                    "u": th["u"], "thr": th["w"],
                    "ts": first_breach["timestamp"].strftime("%d %b, %H:%M"),
                    "days": days_away
                })

    dc = sum(1 for a in alerts if a["lv"]=="danger")
    wc = sum(1 for a in alerts if a["lv"]=="warn")
    ok = len(TH) - len(alerts)

    c1, c2, c3 = st.columns(3)
    for col, lbl, val, color, cls in [
        (c1,"CRITICAL NOW",dc,"#ff5e7e","kc-rose"),
        (c2,"WARNINGS NOW",wc,"#ffd166","kc-amber"),
        (c3,"CLEAR NOW",   ok,"#39d9c8","kc-teal"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card {cls}" style="height:100px">
                <div class="kpi-label">{lbl}</div>
                <div class="kpi-val" style="color:{color};font-size:44px">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:14px'></div>", unsafe_allow_html=True)

    if alerts:
        st.markdown('<div class="sh">⚡ Active Alerts (Current Readings)</div>', unsafe_allow_html=True)
        for a in sorted(alerts, key=lambda x: 0 if x["lv"]=="danger" else 1):
            cls  = "alrt-bad"  if a["lv"]=="danger" else "alrt-warn"
            icon = "🔴" if a["lv"]=="danger" else "🟡"
            st.markdown(f"""
            <div class="alrt {cls}">
                {icon} <strong style="font-family:Plus Jakarta Sans">{a['p']}</strong>
                is <strong style="font-family:Fira Code,monospace">{a['v']:.1f} {a['u']}</strong>
                <span style="color:#1e4a3a;font-family:Fira Code,monospace;font-size:11px">
                 (threshold: {a['thr']} {a['u']})</span>
            </div>""", unsafe_allow_html=True)

    if fore_alerts:
        st.markdown('<div class="sh-pred">🔮 Forecasted Threshold Breaches</div>', unsafe_allow_html=True)
        for fa in fore_alerts:
            st.markdown(f"""
            <div class="alrt alrt-warn" style="border-left-color:#a78bfa;background:rgba(167,139,250,.05);border-color:rgba(167,139,250,.2)">
                🔮 <strong style="font-family:Plus Jakarta Sans">{fa['p']}</strong>
                forecast to reach <strong style="font-family:Fira Code,monospace">{fa['v']:.1f} {fa['u']}</strong>
                on <strong>{fa['ts']}</strong>
                <span style="color:#a78bfa;font-family:Fira Code,monospace;font-size:11px">
                 (~{fa['days']} day(s) from now · warn threshold: {fa['thr']} {fa['u']})</span>
            </div>""", unsafe_allow_html=True)

    # Radar
    st.markdown('<div class="sh">Sensor Health Radar</div>', unsafe_allow_html=True)
    rp  = ["co2","temperature","humidity","dust"]
    rl  = ["CO₂","Temp","Humidity","Dust"]
    nms = {"co2":1500,"temperature":35,"humidity":85,"dust":50}
    vals = [min(1, float(last[p])/nms[p])*100 for p in rp] + \
           [min(1, float(last[rp[0]])/nms[rp[0]])*100]
    fig_r = go.Figure(go.Scatterpolar(
        r=vals, theta=rl+[rl[0]], fill="toself",
        line=dict(color="#39d9c8",width=2.5),
        fillcolor="rgba(57,217,200,.1)",
        hovertemplate="<b>%{theta}</b>: %{r:.0f}%<extra></extra>"
    ))
    fig_r.update_layout(
        polar=dict(bgcolor="rgba(10,16,24,.55)",
                   radialaxis=dict(visible=True,range=[0,100],gridcolor="#162334",
                                   tickfont=dict(family="Fira Code",size=9,color="#1e3a4a")),
                   angularaxis=dict(gridcolor="#162334",
                                    tickfont=dict(family="Fira Code",size=11,color="#4d6e80"))),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#4d6e80",family="Plus Jakarta Sans"),
        showlegend=False, height=360, margin=dict(l=50,r=50,t=20,b=20)
    )
    st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar": False})

    # Event log
    st.markdown('<div class="sh">Alert Event Log</div>', unsafe_allow_html=True)
    hist_log = []
    for _, row in df_h.iterrows():
        for p, th in TH.items():
            if row[p] >= th["w"]:
                hist_log.append({
                    "Time":    row["timestamp"],
                    "Sensor":  th["l"],
                    "Value":   round(row[p],1),
                    "Unit":    th["u"],
                    "Level":   "🔴 Danger" if row[p] >= th["d"] else "🟡 Warning"
                })
    if hist_log:
        df_hl = pd.DataFrame(hist_log).sort_values("Time",ascending=False).head(150)
        st.dataframe(df_hl, use_container_width=True, height=280,
                     column_config={"Time": st.column_config.DatetimeColumn(
                         "Time", format="DD MMM, HH:mm")})

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;font-family:Fira Code,monospace;
            font-size:8.5px;color:#0f1922;padding:6px 0;letter-spacing:3px">
    ECO-SENSE
</div>""", unsafe_allow_html=True)