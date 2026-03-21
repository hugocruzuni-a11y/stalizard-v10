import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO DE INTERFACE ---
st.set_page_config(
    page_title="STARLINE V140 - SUPREME", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Design de Interface de Alta Performance
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono&display=swap');
    
    /* Fundo em Gradiente Profundo */
    .stApp { 
        background: radial-gradient(circle at 50% 0%, #1e293b 0%, #020617 100%); 
        color: #F8FAFC; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Sidebar com efeito Blur */
    [data-testid="stSidebar"] { 
        background-color: rgba(0, 0, 0, 0.3) !important; 
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Advisor Seal - O Cartão de Decisão */
    .advisor-seal { 
        background: rgba(255, 255, 255, 0.02);
        border-radius: 20px; 
        padding: 30px; 
        border: 1px solid rgba(0, 255, 136, 0.2);
        box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        margin-bottom: 25px;
    }

    /* Cartões de Estatística */
    .stats-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #00FF88;
        margin-bottom: 15px;
    }

    /* Títulos e Labels */
    h1, h2, h3 { letter-spacing: -0.04em !important; }
    .stNumberInput label, .stSelectbox label, .stSlider label { 
        font-size: 0.7rem !important; 
        font-weight: 600 !important;
        color: #64748B !important; 
        text-transform: uppercase; 
        letter-spacing: 0.1em; 
    }

    /* Botão Principal Estilo 'Glow' */
    div.stButton > button {
        background: #00FF88 !important;
        color: #000000 !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border-radius: 12px !important;
        border: none !important;
        height: 3.5rem !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(0, 255, 136, 0.2);
        transition: all 0.4s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 255, 136, 0.4);
    }

    /* Glossário e Explicações */
    .help-text { color: #94A3B8; font-size: 0.85rem; line-height: 1.6; }
    
    hr { border-top: 1px solid rgba(255, 255, 255, 0.05) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE LÓGICA (Mantida do V140 PRO) ---
api_key = "8171043bf0a322286bb127947dbd4041"
api_host = "v3.football.api-sports.io"
headers = {"x-apisports-key": api_key}

@st.cache_data(ttl=3600)
def fetch_stats(team_id, league_id):
    try:
        url = f"https://{api_host}/teams/statistics"
        r = requests.get(url, headers=headers, params={"league": league_id, "season": "2025", "team": team_id}).json()
        g = r.get('response', {}).get('goals', {})
        return {
            "h_f": float(g.get('for', {}).get('average', {}).get('home', 1.5)),
            "h_a": float(g.get('against', {}).get('average', {}).get('home', 1.0)),
            "a_f": float(g.get('for', {}).get('average', {}).get('away', 1.2)),
            "a_a": float(g.get('against', {}).get('average', {}).get('away', 1.3))
        }
    except: return {"h_f": 1.5, "h_a": 1.0, "a_f": 1.2, "a_a": 1.3}

def run_math(lh, la, rho, boost):
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

# --- 3. SIDEBAR COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    bankroll = st.number_input("BANCA TOTAL (€)", value=100.0)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    league_map = {"Premier League": 39, "La Liga": 140, "Serie A": 135, "Primeira Liga": 94}
    ln = st.selectbox("LIGA", list(league_map.keys()))
    
    fix = requests.get(f"https://{api_host}/fixtures", headers=headers, 
                       params={"date": date.today().strftime('%Y-%m-%d'), "league": league_map[ln], "season": "2025"}).json().get('response', [])
    
    if fix:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
        m_display = st.selectbox("JOGO DISPONÍVEL", list(m_map.keys()))
        m_id = m_map[m_display]
        m_sel = next(f for f in fix if f['fixture']['id'] == m_id)
    else: m_sel = None

    st.markdown("<hr>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    o1 = c1.number_input("ODD 1", value=2.00); ox = cx.number_input("ODD X", value=3.40); o2 = c2.number_input("ODD 2", value=3.50)
    o_ah0 = st.number_input("ODD AH 0.0 (CASA)", value=1.50)
    o_o25 = st.number_input("ODD OVER 2.5", value=1.90)

    st.markdown("<br>", unsafe_allow_html=True)
    execute = st.button("🚀 INICIAR ALPHA SCAN")

# --- 4. ÁREA DE RESULTADOS SUPREME ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:200px; opacity:0.1;'><h1>ORACLE V140</h1><p>SUPREME QUANT TERMINAL</p></div>", unsafe_allow_html=True)
else:
    # Cálculos
    stats = fetch_stats(m_sel['teams']['home']['id'], league_map[ln])
    lh_b, la_b = (stats['h_f']*stats['a_a'])**0.5, (stats['a_f']*stats['h_a'])**0.5
    ph, px, pa, ah0, o25, mtx = run_math(lh_b, la_b, -0.11, 0.12)
    
    # Header Visual
    st.markdown(f"<h1 style='font-size:60px; margin-bottom:0;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#00FF88; font-weight:300;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h1>", unsafe_allow_html=True)
    st.write(f"PROBABILIDADE DETERMINÍSTICA // DIXON-COLES // {ln}")

    # Layout Principal
    col_main, col_info = st.columns([1.3, 0.7])
    
    mkts = [("Vitória: " + m_sel['teams']['home']['name'], ph, o1), ("AH 0.0: " + m_sel['teams']['home']['name'], ah0, o_ah0), ("Over 2.5 Golos", o25, o_o25)]
    best = sorted([(n,p,b,(p*b)-1) for n,p,b in mkts], key=lambda x: x[3], reverse=True)[0]
    edge = best[3]; kelly = max(0, (edge/(best[2]-1))*0.5)

    with col_main:
        # Advisor Seal - Grande Destaque
        color = "#00FF88" if edge > 0.05 else "#FFD700" if edge > 0 else "#EF4444"
        st.markdown(f"""
            <div class="advisor-seal" style="border-top: 5px solid {color};">
                <p style="color:#64748B; font-size:0.7rem; font-weight:bold; text-transform:uppercase;">Alpha Recommendation</p>
                <h1 style="font-size:3.5rem; margin:10px 0;">{best[0]}</h1>
                <div style="display:flex; gap:30px;">
                    <div><p style="color:#64748B; font-size:0.6rem; margin:0;">EDGE</p><b style="color:{color}; font-size:1.5rem;">{edge:+.1%}</b></div>
                    <div><p style="color:#64748B; font-size:0.6rem; margin:0;">STAKE (HALF-KELLY)</p><b style="font-size:1.5rem;">{bankroll*kelly:.2f}€</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_info:
        st.markdown(f"""
            <div class="stats-card">
                <b>🧠 QUANT INSIGHT</b><br>
                <span style="font-size:0.85rem; color:#94A3B8;">O modelo detetou uma expectativa de <b>{(lh_b+la_b):.2f}</b> golos. Tendência: <b>{"OVER" if (lh_b+la_b) > 2.5 else "UNDER"}</b>.</span>
            </div>
            <div class="stats-card" style="border-color:#3B82F6;">
                <b>🎯 SCORE PROVÁVEL</b><br>
                <span style="font-size:0.85rem; color:#94A3B8;">O resultado exato com maior densidade matemática é o <b>{np.unravel_index(mtx.argmax(), mtx.shape)[0]}-{np.unravel_index(mtx.argmax(), mtx.shape)[1]}</b>.</span>
            </div>
        """, unsafe_allow_html=True)

    # Tabela de Calor
    df = pd.DataFrame([
        ("Match Winner (1)", ph, o1), ("Draw (X)", px, ox), ("Match Winner (2)", pa, o2),
        ("Asian Handicap 0.0", ah0, o_ah0), ("Over 2.5 Goals", o25, o_o25)
    ], columns=["Mercado", "Prob", "Odd"])
    df["Fair"] = 1/df["Prob"]
    df["Edge"] = (df["Prob"] * df["Odd"]) - 1
    
    def color_rows(e):
        if e > 0.10: return 'rgba(255, 215, 0, 0.2)'    # Ouro
        if e > 0.05: return 'rgba(0, 255, 136, 0.2)'    # Verde
        if e < 0: return 'rgba(239, 68, 68, 0.1)'       # Vermelho
        return 'rgba(255, 255, 255, 0.02)'

    fig = go.Figure(data=[go.Table(
        header=dict(values=['MERCADO', 'PROB.', 'ODD JUSTA', 'BOOKIE', 'TRUE EDGE'],
                    fill_color='#0f172a', align='center', font=dict(color='#94A3B8', size=12), height=40),
        cells=dict(values=[df.Mercado, df.Prob.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), df.Odd.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                   fill_color=[[color_rows(e) for e in df["Edge"]]], align='center', font=dict(color='white', size=14), height=35)
    )])
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=250, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # Explicação Final (Ajuda)
    with st.expander("❓ GUIA DE INTERPRETAÇÃO (ESCLARECIMENTO)"):
        st.markdown("""
        <div class="help-text">
        1. <b>True Edge:</b> A vantagem real que o modelo tem sobre a casa de apostas. Se for positivo, a odd da casa está errada (valor).<br>
        2. <b>Odd Justa:</b> O preço real que a aposta deveria ter. Se a odd da casa for MAIOR que esta, tens uma aposta matemática.<br>
        3. <b>Half-Kelly:</b> Uma gestão de banca equilibrada para evitar a falência (ruína) enquanto maximiza o lucro a longo prazo.
        </div>
        """, unsafe_allow_html=True)
