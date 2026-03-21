import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. Configuração de Terminal de Luxo Biométrico
st.set_page_config(page_title="STARLINE V52 - QUANTUM BIOMETRIC", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS "Quantum Biometric" (Design de Elite para Venda de Software)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700;900&display=swap');
    
    /* Configuração Global Clean & Deep Black */
    .stApp { background-color: #000000; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    .block-container { padding: 1rem 2rem 0rem 3rem !important; max-width: 98% !important; }

    /* Painel de Controle (Inputs) Antracite */
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #111111 !important; border: 1px solid #222222 !important; border-radius: 8px !important; color: #FFFFFF !important;
    }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        color: #AAAAAA !important; font-size: 0.7rem !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 1px;
    }

    /* Botão Quantum Néon (O Gatilho do Lucro) */
    div.stButton > button {
        background: linear-gradient(135deg, #00E676 0%, #00C853 100%) !important;
        color: #000000 !important; font-weight: 900; 
        height: 3.8em; width: 100%; border: none; border-radius: 8px; text-transform: uppercase; letter-spacing: 2px;
        box-shadow: 0 4px 15px rgba(0, 230, 118, 0.3); transition: 0.3s ease;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0, 230, 118, 0.5); }

    /* Advisor Biométrico Gauge Container */
    .biometric-container {
        background-color: #050505; padding: 25px; border-radius: 12px; border: 1px solid #111111;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 20px;
    }

    /* Tabela Bloomberg Dark Prestige */
    .stTable { background-color: #0A0A0A !important; border: 1px solid #1A1A1A !important; border-radius: 8px !important; }
    thead tr th { background-color: #000000 !important; color: #FFFFFF !important; font-weight: 800 !important; border-bottom: 2px solid #222222 !important; }
    tbody tr td { color: #E0E0E0 !important; border-bottom: 1px solid #111111 !important; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# Header de Produto Premium
st.markdown("<h1 style='color:#FFFFFF; font-weight:900; margin:0; letter-spacing:-2px; text-align:left;'>🏛️ STARLINE <span style='color:#00E676; font-weight:400;'>BIOMETRIC V52.0</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#AAAAAA; margin-bottom:20px; font-family:\"JetBrains Mono\"'>QUANTUM ALGORITHMIC TRADING TERMINAL // 1.000.000 SIMULATIONS</p>", unsafe_allow_html=True)

# Layout 3 Colunas: Input, Visual Analytics, Quantum Decision
col_in, col_viz, col_res = st.columns([0.9, 1.4, 1.3], gap="medium")

with col_in:
    # Painel de Controle Antracite
    st.markdown("### 🛠️ CONTROL PANEL")
    ctx = st.selectbox("STRATEGIC CONTEXT", ["REGULAR SEASON", "KNOCKOUT / CUP"], key="v52_ctx")
    
    c_teams1, c_teams2 = st.columns(2)
    h_n = c_teams1.text_input("HOME", value="VILLARREAL", key="hn").upper()
    a_n = c_teams2.text_input("AWAY", value="REAL SOCIEDAD", key="an").upper()
    
    st.markdown("<p style='font-size:11px; font-weight:800; color:#AAAAAA; margin-top:15px;'>MÉDIAS GF/GA (5 JOGOS)</p>", unsafe_allow_html=True)
    c_s1, c_s2 = st.columns(2); v_hgf = c_s1.number_input("H-GF", 9.0); v_hga = c_s2.number_input("H-GA", 7.0)
    c_s3, c_s4 = st.columns(2); v_agf = c_s3.number_input("A-GF", 12.0); v_aga = c_s4.number_input("A-GA", 10.0)
    
    st.markdown("<p style='font-size:11px; font-weight:800; color:#AAAAAA; margin-top:15px;'>LIVE MARKET ODDS</p>", unsafe_allow_html=True)
    c_o1, c_o2, c_o3 = st.columns(3); m1 = c_o1.number_input("1", 1.88); mx = c_o2.number_input("X", 4.00); m2 = c_o3.number_input("2", 3.35)
    c_o4, c_o5, c_o6 = st.columns(3); m_o15 = c_o4.number_input("+1.5", 1.10); m_o25 = c_o5.number_input("+2.5", 1.33); m_ob = c_o6.number_input("BTTS", 1.32)
    c_o7, c_o8 = st.columns(2); m_hah = c_o7.number_input("DNB HOME", 1.33); m_u25 = c_o8.number_input("-2.5", 2.65)

    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTE QUANTUM SCAN")
    st.button("🗑️ RESET ENGINE", on_click=reset)

if run:
    # --- QUANTUM ENGINE V52.0 (Deep Math 1M) ---
    adj = 0.67 if "KNOCKOUT" in ctx else 1.0
    lh, la = max(0.01, ((v_hgf/5)*(v_aga/5))**0.5), max(0.01, ((v_agf*adj/5)*(v_hga/5))**0.5)
    
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    norm = ph + px + pa; ph, px, pa = ph/norm, px/norm, pa/norm

    with col_viz:
        st.markdown("### 📊 VISUAL ANALYTICS")
        
        # Gráfico 1: Poisson Probability Curves (Plotly HD)
        fig = go.Figure()
        x_range = list(range(7))
        fig.add_trace(go.Scatter(x=x_range, y=[poisson.pmf(i, lh) for i in x_range], name=h_n, fill='tozeroy', line_color='#00E676', linewidth=3))
        fig.add_trace(go.Scatter(x=x_range, y=[poisson.pmf(i, la) for i in x_range], name=a_n, fill='tozeroy', line_color='#3B82F6', linewidth=3))
        fig.update_layout(title="GOAL PROBABILITY CURVES", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#FFFFFF", margin=dict(l=10,r=10,b=10,t=50), height=380, xaxis=dict(gridcolor='#1A1A1A'), yaxis=dict(gridcolor='#1A1A1A'))
        st.plotly_chart(fig, use_container_width=True)

        # Gráfico 2: Total Goals Probability (Plotly HD)
        hist_data = pd.DataFrame({'Golos': stot})
        hist_fig = px.histogram(hist_data, x='Golos', nbins=10, title="TOTAL GOALS PROBABILITY", color_discrete_sequence=['#FF1744'], opacity=0.8)
        hist_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#FFFFFF", margin=dict(l=10,r=10,b=10,t=40), height=280, showlegend=False, xaxis=dict(gridcolor='#1A1A1A'), yaxis=dict(gridcolor='#1A1A1A'))
        st.plotly_chart(hist_fig, use_container_width=True)

    with col_res:
        st.markdown("### 🧠 QUANTUM DECISION")
        
        # Mapeamento de Mercados
        mkts = [
            ("1X2: HOME", ph, m1, "WIN"), ("1X2: DRAW", px, mx, "DRAW"), ("1X2: AWAY", pa, m2, "WIN"),
            ("OVER 1.5", np.mean(stot>1.5), m_o15, "GOAL"), ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOAL"),
            ("UNDER 2.5", np.mean(stot<2.5), m_u25, "UNDER"), ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOAL"),
            ("DNB: HOME", ph/(ph+pa), m_hah, "PROT")
        ]
        
        # Advisor com Kelly Criterion (25% fracionário para segurança institucional)
        # KELLY = EDGE / (ODD - 1)
        recoms = sorted([(n, p, b, (p*b)-1, t) for n, p, b, t in mkts if (p*b)-1 > 0.05], key=lambda x: x[3], reverse=True)

        if recoms:
            # 🚀 O NOVO MEDIDOR BIOMÉTRICO GAUGE (A Estrela do Ecrã)
            name, p, b, edge, mtype = recoms[0]
            kelly = (edge / (b - 1)) * 0.25 # Gestão de Risco do Hedge Fund
            gauge_val = min(100, edge * 200) # Escala do Gauge para visibilidade
            
            # Gauge Color (Néon se for alto, Vermelho se for baixo)
            g_color = "#00E676" if edge > 0.15 else "#FFEA00" if edge > 0.05 else "#FF1744"

            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = gauge_val,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"{mtype}: {name}", 'font': {'size': 20, 'color': '#FFFFFF'}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#AAAAAA"},
                    'bar': {'color': g_color},
                    'bgcolor': "#111111",
                    'borderwidth': 2,
                    'bordercolor': "#222222",
                    'steps': [{'range': [0, 20], 'color': '#333333'}, {'range': [20, 100], 'color': '#111111'}],
                    'threshold': {'line': {'color': "#FFFFFF", 'width': 4}, 'thickness': 0.75, 'value': 90}
                },
                number = {'suffix': "%", 'font': {'size': 40, 'color': g_color}}
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FFFFFF", height=300, margin=dict(t=50, b=0, l=10, r=10))
            
            # Container Biométrico com Medidor e Stake
            st.markdown("<div class='biometric-container'>", unsafe_allow_html=True)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Stake Advisor (O Toque Final)
            st.markdown(f"""
            <div style='text-align:center; padding-bottom: 20px; font-family:\"JetBrains Mono\"'>
                <span style='color:#AAAAAA; font-size:14px;'>EDGE DETETADA</span><br>
                <span style='font-size:32px; font-weight:900; color:{g_color};'>{edge:+.1%}</span><br>
                <span style='color:#FFFFFF; font-size:16px;'>KELLY STAKE ADVISOR</span><br>
                <span style='font-size:24px; font-weight:900; color:#AAAAAA;'>{kelly:+.1%} DA BANCA</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Tabela Full Heatmap
        st.write("**DETALHE DO MERCADO**")
        table_data = []
        for n, p, b, _ in mkts:
            edge = (p * b) - 1
            ev_bg = "rgba(0, 230, 118, 0.15)" if edge > 0.10 else "rgba(255, 234, 0, 0.15)" if edge > 0 else "rgba(255, 23, 68, 0.10)"
            table_data.append({"MERCADO": n, "PROB": f"{p:.1%}", "JUSTA": f"{1/p:.2f}", "BOOKIE": f"<b>{b:.2f}</b>", "EV": f"<b>{edge:+.1%}</b>", "bg": ev_bg})
        
        df_res = pd.DataFrame(table_data)
        # Renderizar Tabela com Heatmap
        st.table(df_res.drop('bg', axis=1).style.apply(lambda r: [f"background-color: {table_data[r.name]['bg']}"] * len(r), axis=1))

    except Exception as e: st.error(f"ENGINE ERROR V52: {e}")
