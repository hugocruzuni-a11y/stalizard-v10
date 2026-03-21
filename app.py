import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Institutional Configuration
st.set_page_config(
    page_title="STARLINE V118 - HIGH CONTRAST", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. High-Contrast Glassmorphism CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%);
        color: #FFFFFF; font-family: 'Plus Jakarta Sans', sans-serif; 
    }
    
    /* SIDEBAR GLASS */
    [data-testid="stSidebar"] { 
        background-color: rgba(255, 255, 255, 0.01) !important; 
        backdrop-filter: blur(40px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* INPUTS: PRETO NO BRANCO (MÁXIMA LEITURA) */
    [data-testid="stSidebar"] .stNumberInput input, 
    [data-testid="stSidebar"] .stTextInput input {
        background-color: rgba(255, 255, 255, 0.95) !important; /* Fundo quase sólido */
        border: 1px solid #00FF88 !important;
        color: #000000 !important; /* DADOS A PRETO SOLICITADO */
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 800 !important;
        border-radius: 4px !important;
    }

    /* Advisor Seal (Minimalista) */
    .advisor-seal {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(255, 255, 255, 0.02) 100%);
        border-radius: 12px; padding: 20px 30px; border: 1px solid rgba(0, 255, 136, 0.4);
        margin-bottom: 20px;
    }
    .advisor-title { color: white; font-size: 1.8rem; font-weight: 900; margin: 0; }
    .advisor-subtitle { color: #00FF88; font-size: 1rem; font-weight: 800; margin: 0; }

    /* AI Assistance Card */
    .intel-card {
        background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 900; 
        height: 4.5em; width: 100%; border-radius: 8px; border: none; text-transform: uppercase;
        letter-spacing: 2px; box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
    }
    
    label { font-size: 0.72rem !important; font-weight: 700 !important; color: #94A3B8 !important; text-transform: uppercase; letter-spacing: 1.2px; }
    hr { border-top: 1px solid rgba(255, 255, 255, 0.05) !important; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; font-size:24px; font-weight:800;'>🏛️ ORACLE V118</h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='color:white; font-weight:800; margin-top:10px;'>01 // ASSETS</p>", unsafe_allow_html=True)
    h_n = st.text_input("HOME TEAM", "VILLARREAL").upper()
    a_n = st.text_input("AWAY TEAM", "REAL SOCIEDAD").upper()
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:white; font-weight:800;'>02 // STATS</p>", unsafe_allow_html=True)
    c_h, c_a = st.columns(2)
    hgf = c_h.number_input("H-GF", 9.0); hga = c_h.number_input("H-GA", 7.0)
    agf = c_a.number_input("A-GF", 12.0); aga = c_a.number_input("A-GA", 10.0)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:white; font-weight:800;'>03 // MARKET</p>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    m1 = c1.number_input("1", 1.90); mx = cx.number_input("X", 4.00); m2 = c2.number_input("2", 3.35)
    
    st.caption("GOALS LADDER")
    co1, co2 = st.columns(2)
    o05 = co1.number_input("OVER 0.5", 1.05); o15 = co2.number_input("OVER 1.5", 1.16)
    o25 = co1.number_input("OVER 2.5", 1.33); o35 = co2.number_input("OVER 3.5", 1.78)
    
    st.caption("SPECIALS")
    m_ob = st.number_input("BTTS (YES)", 1.32)
    ah_h = st.number_input("AH 0.0 (H)", 1.33); ah_a = st.number_input("AH 0.0 (A)", 1.85)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTE ALPHA SCAN")
    st.button("🗑️ RESET SYSTEM", on_click=reset)

# --- RESULTS ---
if not run:
    st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.1;'><h1>ORACLE V118</h1><p>AWAITING DATA COMMAND</p></div>", unsafe_allow_html=True)
else:
    # ENGINE
    lh = max(0.01, (hgf/5 * aga/5)**0.5); la = max(0.01, (agf/5 * hga/5)**0.5)
    sim_h = np.random.poisson(lh, 1000000); sim_a = np.random.poisson(la, 1000000); stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    norm = ph+px+pa; ph, px, pa = ph/norm, px/norm, pa/norm

    st.markdown(f"<h1 style='letter-spacing:-4px; font-size:55px; margin:0;'>{h_n} vs {a_n}</h1>", unsafe_allow_html=True)
    
    col_res, col_ai = st.columns([1.2, 0.8])
    
    mkts = [
        ("WIN: "+h_n, ph, m1), ("WIN: "+a_n, pa, m2), ("DRAW (X)", px, mx),
        ("OVER 0.5 GOALS", np.mean(stot>0.5), o05), ("OVER 1.5 GOALS", np.mean(stot>1.5), o15),
        ("OVER 2.5 GOALS", np.mean(stot>2.5), o25), ("OVER 3.5 GOALS", np.mean(stot>3.5), o35),
        ("BOTH TEAMS TO SCORE (YES)", np.mean((sim_h>0)&(sim_a>0)), m_ob),
        ("ASIAN HANDICAP 0.0: "+h_n, ph/(ph+pa), ah_h), ("ASIAN HANDICAP 0.0: "+a_n, pa/(ph+pa), ah_a)
    ]
    best = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts], key=lambda x: x[3], reverse=True)[0]

    with col_res:
        st.markdown(f"""
            <div class="advisor-seal">
                <h1 class="advisor-title">{best[0]}</h1>
                <p class="advisor-subtitle">EDGE: {best[3]:+.1%} | PROB: {best[1]:.1%}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_ai:
        st.markdown(f"""
            <div class="intel-card">
                <b style="color:#00FF88;">🧠 AI ASSISTANCE:</b><br>
                <span style="color:#CBD5E1; font-size:0.9rem;">
                Scan complete. Detected <b>{best[3]:.1%} alpha</b>. Discrepancy between simulated goal flow and market pricing confirms high-value entry.
                </span>
            </div>
        """, unsafe_allow_html=True)

    # MATRIX
    df = pd.DataFrame(mkts, columns=["Market", "Prob", "Odd"])
    df["Fair"] = 1/df["Prob"]; df["Edge"] = (df["Prob"] * df["Odd"]) - 1
    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>MARKET</b>', '<b>CONFIDENCE</b>', '<b>FAIR</b>', '<b>BOOKIE</b>', '<b>EDGE</b>'],
                    fill_color='#0A0A0A', align='center', font=dict(color='#64748B', size=11), height=45),
        cells=dict(values=[df.Market, df.Prob.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), 
                           df.Odd.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                   fill_color=[['rgba(0, 255, 136, 0.15)' if e > 0.1 else 'rgba(255,255,255,0.02)' for e in df.Edge]],
                   align='center', font=dict(color='white', size=14), height=35)
    )])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', height=(len(mkts)*35+60))
    st.plotly_chart(fig, use_container_width=True)

    # ANALYTICS
    c1, c2 = st.columns([1.3, 0.7])
    with c1:
        xr = list(range(7))
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig_p.update_layout(title="POISSON DENSITY", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
        st.plotly_chart(fig_p, use_container_width=True)
