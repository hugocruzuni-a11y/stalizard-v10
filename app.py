import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Terminal de Hedge Fund
st.set_page_config(page_title="STARLINE V51 - INSTITUTIONAL", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS "Black Gold" (Design de Alta Performance)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700;900&display=swap');
    
    .stApp { background-color: #0B0F19; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    .block-container { padding: 1.5rem 3rem !important; }

    /* Inputs Estilo Dark Terminal */
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #161B22 !important; border: 1px solid #30363D !important; border-radius: 4px !important; color: #F8FAFC !important;
    }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        color: #8B949E !important; font-size: 0.7rem !important; font-weight: 700 !important; text-transform: uppercase;
    }

    /* Botão Quantum Gold */
    div.stButton > button {
        background: linear-gradient(90deg, #D4AF37 0%, #F1C40F 100%) !important;
        color: #0B0F19 !important; font-weight: 900; 
        height: 3.5em; width: 100%; border: none; border-radius: 4px; text-transform: uppercase; letter-spacing: 2px;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(212, 175, 55, 0.4); }

    /* Advisor Cards Prestige */
    .advice-card {
        padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 10px solid;
        background: #161B22; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .val-win { border-color: #238636; } .val-goal { border-color: #D4AF37; } .val-under { border-color: #1F6FEB; }

    /* Tabela de Trading Profissional */
    .stTable { background-color: #161B22 !important; border: 1px solid #30363D !important; }
    thead tr th { background-color: #0D1117 !important; color: #8B949E !important; border-bottom: 1px solid #30363D !important; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# Header de Software de Prateleira
st.markdown("<h1 style='color:#F8FAFC; font-weight:900; margin:0; letter-spacing:-2px;'>🏛️ STARLINE <span style='color:#D4AF37; font-weight:400;'>INSTITUTIONAL</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E; margin-bottom:20px; font-family:\"JetBrains Mono\"'>QUANTUM ALGORITHMIC TRADING // ENGINE V51.0 // 1M SIMS</p>", unsafe_allow_html=True)

col_in, col_viz, col_data = st.columns([0.9, 1.4, 1.3], gap="large")

with col_in:
    st.markdown("### ⚙️ DATA ENTRY")
    ctx = st.selectbox("STRATEGIC CONTEXT", ["REGULAR SEASON", "KNOCKOUT / CUP"], key="ctx")
    bank = st.number_input("TOTAL BANKROLL (€)", value=1000.0, step=100.0)
    
    c_t1, c_t2 = st.columns(2)
    h_n = c_t1.text_input("HOME", "VILLARREAL").upper()
    a_n = c_t2.text_input("AWAY", "REAL SOCIEDAD").upper()
    
    st.write("**PERFORMANCE STATS**")
    s1, s2, s3, s4 = st.columns(4)
    hgf = s1.number_input("HGF", 9.0); hga = s2.number_input("HGA", 7.0)
    agf = s3.number_input("AGF", 12.0); aga = s4.number_input("AGA", 10.0)
    
    st.write("**MARKET QUOTES**")
    o1, ox, o2 = st.columns(3)
    m1, mx, m2 = o1.number_input("1", 1.88), ox.number_input("X", 4.00), o2.number_input("2", 3.35)
    
    st.write("**GOALS & SPECIALS**")
    g1, g2, g3 = st.columns(3)
    m_o15, m_o25, m_o35 = g1.number_input("O1.5", 1.10), g2.number_input("O2.5", 1.33), g3.number_input("O3.5", 1.78)
    
    g4, g5, g6 = st.columns(3)
    m_u15, m_u25, m_u35 = g4.number_input("U1.5", 4.50), g5.number_input("U2.5", 2.65), g6.number_input("U3.5", 1.50)
    
    sp1, sp2 = st.columns(2)
    m_ob = sp1.number_input("BTTS YES", 1.32); m_dnbh = sp2.number_input("DNB HOME", 1.33)

    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("⚡ EXECUTE QUANTUM SCAN")
    st.button("🗑️ SYSTEM RESET", on_click=reset)

if run:
    # --- QUANTUM ENGINE 1M ---
    adj = 0.67 if "KNOCKOUT" in ctx else 1.0
    lh, la = ((hgf/5)*(aga/5))**0.5, ((agf*adj/5)*(hga/5))**0.5
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    
    with col_viz:
        st.markdown("### 📊 QUANTUM ANALYTICS")
        # Gráfico Poisson Interativo
        x = list(range(7))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=[poisson.pmf(i, lh) for i in x], name=h_n, fill='tozeroy', line_color='#238636'))
        fig.add_trace(go.Scatter(x=x, y=[poisson.pmf(i, la) for i in x], name=a_n, fill='tozeroy', line_color='#1F6FEB'))
        fig.update_layout(title="GOAL PROBABILITY CURVE", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#8B949E", height=380)
        st.plotly_chart(fig, use_container_width=True)

        # Histograma de Volatilidade
        st.write("**GOAL DISTRIBUTION FREQUENCY**")
        hist_data = pd.DataFrame({'Goals': stot})
        fig2 = go.Figure(data=[go.Histogram(x=stot, histnorm='probability', marker_color='#D4AF37', opacity=0.7)])
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#8B949E", height=280, margin=dict(t=0))
        st.plotly_chart(fig2, use_container_width=True)

    with col_data:
        st.markdown("### 💎 INSTITUTIONAL SIGNALS")
        
        # Mapeamento Total de Mercados
        mkts = [
            ("1X2: HOME", ph, m1, "WIN"), ("1X2: DRAW", px, mx, "DRAW"), ("1X2: AWAY", pa, m2, "WIN"),
            ("OVER 1.5", np.mean(stot>1.5), m_o15, "GOAL"), ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOAL"),
            ("OVER 3.5", np.mean(stot>3.5), m_o35, "GOAL"), ("UNDER 1.5", np.mean(stot<1.5), m_u15, "UNDER"),
            ("UNDER 2.5", np.mean(stot<2.5), m_u25, "UNDER"), ("UNDER 3.5", np.mean(stot<3.5), m_u35, "UNDER"),
            ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOAL"), ("DNB: HOME", ph/(ph+pa), m_dnbh, "PROT")
        ]
        
        # Advisor Inteligente com Kelly Criterion
        recoms = sorted([(n, p, b, (p*b)-1, t) for n, p, b, t in mkts if (p*b)-1 > 0.05], key=lambda x: x[3], reverse=True)
        
        for n, p, b, e, t in recoms[:3]:
            # Kelly Criterion: f* = (bp - q) / b -> f* = edge / (odd - 1)
            kelly = (e / (b - 1)) * 0.25 # Kelly fracionário (25%) para segurança institucional
            stake_eur = bank * kelly
            
            c_type = "val-win" if t=="WIN" else "val-goal" if t=="GOAL" else "val-under"
            st.markdown(f"""
            <div class="advice-card {c_type}">
                <span style='color:#8B949E; font-size:0.7rem;'>STRATEGY: {t} // EDGE: {e:+.1%}</span><br>
                <b style='font-size:1.3rem; color:#F8FAFC;'>{n}</b><br>
                <span style='color:#D4AF37;'>STAKE ADVISOR: <b>{stake_eur:.2f}€</b></span> | ODD: <b>{b:.2f}</b>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 🏛️ TOTAL MARKET SCAN")
        df_final = pd.DataFrame([{"MARKET": n, "PROB": f"{p:.1%}", "FAIR": f"{1/p:.2f}", "BOOKIE": f"{b:.2f}", "EV": f"{e:+.1%}"} for n, p, b, e, t in sorted([(n,p,b,(p*b)-1,t) for n,p,b,t in mkts], key=lambda x: x[3], reverse=True)])
        st.table(df_final)

        # Placar Exato Institucional (Dixon-Coles Ajustado)
        st.write("**PROBABLE SCORE (TOP 3)**")
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx[0,0] *= 1.12; mtx[1,1] *= 1.08; mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        sc_cols = st.columns(3)
        for j in range(2, -1, -1):
            sc_cols[2-j].metric(f"{idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
