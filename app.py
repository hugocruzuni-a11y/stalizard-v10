import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Sistema High-End
st.set_page_config(
    page_title="STARLINE V83 // QUANTUM MASTER",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS "Sovereign 2026" - Estabilidade e Design de Luxo
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #000000; color: #F8FAFC; font-family: 'Plus Jakarta Sans', sans-serif; }
    [data-testid="stSidebar"] { background: rgba(10, 10, 15, 0.95) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(255, 255, 255, 0.05); }

    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important; color: #00FF88 !important;
    }
    
    /* Advisor Card de Elite */
    .advisor-box {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        border-radius: 16px; padding: 25px; border-left: 10px solid #00FF88;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6); margin-bottom: 30px;
    }

    /* Matrix Table Professional */
    .trading-matrix { width: 100%; border-collapse: separate; border-spacing: 0 6px; margin: 20px 0; }
    .trading-matrix th { color: #64748B; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; padding: 15px; text-align: left; background: rgba(255,255,255,0.03); }
    .trading-matrix td { padding: 18px 15px; font-size: 0.95rem; background: rgba(255,255,255,0.02); border-top: 1px solid rgba(255,255,255,0.03); }
    .trading-matrix tr:hover td { background: rgba(255,255,255,0.05); }

    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 800; height: 4.5em; width: 100%; border-radius: 12px; border: none;
        text-transform: uppercase; letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: CONTROLO DE DADOS ---
with st.sidebar:
    st.markdown("<h1 style='font-size:22px; color:#00FF88;'>🏛️ COMMAND CENTER</h1>", unsafe_allow_html=True)
    ctx = st.selectbox("ESTRATÉGIA", ["LIGA", "TAÇA/ELIMINATÓRIA"], key="v83_ctx")
    
    st.markdown("---")
    h_n = st.text_input("HOME", "LEIPZIG", key="v83_hn").upper()
    a_n = st.text_input("AWAY", "HOFFENHEIM", key="v83_an").upper()
    
    st.write("DADOS PERFORMANCE (GF/GA)")
    c1, c2 = st.columns(2)
    hgf = c1.number_input("H-GF", 8.0); hga = c2.number_input("H-GA", 12.0)
    agf = c1.number_input("A-GF", 12.0); aga = c2.number_input("A-GA", 10.0)
    
    st.markdown("---")
    st.write("ODDS MERCADO")
    m1 = st.number_input("ODD 1", 1.90); mx = st.number_input("ODD X", 4.00); m2 = st.number_input("ODD 2", 3.35)
    m_o15 = st.number_input("OVER 1.5", 1.16); m_o25 = st.number_input("OVER 2.5", 1.33); m_u25 = st.number_input("UNDER 2.5", 2.65)
    m_ob = st.number_input("BTTS YES", 1.32); m_hah = st.number_input("DNB HOME", 1.33)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTAR QUANTUM SCAN")
    st.button("🗑️ RESET TERMINAL", on_click=reset)

# --- PAINEL PRINCIPAL ---
if run:
    try:
        # 1. Matemática 1M
        adj = 0.67 if "TAÇA" in ctx else 1.0
        lh, la = max(0.01, ((hgf/5)*(aga/5))**0.5), max(0.01, ((agf*adj/5)*(hga/5))**0.5)
        sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
        stot = sim_h + sim_a
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)

        st.markdown(f"<h1 style='letter-spacing:-4px; margin:0; font-size:60px;'>{h_n} <span style='color:#00FF88;'>vs</span> {a_n}</h1>", unsafe_allow_html=True)
        st.markdown("---")

        # 1. QUANTUM ADVISOR (TOPO)
        st.markdown("### 🎯 QUANTUM ADVISOR")
        mkts = [
            ("1X2: "+h_n, ph, m1, "WIN"), ("1X2: "+a_n, pa, m2, "WIN"),
            ("OVER 1.5", np.mean(stot>1.5), m_o15, "GOAL"), ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOAL"),
            ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOAL"), ("DNB: "+h_n, ph/(ph+pa), m_hah, "PROT")
        ]
        recoms = sorted([(n, p, b, (p*b)-1, t) for n, p, b, t in mkts if (p*b)-1 > 0.05], key=lambda x: x[3], reverse=True)

        if recoms:
            name, p, b, edge, mtype = recoms[0]
            st.markdown(f"""
                <div class="advisor-box">
                    <div style="font-size:0.8rem; font-weight:800; color:#64748B; letter-spacing:3px;">PREMIUM {mtype} SIGNAL</div>
                    <div style="font-size:2.5rem; font-weight:900; color:white;">{name}</div>
                    <div style="font-family:'JetBrains Mono'; font-size:1.2rem; color:#00FF88;">
                        EDGE: {edge:+.1%} | CONFIDENCE: {p:.1%} | ODD: {b:.2f} (JUSTA: {1/p:.2f})
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # 2. MARKET MATRIX (MEIO)
        st.markdown("### 💎 MARKET MATRIX (HEATMAP ACTIVE)")
        
        table_body = ""
        all_display = mkts + [("1X2: DRAW", px, mx, "DRAW"), ("UNDER 2.5", np.mean(stot<2.5), m_u25, "UNDER")]
        
        for n, p, b, t in sorted(all_display, key=lambda x: (x[1]*x[2])-1, reverse=True):
            edge = (p * b) - 1
            color = "#00FF88" if edge > 0.10 else "#FACC15" if edge > 0 else "#F87171"
            bg = "rgba(0, 255, 136, 0.1)" if edge > 0.10 else "rgba(255,255,255,0.01)"
            opacity = "1" if edge > 0 else "0.3"
            
            table_body += f"""
            <tr style="background:{bg}; opacity:{opacity};">
                <td style="font-weight:800; border-radius:12px 0 0 12px;">{n}</td>
                <td>{p:.1%}</td>
                <td>{1/p:.2f}</td>
                <td style="color:#00FF88; font-weight:900;">{b:.2f}</td>
                <td style="color:{color}; font-weight:900;">{edge:+.1%}</td>
            </tr>
            """
        
        matrix_html = f"""
        <table class="trading-matrix">
            <thead><tr><th>Mercado</th><th>Probabilidade</th><th>Fair Odd</th><th>Bookie</th><th>Alpha Edge</th></tr></thead>
            <tbody>{table_body}</tbody>
        </table>
        """
        st.write(matrix_html, unsafe_allow_html=True)

        # 3. ANALYTICS GRAPHS (FUNDO)
        st.markdown("### 📊 ANALYTICS & VOLATILITY")
        c_g1, c_g2 = st.columns(2)
        
        with c_g1:
            xr = list(range(7))
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
            fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
            fig.update_layout(title="POISSON DISTRIBUTION", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=300, margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with c_g2:
            hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
            mtx = np.outer(hp, ap); mtx /= mtx.sum()
            idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
            st.write("**TOP PREDICTED SCORES**")
            sc_cols = st.columns(3)
            for j in range(2, -1, -1):
                sc_cols[2-j].metric(f"{idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e:
        st.error(f"ENGINE ERROR V83: {e}")
else:
    st.markdown("<div style='text-align:center; margin-top:20%; opacity:0.1;'><h1>QUANTUM IDLE</h1></div>", unsafe_allow_html=True)
