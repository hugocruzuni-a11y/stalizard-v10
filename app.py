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
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

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
        
        odd_comp = round(random.uniform(1.60, 3.50), 2)
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

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'trade_ledger' not in st.session_state: st.session_state.trade_ledger = generate_institutional_history()

# ==========================================
# 2. MOTOR DE DADOS E ALGORITMOS (APEX MATH)
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
API_HOST = "v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": API_HOST}

def safe_float(val, default=1.0):
    try: 
        if val is None: return default
        return max(float(val), 0.1) 
    except (ValueError, TypeError): return default

def format_form(form_str):
    if not form_str or form_str == 'N/A': return "<span style='color:#64748B;'>N/A</span>"
    recent_form = form_str[-5:]
    html = ""
    for char in recent_form:
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

    def get_momentum_factor(form_str):
        if not form_str or form_str == 'N/A': return 1.0
        recent = form_str[-5:]
        pts = sum([3 if c=='W' else 1 if c=='D' else 0 for c in recent])
        max_pts = len(recent) * 3
        return 0.90 + ((pts / max_pts) * 0.20) if max_pts > 0 else 1.0

    return round(base_xg_h * get_momentum_factor(s_h['form']), 3), round(base_xg_a * get_momentum_factor(s_a['form']), 3)

@st.cache_data(ttl=3600)
def get_pro_stats(team_id, league_id, season="2025"):
    try:
        url = f"https://{API_HOST}/teams/statistics"
        params = {"league": league_id, "season": season, "team": team_id}
        r = requests.get(url, headers=HEADERS, params=params, timeout=10).json()
        
        if not r.get('response') or r['response']['fixtures']['played']['total'] == 0:
            params["season"] = str(int(season) - 1)
            r = requests.get(url, headers=HEADERS, params=params, timeout=10).json()

        stats = r.get('response', {})
        goals = stats.get('goals', {})
        fixtures = stats.get('fixtures', {})
        
        return {
            "h_f": safe_float(goals.get('for', {}).get('average', {}).get('home'), 1.35),
            "h_a": safe_float(goals.get('against', {}).get('average', {}).get('home'), 1.35),
            "a_f": safe_float(goals.get('for', {}).get('average', {}).get('away'), 1.35),
            "a_a": safe_float(goals.get('against', {}).get('average', {}).get('away'), 1.35),
            "form": stats.get('form', 'N/A'),
            "cs_pct": safe_float(stats.get('clean_sheet', {}).get('total', 0), 0) / safe_float(fixtures.get('played', {}).get('total', 1), 1.0)
        }
    except Exception:
        return {"h_f": 1.35, "h_a": 1.35, "a_f": 1.35, "a_a": 1.35, "form": "N/A", "cs_pct": 0.0}

@st.cache_data(ttl=1800)
def get_auto_odds(fixture_id, bookmaker_id=8):
    odds = {k: 0.0 for k in ["1","X","2","O15","U15","O25","U25","BTTS_Y","BTTS_N","AH_P15","AH_00","AH_M10"]}
    try:
        url = f"https://{API_HOST}/odds"
        r = requests.get(url, headers=HEADERS, params={"fixture": fixture_id, "bookmaker": bookmaker_id}, timeout=10).json()
        if not r.get('response'): return odds
        bookmakers = r['response'][0].get('bookmakers', [])
        if not bookmakers: return odds
        
        for bet in bookmakers[0].get('bets', []):
            name = bet['name']
            vals = {v['value']: safe_float(v['odd']) for v in bet['values']}
            if name == 'Match Winner': odds["1"], odds["X"], odds["2"] = vals.get('Home', 0), vals.get('Draw', 0), vals.get('Away', 0)
            elif name == 'Goals Over/Under':
                odds["O25"], odds["U25"] = vals.get('Over 2.5', 0), vals.get('Under 2.5', 0)
            elif name == 'Both Teams Score': odds["BTTS_Y"] = vals.get('Yes', 0)
            elif name == 'Asian Handicap':
                odds["AH_00"] = vals.get('Home +0.0', vals.get('Home 0.0', 0))
    except: pass
    return odds

@st.cache_data(ttl=3600)
def fetch_fixtures(league_id, season="2025", target_date=None):
    if target_date is None: target_date = date.today()
    try:
        url = f"https://{API_HOST}/fixtures"
        params = {"date": target_date.strftime('%Y-%m-%d'), "league": league_id, "season": season}
        r = requests.get(url, headers=HEADERS, params=params, timeout=10).json()
        return r.get('response', [])
    except: return []

