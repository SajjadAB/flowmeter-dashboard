import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Flowmeter Validation Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Background */
.stApp {
    background: #0d1117;
    color: #e6edf3;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

/* Metric cards */
.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 18px 22px;
    text-align: center;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #58a6ff; }
.metric-label {
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #8b949e;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    font-family: 'IBM Plex Mono', monospace;
    color: #58a6ff;
}
.metric-unit {
    font-size: 12px;
    color: #8b949e;
    margin-top: 2px;
}

/* Section headers */
.section-header {
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #8b949e;
    font-family: 'IBM Plex Mono', monospace;
    border-bottom: 1px solid #30363d;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

/* Status badges */
.badge-ok   { background:#1f4f2e; color:#3fb950; border:1px solid #2ea043; padding:2px 10px; border-radius:20px; font-size:11px; font-family:'IBM Plex Mono',monospace; }
.badge-warn { background:#4a2d00; color:#e3b341; border:1px solid #d29922; padding:2px 10px; border-radius:20px; font-size:11px; font-family:'IBM Plex Mono',monospace; }
.badge-err  { background:#4a1a1a; color:#f85149; border:1px solid #da3633; padding:2px 10px; border-radius:20px; font-size:11px; font-family:'IBM Plex Mono',monospace; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: #161b22;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #30363d;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #8b949e;
    border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.5px;
}
.stTabs [aria-selected="true"] {
    background: #21262d !important;
    color: #58a6ff !important;
}

/* Plotly charts transparent bg */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }

/* Selectbox & slider */
.stSelectbox > div, .stSlider > div { color: #c9d1d9; }

/* Divider */
hr { border-color: #30363d; }
</style>
""", unsafe_allow_html=True)

# ─── Data ───────────────────────────────────────────────────────────────────
DATA_OFF = [
    {"pct": 54,  "fixed": 4.35,  "variable": 3.57},
    {"pct": 70,  "fixed": 7.78,  "variable": 8.02},
    {"pct": 100, "fixed": 10.82, "variable": 10.77},
    {"pct": 45,  "fixed": 2.05,  "variable": 2.15},
    {"pct": 40,  "fixed": 0,     "variable": 1.32},
]
DATA_ON = [
    {"pct": 100, "fixed": 86,    "variable": 82},
    {"pct": 80,  "fixed": 73.3,  "variable": 68.29},
    {"pct": 65,  "fixed": 46.61, "variable": 44.12},
    {"pct": 54,  "fixed": 27.49, "variable": 26.86},
    {"pct": 40,  "fixed": 8.81,  "variable": 9.24},
    {"pct": 25,  "fixed": 4.47,  "variable": 5.16},
    {"pct": 10,  "fixed": 2.02,  "variable": 2.92},
    {"pct": 2,   "fixed": 1.91,  "variable": 2.88},
]

@st.cache_data
def load_data():
    df_off = pd.DataFrame(DATA_OFF).sort_values("pct").reset_index(drop=True)
    df_on  = pd.DataFrame(DATA_ON).sort_values("pct").reset_index(drop=True)
    df_off["diff"] = df_off["variable"] - df_off["fixed"]
    df_on["diff"]  = df_on["variable"]  - df_on["fixed"]
    df_off["state"] = "OFF"
    df_on["state"]  = "ON"
    return df_off, df_on

df_off, df_on = load_data()

# ─── Plotly theme ───────────────────────────────────────────────────────────
LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22,27,34,1)",
    font=dict(family="IBM Plex Mono", color="#c9d1d9", size=11),
    margin=dict(l=50, r=30, t=50, b=50),
    xaxis=dict(gridcolor="#21262d", zerolinecolor="#30363d", linecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", zerolinecolor="#30363d", linecolor="#30363d"),
)

LEGEND_STYLE = dict(bgcolor="rgba(0,0,0,0)", bordercolor="#30363d", borderwidth=1)

BLUE   = "#58a6ff"
AMBER  = "#e3b341"
GREEN  = "#3fb950"
RED    = "#f85149"

# ─── Statistics helper ──────────────────────────────────────────────────────
def compute_stats(df):
    y_true = df["fixed"].values
    y_pred = df["variable"].values
    err    = y_pred - y_true
    mae    = np.mean(np.abs(err))
    rmse   = np.sqrt(np.mean(err**2))
    bias   = np.mean(err)
    mask   = y_true != 0
    mape   = np.mean(np.abs(err[mask] / y_true[mask])) * 100 if mask.sum() > 0 else 0
    r2     = np.corrcoef(y_true, y_pred)[0, 1]**2 if len(y_true) > 1 else 0
    return dict(mae=mae, rmse=rmse, bias=bias, mape=mape, r2=r2)

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💧 Flowmeter\nValidation")
    st.markdown("---")
    st.markdown("**PROJECT**")
    st.markdown("UNIT 2 · RU32D010")
    st.markdown("---")
    pump_state = st.radio("Pump State", ["OFF", "ON", "Both"], index=2)
    st.markdown("---")
    tolerance_pct = st.slider("Tolerance (%)", 1, 20, 5, 1)
    st.markdown("---")
    st.markdown("**SENSORS**")
    st.markdown("🔵 Fixed Flowmeter")
    st.markdown("🟡 Portable Flowmeter")
    st.markdown("---")
    st.caption("Flowmeter Validation Dashboard v1.0")

# select data based on pump state
if pump_state == "OFF":
    df = df_off
elif pump_state == "ON":
    df = df_on
else:
    df = pd.concat([df_off, df_on], ignore_index=True)

stats = compute_stats(df)
oot   = df[np.abs(df["diff"]) > (tolerance_pct / 100 * df["fixed"].replace(0, np.nan))].dropna()

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
      <div>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:22px;font-weight:700;color:#e6edf3;">
          Flowmeter Validation Dashboard
        </span><br>
        <span style="font-size:13px;color:#8b949e;font-family:'IBM Plex Mono',monospace;">
          UNIT 2 · RU32D010 · Control Valve Analysis
        </span>
      </div>
      <div>
        {'<span class="badge-ok">● CALIBRATED</span>' if len(oot)==0 else f'<span class="badge-warn">⚠ {len(oot)} OOT POINTS</span>'}
        &nbsp;
        <span style="font-size:11px;color:#8b949e;font-family:'IBM Plex Mono',monospace;">
          Pump: <b style="color:#58a6ff;">{pump_state}</b>
        </span>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# ─── KPI Row ────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
kpi_data = [
    (k1, "MAE",  f"{stats['mae']:.3f}",  "t/h"),
    (k2, "RMSE", f"{stats['rmse']:.3f}", "t/h"),
    (k3, "BIAS", f"{stats['bias']:+.3f}","t/h"),
    (k4, "MAPE", f"{stats['mape']:.2f}", "%"),
    (k5, "R²",   f"{stats['r2']:.4f}",   "correlation"),
]
for col, label, val, unit in kpi_data:
    with col:
        st.markdown(
            f"""<div class="metric-card">
                  <div class="metric-label">{label}</div>
                  <div class="metric-value">{val}</div>
                  <div class="metric-unit">{unit}</div>
                </div>""",
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈  Trend",
    "📊  Difference",
    "🎯  Parity",
    "🌡️  Heatmap",
    "🔬  Bias Analysis",
])

# ══════════════════════════════════════════════════════
# TAB 1 — Trend (Line Chart)
# ══════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Flow Rate vs Valve Opening — Smooth Trend</div>', unsafe_allow_html=True)

    datasets = []
    if pump_state in ("OFF", "Both"):
        datasets.append(("OFF", df_off))
    if pump_state in ("ON", "Both"):
        datasets.append(("ON", df_on))

    cols = st.columns(len(datasets))
    for col, (label, d) in zip(cols, datasets):
        with col:
            fig = go.Figure()

            # Smooth spline via dense x
            from scipy.interpolate import make_interp_spline
            x_new = np.linspace(d["pct"].min(), d["pct"].max(), 300)
            spl_f = make_interp_spline(d["pct"], d["fixed"],    k=min(3, len(d)-1))
            spl_v = make_interp_spline(d["pct"], d["variable"], k=min(3, len(d)-1))
            yf = np.clip(spl_f(x_new), 0, None)
            yv = np.clip(spl_v(x_new), 0, None)

            fig.add_trace(go.Scatter(x=x_new, y=yf, name="Fixed", line=dict(color=BLUE, width=2.5), hovertemplate="Fixed: %{y:.2f} t/h<extra></extra>"))
            fig.add_trace(go.Scatter(x=x_new, y=yv, name="Portable", line=dict(color=AMBER, width=2.5, dash="dot"), hovertemplate="Portable: %{y:.2f} t/h<extra></extra>"))

            # scatter points with labels
            fig.add_trace(go.Scatter(x=d["pct"], y=d["fixed"],    mode="markers+text",
                                     marker=dict(color=BLUE, size=9, line=dict(color="white", width=1)),
                                     text=[f"{v}" for v in d["fixed"]], textposition="top center",
                                     textfont=dict(size=9, color=BLUE), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=d["pct"], y=d["variable"], mode="markers+text",
                                     marker=dict(color=AMBER, size=9, line=dict(color="white", width=1)),
                                     text=[f"{v}" for v in d["variable"]], textposition="bottom center",
                                     textfont=dict(size=9, color=AMBER), showlegend=False, hoverinfo="skip"))

            fig.update_layout(
                **LAYOUT_BASE,
                title=dict(text=f"Pump {label}", font=dict(size=14, color="#e6edf3")),
                xaxis_title="Valve Opening (%)",
                yaxis_title="Flow Rate (t/h)",
                height=420,
                legend=dict(**LEGEND_STYLE, orientation="h", y=1.12, x=0),
            )
            fig.update_xaxes(tickvals=d["pct"], ticktext=[f"{int(v)}%" for v in d["pct"]])
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════
# TAB 2 — Difference Bar Chart
# ══════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Absolute Difference: Portable − Fixed</div>', unsafe_allow_html=True)

    datasets = []
    if pump_state in ("OFF", "Both"):
        datasets.append(("OFF", df_off))
    if pump_state in ("ON", "Both"):
        datasets.append(("ON", df_on))

    cols = st.columns(len(datasets))
    for col, (label, d) in zip(cols, datasets):
        with col:
            colors = [GREEN if x > 0 else RED for x in d["diff"]]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[f"{int(v)}%" for v in d["pct"]],
                y=d["diff"],
                marker_color=colors,
                marker_line_color="rgba(255,255,255,0.15)",
                marker_line_width=1,
                text=[f"{v:+.2f}" for v in d["diff"]],
                textposition="outside",
                textfont=dict(size=10, color="#e6edf3"),
                hovertemplate="Valve: %{x}<br>Diff: %{y:.3f} t/h<extra></extra>",
            ))
            fig.add_hline(y=0, line_color="#8b949e", line_width=1.5)

            tol_val = tolerance_pct / 100 * d["fixed"].replace(0, np.nan)
            fig.add_trace(go.Scatter(
                x=[f"{int(v)}%" for v in d["pct"]],
                y=tol_val,
                mode="lines", name=f"+{tolerance_pct}% tol",
                line=dict(color="#3fb950", width=1, dash="dot"), showlegend=True,
            ))
            fig.add_trace(go.Scatter(
                x=[f"{int(v)}%" for v in d["pct"]],
                y=-tol_val,
                mode="lines", name=f"−{tolerance_pct}% tol",
                line=dict(color="#f85149", width=1, dash="dot"), showlegend=True,
            ))

            fig.update_layout(
                **LAYOUT_BASE,
                title=dict(text=f"Pump {label}", font=dict(size=14, color="#e6edf3")),
                xaxis_title="Valve Opening (%)",
                yaxis_title="Difference (t/h)",
                height=420,
                barmode="group",
                legend=dict(**LEGEND_STYLE, orientation="h", y=1.12, x=0),
            )
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════
# TAB 3 — Parity (Scatter)
# ══════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Parity Plot — Fixed vs Portable Flowmeter</div>', unsafe_allow_html=True)

    datasets = []
    if pump_state in ("OFF", "Both"):
        datasets.append(("OFF", df_off))
    if pump_state in ("ON", "Both"):
        datasets.append(("ON", df_on))

    cols = st.columns(len(datasets))
    for col, (label, d) in zip(cols, datasets):
        with col:
            max_val = max(d["fixed"].max(), d["variable"].max()) * 1.1
            fig = go.Figure()
            # Y=X line
            fig.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val],
                                     mode="lines", name="Perfect Match (Y=X)",
                                     line=dict(color="#8b949e", width=1.5, dash="dash")))
            # tolerance band
            fig.add_trace(go.Scatter(
                x=[0, max_val], y=[0, max_val*(1+tolerance_pct/100)],
                mode="lines", name=f"+{tolerance_pct}%",
                line=dict(color=GREEN, width=1, dash="dot")))
            fig.add_trace(go.Scatter(
                x=[0, max_val], y=[0, max_val*(1-tolerance_pct/100)],
                mode="lines", name=f"−{tolerance_pct}%",
                line=dict(color=RED, width=1, dash="dot"),
                fill="tonexty", fillcolor="rgba(63,185,80,0.05)"))

            # points coloured by valve %
            fig.add_trace(go.Scatter(
                x=d["fixed"], y=d["variable"],
                mode="markers+text",
                text=[f"{int(v)}%" for v in d["pct"]],
                textposition="top right",
                textfont=dict(size=9, color="#c9d1d9"),
                marker=dict(
                    size=14,
                    color=d["pct"],
                    colorscale="Blues",
                    showscale=True,
                    colorbar=dict(title="Valve %", thickness=12, len=0.7),
                    line=dict(color="white", width=1),
                ),
                hovertemplate="Fixed: %{x:.2f} t/h<br>Portable: %{y:.2f} t/h<br>Valve: %{text}<extra></extra>",
                name="Measurements",
            ))
            fig.update_layout(
                **LAYOUT_BASE,
                title=dict(text=f"Pump {label}", font=dict(size=14, color="#e6edf3")),
                height=460,
                showlegend=True,
                legend=LEGEND_STYLE,
            )
            fig.update_xaxes(title_text="Fixed Flowmeter (t/h)", range=[0, max_val])
            fig.update_yaxes(title_text="Portable Flowmeter (t/h)", range=[0, max_val])
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════
# TAB 4 — Heatmap
# ══════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Critical Points Heatmap — Sensor Reading Differences</div>', unsafe_allow_html=True)

    df_all = pd.concat([df_off, df_on], ignore_index=True)
    pivot  = df_all.pivot_table(index="state", columns="pct", values="diff", aggfunc="mean")

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"{int(c)}%" for c in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=[
            [0,   "#1e3a5f"],
            [0.4, "#21262d"],
            [0.5, "#21262d"],
            [0.6, "#21262d"],
            [1,   "#5c2a2a"],
        ],
        zmid=0,
        text=[[f"{v:+.2f}" if not np.isnan(v) else "" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(size=13, color="#e6edf3", family="IBM Plex Mono"),
        hovertemplate="State: %{y}<br>Valve: %{x}<br>Diff: %{z:.3f} t/h<extra></extra>",
        colorbar=dict(
            title=dict(text="Difference (t/h)", font=dict(color="#c9d1d9")),
            tickfont=dict(color="#c9d1d9"),
            thickness=14,
        ),
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        height=280,
    )
    fig.update_xaxes(title_text="Valve Opening (%)")
    fig.update_yaxes(title_text="Pump State")
    
    st.plotly_chart(fig, use_container_width=True)

    # mini legend
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<span class="badge-err">■ Red → Portable reads higher</span>', unsafe_allow_html=True)
    with c2:
        st.markdown('<span class="badge-ok" style="background:#1e3a5f;color:#58a6ff;border-color:#1e3a5f;">■ Blue → Fixed reads higher</span>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# TAB 5 — Bias / Error Dashboard
# ══════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">Bias Plot & Out-of-Tolerance Analysis</div>', unsafe_allow_html=True)

    datasets = []
    if pump_state in ("OFF", "Both"):
        datasets.append(("OFF", df_off))
    if pump_state in ("ON", "Both"):
        datasets.append(("ON", df_on))

    for label, d in datasets:
        st.markdown(f"##### Pump **{label}**")
        mean_vals = (d["fixed"] + d["variable"]) / 2
        diff_vals = d["variable"] - d["fixed"]
        mean_diff = diff_vals.mean()

        fig = go.Figure()
        fig.add_hline(y=0,         line_color="#8b949e", line_width=1)
        fig.add_hline(y=mean_diff, line_color=RED,       line_width=2,
                      annotation_text=f"Bias = {mean_diff:+.3f} t/h",
                      annotation_font_color=RED)

        # color OOT points
        oot_mask = np.abs(diff_vals) > (tolerance_pct / 100 * d["fixed"].replace(0, np.nan).fillna(0))
        colors_pts = [RED if o else BLUE for o in oot_mask]

        fig.add_trace(go.Scatter(
            x=mean_vals, y=diff_vals,
            mode="markers+text",
            text=[f"{int(v)}%" for v in d["pct"]],
            textposition="top right",
            textfont=dict(size=9, color="#c9d1d9"),
            marker=dict(size=13, color=colors_pts, line=dict(color="white", width=1)),
            hovertemplate="Mean: %{x:.2f} t/h<br>Diff: %{y:.3f} t/h<extra></extra>",
            name="Measurements",
        ))
        fig.update_layout(
            **LAYOUT_BASE,
            height=380,
            legend=LEGEND_STYLE,
        )
        fig.update_xaxes(title_text="Mean of Two Flowmeters (t/h)")
        fig.update_yaxes(title_text="Difference  Portable − Fixed  (t/h)")
        st.plotly_chart(fig, use_container_width=True)

        # OOT Table
        d_oot = d[oot_mask.values].copy()
        if len(d_oot):
            d_oot["Abs Error (t/h)"] = np.abs(d_oot["diff"])
            d_oot["Error %"]         = np.abs(d_oot["diff"] / d_oot["fixed"].replace(0, np.nan)) * 100
            d_oot_display = d_oot[["pct","fixed","variable","diff","Abs Error (t/h)","Error %"]].copy()
            d_oot_display.columns = ["Valve %","Fixed (t/h)","Portable (t/h)","Diff (t/h)","Abs Error (t/h)","Error %"]
            d_oot_display["Valve %"] = d_oot_display["Valve %"].apply(lambda x: f"{int(x)}%")
            st.error(f"⚠️  {len(d_oot)} Out-of-Tolerance point(s) at ±{tolerance_pct}% threshold  |  Pump {label}")
            st.dataframe(d_oot_display.style
                         .format({"Fixed (t/h)":"{:.2f}","Portable (t/h)":"{:.2f}",
                                  "Diff (t/h)":"{:+.2f}","Abs Error (t/h)":"{:.2f}","Error %":"{:.1f}%"})
                         .background_gradient(subset=["Abs Error (t/h)", "Error %"], cmap="Reds"),
                         use_container_width=True, hide_index=True)
        else:
            st.success(f"✅  All points within ±{tolerance_pct}% tolerance  |  Pump {label}")

        st.markdown("---")

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center;margin-top:40px;padding:20px;border-top:1px solid #30363d;">
      <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#484f58;">
        Flowmeter Validation Dashboard · UNIT 2 · RU32D010 ·
        Built with Streamlit + Plotly
      </span>
    </div>
    """,
    unsafe_allow_html=True
)
