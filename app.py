import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO SUPREME ---
st.set_page_config(
    page_title="ORACLE V140 - AI QUANT TERMINAL", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { 
        background-color: #020617;
        color: #F8FAFC; 
        font-family: 'Plus Jakarta Sans', sans-serif; 
    }
    
    /* Sidebar Luxury */
    [data-testid="stSidebar"] { 
        background-color: #050a1a !important; 
        border-right: 1px solid rgba(0, 255, 136, 0.1) !important;
    }

    /* Cartão IA / Advisor Seal */
    .ai-box { 
        background: rgba(255, 255, 255, 0.02);
        border-radius: 20px; 
        padding: 30px; 
        border: 1px solid rgba(0, 255, 136, 0.25);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
        margin-bottom: 25px;
    }

    .ai-label { 
        font-size: 0.7rem; font-weight: 800; color: #00FF88; 
        text-transform: uppercase; letter-spacing: 0.2em; 
    }

    .bet-main-title { 
        font-size: 3rem; font-weight: 800; color: #FFFFFF; 
        line-height: 1.1; margin: 10px 0;
    }

    /* Cards de Insight Táctico */
    .insight-pill {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px; padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: 0.3s;
    }
    .insight-pill:hover { border-color: #00FF88; background: rgba(0, 255, 136, 0.02); }

    /* Botão Neon */
    div.stButton > button {
        background: #00FF88 !important; color: #000000 !important;
        font-weight: 800 !important; border-radius: 10px !important;
        height: 3.5em !important; width: 100%; border: none !important;
        text-transform: uppercase; letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE API E CÁLCULO ---
api_key = "8171043bf0a322286bb127947dbd4041" 
api_host = "v3.football.api-sports.io" 
headers = {"x-apisports-key": api_key}

@st.cache_data(ttl=3600)
def get_stats(team_id, league_id):
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

def run_quant_math(lh, la, rho, boost):
    lh *= (1 + boost); la *= (1 - boost)
    max_g = 10
    prob_mtx = np.outer(poisson.pmf(np.arange(max_g), lh), poisson.pmf(np.arange(max_g), la))
    for x in range(2):
        for y in range(2):
            if x==0 and y==0: prob_mtx[x,y] *= max(0, 1 - (lh*la*rho))
            elif x==0 and y==1: prob_mtx[x,y] *= max(0, 1 + (lh*rho))
            elif x==1 and y==0: prob_mtx[x,y] *= max(0, 1 + (la*rho))
            elif x==1 and y==1: prob_mtx[x,y] *= max(0, 1 - rho)
    prob_mtx /= prob_mtx.sum()
    ph, px, pa = np.tril(prob_mtx, -1).sum(), np.trace(prob_mtx), np.triu(prob_mtx, 1).sum()
    ah0 = ph / (ph + pa) if (ph + pa) > 0 else 0
    o25 = prob_mtx[np.add.outer(np.arange(max_g), np.arange(max_g)) > 2.5].sum()
    return ph, px, pa, ah0, o25, prob_mtx

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    bankroll = st.number_input("Banca Atual (€)", value=100.0)
    league_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94}
    ln = st.selectbox("Liga", list(league_map.keys()))
    
    fix = requests.get(f"https://{api_host}/fixtures", headers=headers, params={"date": date.today().strftime('%Y-%m-%d'), "league": league_map[ln], "season": "2025"}).json().get('response', [])
    if fix:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
        m_display = st.selectbox("Jogo", list(m_map.keys()))
        m_sel = next(f for f in fix if f['fixture']['id'] == m_map[m_display])
    else: m_sel = None

    c1, cx, c2 = st.columns(3)
    o1 = c1.number_input("Odd 1", value=2.00); ox = cx.number_input("Odd X", value=3.40); o2 = c2.number_input("Odd 2", value=3.50)
    o_ah0 = st.number_input("AH 0.0 Odd", value=1.55)
    o_o25 = st.number_input("O2.5 Odd", value=1.95)
    scan = st.button("🚀 EXECUTE AI SCAN")

# --- 4. ÁREA DE INTELIGÊNCIA ---
if not scan or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:200px; opacity:0.1;'><h1>ORACLE V140</h1><p>Waiting for Alpha Data...</p></div>", unsafe_allow_html=True)
else:
    s_h = get_stats(m_sel['teams']['home']['id'], league_map[ln])
    s_a = get_stats(m_sel['teams']['away']['id'], league_map[ln])
    lh, la = (s_h['h_f']*s_a['a_a'])**0.5, (s_a['a_f']*s_h['h_a'])**0.5
    ph, px, pa, ah0, o25, mtx = run_quant_math(lh, la, -0.11, 0.12)
    
    st.markdown(f"<h1 style='font-size:3.5rem; margin-bottom:0;'>{m_sel['teams']['home']['name'].upper()} vs {m_sel['teams']['away']['name'].upper()}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#64748B; letter-spacing:3px;'>AI CORE // DIXON-COLES ENGINE // {ln.upper()}</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 0.9])
    
    mkts = [("WIN: "+m_sel['teams']['home']['name'], ph, o1), ("AH 0.0: "+m_sel['teams']['home']['name'], ah0, o_ah0), ("OVER 2.5", o25, o_o25)]
    best = sorted([(n,p,b,(p*b)-1) for n,p,b in mkts], key=lambda x: x[3], reverse=True)[0]
    edge = best[3]; kelly = max(0, (edge/(best[2]-1))*0.5)
    color = "#00FF88" if edge > 0.08 else "#FFD700" if edge > 0.02 else "#EF4444"
    
    with col1:
        st.markdown(f"""
            <div class="ai-box" style="border-left: 8px solid {color};">
                <span class="ai-label">🤖 IA Analista (Oracle)</span>
                <div class="bet-main-title">{best[0]}</div>
                <div style="display:flex; gap:30px; margin-top:20px;">
                    <div><p style="color:#64748B; font-size:0.6rem; margin:0; font-weight:700;">EDGE DETETADO</p><b style="color:{color}; font-size:1.8rem;">{edge:+.1%}</b></div>
                    <div><p style="color:#64748B; font-size:0.6rem; margin:0; font-weight:700;">GESTÃO KELLY</p><b style="font-size:1.8rem; color:white;">{bankroll*kelly:.2f}€</b></div>
                </div>
                <hr style="opacity:0.1; margin:20px 0;">
                <p style="font-size:0.85rem; color:#94A3B8; line-height:1.6;">
                    <b>VERDICTO:</b> O modelo identificou que a odd da casa para <b>{best[0]}</b> está desajustada em relação ao volume de xG projetado. 
                    Com um λ total de <b>{lh+la:.2f}</b>, a probabilidade matemática supera a implícita do mercado em <b>{edge:.1%}</b>.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        # Gráfico Bivariado
        xr = np.arange(7)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name="Home", fill='tozeroy', line_color='#00FF88', line_width=4))
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name="Away", fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#64748B", 
                          margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
        st.plotly_chart(fig, use_container_width=True)

    # Grid de Insights IA
    st.markdown("### 🏛️ INSIGHTS DO ORACLE")
    g1, g2, g3 = st.columns(3)
    
    with g1:
        st.markdown(f"""<div class="insight-pill">
            <b style="color:#00FF88;">📊 Estabilidade do Modelo</b><br>
            <p style="font-size:0.8rem; color:#94A3B8;">O desvio de golos (λH/λA) indica um jogo de <b>{"Alta Volatilidade" if abs(lh-la) < 0.3 else "Controlo Doméstico"}</b>.</p>
        </div>""", unsafe_allow_html=True)
    with g2:
        idx = np.unravel_index(mtx.argmax(), mtx.shape)
        st.markdown(f"""<div class="insight-pill">
            <b style="color:#00FF88;">🎯 Score de Precisão</b><br>
            <p style="font-size:0.8rem; color:#94A3B8;">O placar mais provável pela rede de Poisson é <b>{idx[0]}-{idx[1]}</b> com densidade de <b>{mtx.max():.1%}</b>.</p>
        </div>""", unsafe_allow_html=True)
    with g3:
        st.markdown(f"""<div class="insight-pill">
            <b style="color:#EF4444;">⚠️ Alerta de Risco</b><br>
            <p style="font-size:0.8rem; color:#94A3B8;">{"Cuidado: Mercado de Empate (X) subvalorizado." if px > (1/ox) else "Risco de variância controlado para mercados principais."}</p>
        </div>""", unsafe_allow_html=True)

    # Tabela Heatmap
    df = pd.DataFrame([("Vitória (1)", ph, o1), ("Empate (X)", px, ox), ("Vitória (2)", pa, o2), ("AH 0.0 (Casa)", ah0, o_ah0), ("Over 2.5", o25, o_o25)], columns=["M", "P", "B"])
    df["F"] = 1/df["P"]; df["E"] = (df["P"] * df["B"]) - 1
    
    def get_c(e):
        if e > 0.10: return 'rgba(0, 255, 136, 0.1)'
        if e > 0.02: return 'rgba(245, 158, 11, 0.1)'
        if e < 0: return 'rgba(239, 68, 68, 0.1)'
        return 'rgba(255, 255, 255, 0.01)'

    fig_t = go.Figure(data=[go.Table(
        header=dict(values=['MERCADO', 'PROB. ORACLE', 'ODD JUSTA', 'ODD CASA', 'ALPHA EDGE'], 
                    fill_color='#020617', align='center', font=dict(color='#64748B', size=11), height=50),
        cells=dict(values=[df.M, df.P.map('{:.1%}'.format), df.F.map('{:.2f}'.format), df.B.map('{:.2f}'.format), df.E.map('{:+.1%}'.format)],
                   fill_color=[[get_c(e) for e in df["E"]]], align='center', font=dict(color='white', size=14), height=45)
    )])
    fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=320, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_t, use_container_width=True)
