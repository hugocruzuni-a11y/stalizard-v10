import streamlit as st
import numpy as np
from scipy.stats import poisson, norm
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import date, timedelta
import random
import time
import uuid

# ==========================================
# 1. SETUP DE ELITE (WALL STREET LEVEL)
# ==========================================
st.set_page_config(page_title="APEX QUANT | INSTITUTIONAL", layout="wide", initial_sidebar_state="collapsed")

def safe_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

# --- CSS ULTRA-PREMIUM (BLOOMBERG / PALANTIR AESTHETIC) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700;800&display=swap');
    
    .stApp { background-color: #030508; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    header, footer { visibility: hidden; } 
    
    /* Live Ticker Tape */
    .ticker-wrap { width: 100%; background-color: #0B1120; border-bottom: 1px solid #1E293B; margin-top: -3rem; padding: 5px 0; overflow: hidden; position: sticky; top: 0; z-index: 1000; display: flex; align-items: center; }
    .ticker-title { background: #D4AF37; color: #000; font-weight: 800; font-size: 0.7rem; padding: 4px 15px; text-transform: uppercase; letter-spacing: 1px; z-index: 2; margin-left: 10px; border-radius: 2px; }
    .ticker { display: inline-block; white-space: nowrap; padding-left: 100%; animation: ticker 40s linear infinite; font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #94A3B8; }
    @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .ticker-item { display: inline-block; padding: 0 2rem; border-right: 1px solid #1E293B; }
    .tick-up { color: #10B981; } .tick-down { color: #EF4444; }
    
    /* Executive HUD */
    .hud-container { display: flex; justify-content: space-between; align-items: center; background: linear-gradient(180deg, #070B14 0%, #030508 100%); padding: 20px 30px; border-bottom: 2px solid #1E293B; margin: 0 -3rem 2rem -3rem; }
    .hud-brand { font-family:'JetBrains Mono'; font-weight:800; color:#D4AF37; font-size:1.8rem; letter-spacing:-1px; text-shadow: 0 0 20px rgba(212,175,55,0.2); }
    .hud-stat { display: flex; flex-direction: column; align-items: flex-end; padding: 0 15px; border-right: 1px solid rgba(30,41,59,0.5); }
    .hud-stat:last-child { border-right: none; }
    .hud-label { font-size: 0.65rem; color: #64748B; text-transform: uppercase; font-weight: 800; letter-spacing: 1.5px; margin-bottom: 2px; }
    .hud-value { font-size: 1.6rem; font-family: 'JetBrains Mono', monospace; font-weight: 800; color: #F8FAFC; }
    .text-gold { color: #D4AF37 !important; } .text-cyan { color: #00F0FF !important; }
    
    /* Panels & Glassmorphism */
    .exec-panel { background: rgba(11, 17, 32, 0.7); border: 1px solid #1E293B; border-radius: 6px; padding: 20px; position: relative; overflow: hidden; }
    .exec-panel::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, #00F0FF, transparent); opacity: 0.5; }
    
    /* Order Execution Block */
    .order-block { background: #070B14; border: 1px solid #1E293B; border-left: 3px solid #D4AF37; padding: 15px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
    .btn-exec div.stButton > button { background: #D4AF37; color: #000; border: none; font-weight: 800; font-family: 'JetBrains Mono'; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; transition: all 0.2s; box-shadow: 0 0 15px rgba(212,175,55,0.2); }
    .btn-exec div.stButton > button:hover { background: #FFD700; transform: scale(1.02); box-shadow: 0 0 25px rgba(212,175,55,0.4); }
    
    /* Typography */
    .section-title { font-size: 0.8rem; color: #64748B; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
    .section-title::after { content: ''; flex-grow: 1; height: 1px; background: #1E293B; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE (FUND SIZE)
# ==========================================
def init_ledger():
    np.random.seed(42)
    teams = ["Real Madrid", "Man City", "Arsenal", "Bayern", "Inter", "Liverpool"]
    history = []
    start_d = date.today() - timedelta(days=120)
    for _ in range(400):
        odd_comp = round(random.uniform(1.70, 3.50), 2)
        clv = np.random.normal(loc=0.04, scale=0.035) 
        prob_win = 1 / (odd_comp / (1 + clv))
        stake = round(random.uniform(500, 2500), 2) # Stakes Institucionais
        won = random.random() < prob_win
        history.append({
            "ID": str(uuid.uuid4())[:8], "Date": (start_d + timedelta(days=random.randint(0, 120))).strftime('%Y-%m-%d'),
            "Event": f"{random.choice(teams)} v {random.choice(teams)}", "Market": random.choice(["Home Win", "Over 2.5", "AH -1.0"]),
            "Matched Odd": odd_comp, "True Odd": round(odd_comp / (1 + clv), 2),
            "Stake (€)": stake, "CLV": round(clv, 4), "Status": "Settled - Won" if won else "Settled - Lost"
        })
    return pd.DataFrame(history).sort_values("Date").reset_index(drop=True)

if 'user' not in st.session_state: st.session_state.user = None
if 'ledger' not in st.session_state: st.session_state.ledger = init_ledger()
if 'init_bk' not in st.session_state: st.session_state.init_bk = 1000000.0 # 1 Milhão Banca Inicial
if 'kelly_frac' not in st.session_state: st.session_state.kelly_frac = 0.25

# ==========================================
# 3. QUANTS & MONTE CARLO ENGINE
# ==========================================
def run_monte_carlo_sim(xg_h, xg_a, sims=10000):
    """Simula o jogo 10,000 vezes para criar curvas de distribuição."""
    np.random.seed(int(time.time()))
    home_goals = np.random.poisson(xg_h, sims)
    away_goals = np.random.poisson(xg_a, sims)
    goal_diff = home_goals - away_goals
    total_goals = home_goals + away_goals
    
    hw = np.sum(goal_diff > 0) / sims
    dr = np.sum(goal_diff == 0) / sims
    aw = np.sum(goal_diff < 0) / sims
    o25 = np.sum(total_goals > 2) / sims
    
    # Criar dados para o sino de Gauss (Goal Difference)
    mu, std = norm.fit(goal_diff)
    x_axis = np.linspace(-5, 5, 100)
    p = norm.pdf(x_axis, mu, std)
    
    return {"HW": hw, "D": dr, "AW": aw, "O25": o25}, x_axis, p

def get_portfolio_metrics():
    df = st.session_state.ledger
    res = df[df['Status'].isin(['Settled - Won', 'Settled - Lost'])].copy()
    if res.empty: return {"pnl": 0, "roi": 0, "wr": 0, "sharpe": 0, "var_95": 0, "df": res}
    
    res['PnL'] = res.apply(lambda r: r['Stake (€)'] * (r['Matched Odd'] - 1) if r['Status'] == 'Settled - Won' else -r['Stake (€)'], axis=1)
    pnl = res['PnL'].sum()
    turnover = res['Stake (€)'].sum()
    roi = (pnl / turnover) * 100 if turnover > 0 else 0
    wr = len(res[res['Status'] == 'Settled - Won']) / len(res)
    
    # Risk Metrics
    daily_returns = res['PnL']
    sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(len(res)) if daily_returns.std() > 0 else 0
    var_95 = np.percentile(daily_returns, 5) # Value at Risk 95%
    
    return {"pnl": pnl, "roi": roi, "wr": wr, "sharpe": sharpe, "var_95": var_95, "df": res}

# ==========================================
# 4. LOGIN SCREEN (SECURE TERMINAL)
# ==========================================
if not st.session_state.user:
    st.markdown("<div style='height:25vh;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; font-family:\"JetBrains Mono\"; font-size:3.5rem; margin-bottom:0; color:#D4AF37;'>APEX<span style='color:#FFF;'>QUANT</span></h1><p style='text-align:center; color:#64748B; letter-spacing:4px; font-size:0.7rem; font-weight:800;'>INSTITUTIONAL GRADE TERMINAL</p>", unsafe_allow_html=True)
        with st.form("login"):
            st.text_input("G-7 Security Clearance Key", type="password", placeholder="Authorize Access", key="pwd")
            st.markdown("<div class='btn-exec'>", unsafe_allow_html=True)
            if st.form_submit_button("CONNECT TO EXCHANGE", use_container_width=True):
                st.session_state.user = "CEO_ACCESS"
                safe_rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 5. RENDERIZAÇÃO DO TERMINAL
# ==========================================
metrics = get_portfolio_metrics()
current_bk = st.session_state.init_bk + metrics['pnl']

# --- LIVE TICKER ---
st.markdown("""
<div class="ticker-wrap">
    <div class="ticker-title">LIVE FEED</div>
    <div class="ticker">
        <span class="ticker-item">PINNACLE: ASIAN HANDICAP LIQUIDITY SPIKE DETECTED</span>
        <span class="ticker-item">SYS_EXEC: BOUGHT €2,400 O2.5 @ 1.95 <span class="tick-up">(+3.2% CLV)</span></span>
        <span class="ticker-item">PORTFOLIO SHARPE RATIO: 1.84 <span class="tick-up">▲</span></span>
        <span class="ticker-item">MARKET EFFICIENCY INDEX: 84.2%</span>
        <span class="ticker-item">VAR (95%): €-14,200 <span class="tick-down">▼</span></span>
        <span class="ticker-item">ASIAN SYNDICATE ACTIVITY: HIGH VOLATILITY ON PREMIER LEAGUE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- EXECUTIVE HUD ---
st.markdown(f"""
<div class="hud-container">
    <div class="hud-brand">APEX<span style="color:#FFF;">QUANT</span> <span style="font-size:0.5rem; color:#00F0FF; vertical-align:top;">PRO</span></div>
    <div style="display:flex;">
        <div class="hud-stat"><span class="hud-label">AUM (Assets Under Mgt)</span><span class="hud-value">€{current_bk:,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Net Profit</span><span class="hud-value {'tick-up' if metrics['pnl']>=0 else 'tick-down'}">{metrics['pnl']:+,.0f}</span></div>
        <div class="hud-stat"><span class="hud-label">Yield / Win Rate</span><span class="hud-value text-gold">{metrics['roi']:+.2f}% / {metrics['wr']:.1%}</span></div>
        <div class="hud-stat"><span class="hud-label">Sharpe Ratio</span><span class="hud-value text-cyan">{metrics['sharpe']:.2f}</span></div>
        <div class="hud-stat"><span class="hud-label" title="Value at Risk (95%)">Daily VaR (95%)</span><span class="hud-value tick-down">€{abs(metrics['var_95']):,.0f}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- TRIPLE COLUMN LAYOUT ---
c_left, c_main, c_right = st.columns([1, 2.5, 1.2], gap="large")

# === LEFT: MARKET SCANNER ===
with c_left:
    st.markdown("<div class='section-title'>I. Global Scanner</div>", unsafe_allow_html=True)
    target_date = st.date_input("Trading Session", date.today(), label_visibility="collapsed")
    l_map = {"Premier League": 39, "La Liga": 140, "Champions League": 2, "Primeira Liga": 94}
    league = st.selectbox("Market Tier", list(l_map.keys()), label_visibility="collapsed")
    
    st.markdown("<br><div class='section-title'>Risk Protocol</div>", unsafe_allow_html=True)
    st.session_state.kelly_frac = st.select_slider("Kelly Multiplier", options=[0.1, 0.25, 0.5, 1.0], value=st.session_state.kelly_frac, format_func=lambda x: f"{x}x (Conservative)" if x<0.5 else f"{x}x (Aggressive)")

    # Fake fixture fetch for layout
    matches = ["Arsenal v Man City", "Real Madrid v Barcelona", "Bayern v Dortmund", "Inter v Juventus"]
    m_sel = st.selectbox("Select Target Event", matches)

# === MAIN: QUANTS ENGINE & EXECUTION ===
with c_main:
    st.markdown("<div class='section-title'>II. Algorithmic Intelligence (10k Monte Carlo)</div>", unsafe_allow_html=True)
    
    # 1. Monte Carlo Visuais
    xg_h, xg_a = 2.15, 1.45 # Hardcoded for demo impressiveness
    probs, x_axis, norm_pdf = run_monte_carlo_sim(xg_h, xg_a)
    
    c_m1, c_m2 = st.columns([1, 1])
    with c_m1:
        st.markdown(f"""
        <div class="exec-panel">
            <div style="font-size:0.7rem; color:#00F0FF; margin-bottom:10px; font-family:'JetBrains Mono';">MATCHUP DYNAMICS</div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-size:1.5rem; font-weight:800;">{m_sel.split(' v ')[0]}</div>
                <div style="font-family:'JetBrains Mono'; color:#D4AF37; font-size:1.2rem;">xG {xg_h}</div>
            </div>
            <div style="color:#64748B; font-weight:800; font-size:0.8rem; text-align:center; margin:5px 0;">VS</div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-size:1.5rem; font-weight:800;">{m_sel.split(' v ')[1]}</div>
                <div style="font-family:'JetBrains Mono'; color:#D4AF37; font-size:1.2rem;">xG {xg_a}</div>
            </div>
            <hr style='border-color:#1E293B;'>
            <div style="font-size:0.7rem; color:#64748B;">MONTE CARLO TRUE PROBABILITIES:</div>
            <div style="display:flex; justify-content:space-between; margin-top:5px; font-family:'JetBrains Mono';">
                <div>HW: <span style='color:#FFF;'>{probs['HW']:.1%}</span></div>
                <div>D: <span style='color:#FFF;'>{probs['D']:.1%}</span></div>
                <div>AW: <span style='color:#FFF;'>{probs['AW']:.1%}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_m2:
        # Gráfico Monte Carlo Gaussiano
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_axis, y=norm_pdf, mode='lines', line=dict(color='#00F0FF', width=2), fill='tozeroy', fillcolor='rgba(0, 240, 255, 0.1)', name="Goal Diff PDF"))
        fig.add_vline(x=0, line_dash="dash", line_color="#EF4444", annotation_text="Draw Line")
        fig.update_layout(height=180, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
        fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 2. Sharp vs Soft Bookie Arbitrage
    st.markdown("<br><div class='section-title'>III. Sharp Arbitrage & Execution</div>", unsafe_allow_html=True)
    
    # Simular Value Bet encontrada
    target_mkt = "Match Odds - Home"
    prob_real = probs['HW']
    true_odd = 1 / prob_real
    pinny_odd = true_odd * 1.01 # Linha Sharp (Pinnacle) quase perfeita
    soft_odd = 1.95 # Linha Soft (Bet365/Betano) com erro
    edge = (prob_real * soft_odd) - 1
    
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; text-align:center; background:#0B1120; border:1px solid #1E293B; border-radius:6px; padding:10px; margin-bottom:15px; font-family:'JetBrains Mono';">
        <div><div style="font-size:0.6rem; color:#64748B;">APEX TRUE ODD</div><div style="font-size:1.2rem; color:#00F0FF;">{true_odd:.2f}</div></div>
        <div><div style="font-size:0.6rem; color:#64748B;">PINNACLE (SHARP)</div><div style="font-size:1.2rem; color:#FFF;">{pinny_odd:.2f}</div></div>
        <div><div style="font-size:0.6rem; color:#64748B;">SOFT BOOKIE</div><div style="font-size:1.2rem; color:#D4AF37;">{soft_odd:.2f}</div></div>
        <div><div style="font-size:0.6rem; color:#64748B;">DETECTED EDGE</div><div style="font-size:1.2rem; color:#10B981;">+{edge:.1%}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Execution Block
    stake = current_bk * ((edge / (soft_odd - 1)) * st.session_state.kelly_frac)
    st.markdown(f"""
    <div class="order-block">
        <div>
            <div style="font-size:0.7rem; color:#D4AF37; font-family:'JetBrains Mono'; font-weight:800;">ORDER READY</div>
            <div style="font-size:1.4rem; font-weight:800; color:#FFF;">{target_mkt}</div>
            <div style="font-size:0.8rem; color:#94A3B8;">Position Size: €{stake:,.0f} | Target ROI: €{(stake * (soft_odd-1)):,.0f}</div>
        </div>
        <div class="btn-exec" style="width:200px;">
    """, unsafe_allow_html=True)
    
    if st.button("EXECUTE ALPHA", key="exec_main"):
        new_trade = pd.DataFrame([{"ID": str(uuid.uuid4())[:8], "Date": date.today().strftime('%Y-%m-%d'), "Event": m_sel, "Market": target_mkt, "Matched Odd": soft_odd, "True Odd": round(true_odd, 2), "Stake (€)": round(stake, 2), "CLV": round(edge, 4), "Status": "Pending"}])
        st.session_state.ledger = pd.concat([st.session_state.ledger, new_trade], ignore_index=True)
        st.toast(f"€{stake:,.0f} Executed securely.", icon="💰")
        time.sleep(0.3)
        safe_rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)

# === RIGHT: PORTFOLIO & LEDGER ===
with c_right:
    st.markdown("<div class='section-title'>IV. Portfolio Equity</div>", unsafe_allow_html=True)
    
    df_chart = metrics['df']
    if not df_chart.empty:
        df_chart['Cum_PnL'] = df_chart['PnL'].cumsum()
        
        fig = go.Figure()
        # Preenchimento em gradiente estilo Hedge Fund
        fig.add_trace(go.Scatter(y=df_chart['Cum_PnL'], mode='lines', name='Net Profit', line=dict(color='#D4AF37', width=2), fill='tozeroy', fillcolor='rgba(212, 175, 55, 0.1)'))
        fig.update_layout(height=220, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#64748B"), margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
        fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(30,41,59,0.5)', zeroline=True, zerolinecolor='#1E293B', tickprefix="€")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<br><div class='section-title'>Active Ledger</div>", unsafe_allow_html=True)
    df_display = st.session_state.ledger.sort_values(by="Date", ascending=False).head(10).copy()
    
    edited = st.data_editor(
        df_display,
        column_order=["Market", "Stake (€)", "Status"],
        column_config={
            "Market": st.column_config.TextColumn(width="medium", disabled=True),
            "Stake (€)": st.column_config.NumberColumn(format="€%d", disabled=True),
            "Status": st.column_config.SelectboxColumn(options=["Pending", "Settled - Won", "Settled - Lost"])
        },
        hide_index=True, use_container_width=True, height=280
    )
    
    if not edited.equals(df_display):
        for idx, row in edited.iterrows():
            if row['Status'] != df_display.loc[idx, 'Status']:
                ledger_idx = st.session_state.ledger[st.session_state.ledger['ID'] == row['ID']].index[0]
                st.session_state.ledger.at[ledger_idx, 'Status'] = row['Status']
        safe_rerun()