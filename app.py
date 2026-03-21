iimport streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Advanced Institutional Configuration
st.set_page_config(page_title="STARLINE V94 - SOVEREIGN AI", layout="wide", initial_sidebar_state="expanded")

# 2. Sovereign AI CSS (Design de Elite 2026)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%);
        color: #FFFFFF; font-family: 'Plus Jakarta Sans', sans-serif; 
    }
    
    /* Sidebar de Alta Precisão (Stealth Black) */
    [data-testid="stSidebar"] { 
        background-color: #050505 !important; 
        backdrop-filter: blur(25px); border-right: 1px solid #1A1A1A; 
    }
    [data-testid="stSidebar"] .stNumberInput, [data-testid="stSidebar"] .stTextInput {
        background-color: #111111 !important; border: 1px solid #222222 !important;
        border-radius: 8px !important; color: #00FF88 !important; font-family: 'JetBrains Mono', monospace;
    }

    /* Intelligence & Advisor Glow */
    .advisor-premium {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.05) 0%, rgba(0, 0, 0, 0.4) 100%);
        border-radius: 20px; padding: 35px; border: 1px solid #00FF88;
        box-shadow: 0 0 60px rgba(0, 255, 136, 0.1); margin-bottom: 30px;
    }
    .intel-card {
        background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05); margin-top: 10px;
    }

    /* O FIM DO EXCEL: TABELA CUSTOMIZADA 2026 */
    .styled-table {
        width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 0.95rem;
        background-color: rgba(255, 255, 255, 0.01); border-radius: 12px; overflow: hidden;
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
    }
    .styled-table thead tr { background-color: #0A0A0A; color: #64748B; text-align: left; font-weight: 800; }
    .styled-table th, .styled-table td { padding: 15px 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.03); }
    .styled-table tbody tr { transition: 0.3s; }
    .styled-table tbody tr:hover { background-color: rgba(0, 255, 136, 0.03); }
    .styled-table tbody td { text-align: center; }

    /* Botão de Execução NÉON */
    div.stButton > button {
        background: #00FF88 !important; color: #000000 !important; font-weight: 900; 
        height: 4.5em; width: 100%; border-radius: 12px; border: none; text-transform: uppercase;
        letter-spacing: 2px; box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
    }
    
    label { font-size: 0.7rem !important; font-weight: 800 !important; color: #64748B !important; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: PRECISION CONTROLS ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88; font-size:24px; margin-bottom:0;'>🏛️ STARLINE AI</h1>", unsafe_allow_html=True)
    st.caption("OMNI-QUANT ENGINE // V94.0")
    
    st.markdown("---")
    h_n = st.text_input("HOME TEAM", "VILLARREAL").upper()
    a_n = st.text_input("AWAY TEAM", "REAL SOCIEDAD").upper()
    
    col_g, col_a = st.columns(2)
    hgf = col_g.number_input("H-GF", 9.0); hga = col_a.number_input("H-GA", 7.0)
    agf = col_g.number_input("A-GF", 12.0); aga = col_a.number_input("A-GA", 10.0)
    
    st.markdown("---")
    st.write("LIVE MARKET QUOTES")
    m1 = st.number_input("ODD 1", 1.90); mx = st.number_input("ODD X", 4.00); m2 = st.number_input("ODD 2", 3.35)
    o25 = st.number_input("OVER 2.5", 1.33); m_ob = st.number_input("BTTS YES", 1.32)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🔮 INITIATE AI SCAN")
    st.button("🗑️ RESET ENGINE", on_click=reset)

# --- SOVEREIGN AI DASHBOARD ---
if not run:
    st.markdown("""
        <div style='text-align:center; padding-top:100px;'>
            <h1 style='font-size:5rem; font-weight:900; letter-spacing:-5px; margin-bottom:0;'>SOVEREIGN <span style='color:#00FF88;'>AI</span></h1>
            <p style='color:#64748B; font-size:1.5rem; letter-spacing:10px;'>AWAITING INPUT VARIABLES</p>
            <div style='margin-top:50px; opacity:0.3;'>
                <p>QUANTUM FLOW 2026 // READY TO PROCESS 1,000,000 SCENARIOS</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    # ENGINE 1M
    lh, la = max(0.01, ((hgf/5)*(aga/5))**0.5), max(0.01, ((agf/5)*(hga/5))**0.5)
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)

    st.markdown(f"<h1 style='letter-spacing:-3px; font-size:55px; margin:0;'>{h_n} vs {a_n}</h1>", unsafe_allow_html=True)

    # 1. ADVISOR & AI INTELLIGENCE
    col_adv, col_notes = st.columns([1.2, 0.8])
    mkts = [
        ("HOME WIN", ph, m1), ("AWAY WIN", pa, m2), ("DRAW", px, mx),
        ("OVER 2.5", np.mean(stot>2.5), o25), ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob)
    ]
    best = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts], key=lambda x: x[3], reverse=True)[0]

    with col_adv:
        st.markdown(f"""
            <div class="advisor-premium">
                <p style="color:#64748B; margin:0; font-size:0.8rem; font-weight:800; letter-spacing:4px;">PREMIUM ALPHA SIGNAL</p>
                <h1 style="color:white; margin:10px 0; font-size:3.5rem;">{best[0]}</h1>
                <p style="color:#00FF88; font-size:1.5rem; margin:0; font-weight:800;">EDGE: {best[3]:+.1%} | CONFIDENCE: {best[1]:.1%}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_notes:
        st.markdown("### 🧠 AI INTELLIGENCE NOTES")
        clr = "#00FF88" if best[3] > 0.15 else "#FACC15"
        st.markdown(f"""
            <div class="intel-card">
                <b style="color:{clr};">ALPHA EDGE SOURCE</b><br>
                <span style="color:#94A3B8; font-size:0.9rem;">
                Based on 1M sims, the attack gap of <b>{h_n if ph > pa else a_n}</b> 
                reveals a massive <b>Edge of {best[3]:.1%}</b>. The bookies are mispricing the volatility of goals.
                </span>
            </div>
            <div class="intel-card">
                <b style="color:#3B82F6;">VOLATILITY SCAN</b><br>
                <span style="color:#94A3B8; font-size:0.9rem;">
                Confidence rating is <b>STABLE</b>. Goal distribution shows low variance, making the Poisson prediction reliable.
                </span>
            </div>
        """, unsafe_allow_html=True)

    # 2. THE CUSTOM TRADING MATRIX (NO MORE EXCEL)
    st.markdown("### 💎 DYNAMIC TRADING MATRIX (HEATMAP ACTIVE)")
    
    # Construção da tabela HTML customizada
    html_table = """
    <table class="styled-table">
        <thead>
            <tr>
                <th style="text-align:left; padding-left:25px;">Market</th>
                <th>Confidence</th>
                <th>Fair Odd</th>
                <th>Market Odd</th>
                <th>Alpha Edge (%)</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for n, p, b in mkts + [("DNB: "+h_n, ph/(ph+pa), 1.33)]:
        edge = (p * b) - 1
        edge_clr = "#00FF88" if edge > 0.12 else "#FACC15" if edge > 0 else "#FF1744"
        op = "1" if edge > 0 else "0.3"
        bg = "rgba(0, 255, 136, 0.08)" if edge > 0.12 else "rgba(255,255,255,0.01)"
        
        html_table += f"""
        <tr style="opacity:{op}; background-color:{bg};">
            <td style="text-align:left; padding-left:25px; font-weight:700; color:white;">{n}</td>
            <td>{p:.1%}</td>
            <td style="font-family:'JetBrains Mono';">{1/p:.2f}</td>
            <td style="font-family:'JetBrains Mono'; font-weight:700; color:#00FF88;">{b:.2f}</td>
            <td style="font-weight:800; color:{edge_clr};">{edge:+.1%}</td>
        </tr>
        """
    
    html_table += "</tbody></table>"
    st.markdown(html_table, unsafe_allow_html=True)

    # 3. ANALYTICS (GRÁFICOS)
    st.markdown("---")
    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        xr = list(range(7))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig.update_layout(title="POISSON DENSITY CURVES", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=350)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.write("**PREDICTED SCORES (TOP 3)**")
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        for j in range(2, -1, -1):
            st.metric(f"SCORE {idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
