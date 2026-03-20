import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline
st.set_page_config(page_title="STARLINE PRO", layout="wide")

# 2. CSS Estável (Branco, Profissional)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E293B; }
    div.stButton > button {
        background: #1E293B !important; color: white !important;
        font-weight: bold; width: 100%; border-radius: 4px; height: 3.5em; border: none;
    }
    .ctx-alert {
        padding: 15px; background-color: #FFFBEB; border-left: 5px solid #F59E0B;
        color: #92400E; font-weight: bold; margin-bottom: 20px; border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ STARLINE // OMNI-QUANT")

# --- LAYOUT ---
col_in, col_out = st.columns([1.2, 2], gap="large")

with col_in:
    st.subheader("📋 DADOS DE ENTRADA")
    ctx_choice = st.selectbox("CONTEXTO", ["Liga (Regular)", "Champions/Taça (Playoff)"])
    
    c_h, c_a = st.columns(2)
    h_name = c_h.text_input("HOME TEAM", "LEIPZIG").upper()
    a_name = c_a.text_input("AWAY TEAM", "HOFFENHEIM").upper()
    
    st.write("**ESTATÍSTICAS (ÚLTIMOS 5 JOGOS)**")
    s1, s2, s3, s4 = st.columns(4)
    v_h_gf, v_h_ga = s1.number_input("H-GF", value=8.0), s2.number_input("H-GA", value=12.0)
    v_a_gf, v_a_ga = s3.number_input("A-GF", value=12.0), s4.number_input("A-GA", value=10.0)
    
    st.write("**LIVE ODDS**")
    o_c1, o_c2, o_c3, o_c4 = st.columns(4)
    m_o1, m_ox, m_o2, m_obtts = o_c1.number_input("1", value=1.88), o_c2.number_input("X", value=4.00), o_c3.number_input("2", value=3.35), o_c4.number_input("BTTS", value=1.32)
    
    o_c5, o_c6, o_c7, o_c8 = st.columns(4)
    m_o15, m_o25, m_o35, m_ha0h = o_c5.number_input("+1.5", value=1.10), o_c6.number_input("+2.5", value=1.33), o_c7.number_input("+3.5", value=1.78), o_c8.number_input("DNB-H", value=1.33)

    o_c9, o_c10, o_c11, o_c12 = st.columns(4)
    m_u15, m_u25, m_u35, m_ha0a = o_c9.number_input("-1.5", value=4.55), o_c10.number_input("-2.5", value=2.65), o_c11.number_input("-3.5", value=1.75), o_c12.number_input("DNB-A", value=1.85)

    btn_run = st.button("⚡ GERAR RELATÓRIO STARLINE")

if btn_run:
    try:
        # Fator Playoff
        adj = 0.67 if "Champions" in ctx_choice else 1.0
        
        # Matemática Poisson Neutra
        lh = ((v_h_gf/5) * (v_a_ga/5))**0.5
        la = ((v_a_gf * adj / 5) * (v_h_ga/5))**0.5
        
        sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        stot = sim_h + sim_a
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            if adj < 1.0:
                st.markdown(f'<div class="ctx-alert">⚠️ MODO CHAMPIONS: Ataque do {a_name} reduzido em 33%.</div>', unsafe_allow_html=True)
            
            st.subheader(f"📊 REPORT: {h_name} v {a_name}")
            
            # Mercados V15 PRO (100% Blindados)
            mkts = [
                (f"1X2: {h_name}", ph, m_o1), ("1X2: DRAW", px, m_ox), (f"1X2: {a_name}", pa, m_o2),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_obtts), 
                (f"DNB: {h_name}", ph/(ph+pa), m_ha0h), (f"DNB: {a_name}", pa/(ph+pa), m_ha0a),
                ("OVER 1.5", np.mean(stot>1.5), m_o15), ("UNDER 1.5", np.mean(stot<1.5), m_u15),
                ("OVER 2.5", np.mean(stot>2.5), m_o25), ("UNDER 2.5", np.mean(stot<2.5), m_u25),
                ("OVER 3.5", np.mean(stot>3.5), m_o35), ("UNDER 3.5", np.mean(stot<3.5), m_u35)
            ]

            data_list = []
            ev_scores = [] # Lista separada para guardar as Edges
            
            for n, p, b in mkts:
                edge = (p * b) - 1
                stk = max(0, (edge/(b-1)*5)) if b > 1 else 0
                
                # Definir a cor teórica (mas sem colocar no DataFrame final)
                bg_color = "rgba(255, 255, 255, 0)"
                if edge > 0.08: bg_color = "rgba(0, 255, 149, 0.2)" # Verde
                elif edge > 0: bg_color = "rgba(255, 165, 0, 0.2)"  # Laranja
                ev_scores.append(bg_color)
                
                data_list.append({
                    "MERCADO": n, "PROB": f"{p:.1%}", "JUSTA": f"{1/p:.2f}", 
                    "CASA": f"{b:.2f}", "EDGE": f"{edge:+.1%}", "STAKE": f"{stk:.1f}%"
                })

            # DataFrame LIMPO (Sem color_ref)
            df = pd.DataFrame(data_list)
            
            # --- NOVA TÉCNICA DE COR (Estilo Dinâmico por Índice) ---
            def apply_dynamic_bg(row):
                # O índice do DataFrame corresponde à posição na lista 'ev_scores'
                color = ev_scores[row.name] 
                return [f'background-color: {color}'] * len(row)

            # Renderização da Tabela com Estilo (Heatmap Ativado, Zero Erros)
            st.table(df.style.apply(apply_dynamic_bg, axis=1))

            st.markdown("---")
            st.write("**TOP 5 PLACARES EXATOS:**")
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            scs = st.columns(5)
            for j in range(4, -1, -1):
                with scs[4-j]: st.metric(f"{idx[0][j]} - {idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e:
        st.error(f"ENGINE ERROR V24.1: {e}")
