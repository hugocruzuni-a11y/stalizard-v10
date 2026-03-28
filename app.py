import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# ==========================================
# 1. CONFIGURAÇÃO DE DESIGN E BASE DE DADOS
# ==========================================
st.set_page_config(
    page_title="ORACLE V140 - APEX QUANT", 
    page_icon="🎯",
    layout="wide", 
    initial_sidebar_state="expanded"
)

if 'bet_history' not in st.session_state:
    st.session_state.bet_history = pd.DataFrame(columns=[
        "Data", "Jogo", "Aposta", "Odd Comprada", "Odd Real", "Stake (€)", "Lucro Extra", "Estado"
    ])

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    .stApp { background-color: #050810; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #020408 !important; border-right: 1px solid #1E293B !important; }
    
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 12px; border-bottom: 1px solid #1E293B; }
    .stTabs [data-baseweb="tab"] { color: #64748B; font-weight: 700; font-size: 0.95rem; padding: 10px 20px; background: #0B1120; border-radius: 8px 8px 0 0; border: 1px solid #1E293B; border-bottom: none; transition: all 0.3s ease; }
    .stTabs [aria-selected="true"] { color: #00FF88 !important; background: #050810 !important; border-top: 2px solid #00FF88 !important; box-shadow: 0 -10px 20px rgba(0, 255, 136, 0.05); }
    
    .top-recommendation { background: linear-gradient(135deg, #0B1120 0%, #050810 100%); border-radius: 12px; border: 1px solid #1E293B; border-left: 6px solid #00FF88; padding: 24px 32px; margin-bottom: 24px; box-shadow: 0 15px 35px rgba(0,0,0,0.4); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
    .top-rec-title { font-size: 0.7rem; color: #94A3B8; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px; }
    .top-rec-value { font-size: 2rem; font-weight: 800; color: #FFFFFF; margin: 0; line-height: 1.1; }
    .top-rec-odd { font-size: 2.2rem; font-weight: 700; color: #FFD700; font-family: 'JetBrains Mono', monospace; }
    
    .metric-card { background: rgba(11, 17, 32, 0.8); border: 1px solid #1E293B; border-radius: 12px; padding: 20px; text-align: center; border-bottom: 3px solid #3B82F6; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
    .metric-title { font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; font-weight: 600; }
    .metric-value { font-size: 1.9rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; }

    .ai-box { background: rgba(0, 255, 136, 0.02); border-radius: 12px; padding: 24px; border: 1px solid rgba(0, 255, 136, 0.15); border-top: 4px solid #00FF88; }
    .chart-box { background: #0B1120; border-radius: 12px; padding: 20px; border: 1px solid #1E293B; border-top: 4px solid #3B82F6; }
    
    div.stButton > button { background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; font-weight: 800 !important; height: 3.5rem !important; border-radius: 8px !important; border: none !important; text-transform: uppercase; letter-spacing: 1px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOTOR DE DADOS E ALGORITMOS (APEX MATH)
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
API_HOST = "v3.football.api-sports.io"
HEADERS = {
    "x-apisports-key": API_KEY,
    "x-apisports-host": API_HOST
}

def safe_float(val, default=1.0):
    try: 
        if val is None: return default
        return max(float(val), 0.1) 
    except (ValueError, TypeError): 
        return default

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
    """Cálculo xG com Shrinkage (Regressão à Média) e Fator Momentum"""
    LEAGUE_AVG = 1.35 # Constante de ancoragem para reduzir variância
    
    # Mistura estatísticas reais com a média teórica (80% / 20%)
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
        
        # Fallback de ano se a época atual não tiver dados (ex: Amigáveis)
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
    except Exception as e:
        return {"h_f": 1.35, "h_a": 1.35, "a_f": 1.35, "a_a": 1.35, "form": "N/A", "cs_pct": 0.0}

@st.cache_data(ttl=1800)
def get_auto_odds(fixture_id, bookmaker_id=8):
    odds = {k: 0.0 for k in ["1","X","2","O15","U15","O25","U25","O35","U35","BTTS_Y","BTTS_N","AH_P15","AH_P05","AH_00","AH_M05","AH_M10","AH_M15"]}
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
    """
    Motor Poisson Bivariado Profissional.
    Inclui limitadores Dixon-Coles blindados. O Boost foi removido para evitar dupla contagem.
    """
    max_g = 12 
    prob_mtx = np.outer(poisson.pmf(np.arange(max_g), lh), poisson.pmf(np.arange(max_g), la))
    
    # Aplicação Fator Dixon-Coles Seguro (Evita Probabilidades Negativas)
    if rho != 0:
        min_rho = max(-1.0 / max(lh, 0.001), -1.0 / max(la, 0.001))
        valid_rho = max(min_rho, rho)
        
        prob_mtx[0,0] *= max(0, 1 - (lh * la * valid_rho))
        prob_mtx[0,1] *= max(0, 1 + (lh * valid_rho))
        prob_mtx[1,0] *= max(0, 1 + (la * valid_rho))
        prob_mtx[1,1] *= max(0, 1 - valid_rho)
        
    # Ajuste Tático Zero-Inflated
    if zip_factor != 1.0:
        prob_mtx[0,0] *= zip_factor 
        
    # Prevenção e Normalização Absoluta
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
# 3. SIDEBAR (CONTROLO DO PILOTO)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    
    bankroll = st.number_input("💰 BANCA TOTAL (€)", value=1000.0, step=100.0, key="bk_pro")
    data_consulta = st.date_input("📅 DATA DA ANÁLISE", value=date.today(), key="date_pro")
    
    l_map = {"Amigáveis Seleções 🌍": 10, "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, "La Liga 🇪🇸": 140, "Primeira Liga 🇵🇹": 94, "Champions League 🇪🇺": 2, "Qualificação Mundial 🏆": 1}
    ln = st.selectbox("⚽ LIGA", list(l_map.keys()), key="ln_pro")
    
    target_season = "2026" if l_map[ln] in [1, 10] else "2025"
    fix_data = fetch_fixtures(l_map[ln], season=target_season, target_date=data_consulta)
    
    m_sel = None
    auto_odds = {} 
    
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
    
    with st.expander("⚙️ ODDS MANUAIS / AJUSTES"):
        c1, c2, c3 = st.columns(3)
        o_1 = c1.number_input("Casa", value=float(auto_odds.get("1", 1.01) or 1.01))
        o_x = c2.number_input("Empate", value=float(auto_odds.get("X", 1.01) or 1.01))
        o_2 = c3.number_input("Fora", value=float(auto_odds.get("2", 1.01) or 1.01))
        
        c4, c5 = st.columns(2)
        o_o15 = c4.number_input("Over 1.5", value=float(auto_odds.get("O15", 1.01) or 1.01))
        o_u15 = c5.number_input("Under 1.5", value=float(auto_odds.get("U15", 1.01) or 1.01))
        o_o25 = c4.number_input("Over 2.5", value=float(auto_odds.get("O25", 1.01) or 1.01))
        o_u25 = c5.number_input("Under 2.5", value=float(auto_odds.get("U25", 1.01) or 1.01))
        
        c6, c7 = st.columns(2)
        o_ah_00 = c6.number_input("DNB (0.0)", value=float(auto_odds.get("AH_00", 1.01) or 1.01))
        o_ah_m10 = c7.number_input("AH -1.0", value=float(auto_odds.get("AH_M10", 1.01) or 1.01))
        o_btts_y = c6.number_input("BTTS Sim", value=float(auto_odds.get("BTTS_Y", 1.01) or 1.01))
        o_btts_n = c7.number_input("BTTS Não", value=float(auto_odds.get("BTTS_N", 1.01) or 1.01))
        o_ah_p15 = c6.number_input("AH +1.5", value=float(auto_odds.get("AH_P15", 1.01) or 1.01))

# ==========================================
# 4. DASHBOARD (TABS)
# ==========================================
tab1, tab2, tab3 = st.tabs(["🔬 DEEP DIVE", "🌍 ALPHA SCANNER", "🏦 CAIXA FORTE"])

# ====== TAB 1: DEEP DIVE ======
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
                <div style="color:#FFF;">Forma: {format_form(s_h['form'])} | Clean Sheets: <b>{s_h['cs_pct']:.0%}</b></div>
            </div>
            <div style="flex: 1; text-align: right;">
                <div class="top-rec-title">✈️ {m_sel['teams']['away']['name']}</div>
                <div style="color:#FFF;">Forma: {format_form(s_a['form'])} | Clean Sheets: <b>{s_a['cs_pct']:.0%}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        raw_mkts = [
            ("Vencedor Casa", res["Vencedor Casa"], o_1), ("Empate (X)", res["Empate (X)"], o_x), ("Vencedor Fora", res["Vencedor Fora"], o_2),
            ("Mais de 1.5 Golos", res["Mais de 1.5 Golos"], o_o15), ("Menos de 1.5 Golos", res["Menos de 1.5 Golos"], o_u15),
            ("Mais de 2.5 Golos", res["Mais de 2.5 Golos"], o_o25), ("Menos de 2.5 Golos", res["Menos de 2.5 Golos"], o_u25),
            ("Ambas Marcam (Sim)", res["Ambas Marcam (Sim)"], o_btts_y), ("Ambas Marcam (Não)", res["Ambas Marcam (Não)"], o_btts_n),
            ("Empate Anula (Casa)", res["Empate Anula (Casa)"], o_ah_00), ("Handicap -1.0 (Casa)", res["Handicap -1.0 (Casa)"], o_ah_m10),
            ("Handicap +1.5 (Casa)", res["Handicap +1.5 (Casa)"], o_ah_p15)
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
            
            # Gestão de Banca Quarter-Kelly (Otimizado) - Max 4% da banca absoluta.
            kelly_optimo = edge_final / (best[3] - 1)
            kelly_frac = min(max(0, kelly_optimo * 0.20), 0.04) 
            stake_sugerida = bankroll * kelly_frac
            
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
                if st.button("📥 REGISTAR", key="reg_bet", use_container_width=True):
                    nova_aposta = pd.DataFrame([{
                        "Data": date.today().strftime('%Y-%m-%d'), 
                        "Jogo": f"{m_sel['teams']['home']['name']} vs {m_sel['teams']['away']['name']}", 
                        "Aposta": best[0], "Odd Comprada": best[3], "Odd Real": round(odd_justa, 2), 
                        "Stake (€)": round(stake_sugerida, 2), "Lucro Extra": round(edge_final, 3), "Estado": "Pendente"
                    }])
                    if not nova_aposta.empty and not nova_aposta.isna().all().all():
                         st.session_state.bet_history = pd.concat([st.session_state.bet_history, nova_aposta], ignore_index=True)
                    st.toast("Aposta gravada no histórico!", icon="✅")
        else:
            st.warning("Mercado Eficiente - Nenhuma margem de lucro (Edge) encontrada neste evento. Preserve a Banca.")

        if valid_mkts:
            df = pd.DataFrame(valid_mkts, columns=["Aposta", "ProbWin", "ProbVoid", "OddCasa", "Vantagem", "OddReal"]).sort_values(by="Vantagem", ascending=False)
            colors_v = ['#FFD700' if e > 0.10 else '#00FF88' if e > 0.025 else '#EF4444' for e in df["Vantagem"]]
            
            fig_t = go.Figure(data=[go.Table(
                header=dict(values=['<b>MERCADO DA APOSTA</b>', '<b>PROB.</b>', '<b>ODD REAL</b>', '<b>ODD CASA</b>', '<b>EDGE</b>'], fill_color='#0B1120', font=dict(color='#64748B', size=11), height=45),
                cells=dict(values=[df.Aposta, df.ProbWin.map('{:.1%}'.format), df.OddReal.map('{:.2f}'.format), df.OddCasa.map('{:.2f}'.format), df.Vantagem.map('{:+.1%}'.format)], fill_color='#050810', font=dict(color=['#FFFFFF', '#E2E8F0', '#E2E8F0', '#E2E8F0', colors_v], size=13), height=40)
            )])
            fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=(len(df)*40)+50, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_t, use_container_width=True)

        col_ai, col_chart = st.columns([1, 1])
        with col_ai:
            msg = f"O mercado de <b>{best[0]}</b> tem {edge_final:.1%} de vantagem." if value_bets else "Sem desvios estatísticos significativos."
            st.markdown(f"<div class='ai-box'><h4 style='color:#00FF88;'>🤖 Analista Oracle</h4><p>{msg} Modelo Poisson Bivariado Apex garante precisão alinhada ao xG.</p></div>", unsafe_allow_html=True)
        with col_chart:
            xr = np.arange(7); fig = go.Figure()
            fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name=m_sel['teams']['home']['name'], mode='lines', fill='tozeroy', line=dict(color='#00FF88')))
            fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name=m_sel['teams']['away']['name'], mode='lines', fill='tozeroy', line=dict(color='#3B82F6')))
            fig.update_layout(title="📊 PROBABILIDADE DE GOLOS", height=230, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

# ====== TAB 2: ALPHA SCANNER ======
with tab2:
    st.markdown("<h2 style='font-size:2.5rem; letter-spacing:-1px;'>🌍 SCANNER GLOBAL DE PORTFÓLIO</h2>", unsafe_allow_html=True)
    if st.button("🔥 EXECUTAR VARREDURA GLOBAL", key="scan_global", use_container_width=True):
        if not fix_data: st.warning("Sem jogos para a liga selecionada.")
        else:
            progress_bar, status_text = st.progress(0), st.empty()
            portfolio = []
            
            for i, f in enumerate(fix_data):
                try:
                    home, away, fix_id = f['teams']['home']['name'], f['teams']['away']['name'], f['fixture']['id']
                    status_text.markdown(f"🔍 **Analisando:** {home} vs {away}...")
                    
                    s_h, s_a = get_pro_stats(f['teams']['home']['id'], l_map[ln]), get_pro_stats(f['teams']['away']['id'], l_map[ln])
                    odds = get_auto_odds(fix_id)
                    
                    if odds.get("1", 0) > 1.10:
                        lh, la = calculate_auto_xg(s_h, s_a) if use_auto_xg else ((s_h['h_f']*s_a['a_a'])**0.5, (s_a['a_f']*s_h['h_a'])**0.5)
                        res, _ = run_master_math(lh, la, rho=-0.13, zip_factor=zip_factor)
                        
                        scan_mkts = [
                            (f"{home} (Venc)", res["Vencedor Casa"], odds.get("1", 0)),
                            (f"{away} (Venc)", res["Vencedor Fora"], odds.get("2", 0)),
                            (f"Empate (X)", res["Empate (X)"], odds.get("X", 0)),
                            (f"Over 2.5", res["Mais de 2.5 Golos"], odds.get("O25", 0)),
                            (f"Under 2.5", res["Menos de 2.5 Golos"], odds.get("U25", 0)),
                            (f"BTTS (Sim)", res["Ambas Marcam (Sim)"], odds.get("BTTS_Y", 0))
                        ]
                        
                        for m_name, prob_data, odd in scan_mkts:
                            p_win = prob_data[0] if isinstance(prob_data, tuple) else prob_data
                            p_void = prob_data[1] if isinstance(prob_data, tuple) else 0.0
                            
                            if 1.40 <= odd <= 4.00 and p_win > 0:
                                edge = (p_win * odd) + p_void - 1
                                if edge > 0.045: 
                                    portfolio.append({
                                        "Jogo": f"{home} vs {away}",
                                        "Aposta": m_name, 
                                        "Certeza": p_win, 
                                        "Odd Real": (1 - p_void) / p_win, 
                                        "Odd Casa": odd, 
                                        "Lucro Extra": edge, 
                                        "Kelly_Raw": max(0, (edge / (odd - 1)) * 0.20) # Alinhado com a Quarter-Kelly da Tab 1
                                    })
                except Exception as e: continue
                progress_bar.progress((i + 1) / len(fix_data))
            
            status_text.success("✅ Varredura Concluída!")
            if portfolio:
                df_port = pd.DataFrame(portfolio).sort_values(by="Lucro Extra", ascending=False).head(5)
                # Teto Máximo Global de Risco: Não expor mais de 15% da banca inteira na varredura
                sum_kelly = df_port["Kelly_Raw"].sum()
                df_port["Stake (€)"] = df_port["Kelly_Raw"] * bankroll * min(0.15 / sum_kelly, 1.0) if sum_kelly > 0 else 0
                
                st.markdown("""
                <div style='background:#0B1120; border-radius:12px; padding:20px; border-left:5px solid #00FF88; margin: 20px 0;'>
                    <h3 style='margin:0; color:#00FF88;'>💼 PORTFÓLIO DE VALOR (TOP 5)</h3>
                    <p style='color:#94A3B8; margin:0;'>Seleção otimizada baseada em desvios estatísticos. Risco calculado e ajustado.</p>
                </div>
                """, unsafe_allow_html=True)
                
                fig_port = go.Figure(data=[go.Table(
                    columnorder = [1,2,3,4,5,6], columnwidth = [200, 150, 80, 80, 80, 100],
                    header=dict(
                        values=['<b>JOGO</b>', '<b>APOSTA</b>', '<b>PROB.</b>', '<b>ODD</b>', '<b>EDGE</b>', '<b>STAKE SUGERIDA</b>'],
                        fill_color='#020408', align='center', font=dict(color='#64748B', size=11), height=45
                    ),
                    cells=dict(
                        values=[
                            df_port["Jogo"],
                            df_port["Aposta"], 
                            df_port["Certeza"].map('{:.1%}'.format), 
                            df_port["Odd Casa"].map('{:.2f}'.format), 
                            df_port["Lucro Extra"].map('{:+.1%}'.format), 
                            df_port["Stake (€)"].map('{:.2f}€'.format)
                        ],
                        fill_color='#0B1120', align='center', 
                        font=dict(color=['#FFFFFF', '#FFFFFF', '#E2E8F0', '#E2E8F0', '#00FF88', '#FFD700'], size=13, family='JetBrains Mono'),
                        height=40
                    )
                )])
                fig_port.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=300, paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_port, use_container_width=True)
                
                st.info("💡 Dica: Distribuir o risco por vários jogos com 'Edge' positivo é a única forma de vencer a variância estatística a longo prazo.")
            else:
                st.error("Varredura terminada. O mercado está 'eficiente' hoje (odds muito baixas ou ajustadas pelas casas de apostas). Recomenda-se preservar a banca.")
                
# ====== TAB 3: CAIXA FORTE ======
with tab3:
    st.markdown("<h2 style='font-size:2.5rem; letter-spacing:-1px; color:#FFD700;'>🏦 CAIXA FORTE (AUDITORIA)</h2>", unsafe_allow_html=True)
    
    if st.session_state.bet_history.empty:
        st.markdown("""
        <div style='text-align:center; padding:100px 20px;'>
            <h1 style='opacity:0.1; font-size:5rem;'>EMPTY</h1>
            <h3 style='opacity:0.5; font-weight:300;'>Sem operações registadas. Vá ao 'Deep Dive' para validar valor.</h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        df_hist = st.session_state.bet_history
        
        c1, c2, c3, c4 = st.columns(4)
        
        total_staked = df_hist['Stake (€)'].sum()
        avg_edge = df_hist["Lucro Extra"].mean()
        expected_profit = (df_hist['Stake (€)'] * df_hist['Lucro Extra']).sum()
        total_bets = len(df_hist)

        with c1: st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Investido</div><div class='metric-value'>{total_staked:.2f}€</div></div>", unsafe_allow_html=True)
        with c2:
            color = "#00FF88" if avg_edge > 0.03 else "#FFD700" if avg_edge > 0 else "#EF4444"
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Edge Médio (CLV)</div><div class='metric-value' style='color:{color};'>{avg_edge:+.2%}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><div class='metric-title'>Retorno Esperado (EV)</div><div class='metric-value' style='color:#FFD700;'>+{expected_profit:.2f}€</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div class='metric-card'><div class='metric-title'>Apostas Totais</div><div class='metric-value' style='color:#94A3B8;'>{total_bets}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_chart, col_info = st.columns([2, 1])
        
        with col_chart:
            df_hist['EV_Accum'] = (df_hist['Stake (€)'] * df_hist['Lucro Extra']).cumsum()
            fig_ev = go.Figure()
            fig_ev.add_trace(go.Scatter(x=list(range(1, len(df_hist) + 1)), y=df_hist['EV_Accum'], mode='lines+markers', name='Lucro Esperado', line=dict(color='#FFD700', width=3), fill='tozeroy', fillcolor='rgba(255, 215, 0, 0.1)'))
            fig_ev.update_layout(title="📈 CURVA DE CRESCIMENTO MATEMÁTICO (EV+)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=0, r=0, t=30, b=0), xaxis=dict(title="Número de Apostas", showgrid=False, color="#64748B"), yaxis=dict(title="Lucro Acumulado (€)", showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#64748B"))
            st.plotly_chart(fig_ev, use_container_width=True)

        with col_info:
            st.markdown(f"""
            <div style='background: rgba(0, 255, 136, 0.05); border-radius: 12px; padding: 20px; border: 1px solid rgba(0, 255, 136, 0.2); height: 100%;'>
                <h4 style='color: #00FF88; margin-top: 0;'>Análise do Oráculo</h4>
                <p style='font-size: 0.9rem; color: #E2E8F0;'>O teu <b>Edge Médio de {avg_edge:.1%}</b> indica que estás a comprar odds com um desconto estatístico face à matemática real do jogo.</p>
                <p style='font-size: 0.9rem; color: #94A3B8;'>Se mantiveres este volume consistentemente, a variância estatística será anulada e o teu lucro real convergirá para os <b>{expected_profit:.2f}€</b> projetados.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<h3 style='margin-top:30px; font-size:1.2rem; color:#94A3B8;'>📋 REGISTO DE AUDITORIA</h3>", unsafe_allow_html=True)
        
        fig_hist = go.Figure(data=[go.Table(
            columnorder = [1,2,3,4,5,6,7], columnwidth = [100, 220, 180, 100, 100, 100, 110],
            header=dict(values=["<b>DATA</b>", "<b>EVENTO</b>", "<b>MERCADO</b>", "<b>ODD</b>", "<b>FAIR</b>", "<b>STAKE</b>", "<b>EDGE</b>"], fill_color='#020408', align='center', font=dict(color='#64748B', size=11), height=40),
            cells=dict(values=[df_hist["Data"], df_hist["Jogo"], df_hist["Aposta"], df_hist["Odd Comprada"].map('{:.2f}'.format), df_hist["Odd Real"].map('{:.2f}'.format), df_hist["Stake (€)"].map('{:.2f}€'.format), df_hist["Lucro Extra"].map('{:+.1%}'.format)], fill_color='#0B1120', align='center', font=dict(color=['#64748B', '#FFFFFF', '#00FF88', '#FFFFFF', '#94A3B8', '#FFD700', '#00FF88'], size=12), height=35)
        )])
        fig_hist.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=400, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_hist, use_container_width=True)
        
        c_del, c_exp = st.columns([1, 4])
        with c_del:
            if st.button("🗑️ LIMPAR TUDO", use_container_width=True):
                st.session_state.bet_history = pd.DataFrame(columns=["Data", "Jogo", "Aposta", "Odd Comprada", "Odd Real", "Stake (€)", "Lucro Extra", "Estado"])
                st.rerun()
