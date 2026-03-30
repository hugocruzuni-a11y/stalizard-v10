import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import random

# ==========================================
# 1. CONFIGURAÇÃO DE INTERFACE (ESTILO TRADEMATE PRO)
# ==========================================
st.set_page_config(
    page_title="ORACLE V140 | APEX QUANT SOLUTIONS", 
    page_icon="⚡",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Definição de Cores Profissionais
COLOR_BG = "#06090F"
COLOR_CARD = "#0D1117"
COLOR_ACCENT = "#00FFA3"
COLOR_TEXT = "#E2E8F0"

def inject_ui():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    .stApp {{ background-color: {COLOR_BG}; color: {COLOR_TEXT}; font-family: 'Plus Jakarta Sans', sans-serif; }}
    
    /* Login Terminal */
    .login-container {{
        background: {COLOR_CARD};
        padding: 50px;
        border-radius: 20px;
        border: 1px solid #30363D;
        box-shadow: 0 0 50px rgba(0, 255, 163, 0.05);
        text-align: center;
        margin: auto;
    }}
    
    /* Metric Cards Estilo Trademate */
    .m-card {{
        background: {COLOR_CARD};
        border: 1px solid #1E293B;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid {COLOR_ACCENT};
    }}
    .m-label {{ color: #8B949E; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 800; }}
    .m-value {{ font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 700; color: #FFFFFF; }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 10px 25px;
        border-radius: 8px 8px 0 0;
        color: #8B949E;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_ACCENT} !important;
        color: #000 !important;
        font-weight: 800;
    }}

    /* Buttons */
    div.stButton > button {{
        background: linear-gradient(135deg, {COLOR_ACCENT} 0%, #00D187 100%) !important;
        color: #000 !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        border: none !important;
        height: 3rem;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. GERAÇÃO DE DADOS (HISTÓRICO REALISTA 500 BETS)
# ==========================================
def generate_pro_data():
    if 'bet_history' not in st.session_state:
        data = []
        current_bank = 2500.0
        start_date = datetime.now() - timedelta(days=160)
        
        for i in range(500):
            odd = round(random.uniform(1.80, 3.40), 2)
            edge = random.uniform(-0.02, 0.12)
            fair_odd = round(odd / (1 + edge), 2)
            
            # Probabilidade baseada na odd real
            is_win = random.random() < (1 / fair_odd)
            stake = 50.0  # Stake fixa para consistência
            
            pnl = stake * (odd - 1) if is_win else -stake
            current_bank += pnl
            
            data.append({
                "Data": (start_date + timedelta(hours=i*8)).strftime("%Y-%m-%d %H:%M"),
                "Evento": f"Equipa {random.randint(1,100)} vs Equipa {random.randint(101,200)}",
                "Mercado": random.choice(["Casa", "Over 2.5", "BTTS"]),
                "Odd": odd,
                "Fair": fair_odd,
                "Stake (€)": stake,
                "Edge": edge,
                "Status": "GANHA" if is_win else "PERDIDA",
                "PnL": pnl
            })
        st.session_state.bet_history = pd.DataFrame(data)

# ==========================================
# 3. LÓGICA DE LOGIN
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    inject_ui()
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='height:100px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='login-container'>
                <h1 style='color:{COLOR_ACCENT}; margin-bottom:0;'>ORACLE V140</h1>
                <p style='color:#8B949E; letter-spacing:4px; font-size:0.7rem; font-weight:700;'>QUANTITATIVE TRADING TERMINAL</p>
                <div style='height:30px'></div>
        """, unsafe_allow_html=True)
        
        with st.form("Access"):
            user = st.text_input("Operator ID")
            passw = st.text_input("Secret Key", type="password")
            if st.form_submit_button("UNLOCK SYSTEM"):
                if user == "admin" and passw == "apex123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Credenciais Inválidas")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 4. DASHBOARD TRADEMATE STYLE
# ==========================================
def main_dashboard():
    inject_ui()
    generate_pro_data()
    
    df = st.session_state.bet_history
    total_pnl = df['PnL'].sum()
    roi = (total_pnl / df['Stake (€)'].sum()) * 100
    winrate = (len(df[df['Status'] == "GANHA"]) / 500) * 100

    # Sidebar
    with st.sidebar:
        st.markdown(f"<h2 style='color:{COLOR_ACCENT}'>APEX QUANT</h2>", unsafe_allow_html=True)
        st.metric("PORTFOLIO VALUE", f"{2500 + total_pnl:.2f} €", f"{total_pnl:+.2f} €")
        st.markdown("---")
        if st.button("TERMINATE SESSION"):
            st.session_state.logged_in = False
            st.rerun()

    # Tabs
    t_perf, t_vault = st.tabs(["📊 PERFORMANCE ANALYTICS", "🔒 THE VAULT (AUDIT)"])

    with t_perf:
        # Metricas Principais
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"<div class='m-card'><p class='m-label'>Lucro Total</p><div class='m-value' style='color:{COLOR_ACCENT}'>{total_pnl:+.2f}€</div></div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='m-card'><p class='m-label'>Yield (ROI)</p><div class='m-value'>{roi:+.2f}%</div></div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='m-card'><p class='m-label'>Win Rate</p><div class='m-value'>{winrate:.1f}%</div></div>", unsafe_allow_html=True)
        m4.markdown(f"<div class='m-card'><p class='m-label'>Total Trades</p><div class='m-value'>500</div></div>", unsafe_allow_html=True)

        # Grafico de Equity
        df['Equity'] = df['PnL'].cumsum()
        fig = go.Figure(go.Scatter(y=df['Equity'], fill='tozeroy', line=dict(color=COLOR_ACCENT, width=3)))
        fig.update_layout(
            title="SÉRIE TEMPORAL DE PERFORMANCE",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"), height=450, margin=dict(l=0,r=0,t=40,b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    with t_vault:
        st.markdown(f"<h2 style='color:{COLOR_ACCENT}'>THE VAULT - TRANSACTION LEDGER</h2>", unsafe_allow_html=True)
        st.dataframe(
            df.sort_index(ascending=False),
            column_config={
                "Edge": st.column_config.NumberColumn("Edge (CLV)", format="%.2%"),
                "PnL": st.column_config.NumberColumn("P/L", format="%.2f €"),
                "Odd": st.column_config.NumberColumn("Market Odd", format="%.2f"),
                "Fair": st.column_config.NumberColumn("Fair Odd", format="%.2f"),
            },
            hide_index=True,
            use_container_width=True
        )

# ==========================================
# EXECUÇÃO
# ==========================================
if st.session_state.logged_in:
    main_dashboard()
else:
    login_page()