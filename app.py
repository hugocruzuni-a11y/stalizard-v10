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

# ==========================================
# 1. CONFIGURAÇÃO DE ESTADO E AMBIENTE
# ==========================================
st.set_page_config(
    page_title="Apex Quant | Institutional Terminal", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

def safe_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

def generate_institutional_history():
    np.random.seed(42)
    teams = ["Benfica", "Porto", "Sporting", "Braga", "Real Madrid", "Barcelona", "Arsenal", "Man City", "Liverpool", "Bayern", "Juventus"]
    mkts = ["Match Odds - Home", "Match Odds - Away", "Over 2.5 Goals", "Under 2.5 Goals", "BTTS - Yes"]
    history = []
    date_start = date.today() - timedelta(days=180)
    for _ in range(500):
        d = date_start + timedelta(days=random.randint(0, 180))
        t1, t2 = random.sample(teams, 2)
        odd_comp = round(random.uniform(1.60, 3.50), 2)
        clv = np.random.normal(loc=0.03, scale=0.04)
        prob_win = 1 / (odd_comp / (1 + clv))
        stake = round(random.uniform(50, 250), 2)
        history.append({
            "Date": d.strftime('%Y-%m-%d'), "Event": f"{t1} v {t2}", "Market": random.choice(mkts),
            "Matched Odd": odd_comp, "True Odd": round((odd_comp / (1 + clv)), 2),
            "Stake (€)": stake, "CLV": round(clv, 4), "Status": "Settled - Won" if random.random() < prob_win else "Settled - Lost"
        })
    df = pd.DataFrame(history)
    df['Date'] = pd.to_datetime(df['Date'])
    return df.sort_values("Date").reset_index(drop=True).assign(Date=lambda x: x['Date'].dt.strftime('%Y-%m-%d'))

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'trade_ledger' not in st.session_state: st.session_state.trade_ledger = generate_institutional_history()

# ==========================================
# 2. MOTOR DE DADOS E ALGORITMOS QUANT
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
API_HOST = "v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": API_HOST}

def safe_float(val, default=1.0):
    try: return max(float(val), 0.1) if val is not None else default
    except: return default

def format_form(form_str):
    if not form_str or form_str == 'N/A': return "<span style='color:#64748B;'>N/A</span>"
    html = ""
    for char in form_str[-5:]:
        if char == 'W': html += "<span style='color:#10B981; font-weight:bold; margin-right:2px;'>W</span>"
        elif char == 'D': html += "<span style='color:#F59E0B; font-weight:bold; margin-right:2px;'>D</span>"
        elif char == 'L': html += "<span style='color:#EF4444; font-weight:bold; margin-right:2px;'>L</span>"
    return html

def calculate_auto_xg(s_h, s_a):
    LEAGUE_AVG = 1.35 
    h_attack = (s_h['h_f'] * 0.80) + (LEAGUE_AVG * 0.20)
    h_defense = (s_h['h_a'] * 0.80) + (LEAGUE_AVG * 0.20)
    a_attack = (s_a['a_f'] * 0.80) + (LEAGUE_AVG * 0.20)
    a_defense = (s_a['a_a'] * 0.80) + (LEAGUE_AVG * 0.20)
    base_xg_h = (h_attack * a_defense) / LEAGUE_AVG
    base_xg_a = (a_attack * h_defense) / LEAGUE_AVG
    get_momentum = lambda f: 0.90 + ((sum([3 if c=='W' else 1 if c=='D' else 0 for c in f[-5:]]) / (len(f[-5:])*3)) * 0.20) if f and f!='N/A' and len(f[-5:])>0 else 1.0
    return round(base_xg_h * get_momentum(s_h['form']), 3), round(base_xg_a * get_momentum(s_a['form']), 3)

