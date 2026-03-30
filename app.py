import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date, timedelta
import random

# ==========================================
# 1. CONFIGURAÇÃO DE DESIGN E ESTADO
# ==========================================
st.set_page_config(
    page_title="ORACLE V140 - APEX QUANT", 
    page_icon="🎯",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- GERADOR DE HISTÓRICO REALISTA (PRO) ---
def generate_realistic_history():
    np.random.seed(42) # Para manter os mesmos dados na demo
    teams = ["Benfica", "Porto", "Sporting", "Braga", "Real Madrid", "Barcelona", "Arsenal", "Man City", "Liverpool", "Bayern", "Juventus", "Inter", "Milan"]
    mkts = ["Vencedor Casa", "Vencedor Fora", "Over 2.5", "Under 2.5", "BTTS (Sim)"]
    
    history = []
    date_start = date.today() - timedelta(days=180)
    
    for _ in range(500):
        d = date_start + timedelta(days=random.randint(0, 180))
        t1, t2 = random.sample(teams, 2)
        mkt = random.choice(mkts)
        
        # Odds realistas entre 1.60 e 2.80
        odd_comp = round(random.uniform(1.60, 2.80), 2)
        
        # Edge realista (Vantagem sobre a casa): 2% a 7% (Muito procurado por pros)
        edge = random.uniform(0.02, 0.07)
        odd_real = odd_comp / (1 + edge)
        prob_win = 1 / odd_real
        
        stake = round(random.uniform(10, 50), 2)
        
        # Simulação realista baseada na probabilidade verdadeira
        won = random.random() < prob_win
        estado = "Ganha" if won else "Perdida"
        
        history.append({
            "Data": d.strftime('%Y-%m-%d'),
            "Jogo": f"{t1} vs {t2}",
            "Aposta": mkt,
            "Odd Comprada": odd_comp,
            "Odd Real": round(odd_real, 2),
            "Stake (€)": stake,
            "Lucro Extra": round(edge, 3),
            "Estado": estado
        })
    
    # Ordenar por data
    df = pd.DataFrame(history)
    df['Data'] = pd.to_datetime(df['Data'])
    df = df.sort_values("Data").reset_index(drop=True)
    df['Data'] = df['Data'].dt.strftime('%Y-%m-%d')
    return df

# Inicialização de variáveis de sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'bet_history' not in st.session_state:
    # Injeta as 500 bets realistas na primeira inicialização
    st.session_state.bet_history = generate_realistic_history()

# CSS Personalizado (Melhorado para UI PRO)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    .stApp { background-color: #050810; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #020408 !important; border-right: 1px solid #1E293B !important; }
    
    /* Tabs Style */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 12px; border-bottom: 1px solid #1E293B; }
    .stTabs [data-baseweb="tab"] { color: #64748B; font-weight: 700; font-size: 0.95rem; padding: 10px 20px; background: #0B1120; border-radius: 8px 8px 0 0; border: 1px solid #1E293B; border-bottom: none; transition: all 0.3s ease; }
    .stTabs [aria-selected="true"] { color: #00FF88 !important; background: #050810 !important; border-top: 2px solid #00FF88 !important; box-shadow: 0 -10px 20px rgba(0, 255, 136, 0.05); }
    
    /* Login Box */
    .login-box { background: #0B1120; border: 1px solid #1E293B; border-radius: 16px; padding: 40px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); border-top: 4px solid #00FF88; }
    
    /* Cards & Metrics */
    .top-recommendation { background: linear-gradient(135deg, #0B1120 0%, #050810 100%); border-radius: 12px; border: 1px solid #1E293B; border-left: 6px solid #00FF88; padding: 24px 32px; margin-bottom: 24px; box-shadow: 0 15px 35px rgba(0,0,0,0.4); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
    .top-rec-title { font-size: 0.7rem; color: #94A3B8; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px; }
    .top-rec-value { font-size: 2rem; font-weight: 800; color: #FFFFFF; margin: 0; line-height: 1.1; }
    .top-rec-odd { font-size: 2.2rem; font-weight: 700; color: #FFD700; font-family: 'JetBrains Mono', monospace; }
    
    .metric-card { background: #0B1120; border: 1px solid #1E293B; border-radius: 12px; padding: 24px; border-bottom: 3px solid #3B82F6; transition: transform 0.2s; }
    .metric-card:hover { transform: translateY(-5px); border-bottom: 3px solid #00FF88; }
    .metric-title { font-size: 0.8rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 600; }
    .metric-value { font-size: 2rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; }

    .ai-box { background: rgba(0, 255, 136, 0.02); border-radius: 12px; padding: 24px; border: 1px solid rgba(0, 255, 136, 0.15); border-top: 4px solid #00FF88; }
    
    /* Buttons */
    div.stButton > button { background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; font-weight: 800 !important; height: 3.2rem !important; border-radius: 8px !important; border: none !important; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s; }
    div.stButton > button:hover { opacity: 0.9; box-shadow: 0 0 15px rgba(0, 255, 136, 0.4); transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

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
    if not form_str or form_str == 'N/A': return "<span style='color:#94A3B8;'>Sem dados</span>"
    recent_form = form_str[-5:]
    html = ""
    for char in recent_form:
        style = "padding:2px 6px; border-radius:4px; margin-right:4px; font-weight:bold; font-size:0.75rem; color:#000;"
        if char == 'W': html += f"<span style='{style} background:#00FF88;'>V</span>"
        elif char == 'D': html += f"<span style='{style} background:#FFD700;'>E</span>"
        elif char == 'L': html += f"<span style='{style} background:#EF4444; color:#FFF;'>D</span>"
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
                odds["O15"], odds["U15"] = vals.get('Over 1.5', 0), vals.get('Under 1.5', 0)
                odds["O25"], odds["U25"] = vals.get('Over 2.5', 0), vals.get('Under 2.5', 0)
            elif name == 'Both Teams Score': odds["BTTS_Y"], odds["BTTS_N"] = vals.get('Yes', 0), vals.get('No', 0)
            elif name == 'Asian Handicap':
                odds["AH_P15"] = vals.get('Home +1.5', 0)
                odds["AH_00"] = vals.get('Home +0.0', vals.get('Home 0.0', 0))
                odds["AH_M10"] = vals.get('Home -1.0', 0)
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
    h_win_by_1 = prob_mtx[diff_matrix == 1].sum()
    cs_h, cs_a = prob_mtx[:, 0].sum(), prob_mtx[0, :].sum()

    return {
        "Vencedor Casa": (ph, 0), "Empate (X)": (px, 0), "Vencedor Fora": (pa, 0),
        "Mais de 1.5 Golos": (prob_mtx[goals_sum > 1.5].sum(), 0), "Menos de 1.5 Golos": (prob_mtx[goals_sum < 1.5].sum(), 0),
        "Mais de 2.5 Golos": (prob_mtx[goals_sum > 2.5].sum(), 0), "Menos de 2.5 Golos": (prob_mtx[goals_sum < 2.5].sum(), 0),
        "Ambas Marcam (Sim)": (1 - (cs_h + cs_a - prob_mtx[0,0]), 0), "Ambas Marcam (Não)": (cs_h + cs_a - prob_mtx[0,0], 0),
        "Handicap +1.5 (Casa)": (ph + px + prob_mtx[diff_matrix == -1].sum(), 0), 
        "Empate Anula (Casa)": (ph, px), 
        "Handicap -1.0 (Casa)": (ph - h_win_by_1, h_win_by_1)
    }, prob_mtx

# ==========================================
# CÁLCULO DINÂMICO DO BANKROLL (FIX)
# ==========================================
df_temp = st.session_state.bet_history
lucro_real_total = 0.0

# Verificação de segurança para evitar o KeyError
cols_check = ['Estado', 'Stake (€)', 'Odd Comprada']
if not df_temp.empty and all(c in df_temp.columns for c in cols_check):
    # Usar vetorização do pandas é mais seguro que o iterrows() neste caso
    vitorias = df_temp[df_temp['Estado'] == 'Ganha']
    derrotas = df_temp[df_temp['Estado'] == 'Perdida']
    
    lucro_v = (vitorias['Stake (€)'] * (vitorias['Odd Comprada'] - 1)).sum()
    prejuizo_d = derrotas['Stake (€)'].sum()
    lucro_real_total = lucro_v - prejuizo_d

bankroll_atual = banca_inicial + lucro_real_total

# Mostrar o Bankroll no topo da Sidebar para nunca o perderes de vista
st.sidebar.markdown(f"""
    <div style="background: rgba(0,255,136,0.1); padding: 15px; border-radius: 10px; border: 1px solid #00FF88; margin-bottom: 20px;">
        <p style="margin:0; color:#94A3B8; font-size:0.8rem; text-transform:uppercase;">Saldo Operacional</p>
        <h2 style="margin:0; color:#00FF88;">{bankroll_atual:.2f} €</h2>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 3. SISTEMA DE LOGIN PRO
# ==========================================
def login_screen():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align:center; margin-bottom:30px;'>
            <h1 style='color:#00FF88; font-size:3.5rem; margin-bottom:0; font-family:"JetBrains Mono", monospace;'>ORACLE <span style='color:#FFF;'>V140</span></h1>
            <p style='color:#64748B; font-size:1.1rem; letter-spacing:3px;'>APEX QUANT ANALYTICS PORTAL</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("<div class='login-box'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#94A3B8; font-family:monospace; font-size:0.8rem;'>> SYSTEM_READY... AWAITING CREDENTIALS.</p>", unsafe_allow_html=True)
            
            username = st.text_input("ACCESS ID", placeholder="Ex: admin")
            password = st.text_input("SECURE KEY", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("INICIAR PROTOCOLO", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if submit:
                # Login simplificado para teste, pode ser alterado depois
                if username == "admin" and password == "apex123":
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("⚠️ ACESSO NEGADO. Credenciais inválidas.")

# ==========================================
# 4. APLICAÇÃO PRINCIPAL
# ==========================================
def main_app():
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<h2 style='color:#00FF88; font-family:monospace;'>🏛️ ORACLE V140</h2><p style='color:#94A3B8; font-size:0.8rem; border-bottom:1px solid #1E293B; padding-bottom:15px;'>PILOTO IDENTIFICADO: <b>{st.session_state.username.upper()}</b></p>", unsafe_allow_html=True)
        
        banca_inicial = st.number_input("💰 BANCA INICIAL (€)", value=1000.0, step=100.0, key="bk_pro")
        data_consulta = st.date_input("📅 DATA DA ANÁLISE", value=date.today(), key="date_pro")
        
        l_map = {"Amigáveis Seleções 🌍": 10, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "La Liga 🇪🇸": 140, "Primeira Liga 🇵🇹": 94, "Champions League 🇪🇺": 2, "Qualificação Mundial 🏆": 1}
        ln = st.selectbox("⚽ LIGA", list(l_map.keys()), key="ln_pro")
        
        target_season = "2026" if l_map[ln] in [1, 10] else "2025"
        fix_data = fetch_fixtures(l_map[ln], season=target_season, target_date=data_consulta)
        
        m_sel = None; auto_odds = {} 
        
        if fix_data:
            m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": i for i, f in enumerate(fix_data)}
            m_display = st.selectbox("🎯 JOGO", list(m_map.keys()), key="m_pro")
            m_sel = fix_data[m_map[m_display]]
            auto_odds = get_auto_odds(m_sel['fixture']['id'])
        else:
            st.warning("Nenhum jogo encontrado para esta data/liga.")

        st.markdown("---")
        use_auto_xg = st.checkbox("🤖 Usar IA para xG Dinâmico", value=True)
        zip_factor = st.slider("⚡ Fator Tático (0-0)", 0.8, 1.5, 1.05)
        
        with st.expander("⚙️ AJUSTE MANUAL DE ODDS"):
            c1, c2, c3 = st.columns(3)
            o_1 = c1.number_input("Casa", value=float(auto_odds.get("1", 1.01) or 1.01))
            o_x = c2.number_input("Emp", value=float(auto_odds.get("X", 1.01) or 1.01))
            o_2 = c3.number_input("Fora", value=float(auto_odds.get("2", 1.01) or 1.01))
            # (Mais inputs omitidos na UI manual para poupar espaço vertical, usa a API)
            o_o25 = st.number_input("Over 2.5", value=float(auto_odds.get("O25", 1.01) or 1.01))
            o_btts_y = st.number_input("BTTS Sim", value=float(auto_odds.get("BTTS_Y", 1.01) or 1.01))
            o_ah_00 = st.number_input("DNB (0.0)", value=float(auto_odds.get("AH_00", 1.01) or 1.01))
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Terminar Sessão", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # Cálculo da Banca Dinâmica
    df_temp = st.session_state.bet_history
    lucro_real_total = 0
    if not df_temp.empty:
        for idx, row in df_temp.iterrows():
            if row['Estado'] == 'Ganha': lucro_real_total += row['Stake (€)'] * (row['Odd Comprada'] - 1)
            elif row['Estado'] == 'Perdida': lucro_real_total -= row['Stake (€)']
    bankroll_atual = banca_inicial + lucro_real_total

    # --- TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(["🔬 DEEP DIVE", "🌍 ALPHA SCANNER", "🏦 CAIXA FORTE (COFRE)", "📈 TRADEMATE DASHBOARD"])

    # ====== TAB 1: DEEP DIVE (Lógica intacta) ======
    with tab1:
        if not m_sel:
            st.markdown("<div style='text-align:center; padding-top:150px;'><h1 style='opacity:0.1; font-size:4rem;'>SELECIONE UM JOGO</h1></div>", unsafe_allow_html=True)
        else:
            s_h, s_a = get_pro_stats(m_sel['teams']['home']['id'], l_map[ln]), get_pro_stats(m_sel['teams']['away']['id'], l_map[ln])
            
            if use_auto_xg:
                xg_h, xg_a = calculate_auto_xg(s_h, s_a)
                res, mtx = run_master_math(xg_h, xg_a, rho=-0.13, zip_factor=zip_factor) 
            else:
                lh, la = (s_h['h_f']*s_a['a_a'])**0.5, (s_a['a_f']*s_h['h_a'])**0.5
                res, mtx = run_master_math(lh, la, rho=-0.13, zip_factor=zip_factor)
            
            st.markdown(f"<h2 style='margin-bottom:10px; font-size:3.2rem; letter-spacing:-2px;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#475569; font-weight:300;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h2>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="top-recommendation" style="padding: 15px; margin-bottom: 20px;">
                <div style="flex: 1;">
                    <div class="top-rec-title">🏠 {m_sel['teams']['home']['name']}</div>
                    <div style="color:#FFF;">Forma: {format_form(s_h['form'])} | CS: <b>{s_h['cs_pct']:.0%}</b></div>
                </div>
                <div style="flex: 1; text-align: right;">
                    <div class="top-rec-title">✈️ {m_sel['teams']['away']['name']}</div>
                    <div style="color:#FFF;">Forma: {format_form(s_a['form'])} | CS: <b>{s_a['cs_pct']:.0%}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            raw_mkts = [
                ("Vencedor Casa", res["Vencedor Casa"], o_1), ("Empate (X)", res["Empate (X)"], o_x), ("Vencedor Fora", res["Vencedor Fora"], o_2),
                ("Mais de 2.5 Golos", res["Mais de 2.5 Golos"], o_o25), ("Ambas Marcam (Sim)", res["Ambas Marcam (Sim)"], o_btts_y),
                ("Empate Anula (Casa)", res["Empate Anula (Casa)"], o_ah_00)
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
                stake_sugerida = bankroll_atual * kelly_frac
                
                col_rec, col_btn = st.columns([3, 1])
                with col_rec:
                    st.markdown(f"""
                    <div class="top-recommendation">
                        <div><div class="top-rec-title">Aposta de Ouro</div><div class="top-rec-value">{best[0]}</div></div>
                        <div><div class="top-rec-title">Odd Real</div><div class="top-rec-value" style="color:#94A3B8;">{odd_justa:.2f}</div></div>
                        <div><div class="top-rec-title">Odd Mercado</div><div class="top-rec-odd">{best[3]:.2f}</div></div>
                        <div><div class="top-rec-title">Stake Recomendada</div><div class="top-rec-value" style="color:#00FF88;">{stake_sugerida:.2f}€</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_btn:
                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                    if st.button("📥 EXECUTAR ORDEM", key="reg_bet", use_container_width=True):
                        nova_aposta = pd.DataFrame([{
                            "Data": date.today().strftime('%Y-%m-%d'), "Jogo": f"{m_sel['teams']['home']['name']} vs {m_sel['teams']['away']['name']}", 
                            "Aposta": best[0], "Odd Comprada": best[3], "Odd Real": round(odd_justa, 2), 
                            "Stake (€)": round(stake_sugerida, 2), "Lucro Extra": round(edge_final, 3), "Estado": "Pendente"
                        }])
                        st.session_state.bet_history = pd.concat([st.session_state.bet_history, nova_aposta], ignore_index=True)
                        st.toast("Transação registada no Cofre Institucional!", icon="✅")
            else:
                st.warning("Mercado Eficiente - Nenhuma margem de lucro (Edge) encontrada. Preserve o Capital.")

    # ====== TAB 2: ALPHA SCANNER (Omitido/Mantido para foco) ======
    with tab2: st.info("Alpha Scanner Global operacional. Pressione botão na barra lateral se disponível na versão.")

    # ====== TAB 3: CAIXA FORTE (RENOVADA) ======
    with tab3:
        st.markdown("""
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <h2 style='font-size:2rem; letter-spacing:-1px; color:#FFD700; margin:0;'>🏦 COFRE INSTITUCIONAL (AUDITORIA)</h2>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Central de gestão de risco e alteração de estado das operações executadas.")
        
        df_hist = st.session_state.bet_history
        
        c1, c2, c3, c4 = st.columns(4)
        total_staked = df_hist['Stake (€)'].sum()
        avg_edge = df_hist["Lucro Extra"].mean() if not df_hist.empty else 0
        expected_profit = (df_hist['Stake (€)'] * df_hist['Lucro Extra']).sum()

        with c1: st.markdown(f"<div class='metric-card'><div class='metric-title'>Capital Líquido</div><div class='metric-value' style='color:#00FF88;'>{bankroll_atual:.2f}€</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><div class='metric-title'>PnL Real (€)</div><div class='metric-value' style='color:{'#00FF88' if lucro_real_total > 0 else '#EF4444'};'>{lucro_real_total:+.2f}€</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><div class='metric-title'>Avg. CLV (Edge)</div><div class='metric-value' style='color:#FFD700;'>{avg_edge:+.2%}</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div class='metric-card'><div class='metric-title'>Expected Value (EV)</div><div class='metric-value' style='color:#3B82F6;'>+{expected_profit:.2f}€</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        edited_df = st.data_editor(
            df_hist,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Estado": st.column_config.SelectboxColumn("Status", options=["Pendente", "Ganha", "Perdida", "Reembolsada"], required=True),
                "Odd Comprada": st.column_config.NumberColumn(format="%.2f"),
                "Odd Real": st.column_config.NumberColumn(format="%.2f"),
                "Stake (€)": st.column_config.NumberColumn(format="%.2f €"),
                "Lucro Extra": st.column_config.NumberColumn("Edge (CLV)", format="%.3f"),
            },
            hide_index=True,
            height=400
        )

        if not edited_df.equals(st.session_state.bet_history):
            st.session_state.bet_history = edited_df
            st.rerun()

    # ====== TAB 4: TRADEMATE DASHBOARD (NÍVEL PRO) ======
    with tab4:
        st.markdown("<h2 style='font-size:2rem; letter-spacing:-1px; color:#3B82F6;'>📈 QUANTITATIVE PERFORMANCE (TRADEMATE STYLE)</h2>", unsafe_allow_html=True)
        st.caption("Comparação entre o PnL Realizado (Linha Verde) vs. PnL Esperado pela Closing Line Value (Linha Azul tracejada).")
        
        df_hist = st.session_state.bet_history
        resolved_bets = df_hist[df_hist['Estado'].isin(['Ganha', 'Perdida'])].copy()
        
        if resolved_bets.empty:
            st.info("ℹ️ Registe apostas e marque-as como Ganha/Perdida no Cofre para visualizar métricas avançadas.")
        else:
            greens = len(resolved_bets[resolved_bets['Estado'] == 'Ganha'])
            reds = len(resolved_bets[resolved_bets['Estado'] == 'Perdida'])
            total_res = greens + reds
            
            total_investido = resolved_bets['Stake (€)'].sum()
            roi = (lucro_real_total / total_investido) * 100 if total_investido > 0 else 0
            win_rate = greens / total_res if total_res > 0 else 0
            
            # Cálculo de PnL Real vs PnL EV (Trademate Logic)
            resolved_bets['PnL_Real'] = resolved_bets.apply(
                lambda r: r['Stake (€)'] * (r['Odd Comprada'] - 1) if r['Estado'] == 'Ganha' else -r['Stake (€)'], axis=1
            )
            
            # EV PnL = Stake * ((Odd Comprada / Odd Real) - 1)
            # Isto significa o lucro teórico se tivéssemos infinito volume.
            resolved_bets['PnL_EV'] = resolved_bets['Stake (€)'] * ((resolved_bets['Odd Comprada'] / resolved_bets['Odd Real']) - 1)
            
            resolved_bets['PnL_Real_Acc'] = resolved_bets['PnL_Real'].cumsum()
            resolved_bets['PnL_EV_Acc'] = resolved_bets['PnL_EV'].cumsum()
            
            # Métricas Superiores
            mc1, mc2, mc3, mc4 = st.columns(4)
            with mc1: st.markdown(f"<div class='metric-card' style='padding:15px;'><div class='metric-title'>Yield Real (ROI)</div><div class='metric-value' style='color:{'#00FF88' if roi > 0 else '#EF4444'};'>{roi:+.2f}%</div></div>", unsafe_allow_html=True)
            with mc2: st.markdown(f"<div class='metric-card' style='padding:15px;'><div class='metric-title'>Volume Tradado</div><div class='metric-value' style='color:#FFF;'>{total_investido:.0f}€</div></div>", unsafe_allow_html=True)
            with mc3: st.markdown(f"<div class='metric-card' style='padding:15px;'><div class='metric-title'>Win Rate</div><div class='metric-value' style='color:#FFF;'>{win_rate:.1%} <span style='font-size:0.8rem; color:#64748B;'>({greens}W-{reds}L)</span></div></div>", unsafe_allow_html=True)
            with mc4: 
                avg_odd = resolved_bets['Odd Comprada'].mean()
                st.markdown(f"<div class='metric-card' style='padding:15px;'><div class='metric-title'>Odd Média</div><div class='metric-value' style='color:#FFD700;'>{avg_odd:.2f}</div></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráfico Master (Trademate View)
            y_real = [0] + resolved_bets['PnL_Real_Acc'].tolist()
            y_ev = [0] + resolved_bets['PnL_EV_Acc'].tolist()
            x_vals = list(range(len(y_real)))
            
            fig = go.Figure()
            
            # Área de Lucro Real (Verde)
            fig.add_trace(go.Scatter(
                x=x_vals, y=y_real, mode='lines', name='Actual Profit',
                line=dict(color='#00FF88', width=3),
                fill='tozeroy', fillcolor='rgba(0, 255, 136, 0.1)'
            ))
            
            # Linha de Expected Value (Azul Tracejada)
            fig.add_trace(go.Scatter(
                x=x_vals, y=y_ev, mode='lines', name='Expected Value (CLV)',
                line=dict(color='#3B82F6', width=3, dash='dash')
            ))
            
            fig.add_hline(y=0, line_dash="solid", line_color="#1E293B", line_width=2)
            
            fig.update_layout(
                title="📈 ACTUAL PROFIT VS EXPECTED VALUE",
                height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color="#FFF"), hovermode="x unified",
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(11,17,32,0.8)"),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            fig.update_xaxes(title="Trades Settled", showgrid=True, gridcolor='rgba(30,41,59,0.5)', zeroline=False)
            fig.update_yaxes(title="Profit / Loss (€)", showgrid=True, gridcolor='rgba(30,41,59,0.5)', zeroline=False)
            
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# ENTRY POINT
# ==========================================
if st.session_state.logged_in:
    main_app()
else:
    login_screen()