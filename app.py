import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import matplotlib.pyplot as plt

# 1. Configuração Ultra (Full Macbook Width)
st.set_page_config(page_title="STARLINE ULTRA V43", layout="wide")

# 2. CSS Elite Prestige - Design e Estabilidade Visual
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    .block-container { padding: 1.5rem 2rem 0rem 3rem !important; max-width: 100% !important; }
    
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important; border-radius: 6px !important; 
    }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        font-size: 0.65rem !important; font-weight: 800 !important; color: #64748B !important; text-transform: uppercase;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #111827 0%, #1F2937 100%) !important;
        color: white !important; font-weight: 800; height: 3.5em; width: 100%; border-radius: 8px; border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-top: 15px;
    }

    .advice-card {
        padding: 15px 20px; border-radius: 10px; margin-bottom: 12px; border-left: 6px solid;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); font-size: 0.9rem;
    }
    .val-win { background-color: #ECFDF5; border-color: #059669; color: #064E3B; } 
    .val-strat { background-color: #F0F9FF; border-color: #0EA5E9; color: #075985; }
    .val-neutral { background-color: #F8FAFC; border-color: #94A3B8; color: #475569; }

    .stTable { font-size: 0.82rem !important; border-radius: 10px !important; overflow: hidden; border: 1px solid #E2E8F0; }
    thead tr th { background-color: #F8FAFC !important; color: #1E293B !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

def reset_engine():
    for key in list(st.session_state.keys()): del st.session_state[key]

st.markdown("<h3 style='color:#1E293B; font-weight:800; margin: 0;'>🏛️ STARLINE // OMNI-QUANT <span style='color:#059669; font-size:12px;'>V43.0 TOTAL SCANNER 1M</span></h3>", unsafe_allow_html=True)
st.markdown("---")

col_in, col_mid, col_res = st.columns([1.1, 1.2, 1.3], gap="large")

with col_in:
    ctx = st.selectbox("ESTRATÉGIA", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="v43_ctx")
    
    ch, ca = st.columns(2)
    h_n = ch.text_input("HOME TEAM", value="VILLARREAL", key="v43_hn").upper()
    a_n = ca.text_input("AWAY TEAM", value="REAL SOCIEDAD", key="v43_an").upper()
    
    st.markdown("<p style='font-size:10px; font-weight:800; color:#64748B; margin-top:10px;'>MÉDIAS GF/GA</p>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    v_hgf = s1.number_input("H-GF", value=9.0, key="v43_hgf")
    v_hga = s2.number_input("H-GA", value=7.0, key="v43_hga")
    v_agf = s3.number_input("A-GF", value=12.0, key="v43_agf")
    v_aga = s4.number_input("A-GA", value=10.0, key="v43_aga")
    
    st.markdown("<p style='font-size:10px; font-weight:800; color:#64748B; margin-top:10px;'>ODDS MERCADO (VALORES REAIS)</p>", unsafe_allow_html=True)
    o1, ox, o2 = st.columns(3)
    m_o1 = o1.number_input("ODD 1", value=1.88, key="v43_o1")
    m_ox = ox.number_input("ODD X", value=4.00, key="v43_ox")
    m_o2 = o2.number_input("ODD 2", value=3.35, key="v43_o2")
    
    o15, o25, o35 = st.columns(3)
    m_o15 = o15.number_input("+1.5", value=1.10, key="v43_o15")
    m_o25 = o25.number_input("+2.5", value=1.33, key="v43_o25")
    m_o35 = o35.number_input("+3.5", value=1.78, key="v43_o35")
    
    u15, u25, u35 = st.columns(3)
    m_u15 = u15.number_input("-1.5", value=4.50, key="v43_u15")
    m_u25 = u25.number_input("-2.5", value=2.65, key="v43_u25")
    m_u35 = u35.number_input("-3.5", value=1.50, key="v43_u35")
    
    hah, haa, ob = st.columns(3)
    m_hah = hah.number_input("DNB-H", value=1.33, key="v43_hah")
    m_haa = haa.number_input("DNB-A", value=1.85, key="v43_haa")
    m_ob = ob.number_input("BTTS", value=1.32, key="v43_ob")

    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTAR TOTAL SCANNER 1M")
    st.button("🗑️ RESET ENGINE", on_click=reset_engine)

if run:
    try:
        adj = 0.67 if "Champions" in ctx else 1.0
        lh = max(0.01, ((v_hgf/5)*(v_aga/5))**0.5)
        la = max(0.01, ((v_agf*adj/5)*(v_hga/5))**0.5)
        
        sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
        stot = sim_h + sim_a
        
        ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
        norm = ph + px + pa; ph, px, pa = ph/norm, px/norm, pa/norm

        with col_mid:
            st.markdown("#### 📊 ANALYTICS")
            fig, ax = plt.subplots(figsize=(6, 5), dpi=110)
            xr = np.arange(0, 7)
            ax.fill_between(xr, poisson.pmf(xr, lh), color='#10B981', alpha=0.15)
            ax.plot(xr, poisson.pmf(xr, lh), color='#10B981', marker='o', label=h_n)
            ax.fill_between(xr, poisson.pmf(xr, la), color='#0EA5E9', alpha=0.15)
            ax.plot(xr, poisson.pmf(xr, la), color='#0EA5E9', marker='o', label=a_n)
            ax.set_title("EXPECTATIVA DE GOLOS", fontsize=10, fontweight='800')
            ax.legend(fontsize=8); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            st.pyplot(fig)

            fig2, ax2 = plt.subplots(figsize=(6, 3))
            ax2.hist(stot, bins=np.arange(9)-0.5, density=True, color='#64748B', alpha=0.6, rwidth=0.8)
            ax2.set_title("Frequência de Golos Totais", fontsize=9)
            st.pyplot(fig2)

        with col_res:
            st.markdown("#### 💎 ADVISOR & TOTAL VALUE")
            
            # Mapeamento Completo de Mercados (Overs + Unders + 1X2)
            raw_mkts = [
                {"n": "1X2: HOME", "p": ph, "b": m_o1, "t": "WIN"},
                {"n": "1X2: DRAW", "p": px, "b": m_ox, "t": "DRAW"},
                {"n": "1X2: AWAY", "p": pa, "b": m_o2, "t": "WIN"},
                {"n": "OVER 1.5", "p": np.mean(stot > 1.5), "b": m_o15, "t": "OVER"},
                {"n": "OVER 2.5", "p": np.mean(stot > 2.5), "b": m_o25, "t": "OVER"},
                {"n": "OVER 3.5", "p": np.mean(stot > 3.5), "b": m_o35, "t": "OVER"},
                {"n": "UNDER 1.5", "p": np.mean(stot < 1.5), "b": m_u15, "t": "UNDER"},
                {"n": "UNDER 2.5", "p": np.mean(stot < 2.5), "b": m_u25, "t": "UNDER"},
                {"n": "UNDER 3.5", "p": np.mean(stot < 3.5), "b": m_u35, "t": "UNDER"},
                {"n": "BTTS: YES", "p": np.mean((sim_h>0)&(sim_a>0)), "b": m_ob, "t": "GOAL"},
                {"n": "DNB: HOME", "p": ph/(ph+pa), "b": m_hah, "t": "PROT"},
                {"n": "DNB: AWAY", "p": pa/(ph+pa), "b": m_haa, "t": "PROT"}
            ]
            
            # Advisor Logic
            recoms = sorted([(m['n'], m['p'], m['b'], (m['p']*m['b'])-1, m['t']) for m in raw_mkts if (m['p']*m['b'])-1 > 0.05], key=lambda x: x[3], reverse=True)
            if recoms:
                for name, p, b, edge, mtype in recoms[:3]:
                    s_cls = "val-win" if mtype == "WIN" else "val-strat"
                    st.markdown(f'<div class="advice-card {s_cls}">🚀 <b>{name}</b><br>Edge: {edge:+.1%} | Odd: {b:.2f}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="advice-card val-neutral">🛑 Sem Edge superior a 5%.</div>', unsafe_allow_html=True)

            # Tabela Full
            df_list = []
            for m in raw_mkts:
                edge = (m['p'] * m['b']) - 1
                bg = "rgba(16, 185, 129, 0.12)" if edge > 0.08 else "rgba(245, 158, 11, 0.12)" if edge > 0 else "none"
                df_list.append({"MERCADO": m['n'], "PROB": f"{m['p']:.1%}", "JUSTA": f"{1/m['p']:.2f}", "CASA": f"{m['b']:.2f}", "EDGE": f"{edge:+.1%}", "bg": bg})
            
            df_final = pd.DataFrame(df_list)
            st.table(df_final.drop('bg', axis=1).style.apply(lambda r: [f"background-color: {df_list[r.name]['bg']}"] * len(r), axis=1))

    except Exception as e: st.error(f"ENGINE ERROR V43: {e}")