def run_master_math(lh, la, rho=-0.13, zip_factor=1.0):
    max_g = 12 
    prob_mtx = np.outer(poisson.pmf(np.arange(max_g), lh), poisson.pmf(np.arange(max_g), la))
    
    if rho != 0:
        min_rho = max(-1.0 / max(lh, 0.001), -1.0 / max(la, 0.001))
        valid_rho = max(min_rho, rho)
        prob_mtx[0,0] *= max(0, 1 - (lh * la * valid_rho))
        prob_mtx[0,1] *= max(0, 1 + (lh * valid_rho))
        prob_mtx[1,0] *= max(0, 1 + (la * valid_rho))
        prob_mtx[1,1] *= max(0, 1 - valid_rho)
        
    if zip_factor != 1.0: prob_mtx[0,0] *= zip_factor 
        
    prob_mtx = np.clip(prob_mtx, 0, None)
    prob_sum = prob_mtx.sum()
    if prob_sum > 0: prob_mtx /= prob_sum 
    
    goals_sum = np.add.outer(np.arange(max_g), np.arange(max_g))
    diff_matrix = np.subtract.outer(np.arange(max_g), np.arange(max_g))
    
    ph, px, pa = prob_mtx[diff_matrix > 0].sum(), prob_mtx[diff_matrix == 0].sum(), prob_mtx[diff_matrix < 0].sum()
    cs_h, cs_a = prob_mtx[:, 0].sum(), prob_mtx[0, :].sum()

    # Nomes dos mercados ajustados para inglês (profissional)
    return {
        "Match Odds - Home": (ph, 0), "Match Odds - Draw": (px, 0), "Match Odds - Away": (pa, 0),
        "Over 2.5 Goals": (prob_mtx[goals_sum > 2.5].sum(), 0), 
        "BTTS - Yes": (1 - (cs_h + cs_a - prob_mtx[0,0]), 0), 
        "Draw No Bet - Home": (ph, px)
    }, prob_mtx

