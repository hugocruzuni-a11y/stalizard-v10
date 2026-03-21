import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Terminal de Investimento 2026
st.set_page_config(
    page_title="STARLINE V88 - SOVEREIGN VISION", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. CSS de Alta Legibilidade (Foco em Contraste e Espaçamento)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Fundo Deep Black com Gradiente de Foco */
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 80%);
        color: #FFFFFF; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Sidebar Profissional */
    [data-testid="stSidebar"] { 
        background-color: rgba(10, 10, 15, 0.98) !important; 
        border-right: 1px solid rgba(255,255,255,0.05); 
    }
    
    /* Hero Section - Boas-Vindas */
    .hero-container {
        text-align: center; padding: 80px 40px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 24px; border: 1px solid rgba(255,255,255,0.05);
        margin-top: 50px;
    }

    /* Advisor de Decisão Rápida */
    .advisor-premium {
        background: #0A0A0A; border-left: 8px solid #00FF88;
        padding: 30px; border-radius: 12px; margin-bottom: 30px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }

    /* Tabela Bloomberg Style (Limpa) */
    .stDataFrame {
        border: none !important;
        margin-top: 20px;
    }
    
    /* Labels dos Inputs */
    label { 
        color: #94A3B8 !important; 
        font-weight: 700 !important; 
        text-transform: uppercase; 
        font-size: 0.75rem !important;
        letter-spacing: 1.5px;
    }

    /* Botão Principal */
    div.stButton > button {
        background: #00FF88 !important; color: #000000 !important; font-weight: 900; 
        height: 4.5em; width: 100%; border-radius: 12px; border: none; 
        text-transform: uppercase; letter-spacing: 2px;
        transition: 0.3s;
    }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 30px rgba(0,255,136,0.3); }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR DE COMANDO ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88; font-size:24px;'>🏛️ TERMINAL V88</h1>", unsafe_allow_html=True)
    st.caption("ALGORITHMIC TRADING // 2026")
    
    bank = st.number_input("BANCA PARA GESTÃO (€)", value=1000.0, step=100.0)
    
    st.markdown("---")
    h_n = st.text_input("EQUIPA DA CASA", "LEIPZIG").upper()
    a_n = st.text_input("EQUIPA DE FORA", "HOFFENHEIM").upper()
    
    st.write("MÉDIAS DE PERFORMANCE")
    c1, c2 = st.columns(2)
    hgf = c1.number_input("GOLOS MARCADOS (H)", 8.0); hga = c2.number_input("GOLOS SOFRIDOS (H)", 12.0)
    agf = c1.number_input("GOLOS MARCADOS (A)", 12.0); aga = c2.number_input("GOLOS SOFRIDOS (A)", 10.0)
    
    st.markdown("---")
    st.write("ODDS 1X2")
    m1 = st.number_input("ODD CASA (1)", 1.90); mx = st.number_input("ODD EMPATE (X)", 4.00); m2 = st.number_input("ODD FORA (2)", 3.35)
    
    st.write("MERCADO DE GOLOS")
    o15 = st.number_input("OVER 1.5", 1.16); o25 = st.number_input("OVER 2.5", 1.33); u25 = st.number_input("UNDER 2.5", 2.65)
    
    st.write("ESPECIAIS")
    m_ob = st.number_input("AMBAS MARCAM (SIM)", 1.32); m_hah = st.number_input("DNB (CASA)", 1.33)
    
    run = st.button("🚀 INICIAR ANÁLISE")
    st.button("🗑️ LIMPAR SISTEMA", on_click=reset)

