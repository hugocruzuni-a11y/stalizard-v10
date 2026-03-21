import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO DE DESIGN VIBRANTE ---
st.set_page_config(page_title="ORACLE V140 - NEON", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp { 
        background-color: #05070A;
        background-image: radial-gradient(circle at 20% 35%, rgba(0, 255, 136, 0.05) 0%, transparent 40%),
                          radial-gradient(circle at 80% 10%, rgba(0, 112, 255, 0.05) 0%, transparent 40%);
        color: #E2E8F0;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Sidebar Elétrica */
    [data-testid="stSidebar"] { 
        background-color: rgba(5, 7, 10, 0.95) !important; 
        border-right: 2px solid #00FF88 !important;
        box-shadow: 5px 0 15px rgba(0, 255, 136, 0.1);
    }

    /* Cartão Alpha Neon */
    .neon-card {
        background: rgba(17, 24, 39, 0.8);
        border-radius: 15px;
        padding: 30px;
        border: 1px solid rgba(0, 255, 136, 0.3);
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.15), inset 0 0 10px rgba(0, 255, 136, 0.05);
        margin-bottom: 25px;
    }

    .bet-highlight {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00FF88, #6EE7B7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
    }

    /* Status Badges */
    .status-pill {
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        border: 1px solid currentColor;
    }

    /* Botão Neon */
    div.stButton > button {
        background: linear-gradient(45deg, #00FF88, #0070FF) !important;
        color: #FFFFFF !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        height: 4rem !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.4) !important;
        transition: 0.3s all ease;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.6) !important;
    }

    /* Tabela de Trading */
    .stTable { background: transparent !important; }
    
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE LÓGICA (Dixon-Coles Master) ---
api_key = "8171043bf0a322286bb127947dbd4041"
api_host = "v3.football.api-sports.io"
headers = {"x-apisports-key": api_key}

@st.cache_data(ttl=3600)
def get_stats(team_id, league_id):
    try:
        r = requests.get(f"https://{api_host}/teams/statistics", headers=headers, params={"league": league_id, "season": "2025", "team": team_id}).json()
        g = r.get('response', {}).get('goals', {})
        return {"h_f": float(g.get('for', {}).get('average', {}).get('home', 1.5)), "h_a": float(g.get('against', {}).get('average', {}).get('home', 1.0)),
                "a_f": float(g.get('for', {}).get('average', {}).get('away', 1.2)), "a_a": float(g.get('against', {}).get('average', {}).get('away', 1.3))}
    except: return {"h_f": 1.5, "h_a": 1.0, "a_f": 1.2, "a_a": 1.3}

def run_math(lh, la, rho, boost):
    lh *= (1+boost); la *= (1-boost); max_g = 10
    prob_mtx = np.outer(poisson.pmf(np.arange(max_g), lh), poisson.pmf(np.arange(max_g), la))
    for x in range(2):
        for y in range(2):
            if x==0 and y==0: prob_mtx[x,y] *= (1-lh*la*rho)
            elif x==0 and y==1: prob_mtx[x,y] *= (1+lh*rho)
            elif x==1 and y==0: prob_mtx[x,y] *= (1+la*rho)
            elif x==1 and y==1: prob_mtx[x,y] *= (1-rho)
    prob_mtx /= prob_mtx.sum()
    ph, px, pa = np.tril(prob_mtx, -1).sum(), np.trace(prob_mtx), np.triu(prob_mtx, 1).sum()
    ah0_h = ph / (ph + pa) if (ph + pa) > 0 else 0
    o25 = prob_mtx[np.add.outer(np.arange(max_g), np.arange(max_g)) > 2.5].sum()
    return ph, px, pa, ah0_h, o25, prob_mtx

# --- 3. SIDEBAR COCKPIT ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88; font-size:28px;'>ORACLE V140</h1>", unsafe_allow_html=True)
    bankroll = st.number_input("CAPITAL TOTAL (€)", value=100.0)
    
    l_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94}
    ln = st.selectbox("MERCADO LIGA", list(l_map.keys()))
    
    fix = requests.get(f"https://{api_host}/fixtures", headers=headers, params={"date": date.today().strftime('%Y-%m-%d'), "league": l_map[ln], "season": "2025"}).json().get('response', [])
    if fix:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
        m_display = st.selectbox("CONFRONTO", list(m_map.keys()))
        m_sel = next(f for f in fix if f['fixture']['id'] == m_map[m_display])
    else: m_sel = None

    st.markdown("<hr style='border:1px solid #00FF88; opacity:0.3'>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    o1 = c1.number_input("Odd 1", value=2.00); ox = cx.number_input("Odd X", value=3.40); o2 = c2.number_input("Odd 2", value=3.50)
    o_ah0 = st.number_input("AH 0.0 Odd", value=1.55)
    o_o25 = st.number_input("Over 2.5 Odd", value=1.95)
    
    execute = st.button("EXECUTE ALPHA SCAN")

# --- 4. RESULTADOS VIVOS (NEON EDITION) ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:200px; opacity:0.1;'><h1>ORACLE V140</h1><p>SYSTEM READY // STANDBY MODE</p></div>", unsafe_allow_html=True)
else:
    s = get_stats(m_sel['teams']['home']['id'], l_map[ln])
    lh, la = (s['h_f']*s['a_a'])**0.5, (s['a_f']*s['h_a'])**0.5
    ph, px, pa, ah0, o25, mtx = run_math(lh, la, -0.11, 0.12)
    
    # Header Elétrico
    st.markdown(f"""
        <div style="padding: 20px 0;">
            <span class="status-pill" style="color:#00FF88;">Analysing Live Data</span>
            <h1 style="font-size:4.5rem; margin:10px 0; background: linear-gradient(90deg, #FFFFFF, #475569); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {m_sel['teams']['home']['name'].upper()} <span style="color:#00FF88;">VS</span> {m_sel['teams']['away']['name'].upper()}
            </h1>
        </div>
    """, unsafe_allow_html=True)

    col_res, col_chart = st.columns([1.2, 0.8])

    with col_res:
        mkts = [("WIN: "+m_sel['teams']['home']['name'], ph, o1), ("AH 0.0: "+m_sel['teams']['home']['name'], ah0, o_ah0), ("OVER 2.5", o25, o_o25)]
        best = sorted([(n,p,b,(p*b)-1) for n,p,b in mkts], key=lambda x: x[3], reverse=True)[0]
        edge = best[3]; kelly = max(0, (edge/(best[2]-1))*0.5)
        color = "#00FF88" if edge > 0.08 else "#F59E0B" if edge > 0.02 else "#EF4444"
        
        st.markdown(f"""
            <div class="neon-card" style="border-top: 4px solid {color}; shadow: 0 0 20px {color}44;">
                <p style="color:#94A3B8; font-weight:700; letter-spacing:3px; font-size:0.8rem;">RECOMENDAÇÃO ALPHA</p>
                <p class="bet-highlight" style="background: linear-gradient(90deg, {color}, #FFFFFF); -webkit-background-clip: text;">{best[0]}</p>
                <div style="display:flex; gap:40px; margin-top:20px;">
                    <div><p style="color:#64748B; margin:0;">EDGE</p><b style="color:{color}; font-size:2rem;">{edge:+.1%}</b></div>
                    <div><p style="color:#64748B; margin:0;">STAKE SUGERIDA</p><b style="font-size:2rem; color:#FFFFFF;">{bankroll*kelly:.2f}€</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_chart:
        # Gráfico de Poisson Elétrico
        xr = np.arange(7)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name="Casa", fill='tozeroy', line_color='#00FF88', line_width=4))
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name="Fora", fill='tozeroy', line_color='#0070FF', line_width=4))
        fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(l=0,r=0,t=0,b=0), showlegend=False,
                          xaxis=dict(showgrid=False), yaxis=dict(gridcolor='rgba(255,255,255,0.05)'))
        st.plotly_chart(fig, use_container_width=True)

    # Tabela Futurista
    st.markdown("<h3 style='margin-top:30px;'>TRADING MATRIX</h3>", unsafe_allow_html=True)
    df = pd.DataFrame([("Match Winner (1)", ph, o1), ("Draw (X)", px, ox), ("Match Winner (2)", pa, o2), ("AH 0.0 (DNB)", ah0, o_ah0), ("Over 2.5", o25, o_o25)], columns=["M", "P", "B"])
    df["F"] = 1/df["P"]; df["E"] = (df["P"] * df["B"]) - 1
    
    def get_c(e):
        if e > 0.10: return 'rgba(0, 255, 136, 0.25)'
        if e > 0.02: return 'rgba(245, 158, 11, 0.2)'
        if e < 0: return 'rgba(239, 68, 68, 0.2)'
        return 'rgba(255, 255, 255, 0.05)'

    fig_t = go.Figure(data=[go.Table(
        header=dict(values=['MERCADO', 'PROB.', 'ODD JUSTA', 'ODD CASA', 'EDGE'], fill_color='#111827', align='center', font=dict(color='#00FF88', size=13, family='Orbitron'), height=45),
        cells=dict(values=[df.M, df.P.map('{:.1%}'.format), df.F.map('{:.2f}'.format), df.B.map('{:.2f}'.format), df.E.map('{:+.1%}'.format)],
                   fill_color=[[get_c(e) for e in df["E"]]], align='center', font=dict(color='white', size=14), height=40)
    )])
    fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=300, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_t, use_container_width=True)

    # Guia com Ícones e Cores Vivas
    st.markdown("<hr style='border:1px solid #00FF88; opacity:0.2'>", unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown("<div style='border-left:4px solid #00FF88; padding-left:15px;'><b style='color:#00FF88;'>⚡ ELITE ALPHA</b><br><p style='color:#94A3B8; font-size:0.85rem;'>Edge superior a 10%. Ineficiência crítica detetada nos algoritmos da casa.</p></div>", unsafe_allow_html=True)
    with g2:
        st.markdown("<div style='border-left:4px solid #F59E0B; padding-left:15px;'><b style='color:#F59E0B;'>🔥 PRO VALUE</b><br><p style='color:#94A3B8; font-size:0.85rem;'>Edge entre 2% e 10%. Valor profissional sólido para crescimento de banca.</p></div>", unsafe_allow_html=True)
    with g3:
        st.markdown("<div style='border-left:4px solid #EF4444; padding-left:15px;'><b style='color:#EF4444;'>🚫 MARKET TRAP</b><br><p style='color:#94A3B8; font-size:0.85rem;'>Risco matemático descompensado. A odd oferecida é uma armadilha.</p></div>", unsafe_allow_html=True)
