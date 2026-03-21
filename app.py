import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import matplotlib.pyplot as plt

# 1. Configuração Starline Ultra Prestige
st.set_page_config(page_title="STARLINE ULTRA V44", layout="wide")

# 2. CSS Elite Prestige (Foco em Hierarquia e Leitura Rápida)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Configuração Global Clean */
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    .block-container { padding: 1rem 2rem 0rem 3rem !important; max-width: 95% !important; }

    /* Inputs Modernos com Borda Suave */
    .stNumberInput, .stTextInput, .stSelectbox { 
        background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; margin-bottom: 5px !important; 
    }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        font-size: 0.7rem !important; font-weight: 800 !important; color: #64748B !important; text-transform: uppercase; margin-bottom: 0px !important;
    }

    /* Botão de Execução Ultra Deep Green */
    div.stButton > button {
        background: linear-gradient(135deg, #064E3B 0%, #065F46 100%) !important;
        color: white !important; font-weight: 800; height: 3.5em; width: 100%; border-radius: 8px; border: none;
        box-shadow: 0 4px 12px rgba(6, 78, 59, 0.25);
    }

    /* Advisor Cards Estilizados (A Estrela do Ecrã) */
    .advice-card {
        padding: 20px 25px; border-radius: 12px; margin-bottom: 15px; border-left: 8px solid;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.03);
    }
    .val-prestige { background-color: #ECFDF5; border-color: #10B981; color: #064E3B; } /* Verde - Lucro */
    .val-strategy { background-color: #F0F9FF; border-color: #0EA5E9; color: #075985; } /* Azul - Cobertura */

    /* Tabela Bloomberg Expanded (Otimizada para Macbook) */
    .stTable { font-size: 0.85rem !important; border-radius: 10px !important; overflow: hidden; border: 1px solid #E2E8F0; }
    thead tr th { background-color: #F8FAFC !important; border-bottom: 2px solid #E2E8F0 !important; font-weight: 800 !important; color: #1E293B !important; }
    </style>
    """, unsafe_allow_html=True)

# Função de Reset Robusta
def reset_engine():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Título Prestige Clean com Versão
st.markdown("<h3 style='color:#1E293B; font-weight:800; margin: 10px 0px 5px 0px; letter-spacing:-1px;'>🏛️ STARLINE // OMNI-QUANT <span style='color:#059669; font-size:12px; font-weight:400; letter-spacing:0px;'>V44.0 QUANTUM VISION 1M</span></h3>", unsafe_allow_html=True)
st.markdown("---")

# Layout de 3 Colunas com Gap Largo
col_inputs, col_charts, col_results = st.columns([1, 1.2, 1.3], gap="large")

with col_inputs:
    # 1. Estratégia e Teams (Compacto)
    ctx = st.selectbox("ESTRATÉGIA", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx_v44")
    
    # Teams com maior destaque visual
    c_teams1, c_teams2 = st.columns(2)
    h_n = c_teams1.text_input("HOME TEAM", value="VILLARREAL", key="hn").upper()
    a_n = c_teams2.text_input("AWAY TEAM", value="REAL SOCIEDAD", key="an").upper()
    
    # 2. Stats (Grelha Respirável) GF/GA
    st.markdown("<p style='font-size:11px; font-weight:800; color:#64748B; margin-top:15px; margin-bottom:2px;'>ESTATÍSTICAS GF/GA (ÚLT. 5 JOGOS)</p>", unsafe_allow_html=True)
    c_s1, c_s2, c_s3, c_s4 = st.columns(4)
    v_hgf = c_s1.number_input("H-GF", value=9.0, key="hgf")
    v_hga = c_s2.number_input("H-GA", value=7.0, key="hga")
    v_agf = c_s3.number_input("A-GF", value=12.0, key="agf")
    v_aga = c_s4.number_input("A-GA", value=10.0, key="aga")
    
    # 3. Live Odds Grid (Compacto e Organizado)
    st.markdown("<p style='font-size:11px; font-weight:800; color:#64748B; margin-top:15px; margin-bottom:2px;'>LIVE MARKET ODDS (ENTRADA)</p>", unsafe_allow_html=True)
    c_o1, c_o2, c_o3 = st.columns(3)
    m_o1, m_ox, m_o2 = c_o1.number_input("ODD 1", 1.88), c_o2.number_input("ODD X", 4.00), c_o3.number_input("ODD 2", 3.35)
    
    c_o4, c_o5, c_o6 = st.columns(3)
    m_o15, m_o25, m_o35 = c_o4.number_input("+1.5", 1.10), c_o5.number_input("+2.5", 1.33), c_o6.number_input("+3.5", 1.78)
    
    c_o7, c_o8, c_o9 = st.columns(3)
    m_hah, m_haa, m_ob = c_o7.number_input("DNB-H", 1.33), c_o8.number_input("DNB-A", 1.85), c_o9.number_input("BTTS", 1.32)

    # Ação Ultra
    btn_run = st.button("🚀 EXECUTAR SIMULAÇÃO DE ELITE (1M)")
    st.button("🗑️ RESET ENGINE", on_click=reset_engine)

# --- PROCESSAMENTO ULTRA 1M (O Cérebro) ---
if btn_run:
    try:
        # Matemática Pura com Ajuste de Contexto
        adj = 0.67 if "Champions" in ctx else 1.0
        lh, la = ((v_hgf/5)*(v_aga/5))**0.5, ((v_agf*adj/5)*(v_hga/5))**0.5
        
        # Simulação Ultra 1M (Gerar Amostra Massiva)
        sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
        stot = sim_h + sim_a
        
        # Probabilidades do Mercado 1X2
        ph = np.mean(sim_h > sim_a)
        px = np.mean(sim_h == sim_a)
        pa = np.mean(sim_h < sim_a)
        norm = ph + px + pa
        ph, px, pa = ph/norm, px/norm, pa/norm

        with col_charts:
            st.markdown("#### 📊 VISUAL ANALYTICS")
            
            # Gráfico de Tendência de Golos Poisson (V44 Prestige Style)
            fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
            x_range = np.arange(0, 7)
            ax.fill_between(x_range, poisson.pmf(x_range, lh), color='#10B981', alpha=0.12, label=f"Prob {h_n}")
            ax.plot(x_range, poisson.pmf(x_range, lh), color='#10B981', marker='o', linewidth=2.5)
            ax.fill_between(x_range, poisson.pmf(x_range, la), color='#0EA5E9', alpha=0.12, label=f"Prob {a_n}")
            ax.plot(x_range, poisson.pmf(x_range, la), color='#0EA5E9', marker='o', linewidth=2.5)
            ax.set_title("EXPECTATIVA DE GOLOS (POISSON MODEL)", fontsize=10, fontweight='800')
            ax.legend(fontsize=8); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            st.pyplot(fig)

            # Histograma de Frequência de Golos Totais (Onde o jogo se decide)
            fig2, ax2 = plt.subplots(figsize=(6, 3))
            ax2.hist(stot, bins=np.arange(9)-0.5, density=True, color='#64748B', alpha=0.6, rwidth=0.8)
            ax2.set_title("Probabilidade de Golos Totais no Jogo", fontsize=9)
            st.pyplot(fig2)

        with col_results:
            st.markdown("#### 💎 QUANTUM ADVISOR")
            
            # Lista de Mercados Totalmente Mapeada
            mkt_list = [
                {"n": "1X2: HOME", "p": ph, "b": m_o1, "t": "VITÓRIA"},
                {"n": "1X2: AWAY", "p": pa, "b": m_o2, "t": "VITÓRIA"},
                {"n": "OVER 2.5", "p": np.mean(stot>2.5), "b": m_o25, "t": "GOLOS"},
                {"n": "DNB: AWAY", "p": pa/(ph+pa), "b": m_haa, "t": "PROTEÇÃO"}
            ]
            
            # Lógica Advisor V44 Prestige (Destaque para o principal)
            recoms = sorted([(m['n'], m['p'], m['b'], (m['p']*m['b'])-1, m['t']) for m in mkt_list if (m['p']*m['b'])-1 > 0.05], key=lambda x: x[3], reverse=True)

            if recoms:
                # O Card Principal com Fonte Grande
                best_name, best_p, best_b, best_e, best_t = recoms[0]
                s_cls = "val-prestige" if best_t == "VITÓRIA" else "val-strategy"
                icon = "🚀" if best_t == "VITÓRIA" else "🛡️"
                st.markdown(f"""
                <div class="advice-card {s_cls}">
                    <span style='font-size:1.4rem; font-weight:800; color:#1E293B;'>{icon} {best_t}: {best_name}</span><br>
                    <span style='font-size:1.1rem;'>Edge detectada: <b>{best_e:+.1%}</b></span> | Odd: <b>{best_b:.2f}</b> (Justa: {1/best_p:.2f})
                </div>
                """, unsafe_allow_html=True)
                
                # Outras Recomendações (cards menores)
                for n, p, b, e, t in recoms[1:3]:
                    st.markdown(f'<div class="advice-card val-strategy" style="padding:10px 15px;">🛡️ Cobertura: <b>{n}</b> (Edge: {e:+.1%})</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="advice-card val-neutral">🛑 CONSELHO ULTRA: As odds do mercado estão ajustadas. Evite entradas.</div>', unsafe_allow_html=True)

            # Tabela de Dados (Heatmap de Valor)
            st.write("**DETALHE DO MERCADO**")
            table_data = []
            for m in mkt_list:
                edge = (m['p'] * m['b']) - 1
                bg = "rgba(16, 185, 129, 0.12)" if edge > 0.10 else "rgba(245, 158, 11, 0.12)" if edge > 0 else "none"
                table_data.append({"MERCADO": m['n'], "PROB": f"{m['p']:.1%}", "JUSTA": f"{1/m['p']:.2f}", "CASA": f"{m['b']:.2f}", "EDGE": f"{edge:+.1%}", "bg": bg})
            
            df_res = pd.DataFrame(table_data)
            # Renderizar Tabela com Heatmap
            st.table(df_res.drop('bg', axis=1).style.apply(lambda r: [f"background-color: {table_data[r.name]['bg']}"] * len(r), axis=1))

    except Exception as e: st.error(f"ENGINE ERROR V44: {e}")