# --- CORPO DO TERMINAL ---
if not run:
    st.markdown(f"""
        <div class="hero-container">
            <h1 style="font-size: 5rem; margin-bottom: 0; font-weight: 900; letter-spacing: -4px;">STARLINE</h1>
            <p style="color:#00FF88; font-size: 1.5rem; letter-spacing: 5px; font-weight: 300;">SOVEREIGN VISION V88</p>
            <div style="margin-top: 40px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.05);">
                <p style="color:#64748B; font-family:'JetBrains Mono';">SISTEMA AGUARDANDO PARÂMETROS DE ENTRADA</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    # ENGINE 1.000.000 SIMULAÇÕES
    lh, la = max(0.01, ((hgf/5)*(aga/5))**0.5), max(0.01, ((agf/5)*(hga/5))**0.5)
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    norm = ph+px+pa; ph, px, pa = ph/norm, px/norm, pa/norm

    st.markdown(f"<h1 style='font-size:3.5rem; margin-bottom:0;'>{h_n} <span style='color:#00FF88; font-weight:300;'>vs</span> {a_n}</h1>", unsafe_allow_html=True)

    # 1. ADVISOR DE ELITE (TOP)
    mkts = [
        ("VITÓRIA: "+h_n, ph, m1), ("EMPATE (X)", px, mx), ("VITÓRIA: "+a_n, pa, m2),
        ("MAIS DE 1.5 GOLOS", np.mean(stot>1.5), o15), ("MAIS DE 2.5 GOLOS", np.mean(stot>2.5), o25),
        ("MENOS DE 2.5 GOLOS", np.mean(stot<2.5), u25), ("AMBAS MARCAM (SIM)", np.mean((sim_h>0)&(sim_a>0)), m_ob)
    ]
    recoms = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts if (p*b)-1 > 0.05], key=lambda x: x[3], reverse=True)

    if recoms:
        n, p, b, edge = recoms[0]
        st.markdown(f"""
            <div class="advisor-premium">
                <p style="color:#94A3B8; margin:0; font-size:0.75rem; font-weight:900; letter-spacing:2px;">SINAL DE VALOR DETETADO</p>
                <h1 style="color:white; margin:10px 0; font-size:2.8rem;">{n}</h1>
                <p style="color:#00FF88; font-size:1.3rem; margin:0; font-weight:700;">VALOR ESTIMADO (EDGE): {edge:+.1%} | PROBABILIDADE: {p:.1%}</p>
                <p style="color:#64748B; font-family:'JetBrains Mono'; margin-top:10px;">ODD MERCADO: {b:.2f} | NOSSA ODD: {1/p:.2f}</p>
            </div>
        """, unsafe_allow_html=True)

    # 2. MATRIX DE DADOS (CENTER - LEITURA LIMPA)
    st.markdown("### 💎 MATRIX DE VALOR")
    
    df_data = []
    for n, p, b in mkts:
        edge = (p * b) - 1
        df_data.append({
            "MERCADO": n,
            "PROB (%)": p,
            "ODD JUSTA": 1/p,
            "CASA": b,
            "VALOR (EV)": edge
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(
        df,
        column_config={
            "MERCADO": st.column_config.TextColumn("MERCADO"),
            "PROB (%)": st.column_config.NumberColumn("CONFIANÇA", format="%.1%"),
            "ODD JUSTA": st.column_config.NumberColumn("ODD ALVO", format="%.2f"),
            "CASA": st.column_config.NumberColumn("CASA", format="%.2f"),
            "VALOR (EV)": st.column_config.NumberColumn("LUCRO/EDGE", format="%+.1%"),
        },
        hide_index=True,
        use_container_width=True
    )

    # 3. ANALYTICS (BOTTOM)
    st.markdown("<br>", unsafe_allow_html=True)
    c_graph, c_score = st.columns([1.3, 0.7])
    
    with c_graph:
        xr = list(range(7))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig.update_layout(
            title="DENSIDADE DE GOLOS (POISSON)", 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            font_color="white", height=320, margin=dict(l=0,r=0,t=40,b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with c_score:
        st.write("**PLACAR MAIS PROVÁVEL**")
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        for j in range(2, -1, -1):
            st.metric(f"RESULTADO {idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