@st.cache_data(ttl=3600)
def get_pro_stats(team_id, league_id, season="2025"):
    try:
        r = requests.get(f"https://{API_HOST}/teams/statistics", headers=HEADERS, params={"league": league_id, "season": season, "team": team_id}, timeout=10).json()
        if not r.get('response') or r['response']['fixtures']['played']['total'] == 0:
            r = requests.get(f"https://{API_HOST}/teams/statistics", headers=HEADERS, params={"league": league_id, "season": str(int(season)-1), "team": team_id}, timeout=10).json()
        stats = r.get('response', {})
        goals = stats.get('goals', {}); fixtures = stats.get('fixtures', {})
        return {
            "h_f": safe_float(goals.get('for', {}).get('average', {}).get('home'), 1.35),
            "h_a": safe_float(goals.get('against', {}).get('average', {}).get('home'), 1.35),
            "a_f": safe_float(goals.get('for', {}).get('average', {}).get('away'), 1.35),
            "a_a": safe_float(goals.get('against', {}).get('average', {}).get('away'), 1.35),
            "form": stats.get('form', 'N/A'),
            "cs_pct": safe_float(stats.get('clean_sheet', {}).get('total', 0), 0) / safe_float(fixtures.get('played', {}).get('total', 1), 1.0)
        }
    except: return {"h_f": 1.35, "h_a": 1.35, "a_f": 1.35, "a_a": 1.35, "form": "N/A", "cs_pct": 0.0}

@st.cache_data(ttl=1800)
def get_auto_odds(fixture_id, bookmaker_id=8):
    odds = {}
    try:
        r = requests.get(f"https://{API_HOST}/odds", headers=HEADERS, params={"fixture": fixture_id, "bookmaker": bookmaker_id}, timeout=10).json()
        if not r.get('response'): return odds
        bookmakers = r['response'][0].get('bookmakers', [])
        if not bookmakers: return odds
        
        for bet in bookmakers[0].get('bets', []):
            name = bet['name']
            vals = {v['value']: safe_float(v['odd']) for v in bet['values']}
            if name == 'Match Winner':
                odds["Match Odds - Home"] = vals.get('Home', 0); odds["Match Odds - Draw"] = vals.get('Draw', 0); odds["Match Odds - Away"] = vals.get('Away', 0)
            elif name == 'Goals Over/Under':
                odds["Over 1.5 Goals"] = vals.get('Over 1.5', 0); odds["Under 1.5 Goals"] = vals.get('Under 1.5', 0)
                odds["Over 2.5 Goals"] = vals.get('Over 2.5', 0); odds["Under 2.5 Goals"] = vals.get('Under 2.5', 0)
            elif name == 'Both Teams Score':
                odds["BTTS - Yes"] = vals.get('Yes', 0); odds["BTTS - No"] = vals.get('No', 0)
    except: pass
    return odds

@st.cache_data(ttl=3600)
def fetch_fixtures(league_id, season="2025", target_date=None):
    if target_date is None: target_date = date.today()
    try: return requests.get(f"https://{API_HOST}/fixtures", headers=HEADERS, params={"date": target_date.strftime('%Y-%m-%d'), "league": league_id, "season": season}, timeout=10).json().get('response', [])
    except: return []

