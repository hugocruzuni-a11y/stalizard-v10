import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import matplotlib.pyplot as plt

# 1. Configuração Ultra (Full Width Macbook)
st.set_page_config(page_title="STARLINE ULTRA V41", layout="wide")

# 2. CSS Prestige
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    .block-container { padding: 1.5rem 3rem !important; max-width: 100% !important; }
    
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important; border-radius: 6px !important; 
    }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        font-size: 0.65rem !important; font-weight: 800 !important; color: #64748B !important; text-transform: uppercase;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #064E3B 0%, #065F46 100%) !important;
        color: white !important; font-weight: 800; height: 3.5em; width: 100%; border-radius: 8px; border: none;
        box-shadow: 0 4px 12px rgba(6, 78, 59, 0.2); margin-top: 15px;
    }

    .advice-card {
        padding: 15px 20px; border-radius: 10px; margin-bottom: 12px; border-left: 6px solid;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); font-size: 0.9rem;
    }
    .val-win { background-color: #ECFDF5; border-color: #059669; color: #064E3B; } 
    .val-strat { background-color: #F0F9FF; border-color: #0EA5E9; color: #075985; }
    .val-warn { background-color: #FFFBEB; border-color: #D97706; color: #78350F; }

    .stTable { font-size: 0.82rem !important; border-radius: 10px !important; overflow: hidden; border: 1px solid #E2E8F0; }
    thead tr th { background-color: #F8FAFC !important; color: #1E293B !important; font-weight: 800 !important; border-bottom: 2px solid #E2E8F0 !important; }
    </style>
    """, unsafe_allow_html=True)

def reset_engine():
    for key in list(st.session_state.keys()): del st.session_state[key]

st.markdown("<h3 style='color:#1E293B; font-weight:800; margin: 0; letter-spacing:-1px;'>🏛️ STARLINE // OMNI-QUANT <span style='color:#059669; font-size:12px;'>V41.0 UNDER-SCANNER 1M</span></h3>", unsafe_allow_html=True)
st.markdown("---")

col_in, col_mid, col_res = st.columns([1, 1.2, 1.3], gap="large")

with col_in:
    ctx = st.selectbox("ESTRATÉGIA", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx_v41")
    ch, ca = st.columns(2)
    h_n = ch.text_input("HOME", value="VILLARREAL", key="hn").upper()
    a_n = ca.text_input("AWAY", value="REAL SOCIEDAD", key="an").upper()
    
    st.markdown("**STATS GF/GA (5 JOGOS)**")
    s1, s2, s3, s4 = st.columns(4)
    v_hgf = s1.number_input("H-GF", 9.0); v_hga = s2.number_input("H-GA", 7.0)
    v_agf = s3.number_input("A-GF", 12.0); v_aga = s4.number_input("A-GA", 10.0)
    
    st.markdown("**LIVE ODDS INPUT**")
    o1, ox, o2 = st.columns(3)
    m_o1, m_ox, m_o2 = o1.number_input("1", 1.88), ox.number_input("X", 4.00), o2.number_input("2", 3.35)
    
    o15, o25, u25 = st.columns(3)
    m_o15, m_o25, m_u25 = o15.number_input("+1.5", 1.10), o25.number_input("+2.5", 1.33), u25.number_input("-2.5", 2.65)
    
    hah, haa, ob = st.columns(3)
    m_hah, m_haa, m_ob = hah.number_input("DNB-H", 1.33), haa.number_input("DNB-A", 1.85), ob.number_input("BTTS", 1.32)

    run = st.button("🚀 EXECUTAR UNDER-SCAN 1.000.000")
    st.button("🗑️ RESET ENGINE", on_click=reset_engine)

if run:
    try:
        # Matemática 1M com Vetorização
        adj = 0.67 if "Champions" in ctx else 1.0
        lh, la = ((v_hgf/5)*(v_aga/5))**0.5, ((v_agf*adj/5)*(v_hga/5))**0.5
        sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
        stot = sim_h + sim_a
        
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph+px+pa; ph, px, pa = ph/norm, px/norm, pa/norm

        with col_mid:
            st.markdown("#### 📊 DENSIDADE DE GOLOS")
            fig, ax = plt.subplots(figsize=(6, 5), dpi=110)
            x_range = np.arange(0, 7)
            ax.fill_between(x_range, poisson.pmf(x_range, lh), color='#10B981', alpha=0.15, label=f"Prob {h_n}")
            ax.plot(x_range, poisson.pmf(x_range, lh), color='#10B981', marker='o', linewidth=2)
            ax.fill_between(x_range, poisson.pmf(x_range, la), color='#0EA5E9', alpha=0.15, label=f"Prob {a_n}")
            ax.plot(x_range, poisson.pmf(x_range, la), color='#0EA5E9', marker='o', linewidth=2)
            ax.set_title("EXPECTATIVA POISSON (V41)", fontsize=10, fontweight='800')
            ax.legend(fontsize=8); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            st.pyplot(fig)

            # Gráfico de Barras de Golos Totais (Para visualizar Unders)
            fig2, ax2 = plt.subplots(figsize=(6, 3))
            counts, bins = np.histogram(stot, bins=np.arange(8))
            ax2.bar(bins[:-1], counts/1000000, color='#64748B', alpha=0.7)
            ax2.set_title("Probabilidade de Golos Totais (Jogo)", fontsize=9)
            st.pyplot(fig2)

        with col_res:
            st.markdown("#### 💎 UNDER & VALUE SCAN")
            
            # Mercados Focados em Under e 1X2
            mkt_data = [
                ("1X2: HOME", ph, m_o1, "VITÓRIA"),
                ("1X2: DRAW", px, m_ox, "EMPATE"),
                ("1X2: AWAY", pa, m_o2, "VITÓRIA"),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob, "GOLOS"),
                ("UNDER 0.5", np.mean(stot<0.5), 10.0, "UNDER"),
                ("UNDER 1.5", np.mean(stot<1.5), 4.50, "UNDER"),
                ("UNDER 2.5", np.mean(stot<2.5), m_u25, "UNDER"),
                ("UNDER 3.5", np.mean(stot<3.5), 1.50, "UNDER"),
                ("UNDER 4.5", np.mean(stot<4.5), 1.15, "UNDER"),
                ("OVER 2.5", np.mean(stot>2.5), m_o25, "GOLOS"),
                ("DNB: HOME", ph/(ph+pa), m_hah, "PROTEÇÃO"),
                ("DNB: AWAY", pa/(ph+pa), m_haa, "PROTEÇÃO")
            ]
            
            recoms = sorted([(n, p, b, (p*b)-1, t) for n, p, b, t in mkt_data if (p*b)-1 > 0.04], key=lambda x: x[3], reverse=True)
            for n, p, b, e, t in recoms[:3]:
                style = "val-win" if "VITÓRIA" in n else "val-strat" if "UNDER" in n else "val-warn"
                st.markdown(f'<div class="advice-card {style}">🚀 <b>{n}</b><br>Confiança: {p:.1%} | Edge: {e:+.1%}</div>', unsafe_allow_html=True)

            st.write("**VARREDURA COMPLETA**")
            df_final = []
            for n, p, b, _ in mkt_data:
                edge = (p * b) - 1
                bg = "rgba(16, 185, 129, 0.12)" if edge > 0.08 else "rgba(245, 158, 11, 0.12)" if edge > 0 else "none"
                df_final.append({"MERCADO": n, "PROB": f"{p:.1%}", "JUSTA": f"{1/p:.2f}", "CASA": f"{b:.2f}", "EDGE": f"{edge:+.1%}", "bg": bg})
            
            df_res = pd.DataFrame(df_final)
            st.table(df_res.drop('bg', axis=1).style.apply(lambda r: [f"background-color: {df_final[r.name]['bg']}"] * len(r), axis=1))

    except Exception as e: st.error(f"ENGINE ERROR V41: {e}")