# ==========================================
# 3. DESIGN E AUTENTICAÇÃO (CSS)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Roboto+Mono:wght@400;500&display=swap');
    .stApp { background-color: #0F172A; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0B1120 !important; border-right: 1px solid #1E293B !important; }
    h1, h2, h3 { font-weight: 500; letter-spacing: -0.5px; color: #F8FAFC; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #1E293B; gap: 0; }
    .stTabs [data-baseweb="tab"] { color: #94A3B8; font-weight: 500; font-size: 0.85rem; padding: 12px 24px; background: transparent; border: none; transition: color 0.2s; text-transform: uppercase; letter-spacing: 0.5px; }
    .stTabs [aria-selected="true"] { color: #38BDF8 !important; border-bottom: 2px solid #38BDF8 !important; background: rgba(56, 189, 248, 0.05) !important; }
    .login-wrapper { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
    .auth-panel { background: #0B1120; border: 1px solid #1E293B; border-radius: 4px; padding: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); max-width: 400px; width: 100%; margin: 0 auto; }
    .auth-header { font-size: 1.2rem; font-weight: 600; color: #F8FAFC; margin-bottom: 24px; text-align: center; border-bottom: 1px solid #1E293B; padding-bottom: 16px; }
    .metric-container { background: #0B1120; border: 1px solid #1E293B; border-radius: 4px; padding: 16px; margin-bottom: 16px;}
    .metric-label { font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
    .metric-val { font-size: 1.5rem; font-weight: 500; font-family: 'Roboto Mono', monospace; color: #F8FAFC; }
    .metric-sub { font-size: 0.75rem; margin-top: 4px; color: #94A3B8; }
    .val-pos { color: #10B981 !important; }
    .val-neg { color: #EF4444 !important; }
    div.stButton > button { background: #1E293B !important; color: #F8FAFC !important; font-weight: 500 !important; border-radius: 4px !important; border: 1px solid #334155 !important; transition: background 0.2s; font-size: 0.85rem; }
    div.stButton > button:hover { background: #334155 !important; border-color: #475569 !important; }
    .btn-primary div.stButton > button { background: #0EA5E9 !important; border-color: #0284C7 !important; color: #FFF !important; }
    .btn-primary div.stButton > button:hover { background: #0284C7 !important; }
    .match-header { background: #0B1120; border: 1px solid #1E293B; padding: 20px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;}
    .team-name { font-size: 1.2rem; font-weight: 600; color: #F8FAFC; }
    </style>
""", unsafe_allow_html=True)

def render_auth():
    st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
    with st.form("auth_form"):
        st.markdown("<div class='auth-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='auth-header'>Apex Quant Terminal</div>", unsafe_allow_html=True)
        user_id = st.text_input("User ID", placeholder="admin")
        pass_key = st.text_input("Passkey", type="password", placeholder="admin")
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
                    safe_rerun()
            else:
                st.error("Authentication failed.")
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
# 4. DASHBOARD PRINCIPAL (COMPLETO)
# ==========================================
def render_terminal():
    with st.sidebar:
        st.markdown(f"<div style='color:#94A3B8; font-size:0.75rem; text-transform:uppercase;'>Session: {st.session_state.user}</div>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#1E293B; margin: 10px 0;'>", unsafe_allow_html=True)
        
        initial_capital = st.number_input("Starting Capital (€)", value=10000.0, step=1000.0, format="%.2f")
        
        st.markdown("<br><div style='color:#38BDF8; font-size:0.85rem; font-weight:600; margin-bottom:10px;'>DATA ENGINE SETTINGS</div>", unsafe_allow_html=True)
        target_date = st.date_input("Match Date", value=date.today())
        
        l_map = {"Internationals": 10, "Premier League": 39, "La Liga": 140, "Primeira Liga": 94, "Champions League": 2}
        ln = st.selectbox("Tournament", list(l_map.keys()))
        target_season = "2026" if l_map[ln] == 10 else "2025"
        
        fix_data = fetch_fixtures(l_map[ln], season=target_season, target_date=target_date)
        m_sel = None; auto_odds = {} 
        
        if fix_data:
            m_map = {f"{f['teams']['home']['name']} v {f['teams']['away']['name']}": i for i, f in enumerate(fix_data)}
            m_display = st.selectbox("Select Match", list(m_map.keys()))
            m_sel = fix_data[m_map[m_display]]
            auto_odds = get_auto_odds(m_sel['fixture']['id'])
        else:
            st.warning("No matches found.")

        use_auto_xg = st.checkbox("Use Auto-xG Model", value=True)
        zip_factor = st.slider("Tactical Variance (Zip)", 0.8, 1.5, 1.05)
        
        with st.expander("Manual Odds Adjustment"):
            c1, c2, c3 = st.columns(3)
            o_1 = c1.number_input("Home", value=float(auto_odds.get("1", 1.01) or 1.01))
            o_x = c2.number_input("Draw", value=float(auto_odds.get("X", 1.01) or 1.01))
            o_2 = c3.number_input("Away", value=float(auto_odds.get("2", 1.01) or 1.01))
            o_o25 = st.number_input("Over 2.5", value=float(auto_odds.get("O25", 1.01) or 1.01))
            o_btts_y = st.number_input("BTTS Yes", value=float(auto_odds.get("BTTS_Y", 1.01) or 1.01))
            o_ah_00 = st.number_input("DNB Home", value=float(auto_odds.get("AH_00", 1.01) or 1.01))

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("End Session", use_container_width=True):
            st.session_state.logged_in = False
            safe_rerun()

    # Tabs Principais
    tab_model, tab_ledger, tab_analytics = st.tabs(["Prediction Engine", "Portfolio Ledger", "Performance Analytics"])

    # --- TAB 1: PREDICTION ENGINE (Antigo Deep Dive) ---
    with tab_model:
        st.markdown("<h3 style='margin-top:0;'>Quantitative Match Analysis</h3>", unsafe_allow_html=True)
        
        if not m_sel:
            st.info("Select a match from the sidebar to run the prediction model.")
        else:
            s_h, s_a = get_pro_stats(m_sel['teams']['home']['id'], l_map[ln]), get_pro_stats(m_sel['teams']['away']['id'], l_map[ln])
            
            if use_auto_xg:
                xg_h, xg_a = calculate_auto_xg(s_h, s_a)
                res, mtx = run_master_math(xg_h, xg_a, rho=-0.13, zip_factor=zip_factor) 
            else:
                lh, la = (s_h['h_f']*s_a['a_a'])**0.5, (s_a['a_f']*s_h['h_a'])**0.5
                res, mtx = run_master_math(lh, la, rho=-0.13, zip_factor=zip_factor)
            
            st.markdown(f"""
            <div class="match-header">
                <div>
                    <div class="team-name">{m_sel['teams']['home']['name']}</div>
                    <div style="font-size:0.8rem; color:#94A3B8; margin-top:5px;">Form: {format_form(s_h['form'])} | CS: {s_h['cs_pct']:.0%}</div>
                </div>
                <div style="color:#64748B; font-weight:600;">VS</div>
                <div style="text-align: right;">
                    <div class="team-name">{m_sel['teams']['away']['name']}</div>
                    <div style="font-size:0.8rem; color:#94A3B8; margin-top:5px;">Form: {format_form(s_a['form'])} | CS: {s_a['cs_pct']:.0%}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            raw_mkts = [
                ("Match Odds - Home", res["Match Odds - Home"], o_1), ("Match Odds - Draw", res["Match Odds - Draw"], o_x), 
                ("Match Odds - Away", res["Match Odds - Away"], o_2), ("Over 2.5 Goals", res["Over 2.5 Goals"], o_o25), 
                ("BTTS - Yes", res["BTTS - Yes"], o_btts_y), ("Draw No Bet - Home", res["Draw No Bet - Home"], o_ah_00)
            ]
            
            valid_mkts = []
            for name, prob_data, odd in raw_mkts:
                p_win = prob_data[0] if isinstance(prob_data, tuple) else prob_data
                p_void = prob_data[1] if isinstance(prob_data, tuple) else 0.0
                if odd > 1.05 and p_win > 0:
                    edge = (p_win * odd) + p_void - 1
                    fair_odd = (1 - p_void) / p_win if p_win > 0 else 0
                    valid_mkts.append((name, p_win, p_void, odd, edge, fair_odd))
            
            value_bets = [m for m in valid_mkts if m[4] > 0.025] 
            
            if value_bets:
                safe_bets = [m for m in value_bets if 1.50 <= m[3] <= 3.00]
                best = sorted(safe_bets, key=lambda x: x[4], reverse=True)[0] if safe_bets else sorted(value_bets, key=lambda x: x[4], reverse=True)[0]
                
                edge_final, odd_justa = best[4], best[5]
                kelly_optimo = edge_final / (best[3] - 1)
                kelly_frac = min(max(0, kelly_optimo * 0.20), 0.04) 
                
                # Dinâmica da Banca Atual
                df_temp = calculate_performance(st.session_state.trade_ledger)
                pnl_temp = df_temp['Realized_PnL'].sum() if df_temp is not None else 0
                current_bankroll = initial_capital + pnl_temp
                stake_sugerida = current_bankroll * kelly_frac
                
                col_rec, col_btn = st.columns([3, 1])
                with col_rec:
                    st.markdown(f"""
                    <div style="border-left: 4px solid #38BDF8; padding-left: 15px; margin-bottom: 20px;">
                        <div style="font-size:0.8rem; color:#94A3B8; text-transform:uppercase;">Identified Value Proposition</div>
                        <div style="font-size:1.5rem; font-weight:600; color:#F8FAFC;">{best[0]}</div>
                        <div style="display:flex; gap: 20px; margin-top: 10px;">
                            <div><span style="color:#64748B; font-size:0.8rem;">Matched Odd:</span> <b style="color:#F8FAFC;">{best[3]:.2f}</b></div>
                            <div><span style="color:#64748B; font-size:0.8rem;">True Odd:</span> <b style="color:#94A3B8;">{odd_justa:.2f}</b></div>
                            <div><span style="color:#64748B; font-size:0.8rem;">Edge (CLV):</span> <b style="color:#10B981;">+{edge_final:.2%}</b></div>
                            <div><span style="color:#64748B; font-size:0.8rem;">Rec. Stake:</span> <b style="color:#38BDF8;">€{stake_sugerida:.2f}</b></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_btn:
                    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
                    st.markdown("<div class='btn-primary'>", unsafe_allow_html=True)
                    if st.button("Execute Trade", key="reg_bet", use_container_width=True):
                        new_trade = pd.DataFrame([{
                            "Date": date.today().strftime('%Y-%m-%d'), 
                            "Event": f"{m_sel['teams']['home']['name']} v {m_sel['teams']['away']['name']}", 
                            "Market": best[0], "Matched Odd": best[3], "True Odd": round(odd_justa, 2), 
                            "Stake (€)": round(stake_sugerida, 2), "CLV": round(edge_final, 4), "Status": "Pending"
                        }])
                        st.session_state.trade_ledger = pd.concat([st.session_state.trade_ledger, new_trade], ignore_index=True)
                        st.toast("Trade registered to Portfolio Ledger.", icon="✅")
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Market Efficient - No edge identified above 2.5% threshold.")

    # --- TAB 2: PORTFOLIO LEDGER ---
    with tab_ledger:
        st.markdown("<h3 style='margin-top:0;'>Portfolio Ledger</h3>", unsafe_allow_html=True)
        df_data = st.session_state.trade_ledger
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1: status_flt = st.selectbox("Status Filter", ["All", "Pending", "Settled - Won", "Settled - Lost", "Voided"])
        with col2: mkt_flt = st.selectbox("Market Filter", ["All"] + list(df_data['Market'].unique()))
        
        df_view = df_data.copy()
        if status_flt != "All": df_view = df_view[df_view['Status'] == status_flt]
        if mkt_flt != "All": df_view = df_view[df_view['Market'] == mkt_flt]

        edited_df = st.data_editor(
            df_view,
            use_container_width=True,
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Settled - Won", "Settled - Lost", "Voided"], required=True),
                "Matched Odd": st.column_config.NumberColumn(format="%.2f"),
                "True Odd": st.column_config.NumberColumn(format="%.2f"),
                "Stake (€)": st.column_config.NumberColumn(format="%.2f"),
                "CLV": st.column_config.NumberColumn(format="%.4f"),
            },
            hide_index=True, height=500
        )

        if not edited_df.equals(df_view):
            st.session_state.trade_ledger.loc[edited_df.index] = edited_df
            safe_rerun()

    # --- TAB 3: PERFORMANCE ANALYTICS ---
    with tab_analytics:
        st.markdown("<h3 style='margin-top:0;'>Quantitative Performance Review</h3>", unsafe_allow_html=True)
        perf_data = calculate_performance(st.session_state.trade_ledger)
        
        if perf_data is None or perf_data.empty:
            st.info("Insufficient settled data for statistical analysis.")
        else:
            net_profit = perf_data['Realized_PnL'].sum()
            current_capital = initial_capital + net_profit
            total_trades = len(perf_data)
            wins = len(perf_data[perf_data['Status'] == 'Settled - Won'])
            win_rate = wins / total_trades if total_trades > 0 else 0
            
            turnover = perf_data['Stake (€)'].sum()
            roi = (net_profit / turnover) * 100 if turnover > 0 else 0
            max_drawdown = perf_data['Drawdown'].min()
            clv_positive = len(perf_data[perf_data['CLV'] > 0]) / total_trades if total_trades > 0 else 0
            
            m1, m2, m3, m4, m5 = st.columns(5)
            val_color = "val-pos" if net_profit > 0 else "val-neg"
            roi_color = "val-pos" if roi > 0 else "val-neg"
            
            with m1: st.markdown(f"<div class='metric-container'><div class='metric-label'>Net PnL</div><div class='metric-val {val_color}'>€{net_profit:,.2f}</div><div class='metric-sub'>Capital: €{current_capital:,.2f}</div></div>", unsafe_allow_html=True)
            with m2: st.markdown(f"<div class='metric-container'><div class='metric-label'>Turnover</div><div class='metric-val'>€{turnover:,.0f}</div><div class='metric-sub'>Yield/ROI: <span class='{roi_color}'>{roi:+.2f}%</span></div></div>", unsafe_allow_html=True)
            with m3: st.markdown(f"<div class='metric-container'><div class='metric-label'>Win Rate</div><div class='metric-val'>{win_rate:.1%}</div><div class='metric-sub'>Sample: {total_trades} Trades</div></div>", unsafe_allow_html=True)
            with m4: st.markdown(f"<div class='metric-container'><div class='metric-label'>Max Drawdown</div><div class='metric-val val-neg'>€{max_drawdown:,.0f}</div><div class='metric-sub'>Peak-to-Trough</div></div>", unsafe_allow_html=True)
            with m5: st.markdown(f"<div class='metric-container'><div class='metric-label'>CLV Beaten</div><div class='metric-val' style='color:#38BDF8;'>{clv_positive:.1%}</div><div class='metric-sub'>Market Efficiency</div></div>", unsafe_allow_html=True)
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
            x_vals = list(range(len(perf_data)))
            
            fig.add_trace(go.Scatter(x=x_vals, y=perf_data['Cum_PnL'], mode='lines', name='Realized PnL', line=dict(color='#10B981', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=x_vals, y=perf_data['Cum_EV'], mode='lines', name='Expected Value', line=dict(color='#38BDF8', width=2, dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=x_vals, y=perf_data['Drawdown'], mode='lines', name='Drawdown', line=dict(color='#EF4444', width=1), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.1)'), row=2, col=1)
            
            fig.update_layout(
                height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color="#94A3B8", family="Inter"), hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
                margin=dict(l=0, r=0, t=10, b=0)
            )
            fig.update_xaxes(showgrid=False, zeroline=False)
            fig.update_yaxes(title="PnL (€)", showgrid=True, gridcolor='rgba(30,41,59,0.5)', zeroline=True, zerolinecolor='#1E293B', row=1, col=1)
            fig.update_yaxes(title="Drawdown", showgrid=True, gridcolor='rgba(30,41,59,0.5)', zeroline=True, zerolinecolor='#1E293B', row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)

if st.session_state.logged_in:
    render_terminal()
else:
    render_auth()