def run_master_math(lh, la, rho=-0.13, zip_factor=1.0):
    max_g = 10 
    prob_mtx = np.outer(poisson.pmf(np.arange(max_g), lh), poisson.pmf(np.arange(max_g), la))
    if rho != 0:
        min_rho = max(-1.0 / max(lh, 0.001), -1.0 / max(la, 0.001)); valid_rho = max(min_rho, rho)
        prob_mtx[0,0] *= max(0, 1 - (lh * la * valid_rho)); prob_mtx[0,1] *= max(0, 1 + (lh * valid_rho))
        prob_mtx[1,0] *= max(0, 1 + (la * valid_rho)); prob_mtx[1,1] *= max(0, 1 - valid_rho)
    if zip_factor != 1.0: prob_mtx[0,0] *= zip_factor 
    prob_mtx = np.clip(prob_mtx, 0, None)
    if prob_mtx.sum() > 0: prob_mtx /= prob_mtx.sum()
    
    goals_sum = np.add.outer(np.arange(max_g), np.arange(max_g))
    diff_matrix = np.subtract.outer(np.arange(max_g), np.arange(max_g))
    ph, px, pa = prob_mtx[diff_matrix > 0].sum(), prob_mtx[diff_matrix == 0].sum(), prob_mtx[diff_matrix < 0].sum()
    cs_h, cs_a = prob_mtx[:, 0].sum(), prob_mtx[0, :].sum()

    return {
        "Match Odds - Home": ph, "Match Odds - Draw": px, "Match Odds - Away": pa,
        "Over 1.5 Goals": prob_mtx[goals_sum > 1.5].sum(), "Under 1.5 Goals": prob_mtx[goals_sum < 1.5].sum(),
        "Over 2.5 Goals": prob_mtx[goals_sum > 2.5].sum(), "Under 2.5 Goals": prob_mtx[goals_sum < 2.5].sum(),
        "BTTS - Yes": 1 - (cs_h + cs_a - prob_mtx[0,0]), "BTTS - No": cs_h + cs_a - prob_mtx[0,0]
    }, prob_mtx

