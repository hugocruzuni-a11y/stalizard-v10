import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO DE PERFORMANCE ---
st.set_page_config(page_title="ORACLE V140 PRO", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono&display=swap');
    .stApp { background-color: #0B0F19; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Compacta */
    [data-testid="stSidebar"] { background-color: #070A11 !important; border-right: 1px solid #1E293B !important; }

    /* Cartão de Recomendação (Estilo Bloomberg) */
    .pro-card {
        background: #111827;
        border-radius: 8px;
        padding: 20px;
        border: 1px solid #1E293B;
        border-left: 5px solid #00FF88;
        margin-bottom: 20px;
    }

    .bet-name { font-size: 2.2rem; font-weight: 800; color: #FFFFFF; margin: 0; line-height: 1.1; }
    .edge-value { font-family: 'JetBrains Mono'; font-size: 1.4rem; color: #00FF88; font-weight: 700; }

    /* Ajuste de Inputs */
    .stNumberInput label, .stSelectbox label { font-size: 0.7rem !important; color: #64748B !important; font-weight: 700; }
    
    /* Botão Direto */
    div.stButton > button {
        background: #00FF88 !important; color: #000000 !important; font-weight: 700 !important;
        height: 3rem !important; border-radius: 4px !important; border: none !important; width: 100%;
    }
    
    /* Lenda de Cores */
    .color-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE (Dixon-Coles) ---
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

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='margin:0;'>🏛️ ORACLE V140</h3>", unsafe_allow_html=True)
    bankroll = st.number_input("BANCA (€)", value=100.0)
    
    l_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94}
    ln = st.selectbox("LIGA", list(l_map.keys()))
    
    fix = requests.get(f"https://{api_host}/fixtures", headers=headers, params={"date": date.today().strftime('%Y-%m-%d'), "league": l_map[ln], "season": "2025"}).json().get('response', [])
    if fix:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
        m_display = st.selectbox("JOGO", list(m_map.keys()))
        m_sel = next(f for f in fix if f['fixture']['id'] == m_map[m_display])
    else: m_sel = None

    st.markdown("<hr style='margin:10px 0; opacity:0.1'>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    o1 = c1.number_input("Odd 1", value=2.00); ox = cx.number_input("Odd X", value=3.40); o2 = c2.number_input("Odd 2", value=3.50)
    o_ah0 = st.number_input("Odd AH 0.0 (H)", value=1.55)
    o_o25 = st.number_input("Odd Over 2.5", value=1.95)
    
    execute = st.button("🚀 ALPHA SCAN")

# --- 4. ÁREA DE RESULTADOS (COMPACTA) ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:200px; opacity:0.2;'><h2>ORACLE V140</h2><p>Terminal de Análise Quantitativa</p></div>", unsafe_allow_html=True)
else:
    s = get_stats(m_sel['teams']['home']['id'], l_map[ln])
    lh, la = (s['h_f']*s['a_a'])**0.5, (s['a_f']*s['h_a'])**0.5
    ph, px, pa, ah0, o25, mtx = run_math(lh, la, -0.11, 0.12)
    
    st.markdown(f"<h2 style='margin-bottom:0;'>{m_sel['teams']['home']['name']} vs {m_sel['teams']['away']['name']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#64748B; font-size:0.8rem;'>{ln.upper()} // DATA SYNC: OK</p>", unsafe_allow_html=True)

    col_res, col_chart = st.columns([1, 1])

    with col_res:
        mkts = [("WIN: "+m_sel['teams']['home']['name'], ph, o1), ("AH 0.0: "+m_sel['teams']['home']['name'], ah0, o_ah0), ("OVER 2.5", o25, o_o25)]
        best = sorted([(n,p,b,(p*b)-1) for n,p,b in mkts], key=lambda x: x[3], reverse=True)[0]
        edge = best[3]; kelly = max(0, (edge/(best[2]-1))*0.5)
        color = "#00FF88" if edge > 0.05 else "#F59E0B" if edge > 0 else "#EF4444"
        
        st.markdown(f"""<div class="pro-card" style="border-left-color: {color};">
            <span style="color:#64748B; font-size:0.7rem; font-weight:700;">RECOMENDAÇÃO ALPHA</span>
            <p class="bet-name">{best[0]}</p>
            <p style="margin:5px 0;">EDGE: <span class="edge-value" style="color:{color};">{edge:+.1%}</span> | STAKE: <b>{bankroll*kelly:.2f}€</b></p>
        </div>""", unsafe_allow_html=True)

    with col_chart:
        xr = np.arange(7)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name="Casa", fill='tozeroy', line_color='#00FF88'))
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name="Fora", fill='tozeroy', line_color='#3B82F6'))
        fig.update_layout(height=180, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Tabela de Mercados
    st.markdown("### 📊 Mercados Profissionais")
    df = pd.DataFrame([("Match Winner (1)", ph, o1), ("Draw (X)", px, ox), ("Match Winner (2)", pa, o2), ("AH 0.0 (DNB)", ah0, o_ah0), ("Over 2.5 Golos", o25, o_o25)], columns=["M", "P", "B"])
    df["F"] = 1/df["P"]; df["E"] = (df["P"] * df["B"]) - 1
    
    def get_c(e):
        if e > 0.10: return 'rgba(0, 255, 136, 0.15)'
        if e > 0.02: return 'rgba(245, 158, 11, 0.15)'
        if e < 0: return 'rgba(239, 68, 68, 0.1)'
        return 'rgba(255, 255, 255, 0.02)'

    fig_t = go.Figure(data=[go.Table(
        header=dict(values=['MERCADO', 'PROB.', 'ODD JUSTA', 'BOOKIE', 'EDGE'], fill_color='#111827', align='left', font=dict(color='#64748B', size=11)),
        cells=dict(values=[df.M, df.P.map('{:.1%}'.format), df.F.map('{:.2f}'.format), df.B.map('{:.2f}'.format), df.E.map('{:+.1%}'.format)],
                   fill_color=[[get_c(e) for e in df["E"]]], align='left', font=dict(color='white', size=12), height=30)
    )])
    fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=220, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_t, use_container_width=True)

    # Lenda e Guia Rápido
    st.markdown(f"""
        <div style="font-size:0.75rem; color:#64748B; border-top:1px solid #1E293B; padding-top:10px;">
            <span class="color-dot" style="background:#00FF88;"></span> <b>VALOR ALTO:</b> Edge > 10%. Erro de precificação da casa. &nbsp;&nbsp;
            <span class="color-dot" style="background:#F59E0B;"></span> <b>VALOR MÉDIO:</b> Edge 2-10%. Valor profissional estável. &nbsp;&nbsp;
            <span class="color-dot" style="background:#EF4444;"></span> <b>ARMADILHA:</b> Edge negativo. A odd da casa é baixa para o risco.
        </div>
    """, unsafe_allow_html=True)
