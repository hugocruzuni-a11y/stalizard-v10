import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Advanced Institutional Configuration
st.set_page_config(
    page_title="STARLINE V120 - ELITE TYPO", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Sovereign Elite CSS (The Luxury Typo Edition)
st.markdown("""
    <style>
    /* Importando a Inter - A fonte mais premium para dashboards */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;700&family=JetBrains+Mono:wght@300;400&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%);
        color: #FFFFFF; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* SIDEBAR: PURE GLASS */
    [data-testid="stSidebar"] { 
        background-color: rgba(255, 255, 255, 0.01) !important; 
        backdrop-filter: blur(45px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* INPUTS: TEXTO FINO E ELEGANTE (SEM NEGRITO) */
    [data-testid="stSidebar"] .stNumberInput input, 
    [data-testid="stSidebar"] .stTextInput input {
        background-color: rgba(255, 255, 255, 0.96) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #000000 !important; 
        font-family: 'Inter', sans-serif !important;
        font-weight: 300 !important; /* TEXTO ULTRA FINO */
        font-size: 0.9rem !important;
        border-radius: 4px !important;
        letter-spacing: 0.5px;
    }

    /* Advisor Seal Minimalista */
    .advisor-seal {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
        border-radius: 12px; padding: 20px 30px; border: 1px solid rgba(0, 255, 136, 0.3);
        margin-bottom: 25px; display: inline-block;
    }
    .advisor-title { color: white; font-size: 1.8rem; font-weight: 700; margin: 0; letter-spacing: -1px; }
    .advisor-subtitle { color: #00FF88; font-size: 0.9rem; font-weight: 400; margin: 0; letter-spacing: 1px; }

    /* AI Assistance Card */
    .intel-card {
        background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05); font-weight: 300;
    }

    /* Labels (Títulos dos Campos - Finos) */
    label { 
        font-size: 0.65rem !important; 
        font-weight: 400 !important; 
        color: #64748B !important; 
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        margin-bottom: 5px !important;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 700; 
        height: 4.2em; width: 100%; border-radius: 6px; border: none; text-transform: uppercase;
        letter-spacing: 2px; box-shadow: 0 10px 25px rgba(0, 255, 136, 0.15);
    }
    
    hr { border-top: 1px solid rgba(255, 255, 255, 0.03) !important; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; font-size:22px; font-weight:700; letter-spacing:-1px;'>🏛️ ORACLE V120</h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='color:#475569; font-size:0.7rem; font-weight:700;'>SECTION 01 // ASSETS</p>", unsafe_allow_html=True)
    h_n = st.text_input("HOME TEAM", "VILLARREAL").upper()
    a_n = st.text_input("AWAY TEAM", "REAL SOCIEDAD").upper()
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:0.7rem; font-weight:700;'>SECTION 02 // PERFORMANCE</p>", unsafe_allow_html=True)
    c_h, c_a = st.columns(2)
    hgf = c_h.number_input("H-GF", 9.0); hga = c_h.number_input("H-GA", 7.0)
    agf = c_a.number_input("A-GF", 12.0); aga = c_a.number_input("A-GA", 10.0)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:0.7rem; font-weight:700;'>SECTION 03 // QUOTES</p>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    m1 = c1.number_input("1", 1.90); mx = cx.number_input("X", 4.00); m2 = c2.number_input("2", 3.35)
    
    o25 = st.number_input("O2.5", 1.33)
    m_ob = st.number_input("BTTS", 1.32)
    ah_h = st.number_input("AH 0.0 (H)", 1.33)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTE SCAN")
    st.button("🗑️ RESET", on_click=reset)

# --- RESULTS ---
if not run:
    st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.1;'><h1>ORACLE V120</h1><p>THE ELITE TYPOGRAPHY</p></div>", unsafe_allow_html=True)
else:
    # ENGINE
    lh = max(0.01, (hgf/5 * aga/5)**0.5); la = max(0.01, (agf/5 * hga/5)**0.5)
    sim_h = np.random.poisson(lh, 1000000); sim_a = np.random.poisson(la, 1000000); stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    norm = ph+px+pa; ph, px, pa = ph/norm, px/norm, pa/norm

    # TITULO COM "VS" A VERDE
    st.markdown(f"<h1 style='letter-spacing:-3px; font-size:50px; margin:0; font-weight:700;'>{h_n} <span style='color:#00FF88; font-weight:300;'>vs</span> {a_n}</h1>", unsafe_allow_html=True)
    
    col_res, col_ai = st.columns([1.1, 0.9])
    
    # MERCADOS ABREVIADOS NA TABELA
    mkts = [
        ("1X2: "+h_n, ph, m1), ("1X2: "+a_n, pa, m2), ("1X2: DRAW", px, mx),
        ("O0.5 GOALS", np.mean(stot>0.5), 1.05), ("O1.5 GOALS", np.mean(stot>1.5), 1.16),
        ("O2.5 GOALS", np.mean(stot>2.5), o25), ("O3.5 GOALS", np.mean(stot>3.5), 1.78),
        ("BTTS (YES)", np.mean((sim_h>0)&(sim_a>0)), m_ob),
        ("AH 0.0: "+h_n, ph/(ph+pa), ah_h)
    ]
    best = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts], key=lambda x: x[3], reverse=True)[0]

    with col_res:
        st.markdown(f"""
            <div class="advisor-seal">
                <h1 class="advisor-title">{best[0]}</h1>
                <p class="advisor-subtitle">ALPHA EDGE: {best[3]:+.1%} | PROB: {best[1]:.1%}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_ai:
        st.markdown(f"""
            <div class="intel-card">
                <b style="color:#00FF88;">🧠 AI INSIGHT:</b><br>
                <span style="color:#CBD5E1; font-size:0.85rem; line-height:1.5;">
                Probability flow confirms a <b>{best[3]:.1%} gap</b>. Mathematical divergence detected between Poisson density and market pricing.
                </span>
            </div>
        """, unsafe_allow_html=True)

    # MATRIX - SEM SCROLL, CENTRADA E ABREVIADA
    df = pd.DataFrame(mkts, columns=["Market", "Prob", "Odd"])
    df["Fair"] = 1/df["Prob"]; df["Edge"] = (df["Prob"] * df["Odd"]) - 1
    
    dynamic_height = (len(mkts) * 42) + 60

    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>MARKET</b>', '<b>CONF. (%)</b>', '<b>FAIR</b>', '<b>BOOKIE</b>', '<b>EDGE</b>'],
                    fill_color='#0A0A0A', align='center', font=dict(color='#475569', size=11, family='Inter'), height=45),
        cells=dict(values=[df.Market, df.Prob.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), 
                           df.Odd.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                   fill_color=[['rgba(0, 255, 136, 0.12)' if e > 0.08 else 'rgba(255,255,255,0.01)' for e in df.Edge]],
                   align='center', 
                   font=dict(color='white', size=13, family='Inter'), height=40)
    )])
    
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', height=dynamic_height)
    st.plotly_chart(fig, use_container_width=True)
