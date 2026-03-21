import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Terminal de Investimento
st.set_page_config(page_title="STARLINE V60 - QUANT MASTER", layout="wide", initial_sidebar_state="expanded")

# 2. CSS "Stealth Trading" (Foco Total na Tabela e Legibilidade)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;800;900&display=swap');
    
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Estilizada */
    [data-testid="stSidebar"] { background-color: #0A0A0A !important; border-right: 1px solid #1A1A1A; }
    
    /* Inputs de Alta Precisão */
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #111111 !important; border: 1px solid #333333 !important; color: #00E676 !important;
    }
    
    /* A TABELA MASTER (Design de Software de 10k) */
    .styled-table {
        width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 1rem;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.5); border-radius: 8px; overflow: hidden;
    }
    .styled-table thead tr { background-color: #00E676; color: #000000; text-align: left; font-weight: 900; }
    .styled-table th, .styled-table td { padding: 15px 20px; border-bottom: 1px solid #111111; }
    .styled-table tbody tr:nth-of-type(even) { background-color: #0A0A0A; }
    
    /* Botão de Execução */
    div.stButton > button {
        background: #00E676 !important; color: #000000 !important; font-weight: 900; 
        height: 4em; width: 100%; border-radius: 4px; letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: INPUT DE DADOS ---
with st.sidebar:
    st.markdown("<h2 style='color:#00E676;'>⚙️ CONFIG</h2>", unsafe_allow_html=True)
    bank = st.number_input("BANCA (€)", value=1000.0, step=100.0)
    ctx = st.selectbox("TIPO DE JOGO", ["LIGA", "PLAYOFF"])
    
    st.markdown("---")
    h_n = st.text_input("HOME", "VILLARREAL").upper()
    a_n = st.text_input("AWAY", "REAL SOCIEDAD").upper()
    
    col1, col2 = st.columns(2)
    hgf = col1.number_input("H-GF", 9.0); hga = col2.number_input("H-GA", 7.0)
    agf = col1.number_input("A-GF", 12.0); aga = col2.number_input("A-GA", 10.0)
    
    st.markdown("---")
    st.write("ODDS DO MERCADO")
    m1 = st.number_input("ODD 1", 1.88); mx = st.number_input("ODD X", 4.00); m2 = st.number_input("ODD 2", 3.35)
    m_o25 = st.number_input("OVER 2.5", 1.33); m_u25 = st.number_input("UNDER 2.5", 2.65)
    m_ob = st.number_input("BTTS YES", 1.32)
    
    run = st.button("⚡ GERAR MATRIX DE VALOR")
    st.button("🗑️ RESET", on_click=reset)

# --- PAINEL PRINCIPAL ---
if not run:
    st.markdown("<h1 style='text-align:center; margin-top:20%; color:#1A1A1A;'>AGUARDANDO DADOS PARA ANÁLISE QUANTITATIVA...</h1>", unsafe_allow_html=True)
else:
    # ENGINE 1M
    adj = 0.67 if ctx == "PLAYOFF" else 1.0
    lh = max(0.01, ((hgf/5)*(aga/5))**0.5)
    la = max(0.01, ((agf*adj/5)*(hga/5))**0.5)
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)

    st.markdown(f"<h1 style='margin:0;'>🏛️ {h_n} vs {a_n}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00E676;'>QUANTUM MATRIX ANALYSIS // 1.000.000 SIMULATIONS</p>", unsafe_allow_html=True)

    # Top Row: Gráficos
    c_viz1, c_viz2 = st.columns([1, 1])
    with c_viz1:
        fig = go.Figure()
        xr = list(range(6))
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00E676'))
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6'))
        fig.update_layout(title="DISTRIBUIÇÃO DE GOLOS (POISSON)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
        st.plotly_chart(fig, use_container_width=True)
    with c_viz2:
        # Gauge de Confiança (Maior Edge)
        mkts = [
            ("1X2: HOME", ph, m1), ("1X2: DRAW", px, mx), ("1X2: AWAY", pa, m2),
            ("OVER 2.5", np.mean(stot>2.5), m_o25), ("UNDER 2.5", np.mean(stot<2.5), m_u25), ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob)
        ]
        best = max(mkts, key=lambda x: (x[1]*x[2])-1)
        edge_max = (best[1]*best[2])-1
        
        fig_g = go.Figure(go.Indicator(
            mode = "gauge+number", value = edge_max*100,
            title = {'text': f"MAX EDGE: {best[0]}", 'font': {'size': 18}},
            gauge = {'axis': {'range': [0, 40]}, 'bar': {'color': "#00E676"}, 'bgcolor': "#111111"},
            number = {'suffix': "%", 'font': {'color': "#00E676"}}
        ))
        fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
        st.plotly_chart(fig_g, use_container_width=True)

    # --- A GRANDE TABELA DE TRADING ---
    st.markdown("### 💎 MARKET VALUE MATRIX")
    
    rows = []
    for name, p, b in mkts:
        edge = (p * b) - 1
        kelly = (edge / (b - 1)) * 0.25 if edge > 0 else 0
        stake = bank * kelly
        profit = (stake * b) - stake if stake > 0 else 0
        
        # Cor da linha baseada na Edge
        color = "#00E676" if edge > 0.10 else "#F1C40F" if edge > 0 else "#FF1744"
        
        rows.append({
            "MERCADO": name,
            "PROB (%)": f"{p:.1%}",
            "ODD JUSTA": f"{1/p:.2f}",
            "CASA": f"<b>{b:.2f}</b>",
            "EDGE (%)": f"<span style='color:{color}; font-weight:bold;'>{edge:+.1%}</span>",
            "STAKE (€)": f"{stake:.2f}€",
            "PROFIT ESPERADO (€)": f"<span style='color:{color};'>{profit:.2f}€</span>"
        })

    df = pd.DataFrame(rows)
    st.write(df.to_html(escape=False, index=False, classes='styled-table'), unsafe_allow_html=True)

    # Footer: Placares
    st.markdown("---")
    st.write("**TOP 3 PREDICTED SCORES**")
    hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
    mtx = np.outer(hp, ap); mtx /= mtx.sum()
    idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
    cols = st.columns(3)
    for j in range(2, -1, -1):
        cols[2-j].metric(f"PLACAR {idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
