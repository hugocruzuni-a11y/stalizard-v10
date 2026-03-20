import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline Elite
st.set_page_config(page_title="STARLINE DEEP ADVISOR", layout="wide")

# 2. CSS Profissional Advisor
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1rem; max-width: 95%; }

    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 12px !important;
    }
    
    .btn-run > div > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important; font-weight: 700; height: 3.5em; width: 100%; border-radius: 6px; border: none;
    }
    .btn-clear > div > button {
        background: linear-gradient(135deg, #F87171 0%, #EF4444 100%) !important;
        color: white !important; font-weight: 700; height: 3.5em; width: 100%; border-radius: 6px; border: none;
    }

    .advice-card {
        padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid; font-size: 0.9rem;
    }
    .val-prestige { background-color: #ECFDF5; border-color: #10B981; color: #065F46; } 
    .val-context { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E; }  
    </style>
    """, unsafe_allow_html=True)

def reset_starline():
    for key in st.session_state.keys():
        del st.session_state[key]

st.markdown("### 🏛️ **STARLINE** // OMNI-QUANT <span style='font-size:12px; color:#94A3B8'>V32.0 DEEP LOGIC</span>", unsafe_allow_html=True)
st.markdown("---")

col_in, col_out = st.columns([1.2, 2], gap="large")

with col_in:
    ctx = st.selectbox("CONTEXTO", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx")
    c1, c2 = st.columns(2)
    h_n = c1.text_input("HOME", value="LEIPZIG", key="h_n").upper()
    a_n = c2.text_input("AWAY", value="HOFFENHEIM", key="a_n").upper()
    
    st.write("**STATS GF/GA**")
    s1, s2, s3, s4 = st.columns(4)
    v_hgf, v_hga, v_agf, v_aga = s1.number_input("H-GF", 8.0), s2.number_input("H-GA", 12.0), s3.number_input("A-GF", 12.0), s4.number_input("A-GA", 10.0)
    
    st.write("**LIVE ODDS**")
    o1, ox, o2, ob = st.columns(4)
    m_o1, m_ox, m_o2, m_ob = o1.number_input("1", 1.88), ox.number_input("X", 4.00), o2.number_input("2", 3.35), ob.number_input("BTTS", 1.32)
    
    o15, o25, o35, hah = st.columns(4)
    m_o15, m_o25, m_o35, m_hah = o15.number_input("+1.5", 1.10), o25.number_input("+2.5", 1.33), o35.number_input("+3.5", 1.78), hah.number_input("DNB-H", 1.33)
    u15, u25, u35, haa = st.columns(4)
    m_u15, m_u25, m_u35, m_haa = u15.number_input("-1.5", 4.55), u25.number_input("-2.5", 2.65), u35.number_input("-3.5", 1.75), haa.number_input("DNB-A", 1.85)

    st.markdown('<div class="btn-run">', unsafe_allow_html=True)
    btn_run = st.button("⚡ EXECUTAR DEEP ADVISOR")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
    st.button("🗑️ CLEAR DATA", on_click=reset_starline)
    st.markdown('</div>', unsafe_allow_html=True)

if btn_run:
    try:
        adj = 0.67 if "Champions" in ctx else 1.0
        lh, la = ((v_hgf/5)*(v_aga/5))**0.5, ((v_agf*adj/5)*(v_hga/5))**0.5
        sim_h, sim_a = np.random.poisson(lh, 100000), np.random.poisson(la, 100000)
        stot = sim_h + sim_a
        
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_out:
            st.subheader("🎯 STARLINE DEEP ADVISOR: RECOMENDAÇÕES")
            
            # --- MOTOR DE RECOMENDAÇÃO MÚLTIPLA ---
            all_options = [
                (f"1X2: {h_n}", ph, m_o1, "VENCEDOR"), (f"1X2: {a_n}", pa, m_o2, "VENCEDOR"),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOLOS"),
                ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOLOS"),
                ("OVER 1.5", np.mean(stot>1.5), m_o15, "GOLOS"),
                ("DNB: HOME", ph/(ph+pa), m_hah, "PROTEÇÃO"),
                ("DNB: AWAY", pa/(ph+pa), m_haa, "PROTEÇÃO")
            ]
            
            # Filtrar por Edge Positiva
            recoms = []
            for n, p, b, t in all_options:
                edge = (p * b) - 1
                if edge > 0.02: # Mínimo 2% de Edge para aparecer no Advisor
                    recoms.append((n, p, b, edge, t))
            
            recoms = sorted(recoms, key=lambda x: x[3], reverse=True)

            if not recoms:
                st.info("⚠️ Sem Edge clara detectada. Mercado muito ajustado.")
            else:
                for n, p, b, e, t in recoms[:3]: # Mostra as 3 melhores
                    icon = "💎" if e > 0.10 else "✅"
                    st.markdown(f"""
                    <div class="advice-card val-prestige">
                        {icon} <b>{t}: {n}</b><br>
                        Edge: <b>{e:+.1%}</b> | Odd: <b>{b:.2f}</b> (Justa: {1/p:.2f})
                    </div>
                    """, unsafe_allow_html=True)

            # Tabela Completa
            data_list, styles = [], []
            for n, p, b, _ in all_options:
                edge = (p * b) - 1
                bg = "rgba(0, 255, 149, 0.15)" if edge > 0.08 else "rgba(255, 165, 0, 0.15)" if edge > 0 else "none"
                styles.append(bg)
                data_list.append({"MERCADO": n, "PROB": f"{p:.1%}", "JUSTA": f"{1/p:.2f}", "CASA": f"{b:.2f}", "EDGE": f"{edge:+.1%}"})

            st.table(pd.DataFrame(data_list).style.apply(lambda r: [f'background-color: {styles[r.name]}'] * len(r), axis=1))

            # PlacaRES
            hp, ap = poisson.pmf(range(6), lh), poisson.pmf(range(6), la)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            scs = st.columns(5)
            for j in range(4, -1, -1):
                with scs[4-j]: st.metric(f"{idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")

    except Exception as e: st.error(f"ENGINE ERROR: {e}")
