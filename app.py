import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Sistema de Elite
st.set_page_config(page_title="STARLINE V84 // SOVEREIGN", layout="wide", initial_sidebar_state="expanded")

# 2. CSS de Alto Contraste (Legibilidade 2026)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Prestige */
    [data-testid="stSidebar"] { background-color: #0A0A0A !important; border-right: 1px solid #1A1A1A; }
    
    /* Títulos e Labels */
    h1, h2, h3 { color: #FFFFFF !important; font-weight: 900 !important; letter-spacing: -1px; }
    label { color: #94A3B8 !important; font-weight: 700 !important; text-transform: uppercase; font-size: 0.75rem !important; }

    /* Advisor Box */
    .advisor-card {
        background: #0A0A0A; border: 1px solid #1A1A1A; border-left: 10px solid #00FF88;
        padding: 30px; border-radius: 12px; margin-bottom: 30px;
    }

    /* Botão Executar */
    div.stButton > button {
        background: #00FF88 !important; color: #000000 !important; font-weight: 900; 
        height: 4.5em; width: 100%; border: none; border-radius: 8px; text-transform: uppercase;
    }
    
    /* Estilo da Tabela Nativa (Pandas) */
    .stDataFrame { border: 1px solid #1A1A1A; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; margin-bottom:0;'>⚙️ COMMAND</h2>", unsafe_allow_html=True)
    bank = st.number_input("BANCA TOTAL (€)", value=1000.0)
    ctx = st.selectbox("CONTEXTO", ["LIGA", "TAÇA"])
    
    st.markdown("---")
    h_n = st.text_input("HOME", "LEIPZIG").upper()
    a_n = st.text_input("AWAY", "HOFFENHEIM").upper()
    
    st.write("STATS GF/GA")
    c1, c2 = st.columns(2)
    hgf = c1.number_input("HGF", 8.0); hga = c2.number_input("HGA", 12.0)
    agf = c1.number_input("AGF", 12.0); aga = c2.number_input("AGA", 10.0)
    
    st.markdown("---")
    st.write("ODDS MERCADO")
    m1 = st.number_input("1", 1.90); mx = st.number_input("X", 4.00); m2 = st.number_input("2", 3.35)
    m_o15 = st.number_input("O1.5", 1.16); m_o25 = st.number_input("O2.5", 1.33)
    m_ob = st.number_input("BTTS", 1.32); m_hah = st.number_input("DNB-H", 1.33)
    
    run = st.button("🚀 EXECUTAR QUANTUM SCAN")
    st.button("🗑️ RESET TERMINAL", on_click=reset)

if run:
    # Engine 1M
    adj = 0.67 if ctx == "TAÇA" else 1.0
    lh, la = max(0.01, ((hgf/5)*(aga/5))**0.5), max(0.01, ((agf*adj/5)*(hga/5))**0.5)
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)

    st.markdown(f"<h1>{h_n} vs {a_n}</h1>", unsafe_allow_html=True)

    # 1. ADVISOR (TOP)
    mkts = [
        ("1X2: "+h_n, ph, m1), ("1X2: "+a_n, pa, m2),
        ("OVER 2.5", np.mean(stot>2.5), m_o25), ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob)
    ]
    recoms = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts if (p*b)-1 > 0.05], key=lambda x: x[3], reverse=True)

    if recoms:
        name, p, b, edge = recoms[0]
        st.markdown(f"""
            <div class="advisor-card">
                <p style="color:#64748B; margin:0; font-size:0.8rem; font-weight:800; letter-spacing:2px;">BEST ALPHA SIGNAL</p>
                <h1 style="color:#FFFFFF; margin:10px 0; font-size:3rem;">{name}</h1>
                <h2 style="color:#00FF88; margin:0;">EDGE: {edge:+.1%} | CONFIDANÇA: {p:.1%}</h2>
                <p style="color:#94A3B8; font-family:'JetBrains Mono'; margin-top:10px;">ODD: {b:.2f} (JUSTA: {1/p:.2f})</p>
            </div>
        """, unsafe_allow_html=True)

    # 2. TABELA DE TRADING (MEIO) - Usando Pandas Styler para evitar erros de HTML
    st.markdown("### 💎 MARKET MATRIX (HEATMAP ACTIVE)")
    
    df_data = []
    full_mkts = mkts + [("1X2: DRAW", px, mx), ("OVER 1.5", np.mean(stot>1.5), m_o15), ("DNB: "+h_n, ph/(ph+pa), m_hah)]
    
    for n, p, b in full_mkts:
        edge = (p * b) - 1
        df_data.append({
            "MERCADO": n,
            "PROB (%)": p * 100,
            "ODD JUSTA": 1/p,
            "CASA": b,
            "EDGE (%)": edge * 100
        })
    
    df = pd.DataFrame(df_data)
    
    # Estilização da Tabela
    def color_edge(val):
        color = '#00FF88' if val > 10 else '#FACC15' if val > 0 else '#F87171'
        return f'color: {color}; font-weight: bold'

    st.table(df.style.format({
        'PROB (%)': '{:.1f}%',
        'ODD JUSTA': '{:.2f}',
        'CASA': '{:.2f}',
        'EDGE (%)': '{:+.1f}%'
    }).applymap(color_edge, subset=['EDGE (%)']))

    # 3. GRÁFICOS (FUNDO)
    st.markdown("---")
    st.markdown("### 📊 ANALYTICS & SCORES")
    c_viz, c_sc = st.columns([1.2, 0.8])
    
    with c_viz:
        xr = list(range(7))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88'))
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6'))
        fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color="white", height=300, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with c_sc:
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        for j in range(2, -1, -1):
            st.metric(f"SCORE {idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
