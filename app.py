import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline Elite
st.set_page_config(page_title="STARLINE PRO", layout="wide")

# 2. CSS Profissional (Zero Overlap, Fundo Branco, Botões Coloridos)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    
    /* Blocos de Input com Sombra Suave */
    div[data-testid="stVerticalBlock"] > div { 
        background-color: white; border-radius: 12px; padding: 20px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 15px; 
    }
    
    /* Inputs Standard (Sem margens negativas) */
    .stNumberInput, .stTextInput, .stSelectbox { margin-bottom: 15px !important; }
    
    /* Botões de Ação */
    .stButton > button { width: 100%; border-radius: 8px; height: 3.5em; border: none; font-weight: 700; text-transform: uppercase; }
    
    /* ANALISAR: Verde Neon Sport */
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
    }
    
    /* CLEAR: Laranja/Vermelho Suave */
    .btn-clear > div > button {
        background: linear-gradient(135deg, #F87171 0%, #EF4444 100%) !important;
        color: white !important;
    }

    .ctx-alert {
        padding: 15px; background-color: #FFFBEB; border-left: 5px solid #F59E0B;
        color: #92400E; font-weight: bold; margin-bottom: 25px; border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# Função de Reset (Sem rerun conforme instrução)
def reset_starline():
    for key in st.session_state.keys():
        del st.session_state[key]

st.title("🏛️ STARLINE // OMNI-QUANT")
st.caption("Engine Version 26.0 • Pure Math • Elite Interface")

# --- WORKSPACE ---
col_in, col_out = st.columns([1.2, 2], gap="large")

with col_in:
    with st.form("main_form"):
        st.subheader("📋 Dados Estratégicos")
        v_ctx = st.selectbox("Contexto", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="f_ctx")
        
        c_h, c_a = st.columns(2)
        v_h_name = c_h.text_input("Home Team", value="LEIPZIG", key="f_hn").upper()
        v_a_name = c_a.text_input("Away Team", value="HOFFENHEIM", key="f_an").upper()
        
        st.markdown("**GF / GA (Últimos 5 Jogos)**")
        s1, s2, s3, s4 = st.columns(4)
        v_h_gf = s1.number_input("H-GF", value=8.0, key="f_hgf")
        v_h_ga = s2.number_input("H-GA", value=12.0, key="f_hga")
        v_a_gf = s3.number_input("A-GF", value=12.0, key="f_agf")
        v_a_ga = s4.number_input("A-GA", value=10.0, key="f_aga")
        
        st.markdown("**Odds de Mercado**")
        o1, ox, o2, ob = st.columns(4)
        m_o1, m_ox, m_o2, m_ob = o1.number_input("1", 1.88), ox.number_input("X", 4.00), o2.number_input("2", 3.35), ob.number_input("BTTS", 1.32)
        
        o15, o25, o35, h_h = st.columns(4)
        m_o15, m_o25, m_o35, m_hah = o15.number_input("+1.5", 1.10), o25.number_input("+2.5", 1.33), o35.number_input("+3.5", 1.78), h_h.number_input("DNB-H", 1.33)

        u15, u25, u35, h_a = st.columns(4)
        m_u15, m_u25, m_u35, m_haa = u15.number_input("-1.5", 4.55), u25.number_input("-2.5", 2.65), u35.number_input("-3.5", 1.75), h_a.number_input("DNB-A", 1.85)

        run_analysis = st.form_submit_button("⚡ Analisar Agora")

    st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
    st.button("🗑️ Clear Data", on_click=reset_starline)
    st.markdown('</div>', unsafe_allow_html=True)

# --- PROCESSAMENTO STARLINE ---
if run_analysis:
    try:
        # 1. Matemática Pura (Regra 1)
        v_adj = 0.67 if "Champions" in v_ctx else 1.0
        
        # Lambdas dependem apenas dos dados / 5
        l_h = ((v_h_gf / 5) * (v_a_ga / 5))**0.5
        l_a = ((v_a_gf * v_adj / 5) * (v_h_ga / 5))**0.5
        
        sim_h, sim_a = np.random.poisson(l_h, 100000), np.random.poisson(l_a, 100000)
        stot = sim_h + sim_a
        
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        n = ph + px + pa
        ph, px, pa = ph/n, px/n, pa/n

        with col_out:
            if v_adj < 1.0:
                st.markdown(f'<div class="ctx-alert">⚠️ FATOR PLAYOFF ATIVO: Ataque do {v_a_name} penalizado em 33%.</div>', unsafe_allow_html=True)
            
            st.subheader(f"📊 Relatório: {v_h_name} v {v_a_name}")
            
            mkts = [
                (f"1X2: {v_h_name}", ph, m_o1), ("1X2: DRAW", px, m_ox), (f"1X2: {v_a_name}", pa, m_o2),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob),
                (f"DNB: {v_h_name}", ph/(ph+pa), m_hah), (f"DNB: {v_a_name}", pa/(ph+pa), m_haa),
                ("OVER 1.5", np.mean(stot>1.5), m_o15), ("UNDER 1.5", np.mean(stot<1.5), m_u15),
                ("OVER 2.5", np.mean(stot>2.5), m_o25), ("UNDER 2.5", np.mean(stot<2.5), m_u25),
                ("OVER 3.5", np.mean(stot>3.5), m_o35), ("UNDER 3.5", np.mean(stot<3.5), m_u35)
            ]

            final_rows, ev_styles = [], []
            for name, prob, bookie in mkts:
                edge = (prob * bookie) - 1
                stake = max(0, (edge/(bookie-1)*5)) if bookie > 1 else 0
                
                # Regra 3: Técnica de Cor por Índice (Blindada)
                bg = "rgba(255, 255, 255, 0)"
                if edge > 0.08: bg = "rgba(0, 255, 149, 0.2)"
                elif edge > 0: bg = "rgba(255, 165, 0, 0.2)"
                ev_styles.append(bg)
                
                final_rows.append({
                    "MERCADO": name, "PROB": f"{prob:.1%}", "JUSTA": f"{1/prob:.2f}", 
                    "CASA": f"{bookie:.2f}", "EDGE": f"{edge:+.1%}", "STAKE": f"{stake:.1f}%"
                })

            df_res = pd.DataFrame(final_rows)
            
            # Aplicação de estilo sem colunas técnicas (Regra 3)
            def elite_heatmap(row):
                color = ev_styles[row.name]
                return [f'background-color: {color}; font-weight: bold' if color != "rgba(255, 255, 255, 0)" else ''] * len(row)

            st.table(df_res.style.apply(elite_heatmap, axis=1))

            st.markdown("---")
            st.write("**TOP PLACARES EXATOS**")
            hp, ap = poisson.pmf(range(6), l_h), poisson.pmf(range(6), l_a)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            scs = st.columns(5)
            for j in range(4, -1, -1):
                with scs[4-j]: st.metric(f"{idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e: st.error(f"ENGINE ERROR: {e}")