# ==========================================
# 3. UI & CSS INSTITUCIONAL
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #0B1120; color: #F8FAFC; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #070B14 !important; border-right: 1px solid #1E293B !important; }
    h1, h2, h3 { font-weight: 600; letter-spacing: -0.5px; color: #F8FAFC; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #1E293B; gap: 0; }
    .stTabs [data-baseweb="tab"] { color: #64748B; font-weight: 600; font-size: 0.85rem; padding: 12px 24px; background: transparent; border: none; text-transform: uppercase; letter-spacing: 0.5px; }
    .stTabs [aria-selected="true"] { color: #38BDF8 !important; border-bottom: 2px solid #38BDF8 !important; background: rgba(56, 189, 248, 0.05) !important; }
    .login-wrapper { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
    .auth-panel { background: #070B14; border: 1px solid #1E293B; border-radius: 8px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.8); max-width: 400px; width: 100%; margin: 0 auto; border-top: 3px solid #38BDF8; }
    .metric-container { background: #0F172A; border: 1px solid #1E293B; border-radius: 6px; padding: 16px; margin-bottom: 16px; transition: transform 0.2s; }
    .metric-container:hover { border-color: #38BDF8; }
    .metric-label { font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-weight: 600; }
    .metric-val { font-size: 1.6rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #F8FAFC; }
    .val-pos { color: #10B981 !important; } .val-neg { color: #EF4444 !important; }
    .exec-btn { background: #10B981 !important; color: #0B1120 !important; font-weight: 800 !important; border: none !important; border-radius: 4px; padding: 8px 16px; width: 100%; cursor: pointer; transition: all 0.2s; }
    .exec-btn:hover { background: #059669 !important; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
    </style>
""", unsafe_allow_html=True)

def render_auth():
    st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
    with st.form("auth_form"):
        st.markdown("<div class='auth-panel'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 1.5rem; font-weight: 700; text-align: center; margin-bottom: 20px; font-family: \"JetBrains Mono\";'>APEX<span style='color:#38BDF8;'>QUANT</span></div>", unsafe_allow_html=True)
        user_id = st.text_input("Institutional ID", placeholder="admin")
        pass_key = st.text_input("Access Key", type="password", placeholder="admin")
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("INITIALIZE TERMINAL", use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
        if submit and user_id == "admin" and pass_key == "admin":
            st.session_state.logged_in = True
            st.session_state.user = user_id
            safe_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def calculate_performance(df):
    resolved = df[df['Status'].isin(['Settled - Won', 'Settled - Lost'])].copy()
    if resolved.empty: return None
    resolved['Realized_PnL'] = resolved.apply(lambda r: r['Stake (€)'] * (r['Matched Odd'] - 1) if r['Status'] == 'Settled - Won' else -r['Stake (€)'], axis=1)
    resolved['EV_PnL'] = resolved['Stake (€)'] * ((resolved['Matched Odd'] / resolved['True Odd']) - 1)
    resolved['Cum_PnL'] = resolved['Realized_PnL'].cumsum()
    resolved['Cum_EV'] = resolved['EV_PnL'].cumsum()
    resolved['Peak'] = resolved['Cum_PnL'].cummax()
    resolved['Drawdown'] = resolved['Cum_PnL'] - resolved['Peak']
    return resolved

# ==========================================
# 4. DASHBOARD TERMINAL
# ==========================================
def render_terminal():
    with st.sidebar:
        st.markdown(f"<div style='color:#94A3B8; font-size:0.75rem; text-transform:uppercase;'>Operative: {st.session_state.user}</div><hr style='border-color:#1E293B;'>", unsafe_allow_html=True)
        
        initial_capital = st.number_input("Starting Capital (€)", value=10000.0, step=1000.0)
        kelly_fraction = st.selectbox("Kelly Criterion Profile", options=[1.0, 0.5, 0.25], format_func=lambda x: f"{'Full' if x==1.0 else 'Half' if x==0.5 else 'Quarter'} Kelly ({x})", index=2)
        
        st.markdown("<br><div style='color:#38BDF8; font-size:0.8rem; font-weight:700;'>MARKET SCANNER</div>", unsafe_allow_html=True)
        target_date = st.date_input("Date", value=date.today())
        
        l_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94, "Champions League": 2, "Internationals": 10}
        ln = st.selectbox("Tournament", list(l_map.keys()))
        fix_data = fetch_fixtures(l_map[ln], season="2026" if l_map[ln]==10 else "2025", target_date=target_date)
        
        m_sel = None
        if fix_data:
            m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": f for f in fix_data}
            m_display = st.selectbox("Match", list(m_map.keys()))
            m_sel = m_map[m_display]
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Disconnect", use_container_width=True):
            st.session_state.logged_in = False
            safe_rerun()

    tab_model, tab_ledger, tab_analytics = st.tabs(["Auto-Scanner Engine", "Portfolio Ledger", "Quantitative Analytics"])

    # --- TAB 1: AUTO-SCANNER ---
    with tab_model:
        if not m_sel:
            st.info("Awaiting market selection...")
        else:
            with st.spinner("Fetching Market Odds and Calculating Quant Model..."):
                s_h, s_a = get_pro_stats(m_sel['teams']['home']['id'], l_map[ln]), get_pro_stats(m_sel['teams']['away']['id'], l_map[ln])
                xg_h, xg_a = calculate_auto_xg(s_h, s_a)
                res_probs, mtx = run_master_math(xg_h, xg_a, rho=-0.13)
                live_odds = get_auto_odds(m_sel['fixture']['id'])
            
            st.markdown(f"""
            <div style="background:#0F172A; border:1px solid #1E293B; padding:20px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <div style="flex:1;"><div style="font-size:1.5rem; font-weight:700;">{m_sel['teams']['home']['name']}</div><div style="color:#94A3B8; font-size:0.85rem;">Proj. xG: <b style="color:#38BDF8;">{xg_h:.2f}</b> | Form: {format_form(s_h['form'])}</div></div>
                <div style="font-size:1.2rem; color:#64748B; font-weight:700; padding:0 20px;">VS</div>
                <div style="flex:1; text-align:right;"><div style="font-size:1.5rem; font-weight:700;">{m_sel['teams']['away']['name']}</div><div style="color:#94A3B8; font-size:0.85rem;">Proj. xG: <b style="color:#38BDF8;">{xg_a:.2f}</b> | Form: {format_form(s_a['form'])}</div></div>
            </div>
            """, unsafe_allow_html=True)

            # Algoritmo de cruzamento automático: Modelo vs Live API
            valid_bets = []
            for mkt, prob in res_probs.items():
                mkt_odd = live_odds.get(mkt, 0)
                if mkt_odd > 1.05 and prob > 0:
                    edge = (prob * mkt_odd) - 1
                    if edge > 0:
                        valid_bets.append({"Market": mkt, "Prob": prob, "Odd": mkt_odd, "Edge": edge, "TrueOdd": 1/prob})

            col_list, col_viz = st.columns([1.2, 1])
            
            with col_list:
                st.markdown("<h4 style='color:#F8FAFC; margin-bottom:15px;'><span style='color:#10B981;'>●</span> Automated Value Finder</h4>", unsafe_allow_html=True)
                
                if not live_odds:
                    st.warning("Market liquidity is low. Bookmaker odds not yet available for this event via API.")
                elif not valid_bets:
                    st.info("Market is perfectly efficient. No edges > 0% found for this match.")
                else:
                    valid_bets = sorted(valid_bets, key=lambda x: x["Edge"], reverse=True)
                    df_temp = calculate_performance(st.session_state.trade_ledger)
                    pnl_temp = df_temp['Realized_PnL'].sum() if df_temp is not None else 0
                    current_bk = initial_capital + pnl_temp

                    for i, bet in enumerate(valid_bets):
                        kelly_full = bet["Edge"] / (bet["Odd"] - 1)
                        stake = current_bk * (kelly_full * kelly_fraction)
                        
                        st.markdown(f"""
                        <div style="background:#0F172A; border:1px solid #1E293B; border-left:3px solid #10B981; padding:15px; border-radius:6px; margin-bottom:10px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                <div style="font-weight:700; font-size:1.1rem;">{bet["Market"]}</div>
                                <div style="background:rgba(16,185,129,0.1); color:#10B981; padding:4px 8px; border-radius:4px; font-weight:700; font-size:0.8rem;">EDGE: +{bet["Edge"]:.2%}</div>
                            </div>
                            <div style="display:flex; justify-content:space-between; align-items:center; font-family:'JetBrains Mono'; font-size:0.9rem;">
                                <div><span style="color:#64748B;">API Odd:</span> <b style="color:#F8FAFC;">{bet["Odd"]:.2f}</b></div>
                                <div><span style="color:#64748B;">True Odd:</span> <b style="color:#38BDF8;">{bet["TrueOdd"]:.2f}</b></div>
                                <div><span style="color:#64748B;">Rec. Stake:</span> <b style="color:#F8FAFC;">€{stake:.2f}</b></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"EXECUTE TRADE (Row {i})", key=f"exec_{i}", use_container_width=True):
                            new_trade = pd.DataFrame([{
                                "Date": date.today().strftime('%Y-%m-%d'), "Event": f"{m_sel['teams']['home']['name']} v {m_sel['teams']['away']['name']}", 
                                "Market": bet["Market"], "Matched Odd": bet["Odd"], "True Odd": round(bet["TrueOdd"], 2), 
                                "Stake (€)": round(stake, 2), "CLV": round(bet["Edge"], 4), "Status": "Pending"
                            }])
                            st.session_state.trade_ledger = pd.concat([st.session_state.trade_ledger, new_trade], ignore_index=True)
                            st.toast(f"{bet['Market']} logged to Ledger.", icon="✅")
                            time.sleep(0.5)
                            safe_rerun()

                with st.expander("Manual Override / Line Shopping"):
                    st.caption("Insere odds de corretoras asiáticas ou exchanges para encontrar edges escondidos.")
                    man_odd = st.number_input("Custom Odd", value=1.00, step=0.05)
                    man_mkt = st.selectbox("Market Target", list(res_probs.keys()))
                    if man_odd > 1.05 and res_probs[man_mkt] > 0:
                        man_edge = (res_probs[man_mkt] * man_odd) - 1
                        st.markdown(f"**Calculated Edge:** <span style='color:{'#10B981' if man_edge > 0 else '#EF4444'};'>{(man_edge):.2%}</span>", unsafe_allow_html=True)

            with col_viz:
                st.markdown("<h4 style='color:#F8FAFC; margin-bottom:15px;'>Market Efficiency Chart</h4>", unsafe_allow_html=True)
                if live_odds and valid_bets:
                    markets_plot = [b["Market"] for b in valid_bets]
                    implied_probs = [1/b["Odd"] for b in valid_bets]
                    model_probs = [b["Prob"] for b in valid_bets]
                    
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(x=markets_plot, y=implied_probs, name='Market Implied', marker_color='#334155'))
                    fig_bar.add_trace(go.Bar(x=markets_plot, y=model_probs, name='Model True Prob', marker_color='#38BDF8'))
                    fig_bar.update_layout(
                        barmode='group', paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                        font=dict(color="#94A3B8"), height=350, yaxis_tickformat='.0%',
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Awaiting odds data to generate efficiency chart.")

    # --- TAB 2 & 3: MANTÊM-SE (LEDGER & ANALYTICS) ---
    with tab_ledger:
        st.markdown("<h3 style='margin-top:0;'>Portfolio Ledger</h3>", unsafe_allow_html=True)
        df_view = st.session_state.trade_ledger.copy()
        
        edited_df = st.data_editor(
            df_view, use_container_width=True,
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Settled - Won", "Settled - Lost", "Voided"], required=True),
                "Matched Odd": st.column_config.NumberColumn(format="%.2f"),
                "True Odd": st.column_config.NumberColumn(format="%.2f"),
                "Stake (€)": st.column_config.NumberColumn(format="%.2f"),
                "CLV": st.column_config.NumberColumn(format="%.4f"),
            }, hide_index=True, height=500
        )
        if not edited_df.equals(df_view):
            st.session_state.trade_ledger.loc[edited_df.index] = edited_df
            safe_rerun()

    with tab_analytics:
        perf_data = calculate_performance(st.session_state.trade_ledger)
        if perf_data is not None and not perf_data.empty:
            net_profit = perf_data['Realized_PnL'].sum()
            turnover = perf_data['Stake (€)'].sum()
            roi = (net_profit / turnover) * 100 if turnover > 0 else 0
            
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.markdown(f"<div class='metric-container'><div class='metric-label'>Net PnL</div><div class='metric-val val-pos'>€{net_profit:,.2f}</div></div>", unsafe_allow_html=True)
            with m2: st.markdown(f"<div class='metric-container'><div class='metric-label'>Turnover</div><div class='metric-val'>€{turnover:,.0f}</div></div>", unsafe_allow_html=True)
            with m3: st.markdown(f"<div class='metric-container'><div class='metric-label'>ROI (Yield)</div><div class='metric-val val-pos'>{roi:+.2f}%</div></div>", unsafe_allow_html=True)
            with m4: st.markdown(f"<div class='metric-container'><div class='metric-label'>Max Drawdown</div><div class='metric-val val-neg'>€{perf_data['Drawdown'].min():,.0f}</div></div>", unsafe_allow_html=True)
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
            x_vals = list(range(len(perf_data)))
            fig.add_trace(go.Scatter(x=x_vals, y=perf_data['Cum_PnL'], mode='lines', name='Realized PnL', line=dict(color='#10B981', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=x_vals, y=perf_data['Cum_EV'], mode='lines', name='Expected Value', line=dict(color='#38BDF8', width=2, dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=x_vals, y=perf_data['Drawdown'], mode='lines', name='Drawdown', line=dict(color='#EF4444', width=1), fill='tozeroy'), row=2, col=1)
            fig.update_layout(height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94A3B8"), hovermode="x unified", margin=dict(l=0, r=0, t=10, b=0))
            fig.update_xaxes(showgrid=False, zeroline=False)
            fig.update_yaxes(title="PnL (€)", showgrid=True, gridcolor='rgba(30,41,59,0.5)', row=1, col=1)
            st.plotly_chart(fig, use_container_width=True)

if st.session_state.logged_in: render_terminal()
else: render_auth()