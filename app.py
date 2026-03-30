import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta
import random
import time

# ==========================================
# 1. CONFIGURAÇÃO DE ESTADO E AMBIENTE
# ==========================================
st.set_page_config(
    page_title="Apex Quant | Institutional Terminal", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

def generate_institutional_history():
    """Gera 500 registos realistas com variância estatística apropriada."""
    np.random.seed(42)
    teams = ["Benfica", "Porto", "Sporting", "Braga", "Real Madrid", "Barcelona", "Arsenal", "Man City", "Liverpool", "Bayern", "Juventus", "Inter", "Milan"]
    mkts = ["Match Odds - Home", "Match Odds - Away", "Over 2.5 Goals", "Under 2.5 Goals", "BTTS - Yes"]
    
    history = []
    date_start = date.today() - timedelta(days=180)
    
    for _ in range(500):
        d = date_start + timedelta(days=random.randint(0, 180))
        t1, t2 = random.sample(teams, 2)
        
        # Odds com distribuição realista
        odd_comp = round(random.uniform(1.60, 3.50), 2)
        
        # Closing Line Value (CLV) realista: a maioria é pequena, algumas são negativas (bad beats)
        clv = np.random.normal(loc=0.03, scale=0.04)
        odd_real = odd_comp / (1 + clv)
        prob_win = 1 / odd_real
        
        stake = round(random.uniform(50, 250), 2)
        
        won = random.random() < prob_win
        status = "Settled - Won" if won else "Settled - Lost"
        
        history.append({
            "Date": d.strftime('%Y-%m-%d'),
            "Event": f"{t1} v {t2}",
            "Market": random.choice(mkts),
            "Matched Odd": odd_comp,
            "True Odd": round(odd_real, 2),
            "Stake (€)": stake,
            "CLV": round(clv, 4),
            "Status": status
        })
    
    df = pd.DataFrame(history)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values("Date").reset_index(drop=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    return df

# Inicialização de Sessão
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'trade_ledger' not in st.session_state: st.session_state.trade_ledger = generate_institutional_history()

# ==========================================
# 2. DESIGN INSTITUCIONAL (CSS)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Roboto+Mono:wght@400;500&display=swap');
    
    .stApp { background-color: #0F172A; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0B1120 !important; border-right: 1px solid #1E293B !important; }
    
    /* Tipografia e Tabs */
    h1, h2, h3 { font-weight: 500; letter-spacing: -0.5px; color: #F8FAFC; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #1E293B; gap: 0; }
    .stTabs [data-baseweb="tab"] { color: #94A3B8; font-weight: 500; font-size: 0.85rem; padding: 12px 24px; background: transparent; border: none; transition: color 0.2s; text-transform: uppercase; letter-spacing: 0.5px; }
    .stTabs [aria-selected="true"] { color: #38BDF8 !important; border-bottom: 2px solid #38BDF8 !important; background: rgba(56, 189, 248, 0.05) !important; }
    
    /* Terminal Login */
    .login-wrapper { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
    .auth-panel { background: #0B1120; border: 1px solid #1E293B; border-radius: 4px; padding: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); max-width: 400px; width: 100%; margin: 0 auto; }
    .auth-header { font-size: 1.2rem; font-weight: 600; color: #F8FAFC; margin-bottom: 24px; text-align: center; border-bottom: 1px solid #1E293B; padding-bottom: 16px; }
    
    /* Metrics Board */
    .metric-container { background: #0B1120; border: 1px solid #1E293B; border-radius: 4px; padding: 16px; }
    .metric-label { font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
    .metric-val { font-size: 1.5rem; font-weight: 500; font-family: 'Roboto Mono', monospace; color: #F8FAFC; }
    .metric-sub { font-size: 0.75rem; margin-top: 4px; color: #94A3B8; }
    
    /* Positivo/Negativo Cores */
    .val-pos { color: #10B981 !important; }
    .val-neg { color: #EF4444 !important; }
    
    /* Buttons */
    div.stButton > button { background: #1E293B !important; color: #F8FAFC !important; font-weight: 500 !important; border-radius: 4px !important; border: 1px solid #334155 !important; transition: background 0.2s; font-size: 0.85rem; }
    div.stButton > button:hover { background: #334155 !important; border-color: #475569 !important; }
    .btn-primary div.stButton > button { background: #0EA5E9 !important; border-color: #0284C7 !important; color: #FFF !important; }
    .btn-primary div.stButton > button:hover { background: #0284C7 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. MÓDULO DE AUTENTICAÇÃO
# ==========================================
def render_auth():
    st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
    with st.form("auth_form"):
        st.markdown("<div class='auth-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='auth-header'>Apex Quant Terminal</div>", unsafe_allow_html=True)
        
        user_id = st.text_input("User ID", placeholder="Enter institutional ID")
        pass_key = st.text_input("Passkey", type="password", placeholder="••••••••")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='btn-primary'>", unsafe_allow_html=True)
        submit = st.form_submit_button("Authenticate Session", use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        if submit:
            if user_id == "admin" and pass_key == "admin":
                with st.spinner("Establishing secure connection..."):
                    time.sleep(0.5)
                    st.session_state.logged_in = True
                    st.session_state.user = user_id
                    st.rerun()
            else:
                st.error("Authentication failed. Verify credentials.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 4. MOTOR DE ESTATÍSTICAS
# ==========================================
def calculate_performance(df):
    resolved = df[df['Status'].isin(['Settled - Won', 'Settled - Lost'])].copy()
    if resolved.empty: return None
    
    # Lógica financeira Trademate
    resolved['Realized_PnL'] = resolved.apply(lambda r: r['Stake (€)'] * (r['Matched Odd'] - 1) if r['Status'] == 'Settled - Won' else -r['Stake (€)'], axis=1)
    resolved['EV_PnL'] = resolved['Stake (€)'] * ((resolved['Matched Odd'] / resolved['True Odd']) - 1)
    
    resolved['Cum_PnL'] = resolved['Realized_PnL'].cumsum()
    resolved['Cum_EV'] = resolved['EV_PnL'].cumsum()
    
    resolved['Peak'] = resolved['Cum_PnL'].cummax()
    resolved['Drawdown'] = resolved['Cum_PnL'] - resolved['Peak']
    
    return resolved

# ==========================================
# 5. DASHBOARD PRINCIPAL
# ==========================================
def render_terminal():
    with st.sidebar:
        st.markdown(f"<div style='color:#94A3B8; font-size:0.75rem; text-transform:uppercase;'>Session: {st.session_state.user}</div>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#1E293B; margin: 10px 0;'>", unsafe_allow_html=True)
        
        initial_capital = st.number_input("Starting Bankroll (€)", value=10000.0, step=1000.0, format="%.2f")
        
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
        if st.button("End Session", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    df_data = st.session_state.trade_ledger
    perf_data = calculate_performance(df_data)
    net_profit = perf_data['Realized_PnL'].sum() if perf_data is not None else 0
    current_capital = initial_capital + net_profit

    # Interface de Tabs minimalista
    tab_ledger, tab_analytics = st.tabs(["Trade Ledger", "Performance Analytics"])

    # --- TAB 1: REGISTO DE OPERAÇÕES (Trade Ledger) ---
    with tab_ledger:
        st.markdown("<h3 style='margin-top:0;'>Portfolio Ledger</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1: status_flt = st.selectbox("Status", ["All", "Pending", "Settled - Won", "Settled - Lost", "Voided"])
        with col2: mkt_flt = st.selectbox("Market", ["All"] + list(df_data['Market'].unique()))
        
        df_view = df_data.copy()
        if status_flt != "All": df_view = df_view[df_view['Status'] == status_flt]
        if mkt_flt != "All": df_view = df_view[df_view['Market'] == mkt_flt]

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tabela de dados rigorosa e sem distrações visuais
        edited_df = st.data_editor(
            df_view,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Settled - Won", "Settled - Lost", "Voided"], required=True),
                "Matched Odd": st.column_config.NumberColumn(format="%.2f"),
                "True Odd": st.column_config.NumberColumn(format="%.2f"),
                "Stake (€)": st.column_config.NumberColumn(format="%.2f"),
                "CLV": st.column_config.NumberColumn(format="%.4f"),
            },
            hide_index=True,
            height=600
        )

        if not edited_df.equals(df_view):
            st.session_state.trade_ledger.update(edited_df)
            st.rerun()

    # --- TAB 2: ANÁLISE QUANTITATIVA (Performance Analytics) ---
    with tab_analytics:
        st.markdown("<h3 style='margin-top:0;'>Quantitative Performance Review</h3>", unsafe_allow_html=True)
        
        if perf_data is None or perf_data.empty:
            st.info("Insufficient settled data for statistical analysis.")
        else:
            total_trades = len(perf_data)
            wins = len(perf_data[perf_data['Status'] == 'Settled - Won'])
            win_rate = wins / total_trades
            
            turnover = perf_data['Stake (€)'].sum()
            roi = (net_profit / turnover) * 100 if turnover > 0 else 0
            max_drawdown = perf_data['Drawdown'].min()
            clv_positive = len(perf_data[perf_data['CLV'] > 0]) / total_trades
            
            # Painel de métricas financeiras padrão
            m1, m2, m3, m4, m5 = st.columns(5)
            
            val_color = "val-pos" if net_profit > 0 else "val-neg"
            roi_color = "val-pos" if roi > 0 else "val-neg"
            
            with m1: st.markdown(f"<div class='metric-container'><div class='metric-label'>Net PnL</div><div class='metric-val {val_color}'>€{net_profit:,.2f}</div><div class='metric-sub'>Current Capital: €{current_capital:,.2f}</div></div>", unsafe_allow_html=True)
            with m2: st.markdown(f"<div class='metric-container'><div class='metric-label'>Turnover</div><div class='metric-val'>€{turnover:,.2f}</div><div class='metric-sub'>Yield/ROI: <span class='{roi_color}'>{roi:+.2f}%</span></div></div>", unsafe_allow_html=True)
            with m3: st.markdown(f"<div class='metric-container'><div class='metric-label'>Win Rate</div><div class='metric-val'>{win_rate:.1%}</div><div class='metric-sub'>Sample: {total_trades} Trades</div></div>", unsafe_allow_html=True)
            with m4: st.markdown(f"<div class='metric-container'><div class='metric-label'>Max Drawdown</div><div class='metric-val val-neg'>€{max_drawdown:,.2f}</div><div class='metric-sub'>Peak-to-Trough Drop</div></div>", unsafe_allow_html=True)
            with m5: st.markdown(f"<div class='metric-container'><div class='metric-label'>Closing Line Beaten</div><div class='metric-val' style='color:#38BDF8;'>{clv_positive:.1%}</div><div class='metric-sub'>Market Efficiency Metric</div></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráficos com design limpo (sem gridlines ruidosas, cores contidas)
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
            
            x_vals = list(range(len(perf_data)))
            
            # PnL Realizado vs Expected Value
            fig.add_trace(go.Scatter(x=x_vals, y=perf_data['Cum_PnL'], mode='lines', name='Realized PnL', line=dict(color='#10B981', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=x_vals, y=perf_data['Cum_EV'], mode='lines', name='Expected Value (CLV)', line=dict(color='#38BDF8', width=2, dash='dash')), row=1, col=1)
            
            # Drawdown isolado em baixo
            fig.add_trace(go.Scatter(x=x_vals, y=perf_data['Drawdown'], mode='lines', name='Drawdown', line=dict(color='#EF4444', width=1), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.1)'), row=2, col=1)
            
            fig.update_layout(
                height=600, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color="#94A3B8", family="Inter"),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            # Limpeza visual dos eixos
            fig.update_xaxes(showgrid=False, zeroline=False)
            fig.update_yaxes(title="PnL (€)", showgrid=True, gridcolor='rgba(30,41,59,0.5)', zeroline=True, zerolinecolor='#1E293B', row=1, col=1)
            fig.update_yaxes(title="Drawdown", showgrid=True, gridcolor='rgba(30,41,59,0.5)', zeroline=True, zerolinecolor='#1E293B', row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)

if st.session_state.logged_in:
    render_terminal()
else:
    render_auth()