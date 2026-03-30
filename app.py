import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import date, timedelta
import random
import time
import uuid

# ==========================================
# 1. SETUP DE ELITE & CONFIGURAÇÃO
# ==========================================
st.set_page_config(page_title="APEX QUANT | OS", layout="wide", initial_sidebar_state="collapsed")

def safe_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

# --- CSS INVISÍVEL & UI INSTITUCIONAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Reset Global */
    .stApp { background-color: #050810; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    header, footer { visibility: hidden; } /* Esconde o branding do Streamlit */
    
    /* Tipografia e Cards */
    h1, h2, h3, h4 { font-weight: 600; letter-spacing: -0.03em; color: #FFFFFF; }
    .glass-panel { background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(30, 41, 59, 0.8); border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
    
    /* HUD de Topo */
    .hud-container { display: flex; justify-content: space-between; align-items: center; background: #0B1120; border-bottom: 1px solid #1E293B; padding: 15px 30px; margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 999; }
    .hud-stat { display: flex; flex-direction: column; }
    .hud-label { font-size: 0.7rem; color: #64748B; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; }
    .hud-value { font-size: 1.4rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #F8FAFC; }
    .text-green { color: #10B981 !important; } .text-red { color: #EF4444 !important; } .text-blue { color: #38BDF8 !important; }
    
    /* Botões e Inputs */
    div.stButton > button { background: #1E293B; color: #F8FAFC; font-weight: 600; border-radius: 6px; border: 1px solid #334155; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); }
    div.stButton > button:hover { background: #38BDF8; color: #050810; border-color: #38BDF8; transform: translateY(-1px); }
    .btn-exec div.stButton > button { background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: #000; border: none; font-weight: 800; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3); }
    .btn-exec div.stButton > button:hover { box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5); }
    
    /* Tabs redesenhadas */
    .stTabs [data-baseweb="tab-list"] { background: #0B1120; border-radius: 8px; padding: 4px; gap: 4px; border: 1px solid #1E293B; }
    .stTabs [data-baseweb="tab"] { color: #64748B; font-weight: 600; font-size: 0.85rem; padding: 8px 16px; border-radius: 6px; border: none; background: transparent; }
    .stTabs [aria-selected="true"] { background: #1E293B !important; color: #F8FAFC !important; box-shadow: 0 1px 3px rgba(0,0,0,0.5); }
    
    /* IA Assistant Box */
    .ai-box { background: linear-gradient(180deg, rgba(56,189,248,0.05) 0%, rgba(15,23,42,0) 100%); border-left: 3px solid #38BDF8; padding: 15px 20px; border-radius: 0 8px 8px 0; font-size: 0.9rem; line-height: 1.6; color: #CBD5E1; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. GERADOR DE DADOS & ESTADO DA APP
# ==========================================
def init_ledger():
    np.random.seed(42)
    teams = ["Real Madrid", "Man City", "Arsenal", "Bayern", "Inter", "Liverpool", "Barcelona"]
    history = []
    start_d = date.today() - timedelta(days=90)
    for _ in range(300):
        odd_comp = round(random.uniform(1.60, 3.50), 2)
        clv = np.random.normal(loc=0.035, scale=0.03) # CLV Positivo médio
        prob_win = 1 / (odd_comp / (1 + clv))
        stake = round(random.uniform(50, 150), 2)
        won = random.random() < prob_win
        history.append({
            "ID": str(uuid.uuid4())[:8],
            "Date": (start_d + timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d'),
            "Event": f"{random.choice(teams)} v {random.choice(teams)}",
            "Market": random.choice(["Match Odds - Home", "Over 2.5 Goals", "Asian Handicap -0.5", "BTTS - Yes"]),
            "Matched Odd": odd_comp, "True Odd": round(odd_comp / (1 + clv), 2),
            "Stake (€)": stake, "CLV": round(clv, 4),
            "Status": "Settled - Won" if won else "Settled - Lost"
        })
    df = pd.DataFrame(history)
    return df.sort_values("Date").reset_index(drop=True)

if 'user' not in st.session_state: st.session_state.user = None
if 'ledger' not in st.session_state: st.session_state.ledger = init_ledger()
if 'init_bk' not in st.session_state: st.session_state.init_bk = 10000.0
if 'kelly_frac' not in st.session_state: st.session_state.kelly_frac = 0.25

# ==========================================
# 3. CORE MATEMÁTICO AVANÇADO (DIXON-COLES)
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041")
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def safe_flt(v, df=1.35): return max(float(v), 0.1) if v else df

@st.cache_data(ttl=1800)
def fetch_api(endpoint, params):
    try: return requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=8).json().get('response', [])
    except: return []

def run_dixon_coles_math(xg_h, xg_a, rho=-0.15):
    """
    O Ajuste de Dixon-Coles corrige a falha do Poisson normal que subestima 
    resultados de baixo score (0-0, 1-0, 0-1, 1-1). Essencial para edges precisos.
    """
    max_g = 8
    mtx = np.outer(poisson.pmf(np.arange(max_g), xg_h), poisson.pmf(np.arange(max_g), xg_a))
    
    # Aplicação do Fator Tau (Dixon-Coles)
    tau_00 = max(0, 1 - (xg_h * xg_a * rho))
    tau_10 = max(0, 1 + (xg_h * rho))
    tau_01 = max(0, 1 + (xg_a * rho))
    tau_11 = max(0, 1 - rho)
    
    mtx[0,0] *= tau_00; mtx[1,0] *= tau_10; mtx[0,1] *= tau_01; mtx[1,1] *= tau_11
    mtx /= mtx.sum() # Normalizar
    
    g_sum = np.add.outer(np.arange(max_g), np.arange(max_g))
    diff = np.subtract.outer(np.arange(max_g), np.arange(max_g))
    
    return {
        "Match Odds - Home": mtx[diff > 0].sum(), "Match Odds - Draw": mtx[diff == 0].sum(), "Match Odds - Away": mtx[diff < 0].sum(),
        "Over 1.5 Goals": mtx[g_sum > 1.5].sum(), "Under 1.5 Goals": mtx[g_sum < 1.5].sum(),
        "Over 2.5 Goals": mtx[g_sum > 2.5].sum(), "Under 2.5 Goals": mtx[g_sum < 2.5].sum(),
        "BTTS - Yes": 1 - (mtx[:, 0].sum() + mtx[0, :].sum() - mtx[0,0]),
        "Asian Handicap -1.5": mtx[diff > 1].sum()
    }, mtx

# ==========================================
# 4. ORACLE AI - ASSISTENTE QUANTITATIVO
# ==========================================
def generate_ai_insight(t_home, t_away, xg_h, xg_a, valid_bets):
    """Gera uma análise em linguagem natural simulando um analista quant."""
    diff = abs(xg_h - xg_a)
    
    insight = f"**System Scan:** Matchup indicates a "
    if diff > 1.0: insight += f"heavy tactical dominance for **{'Home' if xg_h > xg_a else 'Away'}**. "
    elif diff < 0.3: insight += "tight, mean-reverting script with high draw probability. "
    else: insight += "moderate advantage scenario. "
    
    if (xg_h + xg_a) > 3.0: insight += "Expected Goals model predicts a high-variance shootout. "
    elif (xg_h + xg_a) < 2.2: insight += "Dixon-Coles adjustment flags this as a low-scoring, structured match. "

    if not valid_bets:
        insight += "\n\n🛡️ **Conclusion:** The Asian syndicates have priced this efficiently. **No actionable EV found.**"
    else:
        best = valid_bets[0]
        insight += f"\n\n🔥 **ALPHA DETECTED:** Bookmakers mispriced **{best['Market']}**. They imply a {1/best['Odd']:.1%} chance, but our pure math model dictates {best['Prob']:.1%}. **Execute for a {best['Edge']*100:.1f}% Yield.**"
        
    return insight

# ==========================================
# 5. CÁLCULO DE PERFORMANCE GLOBAL
# ==========================================
def get_portfolio_metrics():
    df = st.session_state.ledger
    res = df[df['Status'].isin(['Settled - Won', 'Settled - Lost'])].copy()
    
    if res.empty: return {"pnl": 0, "roi": 0, "wr": 0, "pending": 0}
    
    res['PnL'] = res.apply(lambda r: r['Stake (€)'] * (r['Matched Odd'] - 1) if r['Status'] == 'Settled - Won' else -r['Stake (€)'], axis=1)
    pnl = res['PnL'].sum()
    turnover = res['Stake (€)'].sum()
    roi = (pnl / turnover) * 100 if turnover > 0 else 0
    wr = len(res[res['Status'] == 'Settled - Won']) / len(res)
    pending = df[df['Status'] == 'Pending']['Stake (€)'].sum()
    
    return {"pnl": pnl, "roi": roi, "wr": wr, "pending": pending, "df": res}

# ==========================================
# 6. LOGIN ULTRA-RÁPIDO
# ==========================================
if not st.session_state.user:
    st.markdown("<div style='height:20vh;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<h1 style='text-align:center; font-family:\"JetBrains Mono\"; font-size:3rem; margin-bottom:0;'>APEX<span class='text-blue'>OS</span></h1><p style='text-align:center; color:#64748B; letter-spacing:2px; font-size:0.8rem;'>QUANTITATIVE TRADING ENVIRONMENT</p>", unsafe_allow_html=True)
        with st.form("login"):
            st.text_input("Access Key", type="password", placeholder="Press Enter to Authenticate (Type anything)", key="pwd")
            if st.form_submit_button("INITIALIZE", use_container_width=True):
                st.session_state.user = "QUANT_ALPHA"
                safe_rerun()
    st.stop()

# ==========================================
# 7. MAIN DASHBOARD (A OBRA-PRIMA)
# ==========================================
metrics = get_portfolio_metrics()
current_bk = st.session_state.init_bk + metrics['pnl']

# --- TOP HUD (Sempre visível, sem fadiga) ---
st.markdown(f"""
    <div class="hud-container">
        <div><div style="font-family:'JetBrains Mono'; font-weight:700; color:#38BDF8; font-size:1.2rem;">APEX<span style="color:#FFF;">QUANT</span></div><div style="font-size:0.6rem; color:#64748B;">SYSTEM ONLINE</div></div>
        <div class="hud-stat"><span class="hud-label">Bankroll</span><span class="hud-value">€{current_bk:,.2f}</span></div>
        <div class="hud-stat"><span class="hud-label">Net Profit</span><span class="hud-value {'text-green' if metrics['pnl']>=0 else 'text-red'}">{metrics['pnl']:+,.2f}</span></div>
        <div class="hud-stat"><span class="hud-label">Yield (ROI)</span><span class="hud-value {'text-green' if metrics['roi']>=0 else 'text-red'}">{metrics['roi']:+.2f}%</span></div>
        <div class="hud-stat"><span class="hud-label">Win Rate</span><span class="hud-value">{metrics['wr']:.1%}</span></div>
        <div class="hud-stat"><span class="hud-label">Exposure</span><span class="hud-value text-blue">€{metrics['pending']:,.2f}</span></div>
    </div>
""", unsafe_allow_html=True)

# --- LAYOUT PRINCIPAL ---
c_left, c_main, c_right = st.columns([1, 2.5, 1.5], gap="large")

# === COLUNA ESQUERDA: CONTROLO E MERCADO ===
with c_left:
    st.markdown("<h4 style='color:#64748B; font-size:0.8rem; text-transform:uppercase;'>System Controls</h4>", unsafe_allow_html=True)
    with st.container():
        target_date = st.date_input("Market Date", date.today(), label_visibility="collapsed")
        l_map = {"Premier League": 39, "La Liga": 140, "Champions League": 2, "Primeira Liga": 94}
        league = st.selectbox("Tournament", list(l_map.keys()), label_visibility="collapsed")
        
        st.session_state.kelly_frac = st.select_slider("Risk Profile (Kelly)", options=[0.1, 0.25, 0.5, 1.0], value=st.session_state.kelly_frac, format_func=lambda x: f"{x}x Kelly")

    st.markdown("<br><h4 style='color:#64748B; font-size:0.8rem; text-transform:uppercase;'>Event Scanner</h4>", unsafe_allow_html=True)
    fixtures = fetch_api("fixtures", {"date": target_date.strftime('%Y-%m-%d'), "league": l_map[league], "season": "2025"})
    
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fixtures}
        m_display = st.selectbox("Select Match", list(m_map.keys()), label_visibility="collapsed")
        m_sel = m_map[m_display]
        st.button("🔄 Force Refresh API", use_container_width=True)
    else:
        st.info("No fixtures found.")

# === COLUNA CENTRAL: MOTOR QUANTITATIVO & EXECUÇÃO ===
with c_main:
    if not m_sel:
        st.markdown("<div style='text-align:center; padding-top:100px; opacity:0.3;'><h1 style='font-size:4rem;'>AWAITING INPUT</h1><p>Select an event from the scanner.</p></div>", unsafe_allow_html=True)
    else:
        with st.spinner("Processing Dixon-Coles Matrices..."):
            h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
            h_name, a_name = m_sel['teams']['home']['name'], m_sel['teams']['away']['name']
            
            # Dados Mock rápidos para fluidez da demo (Na vida real, usas o fetch_api stats)
            xg_h, xg_a = round(random.uniform(1.1, 2.5), 2), round(random.uniform(0.8, 1.9), 2)
            
            probs, mtx = run_dixon_coles_math(xg_h, xg_a, rho=-0.13)
            
            # Mock de Odds da API
            live_odds = {k: max(1.01, round((1/v) * random.uniform(0.95, 1.10), 2)) for k, v in probs.items() if v > 0}
            
            # Encontrar Edges
            edges = []
            for mkt, prob in probs.items():
                odd = live_odds.get(mkt, 0)
                if odd > 1.05 and prob > 0:
                    edge = (prob * odd) - 1
                    if edge > 0:
                        stake = current_bk * ((edge / (odd - 1)) * st.session_state.kelly_frac)
                        edges.append({"Market": mkt, "Prob": prob, "Odd": odd, "TrueOdd": 1/prob, "Edge": edge, "RecStake": stake})
            edges = sorted(edges, key=lambda x: x["Edge"], reverse=True)

        # Header do Jogo
        st.markdown(f"""
        <div class="glass-panel" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <div style="flex:1;"><div style="font-size:1.8rem; font-weight:700;">{h_name}</div><div style="color:#38BDF8; font-family:'JetBrains Mono';">xG: {xg_h:.2f}</div></div>
            <div style="font-size:1.2rem; color:#64748B; font-weight:700; padding:0 30px;">VS</div>
            <div style="flex:1; text-align:right;"><div style="font-size:1.8rem; font-weight:700;">{a_name}</div><div style="color:#38BDF8; font-family:'JetBrains Mono';">xG: {xg_a:.2f}</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Oracle AI Insight
        st.markdown(f"<div class='ai-box'>🤖 <b>Oracle AI:</b> {generate_ai_insight(h_name, a_name, xg_h, xg_a, edges)}</div><br>", unsafe_allow_html=True)

        # Smart Execution (Order Book Style)
        st.markdown("<h4 style='color:#F8FAFC; border-bottom:1px solid #1E293B; padding-bottom:10px;'>Alpha Execution Board</h4>", unsafe_allow_html=True)
        if not edges:
            st.warning("Market Efficient. No EV+ bets detected.")
        else:
            for i, b in enumerate(edges[:3]): # Mostra os top 3 edges
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1.2])
                with c1: st.markdown(f"<div style='font-weight:600; font-size:1.1rem; padding-top:10px;'>{b['Market']}</div><div style='color:#10B981; font-size:0.8rem; font-weight:700;'>EDGE: +{b['Edge']:.1%}</div>", unsafe_allow_html=True)
                with c2: st.markdown(f"<div style='color:#64748B; font-size:0.7rem;'>API ODD</div><div style='font-family:monospace; font-size:1.2rem;'>{b['Odd']:.2f}</div>", unsafe_allow_html=True)
                with c3: st.markdown(f"<div style='color:#64748B; font-size:0.7rem;'>TRUE ODD</div><div style='color:#38BDF8; font-family:monospace; font-size:1.2rem;'>{b['TrueOdd']:.2f}</div>", unsafe_allow_html=True)
                with c4:
                    st.markdown("<div class='btn-exec' style='padding-top:8px;'>", unsafe_allow_html=True)
                    if st.button(f"BUY €{b['RecStake']:.0f}", key=f"buy_{i}", use_container_width=True):
                        new_trade = pd.DataFrame([{"ID": str(uuid.uuid4())[:8], "Date": date.today().strftime('%Y-%m-%d'), "Event": f"{h_name} v {a_name}", "Market": b["Market"], "Matched Odd": b["Odd"], "True Odd": round(b["TrueOdd"], 2), "Stake (€)": round(b['RecStake'], 2), "CLV": round(b["Edge"], 4), "Status": "Pending"}])
                        st.session_state.ledger = pd.concat([st.session_state.ledger, new_trade], ignore_index=True)
                        st.toast(f"Order filled: {b['Market']}", icon="⚡")
                        time.sleep(0.3)
                        safe_rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<hr style='border-color:#1E293B; margin:10px 0;'>", unsafe_allow_html=True)

# === COLUNA DIREITA: ANALYTICS & LEDGER RÁPIDO ===
with c_right:
    tab_graph, tab_book = st.tabs(["Performance Curve", "Active Ledger"])
    
    with tab_graph:
        df_chart = metrics['df']
        if df_chart is not None and not df_chart.empty:
            df_chart['Cum_PnL'] = df_chart['PnL'].cumsum()
            df_chart['Cum_EV'] = (df_chart['Stake (€)'] * ((df_chart['Matched Odd'] / df_chart['True Odd']) - 1)).cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=df_chart['Cum_PnL'], mode='lines', name='Actual PnL', line=dict(color='#10B981', width=2), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.1)'))
            fig.add_trace(go.Scatter(y=df_chart['Cum_EV'], mode='lines', name='Expected (CLV)', line=dict(color='#38BDF8', width=2, dash='dash')))
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#64748B"), margin=dict(l=0, r=0, t=10, b=0), legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
            fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
            fig.update_yaxes(showgrid=True, gridcolor='rgba(30,41,59,0.5)', zeroline=True, zerolinecolor='#1E293B')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab_book:
        st.markdown("<div style='font-size:0.8rem; color:#64748B; margin-bottom:10px;'>Recent Transactions (Editable)</div>", unsafe_allow_html=True)
        # Mostrar apenas os últimos 15 para eficiência, ordenados por data decrescente
        df_display = st.session_state.ledger.sort_values(by="Date", ascending=False).head(15).copy()
        
        edited = st.data_editor(
            df_display,
            column_order=["Event", "Market", "Status", "Stake (€)"],
            column_config={
                "Event": st.column_config.TextColumn(disabled=True),
                "Market": st.column_config.TextColumn(disabled=True),
                "Stake (€)": st.column_config.NumberColumn(format="€%.0f", disabled=True),
                "Status": st.column_config.SelectboxColumn(options=["Pending", "Settled - Won", "Settled - Lost", "Voided"])
            },
            hide_index=True, use_container_width=True, height=400
        )
        
        # Sincronização segura via ID único
        if not edited.equals(df_display):
            for idx, row in edited.iterrows():
                original_status = df_display.loc[idx, 'Status']
                if row['Status'] != original_status:
                    ledger_idx = st.session_state.ledger[st.session_state.ledger['ID'] == row['ID']].index[0]
                    st.session_state.ledger.at[ledger_idx, 'Status'] = row['Status']
            safe_rerun()