import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO DE DESIGN LIMPO (SEM MANCHAS DE LUZ) ---
st.set_page_config(page_title="ORACLE V140 - ELITE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Fundo Escuro Puro e Sóbrio */
    .stApp { 
        background-color: #020617;
        background-image: none; /* REMOVIDA A LUZ QUE ESTAVA A TAPAR O TEXTO */
        color: #F8FAFC; 
        font-family: 'Plus Jakarta Sans', sans-serif; 
    }
    
    /* Sidebar de Alta Performance */
    [data-testid="stSidebar"] { 
        background-color: #050a1a !important; 
        border-right: 1px solid rgba(0, 255, 136, 0.1) !important;
    }

    /* Advisor Box - Glassmorphism Focado */
    .alpha-box { 
        background: rgba(255, 255, 255, 0.02);
        border-radius: 20px; 
        padding: 35px; 
        border: 1px solid rgba(0, 255, 136, 0.25);
        box-shadow: 0 0 40px rgba(0, 255, 136, 0.05); /* Brilho apenas aqui */
        margin-bottom: 30px;
    }

    .bet-name { 
        font-size: 3.8rem; font-weight: 800; line-height: 1; 
        color: #FFFFFF;
        margin: 10px 0;
    }

    /* Cartões de Insight */
    .insight-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px; padding: 18px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Botão Neon Sólido */
    div.stButton > button {
        background: #00FF88 !important;
        color: #000000 !important; font-weight: 800 !important;
        border-radius: 10px !important; border: none !important;
        height: 3.5em !important; text-transform: uppercase; letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR LÓGICO ---
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

def run_math(lh, la, rho, boost):
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
    ah0_h = ph / (ph + pa) if (ph + pa) > 0 else 0
    o25 = prob_mtx[np.add.outer(np.arange(max_g), np.arange(max_g)) > 2.5].sum()
    return ph, px, pa, ah0_h, o25, prob_mtx

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; letter-spacing:-1px;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    bankroll = st.number_input("BANCA TOTAL (€)", value=100.0)
    league_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94}
    ln = st.selectbox("LIGA", list(league_map.keys()))
    
    fix = requests.get(f"https://{api_host}/fixtures", headers=headers, params={"date": date.today().strftime('%Y-%m-%d'), "league": league_map[ln], "season": "2025"}).json().get('response', [])
    if fix:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
        m_display = st.selectbox("CONFRONTO", list(m_map.keys()))
        m_sel = next(f for f in fix if f['fixture']['id'] == m_map[m_display])
    else: m_sel = None

    c1, cx, c2 = st.columns(3)
    o1 = c1.number_input("Odd 1", value=2.00); ox = cx.number_input("Odd X", value=3.40); o2 = c2.number_input("Odd 2", value=3.50)
    o_ah0 = st.number_input("Odd AH 0.0 (H)", value=1.55)
    o_o25 = st.number_input("Odd Over 2.5", value=1.95)
    scan = st.button("🚀 EXECUTE ALPHA SCAN")

# --- 4. RESULTADOS (ULTRA CLEAN) ---
if not scan or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:200px; opacity:0.1;'><h1>ORACLE V140</h1><p>Ready for Data Injection</p></div>", unsafe_allow_html=True)
else:
    s_h = get_stats(m_sel['teams']['home']['id'], league_map[ln])
    s_a = get_stats(m_sel['teams']['away']['id'], league_map[ln])
    lh, la = (s_h['h_f']*s_a['a_a'])**0.5, (s_a['a_f']*s_h['h_a'])**0.5
    ph, px, pa, ah0, o25, mtx = run_math(lh, la, -0.11, 0.12)
    
    # Título Sem Reflexos
    st.markdown(f"<h1 style='font-size:4rem; margin-bottom:0; color:#FFFFFF;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#00FF88; font-weight:200;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#64748B; letter-spacing:2px; font-weight:600;'>{ln.upper()} // POISSON-DIXON ENGINE</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        mkts = [("WIN: "+m_sel['teams']['home']['name'], ph, o1), ("AH 0.0: "+m_sel['teams']['home']['name'], ah0, o_ah0), ("OVER 2.5", o25, o_o25)]
        best = sorted([(n,p,b,(p*b)-1) for n,p,b in mkts], key=lambda x: x[3], reverse=True)[0]
        edge = best[3]; kelly = max(0, (edge/(best[2]-1))*0.5)
        color = "#00FF88" if edge > 0.08 else "#FFD700" if edge > 0.02 else "#EF4444"
        
        st.markdown(f"""
            <div class="alpha-box" style="border-left: 8px solid {color};">
                <p style="color:#64748B; font-weight:800; font-size:0.7rem; text-transform:uppercase; letter-spacing:3px;">Recomendação Alpha</p>
                <div class="bet-name">{best[0]}</div>
                <div style="display:flex; gap:40px; margin-top:20px;">
                    <div><p style="color:#64748B; font-size:0.6rem; margin:0; font-weight:700;">TRUE EDGE</p><b style="color:{color}; font-size:1.8rem;">{edge:+.1%}</b></div>
                    <div><p style="color:#64748B; font-size:0.6rem; margin:0; font-weight:700;">SUGERIDO (€)</p><b style="font-size:1.8rem; color:white;">{bankroll*kelly:.2f}€</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        # Gráfico limpo
        xr = np.arange(7)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name="Casa", fill='tozeroy', line_color='#00FF88', line_width=4))
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name="Fora", fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#64748B", 
                          margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
        st.plotly_chart(fig, use_container_width=True)

    # Tabela Centralizada e Legenda
    df = pd.DataFrame([("Match Winner (1)", ph, o1), ("Draw (X)", px, ox), ("Match Winner (2)", pa, o2), ("AH 0.0 (DNB)", ah0, o_ah0), ("Over 2.5", o25, o_o25)], columns=["M", "P", "B"])
    df["F"] = 1/df["P"]; df["E"] = (df["P"] * df["B"]) - 1
    
    def get_c(e):
        if e > 0.10: return 'rgba(0, 255, 136, 0.1)'
        if e > 0.02: return 'rgba(245, 158, 11, 0.1)'
        if e < 0: return 'rgba(239, 68, 68, 0.1)'
        return 'rgba(255, 255, 255, 0.01)'

    fig_t = go.Figure(data=[go.Table(
        header=dict(values=['MERCADO', 'PROB. QUANT', 'ODD JUSTA', 'ODD CASA', 'TRUE EDGE'], 
                    fill_color='#020617', align='center', font=dict(color='#64748B', size=11), height=50),
        cells=dict(values=[df.M, df.P.map('{:.1%}'.format), df.F.map('{:.2f}'.format), df.B.map('{:.2f}'.format), df.E.map('{:+.1%}'.format)],
                   fill_color=[[get_c(e) for e in df["E"]]], align='center', font=dict(color='white', size=14), height=45)
    )])
    fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=320, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_t, use_container_width=True)
    
    # Glossário Horizontal Simples
    g1, g2, g3 = st.columns(3)
    with g1: st.markdown(f"""<div class="insight-card" style="border-top: 3px solid #00FF88;"><b style="color:#00FF88; font-size:0.7rem;">🟡 ALPHA GOLD</b><p style="font-size:0.8rem; color:#94A3B8; margin-top:5px;">Edge > 10%. Ineficiência crítica detetada.</p></div>""", unsafe_allow_html=True)
    with g2: st.markdown(f"""<div class="insight-card" style="border-top: 3px solid #F59E0B;"><b style="color:#F59E0B; font-size:0.7rem;">🟢 VALUE PRO</b><p style="font-size:0.8rem; color:#94A3B8; margin-top:5px;">Edge 2-10%. Território profissional estável.</p></div>""", unsafe_allow_html=True)
    with g3: st.markdown(f"""<div class="insight-card" style="border-top: 3px solid #EF4444;"><b style="color:#EF4444; font-size:0.7rem;">🔴 TRAP ZONE</b><p style="font-size:0.8rem; color:#94A3B8; margin-top:5px;">Odd negativa. Fuga obrigatória deste mercado.</p></div>""", unsafe_allow_html=True)
