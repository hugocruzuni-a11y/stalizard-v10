import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. Ultra-High-End Configuration
st.set_page_config(
    page_title="STARLINE V92 - QUANTUM FLOW", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. CSS "Quantum Flow" (The 2026 Stealth Design)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 90%);
        color: #FFFFFF; font-family: 'Plus Jakarta Sans', sans-serif; 
    }
    
    [data-testid="stSidebar"] { 
        background-color: rgba(5, 5, 10, 0.95) !important; 
        backdrop-filter: blur(20px); border-right: 1px solid rgba(255,255,255,0.05); 
    }
    
    .advisor-glow {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 20px; padding: 30px; border: 1px solid rgba(0, 255, 136, 0.2);
        box-shadow: 0 0 50px rgba(0, 255, 136, 0.05); margin-bottom: 30px;
    }

    label { color: #94A3B8 !important; font-weight: 700 !important; text-transform: uppercase; font-size: 0.7rem !important; letter-spacing: 2px; }

    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 900; height: 4.5em; width: 100%; border-radius: 12px; border: none; text-transform: uppercase;
        box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: SYSTEM COMMANDS ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88; font-size:24px;'>🏛️ STARLINE V92</h1>", unsafe_allow_html=True)
    st.caption("QUANTUM FLOW TERMINAL // 2026")
    
    st.markdown("---")
    h_n = st.text_input("HOME TEAM", "VILLARREAL").upper()
    a_n = st.text_input("AWAY TEAM", "REAL SOCIEDAD").upper()
    
    c1, c2 = st.columns(2)
    hgf = c1.number_input("H-GF", 9.0); hga = c2.number_input("H-GA", 7.0)
    agf = c1.number_input("A-GF", 12.0); aga = c2.number_input("A-GA", 10.0)
    
    st.markdown("---")
    m1 = st.number_input("ODD 1", 1.90); mx = st.number_input("ODD X", 4.00); m2 = st.number_input("ODD 2", 3.35)
    o25 = st.number_input("OVER 2.5", 1.33); u25 = st.number_input("UNDER 2.5", 2.65)
    m_ob = st.number_input("BTTS YES", 1.32)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("⚡ EXECUTE QUANTUM SCAN")
    st.button("🗑️ CLEAR SYSTEM", on_click=reset)

# --- MAIN INTERFACE ---
if not run:
    st.markdown("<div style='text-align:center; margin-top:15%; opacity:0.1;'><h1>SYSTEM IDLE</h1><p>WAITING FOR PARAMETERS</p></div>", unsafe_allow_html=True)
else:
    # ENGINE 1M
    lh, la = max(0.01, ((hgf/5)*(aga/5))**0.5), max(0.01, ((agf/5)*(hga/5))**0.5)
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)

    st.markdown(f"<h1 style='letter-spacing:-3px; font-size:50px; margin:0;'>{h_n} <span style='color:#00FF88;'>VS</span> {a_n}</h1>", unsafe_allow_html=True)

    # 1. ADVISOR GLOW (TOP)
    mkts = [
        ("WIN: "+h_n, ph, m1), ("DRAW (X)", px, mx), ("WIN: "+a_n, pa, m2),
        ("OVER 2.5", np.mean(stot>2.5), o25), ("UNDER 2.5", np.mean(stot<2.5), u25),
        ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob)
    ]
    best = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts], key=lambda x: x[3], reverse=True)[0]
    
    st.markdown(f"""
        <div class="advisor-glow">
            <p style="color:#64748B; margin:0; font-size:0.8rem; font-weight:800; letter-spacing:3px;">HIGHEST PROBABILITY SIGNAL DETECTED</p>
            <h1 style="color:white; margin:10px 0; font-size:3rem;">{best[0]}</h1>
            <p style="color:#00FF88; font-size:1.5rem; margin:0; font-weight:800;">ALPHA EDGE: {best[3]:+.1%} | CONFIDENCE: {best[1]:.1%}</p>
        </div>
    """, unsafe_allow_html=True)

    # 2. THE QUANTUM MATRIX (A TABELA DINÂMICA)
    st.markdown("### 💎 INTERACTIVE MARKET MATRIX")
    
    df_data = []
    for n, p, b in mkts + [("DNB: "+h_n, ph/(ph+pa), 1.33)]:
        edge = (p * b) - 1
        df_data.append({"Market": n, "Confidence": p*100, "Fair": 1/p, "Bookie": b, "Edge": edge*100})
    
    df = pd.DataFrame(df_data)

    # Gráfico de Tabela Plotly (Estilo Matrix de Trading)
    fig_table = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>MARKET</b>', '<b>CONFIDENCE (%)</b>', '<b>FAIR ODD</b>', '<b>MARKET ODD</b>', '<b>ALPHA EDGE (%)</b>'],
            fill_color='#0A0A0A',
            align='center', font=dict(color='#94A3B8', size=12), height=40
        ),
        cells=dict(
            values=[df.Market, df.Confidence.map('{:,.1f}%'.format), df.Fair.map('{:,.2f}'.format), 
                    df.Bookie, df.Edge.map('{:+.1f}%'.format)],
            fill_color=[['rgba(255,255,255,0.02)' if e < 0 else 'rgba(0, 255, 136, 0.1)' for e in df.Edge]],
            align='center', font=dict(color='white', size=14), height=45
        )
    )])
    fig_table.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', height=400)
    st.plotly_chart(fig_table, use_container_width=True)

    # 3. ANALYTICS (BOTTOM)
    c_g1, c_g2 = st.columns([1.2, 0.8])
    with c_g1:
        xr = list(range(7))
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig_p.update_layout(title="GOAL DENSITY CURVES", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
        st.plotly_chart(fig_p, use_container_width=True)
    with c_g2:
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        st.write("**TOP 3 PREDICTED SCORES**")
        for j in range(2, -1, -1):
            st.metric(f"SCORE {idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
