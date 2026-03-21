import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Configuration
st.set_page_config(page_title="STARLINE V135 - MATH SOVEREIGN", layout="wide", initial_sidebar_state="expanded")

# 2. Sovereign Elite CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;600;700&display=swap');
    .stApp { background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%); color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.01) !important; backdrop-filter: blur(45px) !important; border-right: 1px solid rgba(255, 255, 255, 0.05) !important; }
    [data-testid="stSidebar"] .stNumberInput input, [data-testid="stSidebar"] .stTextInput input {
        background-color: rgba(255, 255, 255, 0.96) !important; color: #000000 !important; font-weight: 300 !important; border-radius: 4px !important;
    }
    .advisor-seal { background: linear-gradient(135deg, rgba(0, 255, 136, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%); border-radius: 12px; padding: 15px 25px; border: 1px solid rgba(0, 255, 136, 0.4); margin-bottom: 20px; }
    .risk-card { background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 15px 25px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px; }
    .intel-card { background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.05); font-weight: 300; font-size: 0.9rem; margin-bottom: 10px; }
    div.stButton > button { background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; font-weight: 700; height: 4em; width: 100%; text-transform: uppercase; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88;'>🏛️ ORACLE V135</h2>", unsafe_allow_html=True)
    comp_type = st.selectbox("MATCH TYPE", ["LEAGUE / REGULAR", "CHAMPIONS / ELIMINATION"])
    h_score_1st, a_score_1st = 0, 0
    leg_type = "1st Leg"
    if comp_type == "CHAMPIONS / ELIMINATION":
        leg_type = st.radio("LEG SELECTION", ["1st Leg", "2nd Leg"])
        if leg_type == "2nd Leg":
            c1, c2 = st.columns(2)
            h_score_1st = c1.number_input("H-1st Leg", value=0, step=1)
            a_score_1st = c2.number_input("A-1st Leg", value=0, step=1)

    h_n = st.text_input("HOME", "VILLARREAL").upper()
    a_n = st.text_input("AWAY", "REAL SOCIEDAD").upper()
    c_gf, c_ga = st.columns(2)
    hgf = c_gf.number_input("H-GF", value=9, step=1); hga = c_gf.number_input("H-GA", value=7, step=1)
    agf = c_ga.number_input("A-GF", value=12, step=1); aga = c_ga.number_input("A-GA", value=10, step=1)
    
    st.markdown("---")
    c1, cx, c2 = st.columns(3)
    m1 = c1.number_input("1", value=1.90); mx = cx.number_input("X", value=4.00); m2 = c2.number_input("2", value=3.35)
    
    o05_i = st.number_input("O0.5", 1.05); o15_i = st.number_input("O1.5", 1.16)
    o25_i = st.number_input("O2.5", 1.33); o35_i = st.number_input("O3.5", 1.78)
    u05_i = st.number_input("U0.5", 9.50); u15_i = st.number_input("U1.5", 4.50)
    u25_i = st.number_input("U2.5", 2.65); u35_i = st.number_input("U3.5", 1.60)
    m_ob = st.number_input("BTTS (YES)", 1.32)
    ah_h = st.number_input("AH 0.0 (H)", 1.33); ah_a = st.number_input("AH 0.0 (A)", 1.85)
    
    run = st.button("🚀 EXECUTE QUANTUM SCAN")
    st.button("🗑️ RESET", on_click=reset)

# --- ENGINE ---
if run:
    # 1. Base Lambdas
    lh = max(0.01, (hgf/5 * aga/5)**0.5); la = max(0.01, (agf/5 * hga/5)**0.5)
    
    # 2. Tournament Adjustment
    if comp_type == "CHAMPIONS / ELIMINATION" and leg_type == "2nd Leg":
        diff = h_score_1st - a_score_1st
        if diff < 0: lh *= (1 + abs(diff) * 0.12)
        elif diff > 0: la *= (1 + abs(diff) * 0.12)

    # 3. Dixon-Coles Bivariate Matrix (0-5 goals)
    max_g = 6
    mtx = np.zeros((max_g, max_g))
    rho = -0.10 # Correlação padrão institucional
    
    for i in range(max_g):
        for j in range(max_g):
            prob = poisson.pmf(i, lh) * poisson.pmf(j, la)
            # Dixon-Coles Correction Tau
            if i == 0 and j == 0: prob *= (1 - lh*la*rho)
            elif i == 0 and j == 1: prob *= (1 + lh*rho)
            elif i == 1 and j == 0: prob *= (1 + la*rho)
            elif i == 1 and j == 1: prob *= (1 - rho)
            mtx[i, j] = prob
    
    mtx /= mtx.sum() # Normalização rigorosa

    # 4. Market Probability Extraction
    ph = np.sum(np.triu(mtx, 1).T); px = np.sum(np.diag(mtx)); pa = np.sum(np.tril(mtx, -1).T)
    p_over25 = np.sum([mtx[i,j] for i in range(max_g) for j in range(max_g) if i+j > 2.5])
    p_btts = np.sum([mtx[i,j] for i in range(1, max_g) for j in range(1, max_g)])
    p_dnb_h = ph / (ph + pa) if (ph + pa) > 0 else 0.5

    # 5. UI & Results
    st.markdown(f"<h1 style='letter-spacing:-3px; font-size:55px; margin:0;'>{h_n} <span style='color:#00FF88;'>vs</span> {a_n}</h1>", unsafe_allow_html=True)
    
    mkts = [
        ("WIN: "+h_n, ph, m1), ("WIN: "+a_n, pa, m2), ("DRAW (X)", px, mx),
        ("O2.5 GOALS", p_over25, o25_i), ("BTTS (YES)", p_btts, m_ob),
        ("AH 0.0: "+h_n, p_dnb_h, ah_h)
    ]
    best = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts], key=lambda x: x[3], reverse=True)[0]
    kelly = max(0, (best[3] / (best[2] - 1)) * 0.5)

    c_res, c_risk = st.columns([1.1, 0.9])
    with c_res: st.markdown(f"""<div class="advisor-seal"><h1 class="advisor-title">{best[0]}</h1><p class="advisor-subtitle">ALPHA EDGE: {best[3]:+.1%} | PROB: {best[1]:.1%}</p></div>""", unsafe_allow_html=True)
    with c_risk: st.markdown(f"""<div class="risk-card"><b style="color:#FF8C00;">🛡️ QUANTUM ALLOCATION</b><h2 style="margin:5px 0; font-size:2rem;">{kelly:.1%}</h2><p style="color:#64748B; font-size:0.75rem;">STAKE SUGGESTED (HALF-KELLY)</p></div>""", unsafe_allow_html=True)

    # 6. AI Insights
    c_i1, c_i2 = st.columns(2)
    with c_i1: st.markdown(f"""<div class="intel-card"><b style="color:#00FF88;">🧠 AI TACTICAL ANALYSIS</b><br>Trend: <b>{"OPEN" if (lh+la)>2.6 else "TIGHT"}</b> | Correlation: Dixon-Coles Adjusted</div>""", unsafe_allow_html=True)
    with c_i2:
        idx = np.unravel_index(np.argsort(mtx.ravel())[-2:], mtx.shape)
        st.markdown(f"""<div class="intel-card"><b style="color:#00FF88;">🎯 TOP SCORES</b><br>1º: {idx[0][1]}-{idx[1][1]} ({mtx[idx[0][1], idx[1][1]]:.1%}) | 2º: {idx[0][0]}-{idx[1][0]} ({mtx[idx[0][0], idx[1][0]]:.1%})</div>""", unsafe_allow_html=True)

    # 7. Matrix
    df = pd.DataFrame(mkts, columns=["Market", "Prob", "Odd"])
    df["Fair"] = 1/df["Prob"]; df["Edge"] = (df["Prob"] * df["Odd"]) - 1
    colors = [['rgba(0, 255, 136, 0.15)' if e > 0.1 else 'rgba(255, 140, 0, 0.35)' if e > 0.05 else 'rgba(255,255,255,0.01)' for e in df["Edge"]]]
    
    fig = go.Table(header=dict(values=['MARKET','PROB','FAIR','BOOKIE','EDGE'], fill_color='#0A0A0A'),
                   cells=dict(values=[df.Market, df.Prob.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), df.Odd.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)], fill_color=colors))
    st.plotly_chart(go.Figure(data=[fig]), use_container_width=True)

    # 8. Density Graph
    xr = np.arange(0, 7)
    fig_g = go.Figure()
    fig_g.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88'))
    fig_g.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6'))
    st.plotly_chart(fig_g, use_container_width=True)
    st.markdown("""<div class="intel-card"><b style="color:#00FF88;">🌐 MATH INSIGHT:</b> As curvas mostram a densidade de probabilidade. Onde se cruzam, define-se o equilíbrio Dixon-Coles.</div>""", unsafe_allow_html=True)
