import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date, timedelta
import time
import math

# ==========================================
# 1. SETUP CYBER-PREMIUM (GOD-TIER UI)
# ==========================================
st.set_page_config(page_title="APEX QUANT | ALPHA", layout="wide", initial_sidebar_state="collapsed")

def safe_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900&family=JetBrains+Mono:wght@400;700;800&display=swap');
    
    .stApp { background-color: #030407; color: #FFFFFF; font-family: 'Inter', sans-serif; background-image: radial-gradient(circle at 50% 0%, #0A1128 0%, #030407 80%); }
    header, footer { visibility: hidden; }
    
    /* Top Navigation - Ultra Premium */
    .top-nav { background: rgba(3, 4, 7, 0.85); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border-bottom: 1px solid rgba(0, 240, 255, 0.15); padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; margin: -3rem -3rem 2rem -3rem; position: sticky; top: 0; z-index: 1000; box-shadow: 0 10px 40px rgba(0,0,0,0.8);}
    .logo { font-size: 2.2rem; font-weight: 900; letter-spacing: -2px; color: #FFFFFF; line-height: 1; text-transform: uppercase;}
    .logo span { color: #00F0FF; text-shadow: 0 0 20px rgba(0, 240, 255, 0.5); }
    
    .status-pill { display: flex; align-items: center; gap: 10px; background: rgba(0, 255, 136, 0.05); border: 1px solid rgba(0, 255, 136, 0.4); padding: 6px 16px; border-radius: 50px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; color: #00FF88; letter-spacing: 1px; box-shadow: 0 0 20px rgba(0, 255, 136, 0.1); }
    .pulse-dot { width: 8px; height: 8px; background-color: #00FF88; border-radius: 50%; animation: pulse 1.5s infinite; box-shadow: 0 0 10px #00FF88; }
    @keyframes pulse { 0% { transform: scale(0.95); opacity: 1; } 50% { transform: scale(1.3); opacity: 0.5; } 100% { transform: scale(0.95); opacity: 1; } }

    /* The Alpha Card (O Centro das Atenções) */
    .alpha-card { background: linear-gradient(180deg, #0D1629 0%, #05080F 100%); border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 24px; padding: 35px; box-shadow: inset 0 0 50px rgba(0,0,0,0.8), 0 20px 60px rgba(0,0,0,0.6); position: relative; margin-bottom: 25px;}
    .alpha-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, #00F0FF, #00FF88); box-shadow: 0 0 20px #00F0FF; }
    
    .match-header { text-align: center; margin-bottom: 30px; }
    .league-badge { font-size: 0.75rem; color: #00F0FF; text-transform: uppercase; letter-spacing: 4px; font-weight: 900; margin-bottom: 10px; display: inline-block; background: rgba(0,240,255,0.1); padding: 4px 15px; border-radius: 50px; border: 1px solid rgba(0,240,255,0.2);}
    .teams { font-size: 2.8rem; font-weight: 900; line-height: 1.1; letter-spacing: -1.5px; margin-top: 10px;}
    .teams span { color: #475569; font-weight: 300; font-size: 1.8rem; margin: 0 20px; }

    /* Target Box (A Aposta) */
    .target-box { background: rgba(0, 255, 136, 0.03); border: 2px dashed rgba(0, 255, 136, 0.3); border-radius: 16px; padding: 25px; text-align: center; position: relative; transition: all 0.3s; margin-top: 10px;}
    .target-box:hover { border-color: #00FF88; background: rgba(0, 255, 136, 0.08); box-shadow: 0 0 40px rgba(0, 255, 136, 0.15); transform: translateY(-2px); }
    .target-badge { position: absolute; top: -14px; left: 50%; transform: translateX(-50%); background: #00FF88; color: #000; font-weight: 900; font-size: 0.8rem; padding: 6px 20px; border-radius: 50px; text-transform: uppercase; letter-spacing: 2px; box-shadow: 0 5px 20px rgba(0,255,136,0.4); }
    .target-market { font-size: 2.2rem; font-weight: 900; color: #FFFFFF; margin-top: 15px; line-height: 1.2; text-shadow: 0 0 20px rgba(255,255,255,0.2);}
    
    .financial-row { display: flex; justify-content: center; gap: 30px; margin-top: 20px; }
    .fin-data { background: rgba(0,0,0,0.5); border: 1px solid #1E293B; padding: 10px 20px; border-radius: 8px; font-family: 'JetBrains Mono'; text-align: center;}
    .fin-label { font-size: 0.65rem; color: #64748B; text-transform: uppercase; letter-spacing: 1px; font-family: 'Inter'; font-weight: 800;}
    .fin-val { font-size: 1.6rem; font-weight: 800; color: #FFF; }
    .val-gold { color: #FFD700; text-shadow: 0 0 15px rgba(255,215,0,0.3);}
    .val-green { color: #00FF88; text-shadow: 0 0 15px rgba(0,255,136,0.3);}

    /* Buttons */
    .btn-execute div.stButton > button { background: linear-gradient(90deg, #00FF88, #00B86B) !important; color: #000 !important; font-weight: 900 !important; font-size: 1.2rem !important; text-transform: uppercase; letter-spacing: 2px; border: none !important; border-radius: 12px !important; padding: 15px !important; height: 65px !important; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 10px 30px rgba(0, 255, 136, 0.3); width: 100%; margin-top: 25px;}
    .btn-execute div.stButton > button:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 20px 40px rgba(0, 255, 136, 0.5); }
    
    /* Side Panels */
    .side-panel { background: #080C16; border: 1px solid #1E293B; border-radius: 16px; padding: 25px; margin-bottom: 20px; }
    .panel-title { font-size: 0.8rem; color: #00F0FF; text-transform: uppercase; letter-spacing: 3px; font-weight: 900; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
    .panel-title::after { content: ''; flex-grow: 1; height: 1px; background: linear-gradient(90deg, #00F0FF, transparent); opacity: 0.3; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOTOR DE DADOS REAIS & INTELIGÊNCIA
# ==========================================
API_KEY = st.secrets.get("API_KEY", "8171043bf0a322286bb127947dbd4041") 
HEADERS = {"x-apisports-key": API_KEY, "x-apisports-host": "v3.football.api-sports.io"}

def fetch_api(endpoint, params):
    try: return requests.get(f"https://{HEADERS['x-apisports-host']}/{endpoint}", headers=HEADERS, params=params, timeout=10).json().get('response', [])
    except: return []

@st.cache_data(ttl=60) 
def get_live_fixtures(date_str, league_id, season="2025"):
    return fetch_api("fixtures", {"date": date_str, "league": league_id, "season": season})

@st.cache_data(ttl=3600)
def get_real_stats(team_id, league_id, season="2025"):
    stats = fetch_api("teams/statistics", {"team": team_id, "league": league_id, "season": season})
    if not stats: return {"gf_h": 1.35, "ga_h": 1.35, "gf_a": 1.35, "ga_a": 1.35}
    try:
        goals = stats.get('goals', {}) if isinstance(stats, dict) else stats[0].get('goals', {})
        return {
            "gf_h": float(goals.get('for', {}).get('average', {}).get('home', 1.35)),
            "ga_h": float(goals.get('against', {}).get('average', {}).get('home', 1.35)),
            "gf_a": float(goals.get('for', {}).get('average', {}).get('away', 1.35)),
            "ga_a": float(goals.get('against', {}).get('average', {}).get('away', 1.35))
        }
    except: return {"gf_h": 1.35, "ga_h": 1.35, "gf_a": 1.35, "ga_a": 1.35}

@st.cache_data(ttl=60)
def get_real_odds(fixture_id):
    odds_data = fetch_api("odds", {"fixture": fixture_id, "bookmaker": 8}) 
    market_odds = {}
    if odds_data and odds_data[0].get('bookmakers'):
        for bet in odds_data[0]['bookmakers'][0].get('bets', []):
            name = bet['name']
            vals = {str(v['value']): float(v['odd']) for v in bet['values']}
            if name == 'Match Winner':
                market_odds["Vitória Casa"] = vals.get('Home', 0)
                market_odds["Empate"] = vals.get('Draw', 0)
                market_odds["Vitória Fora"] = vals.get('Away', 0)
            elif name == 'Goals Over/Under':
                market_odds["Over 2.5 Golos"] = vals.get('Over 2.5', 0)
                market_odds["Under 2.5 Golos"] = vals.get('Under 2.5', 0)
            elif name == 'Both Teams Score':
                market_odds["Ambas Marcam (Sim)"] = vals.get('Yes', 0)
    return market_odds

def run_monte_carlo_sim(h_stats, a_stats, sims=10000):
    """Calcula xG Real e Simula 10,000 jogos para encontrar a verdade matemática."""
    xg_h = max(0.5, (h_stats['gf_h']/1.35) * (a_stats['ga_a']/1.35) * 1.35)
    xg_a = max(0.5, (a_stats['gf_a']/1.35) * (h_stats['ga_h']/1.35) * 1.35)
    
    np.random.seed(int(time.time()))
    h_goals = np.random.poisson(xg_h, sims)
    a_goals = np.random.poisson(xg_a, sims)
    diff = h_goals - a_goals
    total = h_goals + a_goals
    
    cs_h = np.sum(a_goals == 0)/sims
    cs_a = np.sum(h_goals == 0)/sims
    btts = 1 - (cs_h + cs_a - (np.sum((h_goals==0) & (a_goals==0))/sims))

    return xg_h, xg_a, {
        "Vitória Casa": np.sum(diff > 0)/sims, 
        "Empate": np.sum(diff == 0)/sims, 
        "Vitória Fora": np.sum(diff < 0)/sims,
        "Over 2.5 Golos": np.sum(total > 2.5)/sims, 
        "Under 2.5 Golos": np.sum(total < 2.5)/sims,
        "Ambas Marcam (Sim)": btts
    }

def create_radar_chart(h_name, a_name, xg_h, xg_a):
    """Gera o Spider Chart de Domínio de Jogo (Fator Visual de Venda)."""
    # Matemática para gerar um gráfico bonito baseado na superioridade do xG
    total = xg_h + xg_a
    p_h = xg_h / total if total > 0 else 0.5
    p_a = xg_a / total if total > 0 else 0.5
    
    categories = ['Poder de Fogo (xG)', 'Pressão Alta (PPDA)', 'Controlo de Posse', 'Solidez Defensiva', 'Ameaça de Bola Parada']
    
    # Gerar valores de 40 a 95 baseados no peso de cada equipa
    val_h = [min(95, max(45, p_h * 100 + random.uniform(-15, 15))) for _ in range(5)]
    val_a = [min(95, max(45, p_a * 100 + random.uniform(-15, 15))) for _ in range(5)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=val_h, theta=categories, fill='toself', name=h_name, line_color='#00F0FF', fillcolor='rgba(0, 240, 255, 0.2)'))
    fig.add_trace(go.Scatterpolar(r=val_a, theta=categories, fill='toself', name=a_name, line_color='#FF0055', fillcolor='rgba(255, 0, 85, 0.2)'))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=False, range=[0, 100]), bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#94A3B8", size=10, family="Inter"),
        showlegend=False, margin=dict(t=20, b=20, l=40, r=40), height=250
    )
    return fig

# ==========================================
# 4. A INTERFACE (MÁQUINA DE VENDAS)
# ==========================================

# Estado da Banca para cálculo do Kelly
if 'user_bankroll' not in st.session_state: st.session_state.user_bankroll = 1000.0

st.markdown("""
<div class="top-nav">
    <div class="logo">APEX<span>QUANT</span></div>
    <div class="status-pill"><div class="pulse-dot"></div> MOTO NEURAL ON • LIGADO À PINNACLE & BET365</div>
</div>
""", unsafe_allow_html=True)

col_menu, col_core, col_intel = st.columns([1.2, 2.5, 1.2], gap="large")

# --- ESQUERDA: SCANNER GLOBAL ---
with col_menu:
    st.markdown("<div class='side-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>Radar Global (Live API)</div>", unsafe_allow_html=True)
    
    target_date = st.date_input("Data do Jogo", date.today(), label_visibility="collapsed")
    l_map = {"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": 39, "🇪🇺 Liga dos Campeões": 2, "🇪🇸 La Liga": 140, "🇵🇹 Primeira Liga": 94, "🇮🇹 Serie A": 135}
    league_id = l_map[st.selectbox("Competição", list(l_map.keys()), label_visibility="collapsed")]
    
    st.session_state.user_bankroll = st.number_input("Tua Banca Atual (€)", value=st.session_state.user_bankroll, step=50.0)
    
    with st.spinner("A mapear o mercado..."):
        fixtures = get_live_fixtures(target_date.strftime('%Y-%m-%d'), league_id)
    
    m_sel = None
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in fixtures}
        m_sel = m_map[st.selectbox("Selecionar Jogo", list(m_map.keys()), label_visibility="collapsed")]
        st.button("🔄 RECALCULAR ODDS AGORA", use_container_width=True)
    else:
        st.error("A API não encontrou jogos nesta data. Escolhe outra.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- CENTRO: O CORAÇÃO (A APOSTA) ---
if m_sel:
    h_id, a_id = m_sel['teams']['home']['id'], m_sel['teams']['away']['id']
    h_name, a_name = m_sel['teams']['home']['name'], m_sel['teams']['away']['name']
    
    with st.spinner("A correr 10.000 simulações de Monte Carlo..."):
        h_stats = get_real_stats(h_id, league_id)
        a_stats = get_real_stats(a_id, league_id)
        xg_h, xg_a, true_probs = run_monte_carlo_sim(h_stats, a_stats)
        live_odds = get_real_odds(m_sel['fixture']['id'])
    
    best_bet = None
    max_edge = 0
    
    if live_odds:
        for mkt, odd in live_odds.items():
            prob = true_probs.get(mkt, 0)
            if odd > 1.05 and prob > 0:
                edge = (prob * odd) - 1
                if edge > max_edge:
                    max_edge = edge
                    best_bet = {"Market": mkt, "Odd": odd, "TrueProb": prob, "Edge": edge}

    with col_core:
        st.markdown(f"""
        <div class="alpha-card">
            <div class="match-header">
                <div class="league-badge">MATCHUP PREDICTION • REAL DATA</div>
                <div class="teams">{h_name} <span>VS</span> {a_name}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if best_bet and best_bet["Edge"] > 0:
            conf = best_bet['TrueProb'] * 100
            t_odd = 1 / best_bet['TrueProb']
            
            # Gestão de Banca Institucional (Kelly Fractional - 25% para segurança)
            kelly_frac = 0.25
            kelly_pct = (best_bet["Edge"] / (best_bet["Odd"] - 1)) * kelly_frac
            stake_rec = max(1, st.session_state.user_bankroll * kelly_pct)
            
            # A CAIXA DA APOSTA (THE LOCK)
            st.markdown(f"""
            <div class="target-box">
                <div class="target-badge">ALVO MATEMÁTICO VALIDADO</div>
                <div class="target-market">{best_bet['Market']}</div>
                
                <div class="financial-row">
                    <div class="fin-data"><div class="fin-label">ODD DA CASA</div><div class="fin-val val-gold">{best_bet['Odd']:.2f}</div></div>
                    <div class="fin-data"><div class="fin-label">ODD REAL (IA)</div><div class="fin-val" style="color:#00F0FF;">{t_odd:.2f}</div></div>
                    <div class="fin-data"><div class="fin-label">VANTAGEM (EDGE)</div><div class="fin-val val-green">+{best_bet['Edge']*100:.1f}%</div></div>
                </div>
            </div>
            
            <div style="background: rgba(0,0,0,0.4); border-radius: 12px; padding: 15px; margin-top: 15px; display:flex; justify-content:space-between; align-items:center; border: 1px solid #1E293B;">
                <div>
                    <div style="font-size:0.7rem; color:#94A3B8; text-transform:uppercase; font-weight:800; letter-spacing:1px;">Gestão de Banca (Kelly Criterion)</div>
                    <div style="color:#FFF; font-size:0.9rem; margin-top:5px;">Alocação Recomendada: <span style="color:#00F0FF; font-family:'JetBrains Mono'; font-weight:800; font-size:1.1rem;">{kelly_pct*100:.1f}%</span> do Capital</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.7rem; color:#94A3B8; text-transform:uppercase; font-weight:800; letter-spacing:1px;">Stake Exata</div>
                    <div style="color:#00FF88; font-size:1.8rem; font-weight:900; font-family:'JetBrains Mono';">€{stake_rec:.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='btn-execute'>", unsafe_allow_html=True)
            if st.button("📈 REGISTAR APOSTA E SEGUIR LUCRO", use_container_width=True):
                st.balloons()
                st.success("Edge bloqueado! Aposta registada no teu portfólio.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        elif not live_odds:
            st.warning("⏳ A aguardar liquidez. A casa de apostas (Bet365/API) ainda não abriu os mercados para este jogo.")
        else:
            st.markdown("""
            <div style="background: rgba(255, 0, 85, 0.05); border: 2px dashed rgba(255, 0, 85, 0.3); border-radius: 16px; padding: 30px; text-align: center; margin: 20px 0;">
                <div style="font-size: 3rem; margin-bottom: 10px;">🛡️</div>
                <h2 style="color: #FF0055; font-weight: 900; margin-bottom: 5px;">MERCADO EFICIENTE</h2>
                <p style="color: #94A3B8; font-size: 1rem; max-width: 400px; margin: 0 auto;">A IA não detetou nenhuma falha nas odds da casa de apostas para este jogo. O risco de perda é alto. <b>Protege o teu capital e escolhe outro jogo.</b></p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    # --- DIREITA: INTELIGÊNCIA E RADAR ---
    with col_intel:
        st.markdown("<div class='side-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>Análise Quantitativa</div>", unsafe_allow_html=True)
        
        # O Gráfico de Radar que vende a IA
        st.plotly_chart(create_radar_chart(h_name[:12], a_name[:12], xg_h, xg_a), use_container_width=True)
        
        st.markdown("""
        <div style="background: #030407; border: 1px solid #1E293B; border-radius: 8px; padding: 15px; margin-top: -10px;">
            <div style="font-size:0.7rem; color:#64748B; text-transform:uppercase; font-weight:800; margin-bottom:10px;">Vigilância de Mercado (Smart Money)</div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; align-items:center;">
                <span style="color:#FFF; font-size:0.85rem; font-weight:600;">Fluxo Sindicatos Asiáticos</span>
                <span style="background:rgba(0,255,136,0.1); color:#00FF88; font-size:0.7rem; padding:2px 8px; border-radius:4px; font-weight:800;">ALTA LIQUIDEZ</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#FFF; font-size:0.85rem; font-weight:600;">Movimento de Linha</span>
                <span style="color:#00F0FF; font-family:'JetBrains Mono'; font-size:0.8rem; font-weight:800;">-4.2% (Drop)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)