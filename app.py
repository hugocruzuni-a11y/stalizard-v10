iimport streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração de Página Starline
st.set_page_config(page_title="STARLINE PRO", layout="wide")

# 2. Design Profissional (Fundo Branco e Tabelas Limpas)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    div.stButton > button {
        background: #1E293B !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
        border-radius: 4px;
        height: 3.5em;
        margin-top: 10px;
        border: none;
    }
    /* Estilo para ocultar índices da tabela e limpar bordas */
    .stTable { background-color: white; border-radius: 8px; }
    .ctx-alert {
        padding: 15px; background-color: #FFFBEB; border-left: 5px solid #F59E0B;
        color: #92400E; font-weight: bold; margin-bottom: 20px; border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ STARLINE // OMNI-QUANT")

# --- ÁREA DE INPUT ---
col_in, col_out = st.columns([1.2, 2], gap="large")

with col_in:
    st.subheader("📋 DADOS DE ENTRADA")
    ctx_choice = st.selectbox("CONTEXTO", ["Liga (Regular)", "Champions/Taça (Playoff)"])
    
    c_h, c_a = st.columns(2)
    h_name = c_h.text_input("HOME TEAM", "LEIPZIG").upper()
    a_name = c_a.text_input("AWAY TEAM", "HOFFENHEIM").upper()
    
    st.write("**GF / GA STATS (5-GAME AVG)**")
    s1, s2, s3, s4 = st.columns(4)
    v_h_gf, v_h_ga, v_a_gf, v_a_ga = s1.number_input("H-GF", value=8.0), s2.number_input("H-GA", value=12.0), s3.number_input("A-GF", value=12.0), s4.number_input("A-GA", value=10.0)
    
    st.write("**LIVE MARKET ODDS**")
    o_c1, o_c2, o_c3, o_c4 = st.columns(4)
    m_o1, m_ox, m_o2, m_obtts = o_c1.number_input("1", value=1.88), o_c2.number_input("X", value=4.00), o_c3.number_input("2", value=3.35), o_c4.number_input("BTTS", value=1.32)
    
    o_c5, o_c6, o_c7, o_c8 = st.columns(4)
    m_o15, m_o25, m_o35, m_ha0h = o_c5.number_input("+1.5", value=1.10), o_c6.number_input("+2.5", value=1.33), o_c7.number_input("+3.5", value=1.78), o_c8.number_input("DNB-H", value=1.33)

    o_c9, o_c10, o_c11, o_c12 = st.columns(4)
    m_u15, m_u25, m_u35, m_ha0a = o_c9.number_input("-1.5", value=4.55), o_c10.number_input("-2.5", value=2.65), o_c11.number_input("-3.5", value=1.75), o_c12.number_input("DNB-A", value=1.85)

    btn_run = st.button("⚡ ANALISAR AGORA")

# --- LÓGICA E PROCESSAMENTO ---
if btn_run:
    try:
        # Fator Champions (Penalização de 33% no ataque fora em jogos eliminatórios)
        adj = 0.67 if "Champions" in ctx_choice else 1.0
        
        # Matemática Poisson (Calibrada)
        lh = ((float(v_h_gf)/5)*(float(v_a_ga)/5))**0.5 * 1.12
        la = ((float(v_a_gf) * adj / 5)*(float(v_h_ga)/5))**0.5 * 0.90
        
        sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        stot = sim_h + sim_a
        
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            if adj < 1.0:
                st.markdown(f'<div class="ctx-alert">⚠️ FATOR PLAYOFF: Ataque do {a_name} reduzido para contexto de Champions/Taça.</div>', unsafe_allow_html=True)
            
            st.subheader(f"📊 REPORT: {h_name} v {a_name}")
            
            # LISTA INTEGRAL DE MERCADOS (12)
            mkts = [
                (f"1X2: {h_name}", ph, m_o1), 
                ("1X2: DRAW", px, m_ox), 
                (f"1X2: {a_name}", pa, m_o2),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_obtts), 
                (f"DNB: {h_name}", ph/(ph+pa), m_ha0h), 
                (f"DNB: {a_name}", pa/(ph+pa), m_ha0a),
                ("OVER 1.5", np.mean(stot>1.5), m_o15), 
                ("UNDER 1.5", np.mean(stot<1.5), m_u15),
                ("OVER 2.5", np.mean(stot>2.5), m_o25), 
                ("UNDER 2.5", np.mean(stot<2.5), m_u25),
                ("OVER 3.5", np.mean(stot>3.5), m_o35), 
                ("UNDER 3.5", np.mean(stot<3.5), m_u35)
            ]

            data_list = []
            for name, prob, bookie in mkts:
                edge = (prob * bookie) - 1
                stk = max(0, (edge/(bookie-1)*5)) if bookie > 1 else 0
                
                # Definir cor técnica
                bg_c = "none"
                if edge > 0.08: bg_c = "rgba(0, 255, 149, 0.2)" # Verde
                elif edge > 0: bg_c = "rgba(255, 165, 0, 0.2)"  # Laranja
                
                data_list.append({
                    "MERCADO": name, "PROB %": f"{prob:.1%}", "JUSTA": f"{1/prob:.2f}", 
                    "CASA": f"{bookie:.2f}", "EDGE": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%",
                    "c_ref": bg_c
                })

            # DataFrame e Estilização
            df = pd.DataFrame(data_list)
            
            def apply_bg(row):
                return [f'background-color: {row["c_ref"]}'] * len(row)

            # Renderização Final (Escondendo a coluna de cor e o índice)
            st.table(df.style.apply(apply_bg, axis=1).hide(subset=["c_ref"], axis=1))

            st.markdown("---")
            st.write("**TOP 5 PLACARES EXATOS:**")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            
            sc_cols = st.columns(5)
            for j in range(4, -1, -1):
                with sc_cols[4-j]:
                    st.metric(f"{idx[0][j]} - {idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e:
        st.error(f"Erro no processamento: {e}")
