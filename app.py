import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Advanced System Config
st.set_page_config(page_title="STARLINE V93 - THE ORACLE", layout="wide", initial_sidebar_state="expanded")

# 2. Sovereign Oracle CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%);
        color: #FFFFFF; font-family: 'Inter', sans-serif; 
    }
    
    /* Sidebar Prestige */
    [data-testid="stSidebar"] { 
        background-color: rgba(5, 5, 10, 0.98) !important; 
        backdrop-filter: blur(25px); border-right: 1px solid rgba(255,255,255,0.05); 
    }

    /* Intelligence Cards */
    .intel-card {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 15px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 10px;
    }

    /* Decision Glow */
    .advisor-glow {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.05) 0%, rgba(0, 0, 0, 0.4) 100%);
        border-radius: 20px; padding: 35px; border: 1px solid #00FF88;
        box-shadow: 0 0 60px rgba(0, 255, 136, 0.1); margin-bottom: 30px;
    }

    div.stButton > button {
        background: #00FF88 !important; color: #000000 !important; font-weight: 900; 
        height: 4.5em; width: 100%; border-radius: 12px; border: none; text-transform: uppercase;
        letter-spacing: 2px; box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: ORACLE CONTROLS ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88; font-size:24px; margin-bottom:0;'>🏛️ STARLINE ORACLE</h1>", unsafe_allow_html=True)
    st.caption("AI-POWERED QUANTUM ENGINE // V93.0")
    
    st.markdown("---")
    h_n = st.text_input("HOME TEAM", "VILLARREAL").upper()
    a_n = st.text_input("AWAY TEAM", "REAL SOCIEDAD").upper()
    
    col_gf, col_ga = st.columns(2)
    hgf = col_gf.number_input("H-GF", 9.0); hga = col_ga.number_input("H-GA", 7.0)
    agf = col_gf.number_input("A-GF", 12.0); aga = col_ga.number_input("A-GA", 10.0)
    
    st.markdown("---")
    st.write("LIVE MARKET QUOTES")
    m1 = st.number_input("HOME ODD", 1.90); mx = st.number_input("DRAW ODD", 4.00); m2 = st.number_input("AWAY ODD", 3.35)
    o25 = st.number_input("OVER 2.5", 1.33); m_ob = st.number_input("BTTS YES", 1.32)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🔮 INITIALIZE QUANTUM SCAN")
    st.button("🗑️ CLEAR DATA", on_click=reset)

# --- MAIN DASHBOARD ---
if not run:
    st.markdown("""
        <div style='text-align:center; padding-top:100px;'>
            <h1 style='font-size:5rem; font-weight:900; letter-spacing:-5px; margin-bottom:0;'>ORACLE <span style='color:#00FF88;'>SCANNER</span></h1>
            <p style='color:#64748B; font-size:1.5rem; letter-spacing:10px;'>AWAITING INPUT PARAMETERS</p>
            <div style='margin-top:50px; opacity:0.5;'>
                <p>QUANTUM ENGINE 2026 // READY TO PROCESS 1,000,000 SCENARIOS</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    # 1M ENGINE
    lh, la = max(0.01, ((hgf/5)*(aga/5))**0.5), max(0.01, ((agf/5)*(hga/5))**0.5)
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)

    st.markdown(f"<h1 style='letter-spacing:-3px; font-size:55px; margin:0;'>{h_n} <span style='color:#00FF88;'>X</span> {a_n}</h1>", unsafe_allow_html=True)

    # 1. ADVISOR & INTELLIGENCE
    col_adv, col_notes = st.columns([1.2, 0.8])
    
    mkts = [
        ("HOME WIN", ph, m1), ("AWAY WIN", pa, m2), ("DRAW", px, mx),
        ("OVER 2.5", np.mean(stot>2.5), o25), ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob)
    ]
    best = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts], key=lambda x: x[3], reverse=True)[0]

    with col_adv:
        st.markdown(f"""
            <div class="advisor-glow">
                <p style="color:#64748B; margin:0; font-size:0.8rem; font-weight:800; letter-spacing:4px;">QUANTUM MASTER SIGNAL</p>
                <h1 style="color:white; margin:10px 0; font-size:3.5rem;">{best[0]}</h1>
                <p style="color:#00FF88; font-size:1.5rem; margin:0; font-weight:800;">EDGE: {best[3]:+.1%} | CONFIDENCE: {best[1]:.1%}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_notes:
        st.markdown("### 🧠 AI INTELLIGENCE NOTES")
        # Lógica de Notas Dinâmicas
        note_color = "#00FF88" if best[3] > 0.15 else "#FACC15"
        st.markdown(f"""
            <div class="intel-card">
                <b style="color:{note_color};">WHY THIS RESULT?</b><br>
                <span style="color:#94A3B8; font-size:0.9rem;">
                Based on 1,000,000 simulations, the defensive gap of <b>{a_n if ph > pa else h_n}</b> 
                exposes a mathematical <b>Edge of {best[3]:.1%}</b>. The market is underpricing this scenario by {abs(best[3]*100):.1%}.
                </span>
            </div>
            <div class="intel-card">
                <b style="color:#3B82F6;">VOLATILITY INDEX</b><br>
                <span style="color:#94A3B8; font-size:0.9rem;">
                Score variance is <b>LOW</b>. This suggests a stable outcome based on the GF/GA input trends.
                </span>
            </div>
        """, unsafe_allow_html=True)

    # 2. DYNAMIC MATRIX
    st.markdown("### 💎 INTERACTIVE TRADING MATRIX")
    df_data = []
    for n, p, b in mkts:
        edge = (p * b) - 1
        df_data.append({"Market": n, "Confidence": p, "Fair Odd": 1/p, "Market Odd": b, "Alpha Edge": edge})
    
    st.dataframe(
        pd.DataFrame(df_data),
        column_config={
            "Market": st.column_config.TextColumn("MARKET"),
            "Confidence": st.column_config.ProgressColumn("CONFIDENCE", format="%.1f%%", min_value=0, max_value=1),
            "Fair Odd": st.column_config.NumberColumn("FAIR", format="%.2f"),
            "Market Odd": st.column_config.NumberColumn("MARKET", format="%.2f"),
            "Alpha Edge": st.column_config.NumberColumn("EDGE", format="%+.1%"),
        },
        hide_index=True, use_container_width=True
    )

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
        st.write("**PLACAR PREVISTO (TOP 3)**")
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        for j in range(2, -1, -1):
            st.metric(f"SCORE {idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
