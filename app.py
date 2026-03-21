import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO DE INTERFACE ---
st.set_page_config(
    page_title="STARLINE V140 - ELITE", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono&display=swap');
    
    .stApp { background: radial-gradient(circle at 50% 0%, #0f172a 0%, #020617 100%); color: #F8FAFC; font-family: 'Inter', sans-serif; }
    
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.4) !important; backdrop-filter: blur(15px); border-right: 1px solid rgba(0, 255, 136, 0.1) !important; }

    .advisor-seal { 
        background: rgba(255, 255, 255, 0.02); border-radius: 20px; padding: 30px; 
        border: 1px solid rgba(0, 255, 136, 0.2); box-shadow: 0 20px 50px rgba(0,0,0,0.3); margin-bottom: 25px;
    }

    .intel-card { 
        background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 15px;
    }

    /* Estilização da Lenda de Cores */
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; margin-right: 10px; }
    .badge-elite { background: rgba(255, 215, 0, 0.2); color: #FFD700; border: 1px solid #FFD700; }
    .badge-verygood { background: rgba(0, 255, 136, 0.2); color: #00FF88; border: 1px solid #00FF88; }
    .badge-trap { background: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid #EF4444; }

    div.stButton > button {
        background: #00FF88 !important; color: #000000 !important; font-weight: 700 !important;
        border-radius: 12px !important; height: 3.5rem !important; width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR LÓGICO ---
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

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    bankroll = st.number_input("BANCA (€)", value=100.0)
    league_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94}
    ln = st.selectbox("LIGA", list(league_map.keys()))
    
    fix = requests.get(f"https://{api_host}/fixtures", headers=headers, 
                       params={"date": date.today().strftime('%Y-%m-%d'), "league": league_map[ln], "season": "2025"}).json().get('response', [])
    
    if fix:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
        m_display = st.selectbox("JOGO", list(m_map.keys()))
        m_sel = next(f for f in fix if f['fixture']['id'] == m_map[m_display])
    else: m_sel = None

    c1, cx, c2 = st.columns(3)
    o1 = c1.number_input("Odd 1", value=2.00); ox = cx.number_input("Odd X", value=3.40); o2 = c2.number_input("Odd 2", value=3.50)
    o_ah0 = st.number_input("Odd AH 0.0 (H)", value=1.55)
    o_o25 = st.number_input("Odd Over 2.5", value=1.95)
    execute = st.button("🚀 ALPHA SCAN")

# --- 4. RESULTADOS ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:200px; opacity:0.1;'><h1>ORACLE V140</h1><p>Waiting for Alpha Scan Command...</p></div>", unsafe_allow_html=True)
else:
    s = fetch_stats(m_sel['teams']['home']['id'], league_map[ln])
    lh_f, la_f = (s['h_f']*s['a_a'])**0.5, (s['a_f']*s['h_a'])**0.5
    ph, px, pa, ah0, o25, mtx = run_math(lh_f, la_f, -0.11, 0.12)
    
    st.markdown(f"<h1 style='font-size:55px; margin-bottom:0;'>{m_sel['teams']['home']['name'].upper()} vs {m_sel['teams']['away']['name'].upper()}</h1>", unsafe_allow_html=True)

    col_res, col_chart = st.columns([1, 1])

    with col_res:
        mkts = [("WIN: "+m_sel['teams']['home']['name'], ph, o1), ("AH 0.0: "+m_sel['teams']['home']['name'], ah0, o_ah0), ("OVER 2.5", o25, o_o25)]
        best = sorted([(n,p,b,(p*b)-1) for n,p,b in mkts], key=lambda x: x[3], reverse=True)[0]
        edge = best[3]; kelly = max(0, (edge/(best[2]-1))*0.5)
        color = "#FFD700" if edge > 0.10 else "#00FF88" if edge > 0.02 else "#EF4444"
        
        st.markdown(f"""<div class="advisor-seal" style="border-left: 10px solid {color};">
            <h4 style="margin:0; color:#64748B;">RECOMENDAÇÃO ALPHA</h4>
            <h1 style="font-size:3rem; margin:10px 0;">{best[0]}</h1>
            <h2 style="color:{color}; margin:0;">EDGE: {edge:+.1%} | STAKE: {bankroll*kelly:.2f}€</h2>
        </div>""", unsafe_allow_html=True)

    with col_chart:
        # Gráfico de Densidade de Poisson
        xr = np.arange(7)
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name=m_sel['teams']['home']['name'], fill='tozeroy', line_color='#00FF88'))
        fig_p.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name=m_sel['teams']['away']['name'], fill='tozeroy', line_color='#3B82F6'))
        fig_p.update_layout(title="DISTRIBUIÇÃO DE GOLOS (POISSON)", height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_p, use_container_width=True)

    # TABELA COM MAPA DE CALOR E LENDA
    st.markdown("### 📊 ANÁLISE DE MERCADO ASIÁTICO")
    st.markdown("""
        <div style="margin-bottom:15px;">
            <span class="badge badge-elite">Ouro (>10% Edge)</span>
            <span class="badge badge-verygood">Verde (>2% Edge)</span>
            <span class="badge badge-trap">Vermelho (<0% Edge)</span>
        </div>
    """, unsafe_allow_html=True)

    df = pd.DataFrame([("Match Winner (1)", ph, o1), ("Empate (X)", px, ox), ("Match Winner (2)", pa, o2), ("AH 0.0 (DNB)", ah0, o_ah0), ("Over 2.5 Golos", o25, o_o25)], columns=["M", "P", "B"])
    df["F"] = 1/df["P"]; df["E"] = (df["P"] * df["B"]) - 1
    
    def get_c(e):
        if e > 0.10: return 'rgba(255, 215, 0, 0.3)'
        if e > 0.02: return 'rgba(0, 255, 136, 0.2)'
        if e < 0: return 'rgba(239, 68, 68, 0.2)'
        return 'rgba(255, 255, 255, 0.05)'

    fig_t = go.Figure(data=[go.Table(
        header=dict(values=['MERCADO', 'PROB.', 'ODD JUSTA', 'ODD CASA', 'EDGE'], fill_color='#0f172a', align='center', font=dict(color='white', size=12)),
        cells=dict(values=[df.M, df.P.map('{:.1%}'.format), df.F.map('{:.2f}'.format), df.B.map('{:.2f}'.format), df.E.map('{:+.1%}'.format)],
                   fill_color=[[get_c(e) for e in df["E"]]], align='center', font=dict(color='white', size=13), height=35)
    )])
    fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=250, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_t, use_container_width=True)

    # GUIA DE INTERPRETAÇÃO PREMIUM
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🏛️ GUIA INSTITUCIONAL DE INTERPRETAÇÃO")
    c_g1, c_g2, c_g3 = st.columns(3)
    
    with c_g1:
        st.markdown(f"""<div class="intel-card">
            <b style="color:#FFD700;">🟡 MERCADO DE OURO (ELITE)</b><br>
            <p style="color:#94A3B8; font-size:0.85rem;">Quando o <b>Edge supera os 10%</b>, o modelo identifica um erro grave na precificação da casa. Historicamente, estas são as maiores oportunidades de lucro, onde a odd oferecida é desproporcional à força táctica das equipas.</p>
        </div>""", unsafe_allow_html=True)
        
    with c_g2:
        st.markdown(f"""<div class="intel-card">
            <b style="color:#00FF88;">🟢 MERCADO VERDE (VALOR)</b><br>
            <p style="color:#94A3B8; font-size:0.85rem;">Indica um <b>Edge entre 2% e 10%</b>. É o território dos apostadores profissionais. O lucro aqui vem do volume e da consistência, explorando pequenas ineficiências matemáticas nas odds asiáticas.</p>
        </div>""", unsafe_allow_html=True)
        
    with c_g3:
        st.markdown(f"""<div class="intel-card">
            <b style="color:#EF4444;">🔴 ZONA DE ARMADILHA (TRAP)</b><br>
            <p style="color:#94A3B8; font-size:0.85rem;">Edge negativo. Significa que a odd da casa é mais baixa do que o risco real. <b>Apostar aqui é aceitar prejuízo a longo prazo.</b> O modelo avisa-te para ignorares estes mercados, independentemente do nome das equipas.</p>
        </div>""", unsafe_allow_html=True)
