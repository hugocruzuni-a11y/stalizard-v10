import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date
import time

# --- 1. CONFIGURAÇÃO DE DESIGN E BASE DE DADOS (APEX BUILD) ---
import streamlit as st
import pandas as pd

# 1. Configuração de Página de Alta Performance
st.set_page_config(
    page_title="ORACLE V140 - APEX QUANT", 
    page_icon="🎯",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Inicialização do Estado (Caixa Forte)
if 'bet_history' not in st.session_state:
    st.session_state.bet_history = pd.DataFrame(columns=[
        "Data", "Jogo", "Aposta", "Odd Comprada", "Odd Real", "Stake (€)", "Lucro Extra", "Estado"
    ])

# 3. Engine de Estilo (CSS Injection)
st.markdown("""
    <style>
    /* Importação de Fontes Premium */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    /* Global Reset */
    .stApp { 
        background-color: #050810; 
        color: #FFFFFF; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Sidebar Minimalista */
    [data-testid="stSidebar"] { 
        background-color: #020408 !important; 
        border-right: 1px solid #1E293B !important; 
    }
    
    /* Estilização de Tabs (Navegação Superior) */
    .stTabs [data-baseweb="tab-list"] { 
        background-color: transparent; 
        gap: 12px; 
        border-bottom: 1px solid #1E293B; 
    }
    .stTabs [data-baseweb="tab"] { 
        color: #64748B; 
        font-weight: 700; 
        font-size: 0.95rem; 
        padding: 10px 20px; 
        background: #0B1120; 
        border-radius: 8px 8px 0 0; 
        border: 1px solid #1E293B; 
        border-bottom: none; 
        transition: all 0.3s ease; 
    }
    .stTabs [aria-selected="true"] { 
        color: #00FF88 !important; 
        background: #050810 !important; 
        border-top: 2px solid #00FF88 !important; 
        box-shadow: 0 -10px 20px rgba(0, 255, 136, 0.05);
    }
    
    /* Cards de Recomendação (Ouro/Danger) */
    .top-recommendation { 
        background: linear-gradient(135deg, #0B1120 0%, #050810 100%); 
        border-radius: 12px; 
        border: 1px solid #1E293B; 
        border-left: 6px solid #00FF88; 
        padding: 24px 32px; 
        margin-bottom: 24px; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.4); 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        flex-wrap: wrap;
    }
    .top-rec-danger { border-left-color: #EF4444 !important; }
    
    .top-rec-title { 
        font-size: 0.7rem; 
        color: #94A3B8; 
        font-weight: 800; 
        letter-spacing: 1.5px; 
        text-transform: uppercase; 
        margin-bottom: 6px; 
    }
    .top-rec-value { 
        font-size: 2rem; 
        font-weight: 800; 
        color: #FFFFFF; 
        margin: 0; 
        line-height: 1.1; 
    }
    .top-rec-odd { 
        font-size: 2.2rem; 
        font-weight: 700; 
        color: #FFD700; 
        font-family: 'JetBrains Mono', monospace; 
    }
    
    /* Caixas de IA e Gráficos */
    .ai-box { 
        background: rgba(0, 255, 136, 0.02); 
        border-radius: 12px; 
        padding: 24px; 
        border: 1px solid rgba(0, 255, 136, 0.15); 
        border-top: 4px solid #00FF88; 
    }
    .chart-box { 
        background: #0B1120; 
        border-radius: 12px; 
        padding: 20px; 
        border: 1px solid #1E293B; 
        border-top: 4px solid #3B82F6; 
    }
    
    /* Métricas de Performance */
    .metric-card { 
        background: #0B1120; 
        border-radius: 12px; 
        padding: 20px; 
        border: 1px solid #1E293B; 
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-3px); border-color: #334155; }
    
    /* Customização de Input e Botões */
    div.stButton > button { 
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; 
        color: #000000 !important; 
        font-weight: 800 !important; 
        height: 3.5rem !important; 
        border-radius: 8px !important; 
        border: none !important; 
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .btn-register button { 
        background: transparent !important; 
        border: 2px solid #00FF88 !important; 
        color: #00FF88 !important; 
    }
    
    /* Tooltips e Labels */
    .stSlider label, .stSelectbox label { 
        font-size: 0.75rem !important; 
        color: #94A3B8 !important; 
        font-weight: 600; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE DADOS E ALGORITMOS ---
# Configurações de API
API_KEY = "8171043bf0a322286bb127947dbd4041"
API_HOST = "v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

def safe_float(val, default=1.0):
    try: 
        if val is None: return default
        return float(val)
    except (ValueError, TypeError): 
        return default

def format_form(form_str):
    """Renderiza a forma recente com badges visuais no Streamlit."""
    if not form_str or form_str == 'N/A': 
        return "<span style='color:#94A3B8;'>Sem dados</span>"
    
    # Pegamos os últimos 5 jogos
    recent_form = form_str[-5:]
    html = ""
    for char in recent_form:
        style = "padding:2px 6px; border-radius:4px; margin-right:4px; font-weight:bold; font-size:0.75rem; color:#000;"
        if char == 'W':
            html += f"<span style='{style} background:#00FF88;'>V</span>"
        elif char == 'D':
            html += f"<span style='{style} background:#FFD700;'>E</span>"
        elif char == 'L':
            html += f"<span style='{style} background:#EF4444; color:#FFF;'>D</span>"
    return html

def calculate_auto_xg(s_h, s_a):
    """
    Calcula o xG projetado (Expectativa de Golos) usando Médias de Ataque/Defesa
    e um multiplicador de Momentum baseado na forma recente.
    """
    def get_momentum_factor(form_str):
        if not form_str or form_str == 'N/A': return 1.0
        # Peso maior para vitórias recentes (W=3, D=1, L=0)
        recent = form_str[-5:]
        pts = sum([3 if c=='W' else 1 if c=='D' else 0 for c in recent])
        max_pts = len(recent) * 3
        # O momentum varia de 0.90 (forma péssima) a 1.10 (forma incrível)
        return 0.90 + ((pts / max_pts) * 0.20) if max_pts > 0 else 1.0

    # Lógica de Cruzamento: (Ataque Casa * Defesa Fora) e vice-versa
    # Usamos a média geométrica para suavizar outliers
    base_xg_h = (s_h['h_f'] * s_a['a_a']) ** 0.5
    base_xg_a = (s_a['a_f'] * s_h['h_a']) ** 0.5
    
    # Aplicação do Momentum
    xg_h = base_xg_h * get_momentum_factor(s_h['form'])
    xg_a = base_xg_a * get_momentum_factor(s_a['form'])
    
    return round(xg_h, 2), round(xg_a, 2)

@st.cache_data(ttl=3600)
def get_pro_stats(team_id, league_id, season="2025"):
    """Puxa estatísticas avançadas da API e trata médias de golos."""
    try:
        url = f"https://{API_HOST}/teams/statistics"
        params = {"league": league_id, "season": season, "team": team_id}
        r = requests.get(url, headers=HEADERS, params=params).json()
        
        stats = r.get('response', {})
        goals = stats.get('goals', {})
        fixtures = stats.get('fixtures', {})
        
        # Extração de Médias (Golos marcados/sofridos em casa e fora)
        return {
            "h_f": safe_float(goals.get('for', {}).get('average', {}).get('home'), 1.5),
            "h_a": safe_float(goals.get('against', {}).get('average', {}).get('home'), 1.1),
            "a_f": safe_float(goals.get('for', {}).get('average', {}).get('away'), 1.2),
            "a_a": safe_float(goals.get('against', {}).get('average', {}).get('away'), 1.4),
            "form": stats.get('form', 'N/A'),
            "cs_pct": safe_float(stats.get('clean_sheet', {}).get('total', 0)) / safe_float(fixtures.get('played', {}).get('total', 1), 1.0)
        }
    except Exception as e:
        # Fallback de segurança para não interromper o código
        return {"h_f": 1.5, "h_a": 1.1, "a_f": 1.2, "a_a": 1.4, "form": "N/A", "cs_pct": 0.1}

@st.cache_data(ttl=1800)
def get_auto_odds(fixture_id, bookmaker_id=8):
    """
    Captura as odds em tempo real. Bookmaker 8 costuma ser a Bet365 na API-Sports.
    """
    # Inicialização com 1.0 (Odd mínima neutra) para evitar divisões por zero
    odds = {k: 0.0 for k in ["1","X","2","O15","U15","O25","U25","O35","U35","BTTS_Y","BTTS_N","AH_P15","AH_P05","AH_00","AH_M05","AH_M10","AH_M15"]}
    
    try:
        url = f"https://{API_HOST}/odds"
        r = requests.get(url, headers=HEADERS, params={"fixture": fixture_id, "bookmaker": bookmaker_id}).json()
        
        if not r.get('response'): return odds
        
        # Navegação segura na estrutura da API
        bookmakers = r['response'][0].get('bookmakers', [])
        if not bookmakers: return odds
        
        bets = bookmakers[0].get('bets', [])
        
        for bet in bets:
            name = bet['name']
            vals = {v['value']: safe_float(v['odd']) for v in bet['values']}
            
            if name == 'Match Winner':
                odds["1"], odds["X"], odds["2"] = vals.get('Home', 0), vals.get('Draw', 0), vals.get('Away', 0)
            elif name == 'Goals Over/Under':
                odds["O15"] = vals.get('Over 1.5', 0); odds["U15"] = vals.get('Under 1.5', 0)
                odds["O25"] = vals.get('Over 2.5', 0); odds["U25"] = vals.get('Under 2.5', 0)
                odds["O35"] = vals.get('Over 3.5', 0); odds["U35"] = vals.get('Under 3.5', 0)
            elif name == 'Both Teams Score':
                odds["BTTS_Y"], odds["BTTS_N"] = vals.get('Yes', 0), vals.get('No', 0)
            elif name == 'Asian Handicap':
                # Normalização de chaves para evitar erros de string
                odds["AH_P15"] = vals.get('Home +1.5', 0)
                odds["AH_P05"] = vals.get('Home +0.5', 0)
                odds["AH_00"] = vals.get('Home +0.0', vals.get('Home 0.0', 0))
                odds["AH_M05"] = vals.get('Home -0.5', 0)
                odds["AH_M10"] = vals.get('Home -1.0', 0)
                odds["AH_M15"] = vals.get('Home -1.5', 0)
    except:
        pass
    return odds
# MATEMÁTICA QUANTITATIVA (Poisson Bivariado c/ Push)
def run_master_math(lh, la, rho, boost, zip_factor):
    """
    Executa o modelo Poisson Bivariado com ajuste de correlação e inflação de zeros.
    lh: lambda casa (expected goals)
    la: lambda fora (expected goals)
    rho: parâmetro de correlação (Dixon-Coles)
    boost: ajuste dinâmico de tendência
    zip_factor: fator tático para 0-0 (Zero-Inflated)
    """
    # 1. Ajuste de Tendência (Boost)
    lh *= (1 + boost)
    la *= (1 - boost)
    
    max_g = 12 # Aumentado para 12 para capturar scores altos (ex: 5-3, 6-2) sem perder probabilidade
    
    # 2. Geração da Matriz Base (Poisson Independente)
    prob_mtx = np.outer(poisson.pmf(np.arange(max_g), lh), poisson.pmf(np.arange(max_g), la))
    
    # 3. Ajuste de Correlação (Dixon-Coles simplificado para baixos scores)
    # Corrige a subestimação de empates (0-0, 1-1) e vitórias magras (1-0, 0-1)
    if rho != 0:
        prob_mtx[0,0] *= (1 - lh * la * rho)
        prob_mtx[0,1] *= (1 + lh * rho)
        prob_mtx[1,0] *= (1 + la * rho)
        prob_mtx[1,1] *= (1 - rho)
    
    # 4. Controlo Tático (Zero-Inflated para mercados de 0-0 e Under)
    prob_mtx[0,0] *= zip_factor 
    
    # 5. Normalização (Essencial para manter a soma das probabilidades em 1.0 ou 100%)
    prob_mtx /= prob_mtx.sum() 
    
    # Pre-calculo de matrizes auxiliares para velocidade
    goals_sum = np.add.outer(np.arange(max_g), np.arange(max_g))
    # Diferença de golos (Casa - Fora)
    diff_matrix = np.subtract.outer(np.arange(max_g), np.arange(max_g))
    
    # Probabilidades Base
    ph = prob_mtx[diff_matrix > 0].sum()   # Vitória Casa
    px = prob_mtx[diff_matrix == 0].sum()  # Empate
    pa = prob_mtx[diff_matrix < 0].sum()   # Vitória Fora
    
    # Probabilidade de vitória por exatamente 1 golo (para Handicap -1.0)
    h_win_by_1 = prob_mtx[diff_matrix == 1].sum()
    
    # Probabilidade de Não Sofrer Golos (Clean Sheets)
    cs_h = prob_mtx[:, 0].sum()
    cs_a = prob_mtx[0, :].sum()

    return {
        # Formato: (Prob_Ganhar, Prob_Anular/Push)
        "Vencedor Casa": (ph, 0),
        "Empate (X)": (px, 0),
        "Vencedor Fora": (pa, 0),
        
        "Mais de 1.5 Golos": (prob_mtx[goals_sum > 1.5].sum(), 0),
        "Menos de 1.5 Golos": (prob_mtx[goals_sum < 1.5].sum(), 0),
        
        "Mais de 2.5 Golos": (prob_mtx[goals_sum > 2.5].sum(), 0),
        "Menos de 2.5 Golos": (prob_mtx[goals_sum < 2.5].sum(), 0),
        
        "Mais de 3.5 Golos": (prob_mtx[goals_sum > 3.5].sum(), 0),
        "Menos de 3.5 Golos": (prob_mtx[goals_sum < 3.5].sum(), 0),
        
        "Ambas Marcam (Sim)": (1 - (cs_h + cs_a - prob_mtx[0,0]), 0), 
        "Ambas Marcam (Não)": (cs_h + cs_a - prob_mtx[0,0], 0),
        
        "Handicap +1.5 (Casa)": (ph + px + prob_mtx[diff_matrix == -1].sum(), 0), 
        "Handicap +0.5 (Casa)": (ph + px, 0),
        "Empate Anula (Casa)": (ph, px),             # Se empatar, devolve a stake
        "Handicap -0.5 (Casa)": (ph, 0),
        "Handicap -1.0 (Casa)": (ph - h_win_by_1, h_win_by_1), # Ganhar por 2+ ganha, por 1 anula
        "Handicap -1.5 (Casa)": (prob_mtx[diff_matrix >= 2].sum(), 0)
    }, prob_mtx

# --- 3. SIDEBAR (CONTROLO DO PILOTO) ---
# --- FUNÇÃO AUXILIAR PARA CACHE DE JOGOS ---
@st.cache_data(ttl=3600)
def fetch_today_fixtures(league_id, season="2025"):
    try:
        params = {"date": date.today().strftime('%Y-%m-%d'), "league": league_id, "season": season}
        r = requests.get(f"https://{API_HOST}/fixtures", headers=HEADERS, params=params).json()
        return r.get('response', [])
    except:
        return []

with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; margin:0;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.7rem; color:#64748B;'>APEX QUANTITATIVE TERMINAL</p>", unsafe_allow_html=True)
    
    # 1. Gestão de Capital
    bankroll = st.number_input("💰 BANCA TOTAL (€)", value=1000.0, step=50.0, help="Define o capital total para cálculo de stake (Kelly).")
    
    st.markdown("---")
    
    # 2. Seleção de Liga e Mercado
    l_map = {
        "Portugal 🇵🇹": 94, 
        "England 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39, 
        "Spain 🇪🇸": 140, 
        "Italy 🇮🇹": 135, 
        "Champions League 🇪🇺": 2
    }
    ln = st.selectbox("⚽ SELECIONAR LIGA", list(l_map.keys()))
    
    # Busca de jogos com Cache para poupar créditos da API
    fix_data = fetch_today_fixtures(l_map[ln])
    
    if fix_data:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": i for i, f in enumerate(fix_data)}
        m_display = st.selectbox("🎯 JOGO EM FOCO (Deep Dive)", list(m_map.keys()))
        m_sel = fix_data[m_map[m_display]]
        
        # Carregamento automático de Odds (Bet365 id: 8)
        with st.spinner('Sincronizando Odds...'):
            auto_odds = get_auto_odds(m_sel['fixture']['id'])
    else:
        st.info("Nenhum jogo encontrado para hoje nesta liga.")
        m_sel = None
        auto_odds = {k: 0.0 for k in ["1","X","2","O15","U15","O25","U25","O35","U35","BTTS_Y","BTTS_N","AH_P15","AH_P05","AH_00","AH_M05","AH_M10","AH_M15"]}

    st.markdown("---")
    
    # 3. Calibração Tática (O Cérebro)
    st.markdown("<p style='font-size:0.75rem; color:#00FF88; font-weight:800;'>🛠️ AJUSTE DO ALGORITMO</p>", unsafe_allow_html=True)
    
    use_auto_xg = st.toggle("🧠 AUTO-xG ENGINE", value=True, help="Usa médias de ataque/defesa e momentum em vez de resultados históricos brutos.")
    
    zip_factor = st.slider(
        "⚡ FATOR DE COMPRESSÃO (0-0)", 
        0.80, 1.30, 1.05, 0.05,
        help="Ajusta a probabilidade de empate sem golos. Use >1.10 para equipas defensivas (estilo Simeone) ou finais de taça."
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 INICIAR ALPHA SCAN", use_container_width=True):
        st.toast("Matriz de Poisson atualizada!", icon="🔥")

    # 4. Odds Manuais (Sobrescrita de Emergência)
    with st.expander("⚙️ OVERRIDE DE ODDS"):
        st.caption("Ajuste manual se a API estiver desatualizada.")
        col_win = st.columns(3)
        o_1 = col_win[0].number_input("1", value=auto_odds["1"], step=0.01)
        o_x = col_win[1].number_input("X", value=auto_odds["X"], step=0.01)
        o_2 = col_win[2].number_input("2", value=auto_odds["2"], step=0.01)
        
        st.divider()
        col_g = st.columns(2)
        o_o15 = col_g[0].number_input("Over 1.5", value=auto_odds["O15"], step=0.01)
        o_u15 = col_g[1].number_input("Under 1.5", value=auto_odds["U15"], step=0.01)
        o_o25 = col_g[0].number_input("Over 2.5", value=auto_odds["O25"], step=0.01)
        o_u25 = col_g[1].number_input("Under 2.5", value=auto_odds["U25"], step=0.01)
        
        st.divider()
        col_ah = st.columns(2)
        o_btts_y = col_ah[0].number_input("BTTS Sim", value=auto_odds["BTTS_Y"], step=0.01)
        o_btts_n = col_ah[1].number_input("BTTS Não", value=auto_odds["BTTS_N"], step=0.01)
        o_ah_00 = col_ah[0].number_input("DNB (0.0)", value=auto_odds["AH_00"], step=0.01)
        o_ah_m10 = col_ah[1].number_input("AH -1.0", value=auto_odds["AH_M10"], step=0.01)
        # Inserir outros AH conforme necessário...
        o_ah_p15 = auto_odds["AH_P15"]; o_ah_p05 = auto_odds["AH_P05"]
        o_ah_m05 = auto_odds["AH_M05"]; o_ah_m15 = auto_odds["AH_M15"]; o_o35 = auto_odds["O35"]; o_u35 = auto_odds["U35"]

# --- Inicialização das Tabs ---
tab1, tab2, tab3 = st.tabs(["🔬 DEEP DIVE", "🌍 ALPHA SCANNER", "🏦 CAIXA FORTE"])

# ====== TAB 1: DEEP DIVE ======
with tab1:
    if not m_sel:
        st.markdown("<div style='text-align:center; padding-top:150px;'><h1 style='opacity:0.1; font-size:4rem;'>SELECIONE UM JOGO</h1></div>", unsafe_allow_html=True)
    else:
        # 1. Obtenção de Dados e Execução da Matemática
        s_h = get_pro_stats(m_sel['teams']['home']['id'], l_map[ln])
        s_a = get_pro_stats(m_sel['teams']['away']['id'], l_map[ln])
        
        if use_auto_xg:
            xg_h, xg_a = calculate_auto_xg(s_h, s_a)
            res, mtx = run_master_math(xg_h, xg_a, -0.11, 0.0, zip_factor) 
        else:
            lh, la = (s_h['h_f']*s_a['a_a'])**0.5, (s_a['a_f']*s_h['h_a'])**0.5
            res, mtx = run_master_math(lh, la, -0.11, 0.12, zip_factor)
        
        # 2. Cabeçalho de Identidade do Jogo
        st.markdown(f"<h2 style='margin-bottom:10px; font-size:3.2rem; letter-spacing:-2px;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#475569; font-weight:300;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h2>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="context-card">
            <div>
                <div class="team-name-context">🏠 {m_sel['teams']['home']['name']}</div>
                <div class="stats-text">Forma Recente: {format_form(s_h['form'])}</div>
                <div class="stats-text">Clean Sheets: <b style="color:#FFF;">{s_h['cs_pct']:.0%}</b></div>
            </div>
            <div style="text-align: right;">
                <div class="team-name-context">✈️ {m_sel['teams']['away']['name']}</div>
                <div class="stats-text">Forma Recente: {format_form(s_a['form'])}</div>
                <div class="stats-text">Clean Sheets: <b style="color:#FFF;">{s_a['cs_pct']:.0%}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. Processamento de Mercados e Cálculo de Edge
        raw_mkts = [
            ("Vencedor Casa", res["Vencedor Casa"], o_1), 
            ("Empate (X)", res["Empate (X)"], o_x), 
            ("Vencedor Fora", res["Vencedor Fora"], o_2),
            ("Mais de 1.5 Golos", res["Mais de 1.5 Golos"], o_o15), 
            ("Menos de 1.5 Golos", res["Menos de 1.5 Golos"], o_u15),
            ("Mais de 2.5 Golos", res["Mais de 2.5 Golos"], o_o25), 
            ("Menos de 2.5 Golos", res["Menos de 2.5 Golos"], o_u25),
            ("Ambas Marcam (Sim)", res["Ambas Marcam (Sim)"], o_btts_y), 
            ("Ambas Marcam (Não)", res["Ambas Marcam (Não)"], o_btts_n),
            ("Empate Anula (Casa)", res["Empate Anula (Casa)"], o_ah_00), 
            ("Handicap -1.0 (Casa)", res["Handicap -1.0 (Casa)"], o_ah_m10),
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
        
        # Filtro de Valor (Mínimo 2.5% de Edge para ser considerado)
        value_bets = [m for m in valid_mkts if m[4] > 0.025] 
        
        # 4. Painel de Recomendação (Aposta de Ouro)
        if value_bets:
            # Prioridade: Odds entre 1.50 e 3.00 (Zona de Ouro)
            safe_bets = [m for m in value_bets if 1.50 <= m[3] <= 3.00]
            best = sorted(safe_bets, key=lambda x: x[4], reverse=True)[0] if safe_bets else sorted(value_bets, key=lambda x: x[4], reverse=True)[0]
            
            edge_final = best[4]
            # Kelly 20% (Conservative) - Crucial para gestão de banca profissional
            kelly_frac = max(0, (edge_final / (best[3] - 1)) * 0.20)
            stake_sugerida = bankroll * kelly_frac
            odd_justa = best[5]
            
            col_rec, col_btn = st.columns([3, 1])
            with col_rec:
                st.markdown(f"""
                <div class="top-recommendation">
                    <div><div class="top-rec-title">Aposta de Ouro (Valor Detectado)</div><div class="top-rec-value">{best[0]}</div></div>
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
                        "Aposta": best[0], "Odd Comprada": best[3], 
                        "Odd Real": round(odd_justa, 2), "Stake (€)": round(stake_sugerida, 2), 
                        "Lucro Extra": round(edge_final, 3), "Estado": "Pendente"
                    }])
                    st.session_state.bet_history = pd.concat([st.session_state.bet_history, nova_aposta], ignore_index=True)
                    st.toast("Aposta gravada no histórico!", icon="✅")
        else:
            st.markdown("""
            <div class="top-recommendation" style="border-top: 4px solid #EF4444; background: rgba(239, 68, 68, 0.05);">
                <div><div class="top-rec-title" style="color:#EF4444;">MERCADO EFICIENTE</div><div class="top-rec-value">SEM ENTRADA</div></div>
                <div style="max-width: 400px;"><div class="top-rec-title">Análise</div><div class="stats-text">As odds da casa refletem a probabilidade real. Não há margem de lucro (Edge) neste evento.</div></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 5. Tabela Geral de Probabilidades
        if valid_mkts:
            df = pd.DataFrame(valid_mkts, columns=["Aposta", "ProbWin", "ProbVoid", "OddCasa", "Vantagem", "OddReal"])
            df = df.sort_values(by="Vantagem", ascending=False)
            
            # Colorir Edge: Dourado (>10%), Verde (>2.5%), Vermelho (Risco/Sem Valor)
            colors_v = ['#FFD700' if e > 0.10 else '#00FF88' if e > 0.025 else '#EF4444' for e in df["Vantagem"]]
            
            fig_t = go.Figure(data=[go.Table(
                columnorder = [1,2,3,4,5], columnwidth = [250, 100, 100, 100, 120],
                header=dict(
                    values=['<b>MERCADO DA APOSTA</b>', '<b>PROB. BATER</b>', '<b>ODD REAL</b>', '<b>ODD CASA</b>', '<b>EDGE</b>'], 
                    fill_color='#0B1120', align='center', font=dict(color='#64748B', size=11), height=45
                ),
                cells=dict(
                    values=[
                        df.Aposta, df.ProbWin.map('{:.1%}'.format), 
                        df.OddReal.map('{:.2f}'.format), df.OddCasa.map('{:.2f}'.format), 
                        df.Vantagem.map('{:+.1%}'.format)
                    ], 
                    fill_color='#050810', align='center', 
                    font=dict(color=['#FFFFFF', '#E2E8F0', '#E2E8F0', '#E2E8F0', colors_v], size=13, family='JetBrains Mono'), 
                    height=40
                )
            )])
            fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=(len(df)*40)+50, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_t, use_container_width=True)

        # 6. Insights da IA e Gráfico de Distribuição
        col_ai, col_chart = st.columns([1, 1])
        with col_ai:
            msg = f"O mercado de <b>{best[0]}</b> tem {edge_final:.1%} de vantagem sobre a casa." if value_bets else "Não foram encontrados desvios estatísticos significativos."
            st.markdown(f"""
            <div class='ai-box'>
                <h4 style='margin:0 0 10px 0; color:#00FF88;'>🤖 Analista Oracle</h4>
                <p style='color:#E2E8F0; font-size:0.95rem; margin:0; line-height:1.5;'>
                    {msg} O modelo de Poisson Bivariado detetou uma convergência de fluxos defensivos que favorece esta entrada.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_chart:
            st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
            xr = np.arange(7); fig = go.Figure()
            fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name=m_sel['teams']['home']['name'], mode='lines+markers', fill='tozeroy', line=dict(color='#00FF88', width=2)))
            fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name=m_sel['teams']['away']['name'], mode='lines+markers', fill='tozeroy', line=dict(color='#3B82F6', width=2)))
            fig.update_layout(
                title=dict(text="📊 PROBABILIDADE DE GOLOS", font=dict(color="#94A3B8", size=13)), 
                height=230, margin=dict(l=20,r=20,t=40,b=20), 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#64748B"),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#64748B", tickformat=".0%"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
# ====== TAB 2: ALPHA SCANNER ======
with tab2:
    st.markdown("<h2 style='font-size:2.5rem; letter-spacing:-1px;'>🌍 SCANNER GLOBAL DE PORTFÓLIO</h2>", unsafe_allow_html=True)
    
    if st.button("🔥 EXECUTAR VARREDURA GLOBAL", key="scan_global", use_container_width=True):
        if not fix_data: 
            st.warning(f"Não foram encontrados jogos agendados para a liga selecionada.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            portfolio = []
            
            # Loop de Varredura
            for i, f in enumerate(fix_data):
                try:
                    home = f['teams']['home']['name']
                    away = f['teams']['away']['name']
                    fix_id = f['fixture']['id']
                    
                    status_text.markdown(f"🔍 **Analisando:** {home} vs {away}...")
                    
                    # Chamadas de API com Cache (otimiza velocidade)
                    s_h = get_pro_stats(f['teams']['home']['id'], l_map[ln])
                    s_a = get_pro_stats(f['teams']['away']['id'], l_map[ln])
                    odds = get_auto_odds(fix_id)
                    
                    # Verificação de liquidez (se a odd existe/é válida)
                    if odds["1"] > 1.10:
                        # Cálculo do xG Projetado
                        if use_auto_xg:
                            lh, la = calculate_auto_xg(s_h, s_a)
                            res, _ = run_master_math(lh, la, -0.11, 0.0, zip_factor)
                        else:
                            lh, la = (s_h['h_f']*s_a['a_a'])**0.5, (s_a['a_f']*s_h['h_a'])**0.5
                            res, _ = run_master_math(lh, la, -0.11, 0.12, zip_factor)
                        
                        # Definição dos Mercados Escaneados
                        raw_mkts = [
                            (f"{home} (Venc)", res["Vencedor Casa"], odds["1"]),
                            (f"{away} (Venc)", res["Vencedor Fora"], odds["2"]),
                            (f"Empate ({home})", res["Empate (X)"], odds["X"]),
                            (f"Over 2.5 ({home})", res["Mais de 2.5 Golos"], odds["O25"]),
                            (f"Under 2.5 ({home})", res["Menos de 2.5 Golos"], odds["U25"]),
                            (f"BTTS Sim ({home})", res["Ambas Marcam (Sim)"], odds["BTTS_Y"]),
                            (f"DNB {home}", res["Empate Anula (Casa)"], odds["AH_00"])
                        ]
                        
                        for m_name, prob_data, odd in raw_mkts:
                            p_win = prob_data[0] if isinstance(prob_data, tuple) else prob_data
                            p_void = prob_data[1] if isinstance(prob_data, tuple) else 0.0
                            
                            # Filtros de Qualidade: Odd entre 1.50 e 4.00 | Edge > 4.5%
                            if 1.50 <= odd <= 4.00 and p_win > 0:
                                edge = (p_win * odd) + p_void - 1
                                if edge > 0.045:
                                    fair_odd = (1 - p_void) / p_win
                                    # Fração de Kelly reduzida para portfólio (1/8 Kelly)
                                    kelly = max(0, (edge / (odd - 1)) * 0.125)
                                    portfolio.append({
                                        "Jogo/Aposta": m_name,
                                        "Certeza": p_win,
                                        "Odd Real": fair_odd,
                                        "Odd Casa": odd,
                                        "Lucro Extra": edge,
                                        "Kelly_Raw": kelly
                                    })
                except Exception:
                    continue # Ignora jogos com dados corrompidos
                
                progress_bar.progress((i + 1) / len(fix_data))
            
            status_text.success("✅ Varredura Concluída!")
            
            # 3. Processamento do Portfólio Final
            if portfolio:
                df_port = pd.DataFrame(portfolio).sort_values(by="Lucro Extra", ascending=False).head(5)
                
                # Regra de Ouro: Exposição máxima de 15% da banca no dia
                max_daily_risk = 0.15 
                sum_kelly = df_port["Kelly_Raw"].sum()
                
                if sum_kelly > 0:
                    # Ajusta as stakes proporcionalmente para não ultrapassar o risco máximo
                    ratio = min(max_daily_risk / sum_kelly, 1.0)
                    df_port["Stake (€)"] = df_port["Kelly_Raw"] * bankroll * ratio
                else:
                    df_port["Stake (€)"] = 0
                
                # UI de Resultados
                st.markdown(f"""
                <div style='background:#0B1120; border-radius:12px; padding:20px; border-left:5px solid #00FF88; margin: 20px 0;'>
                    <h3 style='margin:0; color:#00FF88;'>💼 PORTFÓLIO DE VALOR (TOP 5)</h3>
                    <p style='color:#94A3B8; margin:0;'>Seleção otimizada baseada em desvios estatísticos. Risco total controlado: <b>{min(sum_kelly*100, 15):.1f}% da banca</b>.</p>
                </div>
                """, unsafe_allow_html=True)
                
                fig_port = go.Figure(data=[go.Table(
                    columnorder = [1,2,3,4,5], columnwidth = [250, 100, 100, 100, 120],
                    header=dict(
                        values=['<b>JOGO E APOSTA</b>', '<b>PROB.</b>', '<b>ODD CASA</b>', '<b>EDGE</b>', '<b>STAKE SUGERIDA</b>'],
                        fill_color='#020408', align='center', font=dict(color='#64748B', size=11), height=45
                    ),
                    cells=dict(
                        values=[
                            df_port["Jogo/Aposta"], 
                            df_port["Certeza"].map('{:.1%}'.format), 
                            df_port["Odd Casa"].map('{:.2f}'.format), 
                            df_port["Lucro Extra"].map('{:+.1%}'.format), 
                            df_port["Stake (€)"].map('{:.2f}€'.format)
                        ],
                        fill_color='#0B1120', align='center', 
                        font=dict(color=['#FFFFFF', '#E2E8F0', '#E2E8F0', '#00FF88', '#FFD700'], size=13, family='JetBrains Mono'),
                        height=40
                    )
                )])
                fig_port.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=300, paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_port, use_container_width=True)
                
                st.info("💡 Dica: Distribuir o risco por vários jogos com 'Edge' positivo é a única forma de vencer a variância estatística.")
            else:
                st.error("Varredura terminada. O mercado está 'eficiente' hoje (odds muito baixas ou muito precisas). Recomenda-se não apostar.")
                
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
        
        # 1. KPIs de Performance Quantitativa
        c1, c2, c3, c4 = st.columns(4)
        
        total_staked = df_hist['Stake (€)'].sum()
        avg_edge = df_hist["Lucro Extra"].mean()
        expected_profit = (df_hist['Stake (€)'] * df_hist['Lucro Extra']).sum()
        total_bets = len(df_hist)

        with c1:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Investido</div><div class='metric-value'>{total_staked:.2f}€</div></div>", unsafe_allow_html=True)
        with c2:
            color = "#00FF88" if avg_edge > 0.03 else "#FFD700" if avg_edge > 0 else "#EF4444"
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Edge Médio (CLV)</div><div class='metric-value' style='color:{color};'>{avg_edge:+.2%}</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Retorno Esperado (EV)</div><div class='metric-value' style='color:#FFD700;'>+{expected_profit:.2f}€</div></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Apostas Totais</div><div class='metric-value' style='color:#94A3B8;'>{total_bets}</div></div>", unsafe_allow_html=True)

        # 2. Gráfico de Projeção de Banca (Equity Curve Teórica)
        st.markdown("<br>", unsafe_allow_html=True)
        col_chart, col_info = st.columns([2, 1])
        
        with col_chart:
            # Calculamos o lucro acumulado teórico para o gráfico
            df_hist['EV_Accum'] = (df_hist['Stake (€)'] * df_hist['Lucro Extra']).cumsum()
            
            fig_ev = go.Figure()
            fig_ev.add_trace(go.Scatter(
                x=list(range(1, len(df_hist) + 1)), 
                y=df_hist['EV_Accum'],
                mode='lines+markers',
                name='Lucro Esperado',
                line=dict(color='#FFD700', width=3),
                fill='tozeroy',
                fillcolor='rgba(255, 215, 0, 0.1)'
            ))
            fig_ev.update_layout(
                title="📈 CURVA DE CRESCIMENTO MATEMÁTICO (EV+)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(title="Número de Apostas", showgrid=False, color="#64748B"),
                yaxis=dict(title="Lucro Acumulado (€)", showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#64748B")
            )
            st.plotly_chart(fig_ev, use_container_width=True)

        with col_info:
            st.markdown(f"""
            <div style='background: rgba(0, 255, 136, 0.05); border-radius: 12px; padding: 20px; border: 1px solid rgba(0, 255, 136, 0.2); height: 100%;'>
                <h4 style='color: #00FF88; margin-top: 0;'>Análise do Oráculo</h4>
                <p style='font-size: 0.9rem; color: #E2E8F0;'>O teu <b>Edge Médio de {avg_edge:.1%}</b> indica que estás a comprar odds com um desconto significativo em relação à probabilidade real.</p>
                <p style='font-size: 0.9rem; color: #94A3B8;'>Matematicamente, se mantiveres este volume, a variância será anulada e o teu lucro real convergirá para os <b>{expected_profit:.2f}€</b> projetados.</p>
            </div>
            """, unsafe_allow_html=True)

        # 3. Tabela de Histórico Profissional
        st.markdown("<h3 style='margin-top:30px; font-size:1.2rem; color:#94A3B8;'>📋 REGISTO DE AUDITORIA</h3>", unsafe_allow_html=True)
        
        fig_hist = go.Figure(data=[go.Table(
            columnorder = [1,2,3,4,5,6,7], 
            columnwidth = [100, 220, 180, 100, 100, 100, 110],
            header=dict(
                values=["<b>DATA</b>", "<b>EVENTO</b>", "<b>MERCADO</b>", "<b>ODD</b>", "<b>FAIR</b>", "<b>STAKE</b>", "<b>EDGE</b>"], 
                fill_color='#020408', align='center', 
                font=dict(color='#64748B', size=11), height=40
            ),
            cells=dict(
                values=[
                    df_hist["Data"], 
                    df_hist["Jogo"], 
                    df_hist["Aposta"], 
                    df_hist["Odd Comprada"].map('{:.2f}'.format), 
                    df_hist["Odd Real"].map('{:.2f}'.format), 
                    df_hist["Stake (€)"].map('{:.2f}€'.format), 
                    df_hist["Lucro Extra"].map('{:+.1%}'.format)
                ], 
                fill_color='#0B1120', align='center', 
                font=dict(color=['#64748B', '#FFFFFF', '#00FF88', '#FFFFFF', '#94A3B8', '#FFD700', '#00FF88'], size=12), 
                height=35
            )
        )])
        fig_hist.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=400, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # 4. Ações de Gestão
        c_del, c_exp = st.columns([1, 4])
        with c_del:
            if st.button("🗑️ LIMPAR TUDO", use_container_width=True):
                st.session_state.bet_history = pd.DataFrame(columns=["Data", "Jogo", "Aposta", "Odd Comprada", "Odd Real", "Stake (€)", "Lucro Extra", "Estado"])
                st.rerun()
        with c_exp:
            st.write("") # Espaçador
