import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO DE DESIGN ---
st.set_page_config(
    page_title="STARLINE V140 PRO - QUANT TERMINAL",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    .stApp { background: radial-gradient(circle at 50% -20%, #0f172a 0%, #000000 95%); color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    [data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.8) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(0, 255, 136, 0.1); }
    
    .advisor-seal { 
        background: rgba(255, 255, 255, 0.02); border-radius: 16px; padding: 25px; 
        border: 1px solid rgba(0, 255, 136, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 25px;
    }

    .risk-card { background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px; }

    .intel-card { 
        background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 18px; 
        border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 12px;
    }

    .legend-box { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 5px; vertical-align: middle; }
    
    h1, h2, h3 { letter-spacing: -0.05em; font-weight: 700; }
    .stNumberInput label, .stSelectbox label { font-size: 0.65rem !important; color: #94A3B8 !important; text-transform: uppercase; letter-spacing: 0.1em; }
    
    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 800; height: 3.5em; border-radius: 8px;
        border: none; text-transform: uppercase; letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE API E MATEMÁTICA ---
api_key = "8171043bf0a322286bb127947dbd4041" 
api_host = "v3.football.api-sports.io" 
headers = {"x-apisports-key": api_key}

@st.cache_data(ttl=3600)
def get_team_stats(team_id, league_id):
    try:
        url = f"https://{api_host}/teams/statistics"
        res = requests.get(url, headers=headers, params={"league": league_id, "season": "2025", "team": team_id}).json()
        goals = res.get('response', {}).get('goals', {})
        return {
            "h_for": float(goals.get('for', {}).get('average', {}).get('home', 1.5)),
            "h_aga": float(goals.get('against', {}).get('average', {}).get('home', 1.0)),
            "a_for": float(goals.get('for', {}).get('average', {}).get('away', 1.2)),
            "a_aga": float(goals.get('against', {}).get('average', {}).get('away', 1.3))
        }
    except: return {"h_for": 1.5, "h_aga": 1.0, "a_for": 1.2, "a_aga": 1.3}

def calculate_probs(lh, la, rho, boost):
    lh *= (1 + boost); la *= (1 - boost)
    max_g = 10
    prob_mtx = np.outer(poisson.pmf(np.arange(max_g), lh), poisson.pmf(np.arange(max_g), la))
    for x in range(2):
        for y in range(2):
            if x==0 and y==0: prob_mtx[x,y] *= (1 - lh*la*rho)
            elif x==0 and y==1: prob_mtx[x,y] *= (1 + lh*rho)
            elif x==1 and y==0: prob_mtx[x,y] *= (1 + la*rho)
            elif x==1 and y==1: prob_mtx[x,y] *= (1 - rho)
    prob_mtx /= prob_mtx.sum()
    ph, px, pa = np.tril(prob_mtx, -1).sum(), np.trace(prob_mtx), np.triu(prob_mtx, 1).sum()
    ah0_h = ph / (ph + pa) if (ph + pa) > 0 else 0
    o25 = prob_mtx[np.add.outer(np.arange(max_g), np.arange(max_g)) > 2.5].sum()
    return ph, px, pa, ah0_h, o25, prob_mtx

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88; font-size:24px;'>🏛️ ORACLE V140</h1>", unsafe_allow_html=True)
    bankroll = st.number_input("Banca Total (€)", value=100.0)
    
    league_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94}
    l_name = st.selectbox("Liga", list(league_map.keys()))
    
    fixtures = requests.get(f"https://{api_host}/fixtures", headers=headers, 
                           params={"date": date.today().strftime('%Y-%m-%d'), "league": league_map[l_name], "season": "2025"}).json().get('response', [])
    
    if fixtures:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fixtures}
        m_display = st.selectbox("Jogo", list(m_map.keys()))
        m_sel = next(f for f in fixtures if f['fixture']['id'] == m_map[m_display])
    else: m_sel = None

    c1, cx, c2 = st.columns(3)
    odd1 = c1.number_input("Odd 1", value=2.10); oddx = cx.number_input("Odd X", value=3.40); odd2 = c2.number_input("Odd 2", value=3.50)
    odd_ah0 = st.number_input("Odd AH 0.0 (H)", value=1.55)
    odd_o25 = st.number_input("Odd Over 2.5", value=1.90)
    scan = st.button("🚀 EXECUTAR ALPHA SCAN")

# --- 4. ÁREA DE RESULTADOS ---
if not scan or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.1;'><h1>ORACLE V140</h1><p>Sovereign Quant Terminal</p></div>", unsafe_allow_html=True)
else:
    s_h = get_team_stats(m_sel['teams']['home']['id'], league_map[l_name])
    s_a = get_team_stats(m_sel['teams']['away']['id'], league_map[l_name])
    lh, la = (s_h['h_for']*s_a['a_aga'])**0.5, (s_a['a_for']*s_h['h_aga'])**0.5
    ph, px, pa, ah0, o25, mtx = calculate_probs(lh, la, -0.11, 0.12)
    
    st.markdown(f"<h1 style='font-size:50px; margin-bottom:0;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#00FF88; font-weight:200;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h1>", unsafe_allow_html=True)

    col_main, col_side = st.columns([1.2, 0.8])
    mkts = [("WIN: "+m_sel['teams']['home']['name'], ph, odd1), ("AH 0.0: "+m_sel['teams']['home']['name'], ah0, odd_ah0), ("OVER 2.5", o25, odd_o25)]
    best = sorted([(n,p,b,(p*b)-1) for n,p,b in mkts], key=lambda x: x[3], reverse=True)[0]
    edge = best[3]; kelly = max(0, (edge/(best[2]-1))*0.5)
    color = "#00FF88" if edge > 0.05 else "#FFD700" if edge > 0.02 else "#EF4444"
    
    with col_main:
        st.markdown(f"""<div class="advisor-seal" style="border-color:{color};">
            <p style="color:#94A3B8; font-size:0.7rem; text-transform:uppercase; margin-bottom:5px;">Aposta Recomendada</p>
            <h1 style="margin:0; font-size:2.5rem;">{best[0]}</h1>
            <div style="display:flex; gap:20px; margin-top:15px;">
                <div><p style="font-size:0.6rem; color:#94A3B8; margin:0;">EDGE</p><b style="color:{color}; font-size:1.2rem;">{edge:+.1%}</b></div>
                <div><p style="font-size:0.6rem; color:#94A3B8; margin:0;">STAKE</p><b style="font-size:1.2rem;">{bankroll*kelly:.2f}€</b></div>
            </div></div>""", unsafe_allow_html=True)

    with col_side:
        conf = 100 * (1 - (np.sqrt(lh+la)/(lh+la)/2.8))
        st.markdown(f"""<div class="risk-card"><p style="color:#94A3B8; font-size:0.7rem; text-transform:uppercase; margin-bottom:5px;">Confiança do Sistema</p>
            <h2 style="margin:0; font-size:2.2rem;">{conf:.1f}%</h2></div>""", unsafe_allow_html=True)

    # --- TABELA DE MERCADOS ---
    st.markdown("### 📊 FULL MARKET HEATMAP")
    df = pd.DataFrame([("Vitória Casa", ph, odd1), ("Empate (X)", px, oddx), ("Vitória Fora", pa, odd2), ("AH 0.0 (Casa)", ah0, odd_ah0), ("Over 2.5 Golos", o25, odd_o25)], columns=["M", "P", "B"])
    df["F"] = 1/df["P"]; df["E"] = (df["P"] * df["B"]) - 1
    
    def get_c(e):
        if e > 0.10: return 'rgba(255, 215, 0, 0.25)'
        if e > 0.05: return 'rgba(0, 255, 136, 0.25)'
        if e > 0.02: return 'rgba(0, 255, 136, 0.08)'
        if e < 0: return 'rgba(239, 68, 68, 0.1)'
        return 'rgba(255, 255, 255, 0.02)'

    row_colors = [[get_c(e) for e in df["E"]]]
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=['MERCADO', 'PROB.', 'ODD JUSTA', 'ODD CASA', 'EDGE'], fill_color='#0A0A0A', align='center', font=dict(color='#94A3B8', size=11)),
        cells=dict(values=[df.M, df.P.map('{:.1%}'.format), df.F.map('{:.2f}'.format), df.B.map('{:.2f}'.format), df.E.map('{:+.1%}'.format)],
                   fill_color=row_colors, align='center', font=dict(color='white', size=13), height=35))])
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=250, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # --- GLOSSÁRIO ---
    st.markdown("""
        <div class="intel-card">
            <b style="font-size:0.9rem;">📖 LEGENDA DE VALOR</b><hr style="opacity:0.1; margin:10px 0;">
            <span class="legend-box" style="background:rgba(255,215,0,0.6);"></span> <b>Elite (>10%)</b>: Erro massivo da casa. Sniper mode. <br>
            <span class="legend-box" style="background:rgba(0,255,136,0.6);"></span> <b>Muito Boa (5-10%)</b>: Valor profissional sólido.<br>
            <span class="legend-box" style="background:rgba(0,255,136,0.2);"></span> <b>Boa (2-5%)</b>: Vantagem matemática aceitável.<br>
            <span class="legend-box" style="background:rgba(239,68,68,0.4);"></span> <b>Trap (<0%)</b>: Armadilha. A casa tem a vantagem total.
        </div>
    """, unsafe_allow_html=True)
