import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Terminal de Investimento 2026
st.set_page_config(page_title="STARLINE V87 - SOVEREIGN", layout="wide", initial_sidebar_state="expanded")

# 2. Estilização de Luxo (Glassmorphism & High Contrast)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at 50% 0%, #1e293b 0%, #000000 100%);
        color: #FFFFFF; font-family: 'Plus Jakarta Sans', sans-serif; 
    }
    
    /* Sidebar de Elite */
    [data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.9) !important; backdrop-filter: blur(15px); border-right: 1px solid rgba(255,255,255,0.05); }
    
    /* Welcome Hero Section */
    .hero-text {
        text-align: center; padding: 100px 20px;
        background: linear-gradient(180deg, rgba(0,255,136,0.1) 0%, rgba(0,0,0,0) 100%);
        border-radius: 20px; border: 1px solid rgba(255,255,255,0.03);
    }

    /* Advisor Signal */
    .advisor-premium {
        background: rgba(255, 255, 255, 0.03); border-left: 8px solid #00FF88;
        padding: 25px; border-radius: 12px; margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.05);
    }

    /* Botão de Alta Performance */
    div.stButton > button {
        background: #00FF88 !important; color: #000000 !important; font-weight: 800; 
        height: 4em; width: 100%; border-radius: 10px; border: none; text-transform: uppercase; letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR DE COMANDO ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88;'>🏛️ TERMINAL</h2>", unsafe_allow_html=True)
    bank = st.number_input("BANCA TOTAL (€)", value=1000.0)
    
    st.markdown("---")
    h_n = st.text_input("EQUIPA CASA", "LEIPZIG").upper()
    a_n = st.text_input("EQUIPA FORA", "HOFFENHEIM").upper()
    
    st.write("MÉDIAS DE GOLOS (5 JOGOS)")
    c1, c2 = st.columns(2)
    hgf = c1.number_input("GOLOS MARCADOS (CASA)", 8.0); hga = c2.number_input("GOLOS SOFRIDOS (CASA)", 12.0)
    agf = c1.number_input("GOLOS MARCADOS (FORA)", 12.0); aga = c2.number_input("GOLOS SOFRIDOS (FORA)", 10.0)
    
    st.markdown("---")
    st.write("ODDS DO MERCADO")
    m1 = st.number_input("VITÓRIA CASA (1)", 1.90); mx = st.number_input("EMPATE (X)", 4.00); m2 = st.number_input("VITÓRIA FORA (2)", 3.35)
    
    st.write("MERCADO DE GOLOS")
    o15 = st.number_input("MAIS DE 1.5", 1.16); o25 = st.number_input("MAIS DE 2.5", 1.33); o35 = st.number_input("MAIS DE 3.5", 1.78)
    u15 = st.number_input("MENOS DE 1.5", 4.50); u25 = st.number_input("MENOS DE 2.5", 2.65); u35 = st.number_input("MENOS DE 3.5", 1.50)
    
    st.write("ESPECIAIS")
    m_ob = st.number_input("AMBAS MARCAM (SIM)", 1.32); m_hah = st.number_input("DNB (EMPATE ANULA CASA)", 1.33)
    
    run = st.button("🚀 EXECUTAR ANÁLISE QUÂNTICA")
    st.button("🗑️ REINICIAR", on_click=reset)

# --- PAINEL PRINCIPAL ---
if not run:
    st.markdown(f"""
        <div class="hero-text">
            <h1 style="font-size: 4rem; margin-bottom: 0;">STARLINE <span style="color:#00FF88;">V87</span></h1>
            <p style="color:#94A3B8; font-size: 1.2rem;">SISTEMA INSTITUCIONAL DE PREVISÃO ALGORÍTMICA</p>
            <p style="color:#64748B; font-family:'JetBrains Mono'; mt-4">PRONTO PARA PROCESSAR 1.000.000 DE SIMULAÇÕES</p>
        </div>
    """, unsafe_allow_html=True)
else:
    # ENGINE 1M
    lh, la = max(0.01, ((hgf/5)*(aga/5))**0.5), max(0.01, ((agf/5)*(hga/5))**0.5)
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)

    st.markdown(f"<h1 style='margin-bottom:0;'>{h_n} vs {a_n}</h1>", unsafe_allow_html=True)

    # 1. ADVISOR (TOP)
    all_mkts = [
        ("VITÓRIA: "+h_n, ph, m1), ("EMPATE", px, mx), ("VITÓRIA: "+a_n, pa, m2),
        ("MAIS DE 1.5 GOLOS", np.mean(stot>1.5), o15), ("MAIS DE 2.5 GOLOS", np.mean(stot>2.5), o25),
        ("MAIS DE 3.5 GOLOS", np.mean(stot>3.5), o35), ("MENOS DE 1.5 GOLOS", np.mean(stot<1.5), u15),
        ("MENOS DE 2.5 GOLOS", np.mean(stot<2.5), u25), ("MENOS DE 3.5 GOLOS", np.mean(stot<3.5), u35),
        ("AMBAS MARCAM: SIM", np.mean((sim_h>0)&(sim_a>0)), m_ob), ("EMPATE ANULA (DNB CASA)", ph/(ph+pa), m_hah)
    ]
    recoms = sorted([(n, p, b, (p*b)-1) for n, p, b in all_mkts if (p*b)-1 > 0.05], key=lambda x: x[3], reverse=True)

    if recoms:
        n, p, b, edge = recoms[0]
        st.markdown(f"""
            <div class="advisor-premium">
                <p style="color:#64748B; margin:0; font-size:0.8rem; font-weight:800; letter-spacing:2px;">SINAL ALPHA DETETADO</p>
                <h2 style="color:white; margin:10px 0;">{n}</h2>
                <span style="color:#00FF88; font-weight:800; font-size:1.4rem;">LUCRO ESPERADO (EDGE): {edge:+.1%}</span> | 
                <span style="color:#FFFFFF;">PROBABILIDADE: {p:.1%}</span>
            </div>
        """, unsafe_allow_html=True)

    # 2. MATRIX (CENTER)
    st.markdown("### 💎 MATRIZ DE MERCADO COMPLETA")
    
    df_data = []
    for n, p, b in all_mkts:
        edge = (p * b) - 1
        df_data.append({
            "MERCADO": n,
            "PROBABILIDADE": p,
            "ODD JUSTA": 1/p,
            "ODD CASA": b,
            "VALOR (EV)": edge
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(
        df,
        column_config={
            "MERCADO": st.column_config.TextColumn("MERCADO (DESCRITIVO)"),
            "PROBABILIDADE": st.column_config.ProgressColumn("CONFIANÇA (%)", format="%.1f%%", min_value=0, max_value=1),
            "ODD JUSTA": st.column_config.NumberColumn("NOSSA ODD", format="%.2f"),
            "ODD CASA": st.column_config.NumberColumn("ODD CASA", format="%.2f"),
            "VALOR (EV)": st.column_config.NumberColumn("LUCRO POTENCIAL", format="%+.1%"),
        },
        hide_index=True,
        use_container_width=True
    )

    # 3. GRÁFICOS (BOTTOM)
    st.markdown("<br>", unsafe_allow_html=True)
    c_viz, c_sc = st.columns([1.3, 0.7])
    
    with c_viz:
        xr = list(range(7))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88'))
        fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=300, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with c_sc:
        st.write("**PLACAR MAIS PROVÁVEL**")
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        for j in range(2, -1, -1):
            st.metric(f"RESULTADO {idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
