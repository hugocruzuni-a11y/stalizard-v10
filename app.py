import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. Configuração de Terminal de Luxo Biométrico
st.set_page_config(page_title="STARLINE V52.1 - QUANTUM BIOMETRIC", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS "Quantum Biometric" (Dark Theme de Alta Performance)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700;900&display=swap');
    
    .stApp { background-color: #000000; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    .main .block-container { padding: 1.5rem 3rem !important; max-width: 100% !important; }

    /* Inputs Antracite */
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #111111 !important; border: 1px solid #222222 !important; border-radius: 8px !important; color: #FFFFFF !important;
    }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        color: #AAAAAA !important; font-size: 0.7rem !important; font-weight: 700 !important; text-transform: uppercase;
    }

    /* Botão Néon Quantum */
    div.stButton > button {
        background: linear-gradient(135deg, #00E676 0%, #00C853 100%) !important;
        color: #000000 !important; font-weight: 900; 
        height: 3.8em; width: 100%; border: none; border-radius: 8px; text-transform: uppercase; letter-spacing: 2px;
        box-shadow: 0 4px 15px rgba(0, 230, 118, 0.3);
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0, 230, 118, 0.5); }

    /* Tabela de Trading */
    .stTable { background-color: #0A0A0A !important; border: 1px solid #1A1A1A !important; border-radius: 8px !important; }
    thead tr th { background-color: #000000 !important; color: #FFFFFF !important; font-weight: 800 !important; border-bottom: 2px solid #222222 !important; }
    
    /* Gauge Container */
    .biometric-box { background-color: #050505; padding: 20px; border-radius: 12px; border: 1px solid #111111; }
    </style>
    """, unsafe_allow_html=True)

def reset_engine():
    for key in list(st.session_state.keys()): del st.session_state[key]

# Header
st.markdown("<h1 style='color:#FFFFFF; font-weight:900; margin:0; letter-spacing:-2px;'>🏛️ STARLINE <span style='color:#00E676; font-weight:400;'>BIOMETRIC V52.1</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#AAAAAA; margin-bottom:20px; font-family:\"JetBrains Mono\"'>QUANTUM TRADING TERMINAL // 1.000.000 SIMULATIONS</p>", unsafe_allow_html=True)

# Layout: Inputs, Gráficos, Resultados
col_in, col_viz, col_res = st.columns([1, 1.4, 1.3], gap="large")

with col_in:
    st.markdown("### 🛠️ CONFIG")
    ctx = st.selectbox("CONTEXT", ["REGULAR SEASON", "KNOCKOUT / CUP"], key="v521_ctx")
    bank = st.number_input("TOTAL BANK (€)", value=1000.0, step=100.0, key="v521_bank")
    
    c_t1, c_t2 = st.columns(2)
    h_n = c_t1.text_input("HOME", "VILLARREAL", key="v521_hn").upper()
    a_n = c_t2.text_input("AWAY", "REAL SOCIEDAD", key="v521_an").upper()
    
    st.write("**STATS GF/GA**")
    s1, s2, s3, s4 = st.columns(4)
    v_hgf = s1.number_input("HGF", value=9.0, key="v521_hgf"); v_hga = s2.number_input("HGA", value=7.0, key="v521_hga")
    v_agf = s3.number_input("AGF", value=12.0, key="v521_agf"); v_aga = s4.number_input("AGA", value=10.0, key="v521_aga")
    
    st.write("**MARKET QUOTES**")
    o1, ox, o2 = st.columns(3)
    m1 = o1.number_input("ODD 1", 1.88, key="v521_o1")
    mx = ox.number_input("ODD X", 4.00, key="v521_ox")
    m2 = o2.number_input("ODD 2", 3.35, key="v521_o2")
    
    st.write("**SPECIALS**")
    g1, g2, g3 = st.columns(3)
    m_o15 = g1.number_input("+1.5", 1.10, key="v521_o15")
    m_o25 = g2.number_input("+2.5", 1.33, key="v521_o25")
    m_u25 = g3.number_input("-2.5", 2.65, key="v521_u25")
    
    g4, g5 = st.columns(2)
    m_ob = g4.number_input("BTTS", 1.32, key="v521_ob")
    m_hah = g5.number_input("DNB-H", 1.33, key="v521_hah")

    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTE QUANTUM SCAN")
    st.button("🗑️ RESET ENGINE", on_click=reset_engine)

if run:
    try:
        # Engine de Elite 1M
        adj = 0.67 if "KNOCKOUT" in ctx else 1.0
        lh = max(0.01, ((v_hgf/5)*(v_aga/5))**0.5)
        la = max(0.01, ((v_agf*adj/5)*(v_hga/5))**0.5)
        
        sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
        stot = sim_h + sim_a
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa; ph, px, pa = ph/norm, px/norm, pa/norm

        with col_viz:
            st.markdown("### 📊 VISUAL ANALYTICS")
            # Gráfico de Curvas Interativo
            xr = list(range(7))
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00E676'))
            fig.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6'))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#FFFFFF", height=380, margin=dict(l=0,r=0,b=0,t=40))
            st.plotly_chart(fig, use_container_width=True)

            # Histograma de Volatilidade
            fig2 = go.Figure(data=[go.Histogram(x=stot, histnorm='probability', marker_color='#FF1744', opacity=0.7)])
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#FFFFFF", height=280, margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig2, use_container_width=True)

        with col_res:
            st.markdown("### 🧠 QUANTUM DECISION")
            
            # Mapeamento Total
            mkts = [
                ("1X2: HOME", ph, m1, "WIN"), ("1X2: DRAW", px, mx, "DRAW"), ("1X2: AWAY", pa, m2, "WIN"),
                ("OVER 1.5", np.mean(stot>1.5), m_o15, "GOAL"), ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOAL"),
                ("UNDER 2.5", np.mean(stot<2.5), m_u25, "UNDER"), ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOAL"),
                ("DNB: HOME", ph/(ph+pa), m_hah, "PROT")
            ]
            
            # Advisor com Gauge
            recoms = sorted([(n, p, b, (p*b)-1, t) for n, p, b, t in mkts if (p*b)-1 > 0.05], key=lambda x: x[3], reverse=True)
            
            if recoms:
                best_n, best_p, best_b, best_e, best_t = recoms[0]
                kelly = (best_e / (best_b - 1)) * 0.25
                gauge_color = "#00E676" if best_e > 0.15 else "#FFEA00"
                
                fig_g = go.Figure(go.Indicator(
                    mode = "gauge+number", value = min(100, best_e * 200),
                    title = {'text': f"{best_t}: {best_n}", 'font': {'size': 18, 'color': '#FFFFFF'}},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': gauge_color}, 'bgcolor': "#111111"},
                    number = {'suffix': "%", 'font': {'color': gauge_color}}
                ))
                fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FFFFFF", height=280, margin=dict(t=50,b=0,l=10,r=10))
                st.plotly_chart(fig_g, use_container_width=True)
                
                st.metric("KELLY STAKE ADVISOR", f"{(bank * kelly):.2f} €", f"{best_e:+.1%} EDGE")
            
            st.write("**TOTAL MARKET SCAN**")
            table_data = []
            for n, p, b, _ in mkts:
                edge = (p * b) - 1
                bg = "rgba(0, 230, 118, 0.15)" if edge > 0.10 else "rgba(255, 234, 0, 0.15)" if edge > 0 else "none"
                table_data.append({"MARKET": n, "PROB": f"{p:.1%}", "FAIR": f"{1/p:.2f}", "BOOKIE": f"{b:.2f}", "EV": f"{edge:+.1%}", "bg": bg})
            
            df_final = pd.DataFrame(table_data)
            st.table(df_final.drop('bg', axis=1).style.apply(lambda r: [f"background-color: {table_data[r.name]['bg']}"] * len(r), axis=1))

    except Exception as e:
        st.error(f"ENGINE ERROR V52.1: {e}")
