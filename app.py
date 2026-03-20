import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline Ultra
st.set_page_config(page_title="STARLINE", layout="wide")

# 2. CSS Elite (Fundo Branco, Design Advisor)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1.5rem !important; max-width: 96%; }
    
    .stNumberInput, .stTextInput, .stSelectbox { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; }
    
    /* Botão Ultra Verde Esmeralda */
    div.stButton > button {
        background: linear-gradient(135deg, #064E3B 0%, #065F46 100%) !important;
        color: white !important; font-weight: 800; height: 3.5em; width: 100%; border: none; border-radius: 8px;
        box-shadow: 0 4px 12px rgba(6, 78, 59, 0.2);
    }
    
    .advice-card {
        padding: 15px 20px; border-radius: 10px; margin-bottom: 12px; border-left: 6px solid;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03); font-size: 0.9rem;
    }
    .val-ultra { background-color: #ECFDF5; border-color: #059669; color: #064E3B; }
    .val-warn { background-color: #FFFBEB; border-color: #D97706; color: #78350F; }
    </style>
    """, unsafe_allow_html=True)

def reset_ultra():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

st.markdown("<h2 style='color:#1E293B; font-weight:800; margin-bottom:0;'>🏛️ STARLINE // By Cruz <span style='color:#059669; font-size:14px;'>V1.ULTRA</span></h2>", unsafe_allow_html=True)
st.markdown("---")

col_in, col_out = st.columns([1.1, 2], gap="large")

with col_in:
    ctx = st.selectbox("ESTRATÉGIA", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx")
    
    c1, c2 = st.columns(2)
    h_n = c1.text_input("HOME", value="LEIPZIG", key="h_n").upper()
    a_n = c2.text_input("AWAY", value="HOFFENHEIM", key="a_n").upper()
    
    st.write("**STATS GF/GA**")
    s1, s2, s3, s4 = st.columns(4)
    v_hgf, v_hga, v_agf, v_aga = s1.number_input("H-GF", ), s2.number_input("H-GA", ), s3.number_input("A-GF", ), s4.number_input("A-GA", )
    
    st.write("**LIVE ODDS**")
    g1 = st.columns(4)
    m_o1, m_ox, m_o2, m_ob = g1[0].number_input("1", ), g1[1].number_input("X", ), g1[2].number_input("2", ), g1[3].number_input("BTTS", )
    
    g2 = st.columns(4)
    m_o15, m_o25, m_o35, m_hah = g2[0].number_input("+1.5", ), g2[1].number_input("+2.5", ), g2[2].number_input("+3.5", ), g2[3].number_input("DNB-H", )

    g3 = st.columns(4)
    m_u15, m_u25, m_u35, m_haa = g3[0].number_input("-1.5", ), g3[1].number_input("-2.5", ), g3[2].number_input("-3.5", ), g3[3].number_input("DNB-A", )

    btn_run = st.button("🚀 EXECUTAR")
    st.button("🗑️ RESET ENGINE", on_click=reset_ultra)

if btn_run:
    try:
        # --- MATEMÁTICA ULTRA V34.1 ---
        adj = 0.67 if "Champions" in ctx else 1.0
        lh = ((v_hgf/5) * (v_aga/5))**0.5
        la = ((v_agf * adj / 5) * (v_hga/5))**0.5
        
        # 1 Milhão de Simulações
        sim_h = np.random.poisson(lh, 1000000)
        sim_a = np.random.poisson(la, 1000000)
        stot = sim_h + sim_a
        
        ph = np.mean(sim_h > sim_a)
        px = np.mean(sim_h == sim_a)
        pa = np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            st.markdown("#### 🎯 ULTRA ADVISOR")
            
            # Mercados para análise (Corrigido para 5 elementos por tuplo)
            targets = [
                (f"1X2: {h_n}", ph, m_o1, "VITÓRIA", "1X2"),
                (f"1X2: {a_n}", pa, m_o2, "VITÓRIA", "1X2"),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOLOS", "BTTS"),
                ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOLOS", "O/U"),
                ("DNB: HOME", ph/(ph+pa), m_hah, "PROTEÇÃO", "DNB"),
                ("DNB: AWAY", pa/(ph+pa), m_haa, "PROTEÇÃO", "DNB")
            ]
            
            # Advisor Logic
            recoms = []
            for name, p, b, cat, m_type in targets:
                edge = (p * b) - 1
                if edge > 0.04: # Filtro de 4% de Edge para nível Ultra
                    recoms.append((name, p, b, edge, cat))
            
            recoms = sorted(recoms, key=lambda x: x[3], reverse=True)

            if recoms:
                for n, p, b, e, t in recoms[:3]:
                    st.markdown(f"""
                    <div class="advice-card val-ultra">
                        🚀 <b>{t}: {n}</b><br>
                        Confiança: <b>{p:.1%}</b> | Edge: <b>{e:+.1%}</b> | Odd: <b>{b:.2f}</b>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="advice-card val-warn">🛑 MERCADO AJUSTADO: Sem valor claro acima de 4% em 1M de ciclos.</div>', unsafe_allow_html=True)

            # Tabela (Incluindo todos os mercados para o heatmap)
            full_list = targets + [("1X2: DRAW", px, m_ox, "EMPATE", "1X2"), ("OVER 1.5", np.mean(stot>1.5), m_o15, "GOLOS", "O/U")]
            res_data, styles = [], []
            for n, p, b, _, _ in full_list:
                edge = (p * b) - 1
                bg = "rgba(5, 150, 105, 0.15)" if edge > 0.10 else "rgba(245, 158, 11, 0.15)" if edge > 0 else "none"
                styles.append(bg)
                res_data.append({"MERCADO": n, "PROB %": f"{p:.1%}", "FAIR": f"{1/p:.2f}", "CASA": f"{b:.2f}", "EDGE": f"{edge:+.1%}"})

            st.table(pd.DataFrame(res_data).style.apply(lambda r: [f'background-color: {styles[r.name]}'] * len(r), axis=1))

            # Scores Exatos
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            mtx[0,0] *= 1.12; mtx[1,1] *= 1.08 # Dixon-Coles Correction V34
            mtx /= mtx.sum()
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            scs = st.columns(5)
            for j in range(4, -1, -1):
                with scs[4-j]: st.metric(f"{idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e:
        st.error(f"ENGINE ERROR V34.1: {e}")
