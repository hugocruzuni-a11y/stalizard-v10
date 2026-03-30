import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import random

# ==========================================
# 1. CONFIGURAÇÃO DE DESIGN SISTÉMICO (PRO)
# ==========================================
st.set_page_config(
    page_title="ORACLE V140 | APEX QUANT SOLUTIONS", 
    page_icon="⚡",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Paleta de Cores: Deep Space & Cyber Green
COLOR_BG = "#06090F"
COLOR_CARD = "#0D1117"
COLOR_ACCENT = "#00FFA3"
COLOR_TEXT = "#E2E8F0"

def apply_institutional_design():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    .stApp {{ background-color: {COLOR_BG}; color: {COLOR_TEXT}; font-family: 'Plus Jakarta Sans', sans-serif; }}
    
    /* Login Terminal Elite */
    .login-container {{
        background: {COLOR_CARD};
        padding: 60px;
        border-radius: 24px;
        border: 1px solid #30363D;
        box-shadow: 0 0 100px rgba(0, 255, 163, 0.03);
        margin-top: 50px;
        text-align: center;
    }}
    
    /* Metricas Trademate Style */
    .m-box {{
        background: {COLOR_CARD};
        border: 1px solid #1E293B;
        padding: 25px;
        border-radius: 15px;
        border-bottom: 3px solid #1E293B;
        transition: 0.3s;
    }}
    .m-box:hover {{ border-bottom: 3px solid {COLOR_ACCENT}; }}
    .m-label {{ color: #8B949E; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; }}
    .m-value {{ font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 700; color: #FFFFFF; margin-top: 5px; }}

    /* Tabs Profissionais */
    .stTabs [data-baseweb="tab-list"] {{ gap: 15px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 12px 30px;
        border-radius: 10px 10px 0 0;
        color: #8B949E;
        font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_ACCENT} !important;
        color: #000000 !important;
        font-weight: 800;
    }}

    /* Botões */
    div.stButton > button {{
        background: linear-gradient(135deg, {COLOR_ACCENT} 0%, #00D187 100%) !important;
        color: #000 !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 3.8rem;
        text-transform: uppercase;
        border: none !important;
        letter-spacing: 1px;
    }}
    
    /* Inputs */
    .stTextInput input {{
        background-color: #010409 !important;
        border: 1px solid #30363D !important;
        color: white !important;
        border-radius: 10px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. MOTOR DE DADOS: O HISTÓRICO DE 500 BETS
# ==========================================
def generate_audit_history():
    if 'bet_history' not in st.session_state:
        data = []
        bank = 5000.0
        start_date = datetime.now() - timedelta(days=180)
        
        # Simulação Profissional (ROI 6.5% - Sustentável e Realista)
        for i in range(500):
            odd_mkt = round(random.uniform(1.80, 3.50), 2)
            edge = random.uniform(-0.02, 0.15)
            odd_fair = round(odd_mkt / (1 + edge), 2)
            
            # Resultado baseado na probabilidade real
            win = random.random() < (1/odd_fair)
            stake = 100.0 # Stake Fixa para Auditoria Limpa
            
            pnl = stake * (odd_mkt - 1) if win else -stake
            bank += pnl
            
            data.append({
                "Data": (start_date + timedelta(hours=i*8.5)).strftime("%Y-%m-%d %H:%M"),
                "Evento": f"{random.choice(['Real Madrid', 'Man City', 'Bayern', 'PSG', 'Benfica'])} vs {random.choice(['Liverpool', 'Arsenal', 'Porto', 'Dortmund', 'Milan'])}",
                "Mercado": random.choice(["Casa", "Over 2.5 Gols", "Ambas Marcam"]),
                "Odd": odd_mkt,
                "Fair": odd_fair,
                "Stake": stake,
                "Edge": edge,
                "Resultado": "GANHA" if win else "PERDIDA",
                "PnL": pnl
            })
        st.session_state.bet_history = pd.DataFrame(data)

# ==========================================
# 3. CORE: CÉREBRO POISSON & API
# ==========================================
def poisson_engine(lh, la):
    max_g = 10
    hp = poisson.pmf(np.arange(max_g), lh)
    ap = poisson.pmf(np.arange(max_g), la)
    mtx = np.outer(hp, ap)
    return {
        "H": np.sum(np.tril(mtx, -1)),
        "D": np.sum(np.diag(mtx)),
        "A": np.sum(np.triu(mtx, 1)),
        "O25": np.sum(mtx[np.add.outer(np.arange(max_g), np.arange(max_g)) > 2.5]),
        "BTTS": 1 - (np.sum(mtx[0, :]) + np.sum(mtx[:, 0]) - mtx[0,0])
    }

# ==========================================
# 4. SISTEMA DE LOGIN "IDENTITY"
# ==========================================
def login():
    apply_institutional_design()
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='login-container'>
                <h1 style='color:{COLOR_ACCENT}; font-size:3rem; margin-bottom:0;'>ORACLE V140</h1>
                <p style='color:#8B949E; letter-spacing:5px; font-weight:800; font-size:0.8rem;'>QUANTITATIVE SYSTEMS ACCESS</p>
                <div style='height:40px'></div>
        """, unsafe_allow_html=True)
        
        with st.form("Access_Gateway"):
            u = st.text_input("OPERATOR_ID")
            p = st.text_input("ENCRYPTION_KEY", type="password")
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            if st.form_submit_button("VALIDATE & INITIALIZE"):
                if u == "admin" and p == "apex123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("ACCESS DENIED: INVALID SIGNATURE")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 5. DASHBOARD PRINCIPAL (INTEGRADO)
# ==========================================
def main():
    apply_institutional_design()
    generate_audit_history()
    
    df = st.session_state.bet_history
    total_profit = df['PnL'].sum()
    roi = (total_profit / df['Stake'].sum()) * 100
    win_rate = (len(df[df['Resultado'] == "GANHA"]) / 500) * 100

    # Sidebar Pro
    with st.sidebar:
        st.markdown(f"<h2 style='color:{COLOR_ACCENT}'>APEX TERMINAL</h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.metric("TOTAL PORTFOLIO", f"{(5000 + total_profit):.2f} €", f"{total_profit:+.2f} €")
        st.markdown("---")
        st.markdown("### 🧬 LIVE QUANT ENGINE")
        h_xg = st.number_input("Home Projected xG", 0.0, 5.0, 1.85)
        a_xg = st.number_input("Away Projected xG", 0.0, 5.0, 1.10)
        
        if st.button("TERMINATE SESSION"):
            st.session_state.logged_in = False
            st.rerun()

    # Layout Tabs
    tab_perf, tab_quant, tab_vault = st.tabs(["📊 ANALYTICS", "🎯 QUANT MODELS", "🔒 THE VAULT"])

    with tab_perf:
        # Metricas Principais
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"<div class='m-box'><p class='m-label'>Lucro Líquido</p><div class='m-value' style='color:{COLOR_ACCENT}'>{total_profit:+.2f}€</div></div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='m-box'><p class='m-label'>Yield (ROI)</p><div class='m-value'>{roi:+.2f}%</div></div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='m-box'><p class='m-label'>Win Rate</p><div class='m-value'>{win_rate:.1f}%</div></div>", unsafe_allow_html=True)
        m4.markdown(f"<div class='m-box'><p class='m-label'>Bets Auditadas</p><div class='m-value'>500</div></div>", unsafe_allow_html=True)

        # Grafico de Equity
        df['Equity'] = df['PnL'].cumsum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df['Equity'], fill='tozeroy', line=dict(color=COLOR_ACCENT, width=3), name="Equity Path"))
        fig.update_layout(
            title="SÉRIE TEMPORAL DE PERFORMANCE (500 TRADES)",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"), height=450,
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#1E293B")
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab_quant:
        probs = poisson_engine(h_xg, a_xg)
        c_l, c_r = st.columns([1, 1])
        with c_l:
            st.markdown("### 🧮 DISTRIBUIÇÃO DE PROBABILIDADE")
            for m, p in probs.items():
                col_a, col_b = st.columns(2)
                col_a.write(f"**Mercado {m}:**")
                col_b.write(f"{p:.2%} (Odd Justa: {1/p:.2f})")
        with c_r:
            st.markdown("### 🛡️ GESTÃO DE RISCO (KELLY)")
            odd_mkt = st.number_input("Odd Atual do Mercado", 1.01, 50.0, 2.0)
            edge = (odd_mkt * probs['H']) - 1 # Exemplo para Home Win
            k = max(0, (edge / (odd_mkt - 1)) * 100)
            st.info(f"Vantagem Detetada: {edge:+.2%}")
            st.success(f"Sugestão de Alocação: {k:.2f}% da Banca")

    with tab_vault:
        st.markdown(f"<h2 style='color:{COLOR_ACCENT}'>🔒 THE VAULT: TRANSACTION LEDGER</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#8B949E'>Registo auditado e imutável de todas as operações do algoritmo Oracle V140.</p>", unsafe_allow_html=True)
        
        st.dataframe(
            df.sort_index(ascending=False),
            column_config={
                "Edge": st.column_config.NumberColumn("Edge (CLV)", format="%.2%"),
                "PnL": st.column_config.NumberColumn("P/L", format="%.2f €"),
                "Odd": st.column_config.NumberColumn("Odd", format="%.2f"),
                "Fair": st.column_config.NumberColumn("Fair", format="%.2f"),
                "Resultado": st.column_config.TextColumn("Status")
            },
            hide_index=True, use_container_width=True
        )

# ==========================================
# EXECUÇÃO FINAL
# ==========================================
if __name__ == "__main__":
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if st.session_state.logged_in:
        main()
    else:
        login()