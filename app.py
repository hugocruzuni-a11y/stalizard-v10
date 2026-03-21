import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Advanced Institutional Configuration
st.set_page_config(
    page_title="STARLINE V121 - SOVEREIGN OMNI", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Sovereign Elite CSS (Luxury Glass & Inter Typo)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;600;700&family=JetBrains+Mono:wght@300;400&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%);
        color: #FFFFFF; font-family: 'Inter', sans-serif; 
    }
    
    /* SIDEBAR: PURE GLASS */
    [data-testid="stSidebar"] { 
        background-color: rgba(255, 255, 255, 0.01) !important; 
        backdrop-filter: blur(45px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* INPUTS: PURE ELEGANCE (NO BOLD) */
    [data-testid="stSidebar"] .stNumberInput input, 
    [data-testid="stSidebar"] .stTextInput input {
        background-color: rgba(255, 255, 255, 0.96) !important;
        border: 1px solid rgba(0, 255, 136, 0.2) !important;
        color: #000000 !important; 
        font-family: 'Inter', sans-serif !important;
        font-weight: 400 !important; 
        font-size: 0.85rem !important;
        border-radius: 4px !important;
    }

    /* Advisor Seal */
    .advisor-seal {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
        border-radius: 12px; padding: 15px 25px; border: 1px solid rgba(0, 255, 136, 0.3);
        margin-bottom: 20px; display: inline-block;
    }
    .advisor-title { color: white; font-size: 1.6rem; font-weight: 700; margin: 0; letter-spacing: -1px; }
    .advisor-subtitle { color: #00FF88; font-size: 0.85rem; font-weight: 400; margin: 0; letter-spacing: 1px; }

    /* AI Assistance Card */
    .intel-card {
        background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05); font-weight: 300; font-size: 0.9rem;
    }

    label { font-size: 0.62rem !important; font-weight: 600 !important; color: #64748B !important; text-transform: uppercase; letter-spacing: 1.2px; }

    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 700; 
        height: 4em; width: 100%; border-radius: 6px; border: none; text-transform: uppercase;
        letter-spacing: 2px; box-shadow: 0 10px 25px rgba(0, 255, 136, 0.1);
    }
    
    hr { border-top: 1px solid rgba(255, 255, 255, 0.03) !important; margin: 15px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; font-size:22px; font-weight:700;'>🏛️ ORACLE V121</h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='color:#475569; font-size:0.65rem; font-weight:700;'>01 // IDENTIFICATION</p>", unsafe_allow_html=True)
    h_n = st.text_input("HOME", "VILLARREAL").upper()
    a_n = st.text_input("AWAY", "REAL SOCIEDAD").upper()
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:0.65rem; font-weight:700;'>02 // PERFORMANCE (LAST 5)</p>", unsafe_allow_html=True)
    c_h, c_a = st.columns(2)
    hgf = c_h.number_input("H-GF", 9.0); hga = c_h.number_input("H-GA", 7.0)
    agf = c_a.number_input("A-GF", 12.0); aga = c_a.number_input("A-GA", 10.0)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:0.65rem; font-weight:700;'>03 // LIVE QUOTES</p>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    m1 = c1.number_input("1", 1.90); mx = cx.number_input("X", 4.00); m2 = c2.number_input("2", 3.35)
    
    st.write("OVER LADDER")
    co1, co2 = st.columns(2)
    o05 = co1.number_input("O0.5", 1.05); o15 = co2.number_input("O1.5", 1.16)
    o25 = co1.number_input("O2.5", 1.33); o35 = co2.number_input("O3.5", 1.78)
    
    st.write("UNDER LADDER")
    cu1, cu2 = st.columns(2)
    u15 = cu1.number_input("U1.5", 4.50); u25 = cu2.number_input("U2.5", 2.65)
    
    st.write("SPECIALS")
    m_ob = st.number_input("BTTS (YES)", 1.32)
    ah_h = st.number_input("AH 0.0 (H)", 1.33); ah_a = st.number_input("AH 0.0 (A)", 1.85)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTE ALPHA SCAN")
    st.button("🗑️ RESET ENGINE", on_click=reset)

# --- RESULTS INTERFACE ---
if not run:
    st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.1;'><h1>ORACLE V121</h1><p>SOVEREIGN OMNIPOTENCE BUILD</p></div>", unsafe_allow_html=True)
else:
    # ENGINE: INSTITUTIONAL MATH
    lh = max(0.01, (hgf/5 * aga/5)**0.5); la = max(0.01, (agf/5 * hga/5)**0.5)
    sim_h = np.random.poisson(lh, 1000000); sim_a = np.random.poisson(la, 1000000); stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    norm = ph+px+pa; ph, px, pa = ph/norm, px/norm, pa/norm

    st.markdown(f"<h1 style='letter-spacing:-3px; font-size:55px; margin:0; font-weight:700;'>{h_n} <span style='color:#00FF88; font-weight:300;'>vs</span> {a_n}</h1>", unsafe_allow_html=True)
    
    col_res, col_ai = st.columns([1.1, 0.9])
    
    # MERCADOS COMPLETOS E ABREVIADOS
    mkts = [
        ("WIN: "+h_n, ph, m1), ("WIN: "+a_n, pa, m2), ("DRAW (X)", px, mx),
        ("O0.5 GOALS", np.mean(stot>0.5), o05), ("O1.5 GOALS", np.mean(stot>1.5), o15),
        ("O2.5 GOALS", np.mean(stot>2.5), o25), ("O3.5 GOALS", np.mean(stot>3.5), o35),
        ("U1.5 GOALS", np.mean(stot<1.5), u15), ("U2.5 GOALS", np.mean(stot<2.5), u25),
        ("BTTS (YES)", np.mean((sim_h>0)&(sim_a>0)), m_ob),
        ("AH 0.0: "+h_n, ph/(ph+pa), ah_h), ("AH 0.0: "+a_n, pa/(ph+pa), ah_a)
    ]
    best = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts], key=lambda x: x[3], reverse=True)[0]

    with col_res:
        st.markdown(f"""
            <div class="advisor-seal">
                <h1 class="advisor-title">{best[0]}</h1>
                <p class="advisor-subtitle">ALPHA EDGE: {best[3]:+.1%} | CONFIDENCE: {best[1]:.1%}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_ai:
        st.markdown(f"""
            <div class="intel-card">
                <b style="color:#00FF88;">🧠 AI ASSISTANCE:</b><br>
                <span style="color:#CBD5E1; line-height:1.5;">
                Probability flow identifies a <b>{best[3]:.1%} gap</b>. Mathematical divergence confirmed between Poisson density and market quotes. High precision entry suggested.
                </span>
            </div>
        """, unsafe_allow_html=True)

    # MATRIX INFINITA (FULL SPECTRUM)
    df = pd.DataFrame(mkts, columns=["Market", "Prob", "Odd"])
    df["Fair"] = 1/df["Prob"]; df["Edge"] = (df["Prob"] * df["Odd"]) - 1
    
    dynamic_height = (len(mkts) * 42) + 60

    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>MARKET</b>', '<b>CONF. (%)</b>', '<b>FAIR</b>', '<b>BOOKIE</b>', '<b>EDGE</b>'],
                    fill_color='#0A0A0A', align='center', font=dict(color='#475569', size=11, family='Inter'), height=45),
        cells=dict(values=[df.Market, df.Prob.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), 
                           df.Odd.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                   fill_color=[['rgba(0, 255, 136, 0.12)' if e > 0.1 else 'rgba(255,255,255,0.01)' for e in df.Edge]],
                   align='center', font=dict(color='white', size=13, family='Inter'), height=40)
    )])
    
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', height=dynamic_height)
    st.plotly_chart(fig, use_container_width=True)

    # ANALYTICS
    c1, c2 = st.columns([1.3, 0.7])
    with c1:
        xr = list(range(7))
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig_p.update_layout(title="POISSON DISTRIBUTION DENSITY", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
        st.plotly_chart(fig_p, use_container_width=True)
    with c2:
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        st.write("**TOP PROBABLE SCORES**")
        for j in range(2, -1, -1):
            st.metric(f"SCORE {idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
