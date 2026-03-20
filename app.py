import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# 1. Configuração Starline PRO
st.set_page_config(page_title="STARLINE PRO", layout="wide")

# 2. CSS Avançado e Sofisticado (Fundo Branco, Design Moderno e Botões Coloridos)
st.markdown("""
    <style>
    /* Importar fonte moderna 'Inter' */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    /* Definições Globais */
    .stApp { background-color: #FFFFFF; color: #1E293B; font-family: 'Inter', sans-serif; }
    
    /* Organização em Cards com Sombras Suaves */
    div[data-testid="stVerticalBlock"] > div { background-color: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); margin-bottom: 20px; }
    
    /* Inputs Estilizados */
    .stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; color: #1E293B !important; font-size: 16px !important; transition: all 0.2s;
    }
    .stNumberInput input:focus, .stTextInput input:focus { border-color: #38BDF8 !important; box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.1) !important; }
    
    /* Títulos e Tipografia */
    h1, h2, h3 { color: #0F172A !important; letter-spacing: -0.5px; }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        font-size: 0.75rem !important; font-weight: 700 !important; color: #64748B !important; text-transform: uppercase; letter-spacing: 0.5px;
    }

    /* --- ESTILIZAÇÃO DOS BOTÕES (COM CORES) --- */
    
    /* Wrapper para controlar as cores individualmente */
    .stButton > button { width: 100%; border-radius: 8px; height: 3.5em; border: none; font-weight: 700; font-size: 16px; transition: all 0.2s; text-transform: uppercase; letter-spacing: 0.5px; }

    /* Botão ANALISAR (Verde Sport/Neon) */
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white !important;
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2);
    }
    div[data-testid="stFormSubmitButton"] > button:hover { transform: translateY(-1px); box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3); }

    /* Botão CLEAR (Vermelho/Laranja Suave) */
    div.stButton > button:nth-of-type(1) { /* Corrigido para o botão CLEAR */
        background: linear-gradient(135deg, #F87171 0%, #EF4444 100%);
        color: white !important;
        box-shadow: 0 4px 6px -1px rgba(248, 113, 113, 0.2);
    }
    div.stButton > button:nth-of-type(1):hover { transform: translateY(-1px); box-shadow: 0 10px 15px -3px rgba(248, 113, 113, 0.3); }

    /* Alerta Champions */
    .ctx-alert {
        padding: 15px; background-color: #FFFBEB; border-left: 5px solid #F59E0B;
        color: #92400E; font-weight: bold; margin-bottom: 25px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    /* Tabela Bloomberg Style */
    .stTable { background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    thead tr th { background-color: #F1F5F9 !important; border-bottom: 2px solid #E2E8F0 !important; color: #1E293B !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# Função para resetar os campos (Corrigida e Segura)
def reset_data():
    # Mantemos apenas o contexto e os nomes das equipas, limpamos o resto
    for key in ['hgf', 'hga', 'agf', 'aga', 'o1', 'ox', 'o2', 'ob', 'o15', 'o25', 'o35', 'hah', 'u15', 'u25', 'u35', 'haa']:
        if key in st.session_state:
            del st.session_state[key]

st.title("🏛️ STARLINE // OMNI-QUANT")
st.markdown("---")

# --- COLUNAS DE TRABALHO ---
col_in, col_out = st.columns([1.2, 2], gap="large")

with col_in:
    # 1. Configuração Inicial (Formulário)
    with st.form("starline_form", clear_on_submit=False):
        st.subheader("🛠️ Configuração Inicial")
        comp_type = st.selectbox("Contexto da Partida", ["Liga (Regular)", "Champions/Taça (Playoff)"], key="ctx")
        
        c_h, c_a = st.columns(2)
        h_name = c_h.text_input("Equipa Casa", value="LEIPZIG", key="h_n").upper()
        a_name = c_a.text_input("Equipa Fora", value="HOFFENHEIM", key="a_n").upper()
        
        # 2. Estatísticas
        st.markdown("### ⚽ Médias (GF / GA STATS)")
        cg1, cg2, cg3, cg4 = st.columns(4)
        v_h_gf = cg1.number_input("H-GF", value=8.0, key="hgf")
        v_h_ga = cg2.number_input("H-GA", value=12.0, key="hga")
        v_a_gf = cg3.number_input("A-GF", value=12.0, key="agf")
        v_a_ga = cg4.number_input("A-GA", value=10.0, key="aga")
        
        # 3. Odds
        st.markdown("### 💹 Odds Reais (Market)")
        oc1, oc2, oc3, oc4 = st.columns(4)
        m_o1, m_ox, m_o2, m_obtts = oc1.number_input("1", value=1.88, key="o1"), oc2.number_input("X", value=4.00, key="ox"), oc3.number_input("2", value=3.35, key="o2"), oc4.number_input("BTTS", value=1.32, key="ob")
        
        oc5, oc6, oc7, oc8 = st.columns(4)
        m_o15, m_o25, m_o35, m_hah = oc5.number_input("+1.5", value=1.10, key="o15"), oc6.number_input("+2.5", value=1.33, key="o25"), oc7.number_input("+3.5", value=1.78, key="o35"), oc8.number_input("DNB-H", value=1.33, key="hah")

        oc9, oc10, oc11, oc12 = st.columns(4)
        m_u15, m_u25, m_u35, m_haa = oc9.number_input("-1.5", value=4.55, key="u15"), oc10.number_input("-2.5", value=2.65, key="u25"), oc11.number_input("-3.5", value=1.75, key="u35"), oc12.number_input("DNB-A", value=1.85, key="haa")

        # Botão de Ação Colorido (Verde Neon/Sport)
        btn_run = st.form_submit_button("⚡ GERAR ANÁLISE QUANTITATIVA")

    # Botão CLEAR Colorido (Vermelho/Laranja Suave)
    st.button("🗑️ CLEAR DATA", on_click=reset_data)

# --- RESULTADOS PREMIUM (MANTÉM IGUAL) ---
if btn_run:
    try:
        # Recuperação da Lógica Fator Champions
        calc_a_gf = float(v_a_gf)
        if comp_type == "Champions/Taça (Playoff)":
            calc_a_gf = v_a_gf * 0.67
            st.warning("⚡ **Fator Playoff Ativado:** Ajuste de agressividade para equipa visitante aplicado.")

        # Lambdas (Matemática Pura V15/V20)
        l_h = ((v_h_gf/5)*(v_a_ga/5))**0.5 * 1.12
        l_a = ((calc_a_gf/5)*(v_h_ga/5))**0.5 * 0.90
        
        sim_h, sim_a = np.random.poisson(l_h, 100000), np.random.poisson(l_a, 100000)
        s_tot = sim_h + sim_a
        
        p_h = np.mean(sim_h > sim_a)
        p_x = np.mean(sim_h == sim_a)
        p_a = np.mean(sim_h < sim_a)
        norm = p_h + p_x + p_a
        p_h, p_x, p_a = p_h/norm, p_x/norm, p_a/norm

        with col_out:
            st.subheader(f"📊 Relatório Quântico: {h_name} vs {a_name}")
            
            # Mercados V18
            mkts = [
                (f"1X2: {h_name}", p_h, m_o1), ("1X2: DRAW", p_x, m_ox), (f"1X2: {a_name}", p_a, m_o2),
                ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_obtts), 
                (f"DNB: {h_name}", p_h/(p_h+p_a), m_hah), (f"DNB: {a_name}", p_a/(p_h+p_a), m_haa),
                ("OVER 1.5", np.mean(s_tot>1.5), m_o15), ("UNDER 1.5", np.mean(s_tot<1.5), m_u15),
                ("OVER 2.5", np.mean(s_tot>2.5), m_o25), ("UNDER 2.5", np.mean(s_tot<2.5), m_u25),
                ("OVER 3.5", np.mean(s_tot>3.5), m_o35), ("UNDER 3.5", np.mean(s_tot<3.5), m_u35)
            ]

            final_data = []
            for name, prob, bookie in mkts:
                edge = (prob * bookie) - 1
                stake = max(0, (edge/(bookie-1)*5)) if bookie > 1 else 0
                
                # Indicador de Valor Prestige
                if edge > 0.08: status = "💎 ALTO VALOR"
                elif edge > 0: status = "✅ POSITIVO"
                else: status = "❌ SEM VALOR"
                
                final_data.append({
                    "ANÁLISE": status, "MERCADO": name, "PROB %": f"{p:.1%}", 
                    "ODD": f"{bookie:.2f}", "EDGE %": f"{edge:+.1%}", "STAKE %": f"{stake:.1f}%", "val": edge
                })

            df_final = pd.DataFrame(final_data)
            
            # Função de Destaque Neon (Heatmap Ativado)
            def highlight_value(row):
                color = 'white'
                if row['val'] > 0.08: color = '#00FF95' # Verde Neon
                elif row['val'] > 0: color = '#FFA500' # Laranja Ouro
                return [f'color: {color}'] * len(row)

            st.table(df_final.drop(columns=['val']).style.apply(highlight_value, axis=1))

            st.markdown("---")
            st.subheader("🎯 Probabilidade de Placares Exatos")
            hp, ap = poisson.pmf(range(6), l_h), poisson.pmf(range(6), l_a)
            mtx = np.outer(hp, ap)
            idx = np.unravel_index(np.argsort(mtx.ravel())[-5:], mtx.shape)
            
            sc_cols = st.columns(5)
            for i in range(4, -1, -1):
                with sc_cols[4-i]:
                    st.metric(f"{idx[0][i]} - {idx[1][i]}", f"{mtx[idx[0][i], idx[1][i]]:.1%}")
    
    except Exception as e:
        st.error(f"Erro no processamento PRO: {e}")
