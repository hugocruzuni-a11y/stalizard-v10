import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO DE ALTA FIDELIDADE ---
st.set_page_config(page_title="ORACLE V140 PRO - MASTER", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #070A11; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1E293B !important; }

    /* Cartão de Recomendação Alpha */
    .pro-card {
        background: #111827; border-radius: 12px; padding: 25px; border: 1px solid #1E293B;
        border-left: 6px solid #00FF88; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .bet-name { font-size: 2.5rem; font-weight: 800; color: #FFFFFF; margin: 0; line-height: 1; letter-spacing: -1px; }
    .edge-value { font-family: 'JetBrains Mono'; font-size: 1.5rem; color: #00FF88; font-weight: 700; }

    /* Cartão de Insight da IA */
    .ia-insight-card {
        background: rgba(0, 255, 136, 0.03); border-radius: 10px; padding: 15px;
        border: 1px dashed rgba(0, 255, 136, 0.3); margin-top: 15px; font-size: 0.9rem;
    }

    /* Tabelas e Inputs */
    .stNumberInput label, .stSelectbox label { font-size: 0.75rem !important; color: #94A3B8 !important; font-weight: 700; text-transform: uppercase; }
    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; 
        font-weight: 800 !important; height: 3.5rem !important; border-radius: 8px !important; border: none !important; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR QUANTITATIVO (DIXON-COLES MASTER) ---
api_key = "8171043bf0a322286bb127947dbd4041"
api_host = "v3.football.api-sports.io"
headers = {"x-apisports-key": api_key}

@st.cache_data(ttl=3600)
def get_pro_stats(team_id, league_id):
    try:
        r = requests.get(f"https://{api_host}/teams/statistics", headers=headers, params={"league": league_id, "season": "2025", "team": team_id}).json()
        g = r.get('response', {}).get('goals', {})
        return {"h_f": float(g.get('for', {}).get('average', {}).get('home', 1.5)), "h_a": float(g.get('against', {}).get('average', {}).get('home', 1.0)),
                "a_f": float(g.get('for', {}).get('average', {}).get('away', 1.2)), "a_a": float(g.get('against', {}).get('average', {}).get('away', 1.3))}
    except: return {"h_f": 1.5, "h_a": 1.0, "a_f": 1.2, "a_a": 1.3}

def run_master_math(lh, la, rho, boost):
    lh *= (1+boost); la *= (1-boost); max_g = 10
    prob_mtx = np.outer(poisson.pmf(np.arange(max_g), lh), poisson.pmf(np.arange(max_g), la))
    for x in range(2):
        for y in range(2):
            if x==0 and y==0: prob_mtx[x,y] *= (1-lh*la*rho)
            elif x==0 and y==1: prob_mtx[x,y] *= (1+lh*rho)
            elif x==1 and y==0: prob_mtx[x,y] *= (1+la*rho)
            elif x==1 and y==1: prob_mtx[x,y] *= (1-rho)
    prob_mtx /= prob_mtx.sum()
    
    # Probabilidades Base
    ph, px, pa = np.tril(prob_mtx, -1).sum(), np.trace(prob_mtx), np.triu(prob_mtx, 1).sum()
    
    # Handicaps Asiáticos (Lógica de Diagonais)
    h_win_by_1 = np.trace(prob_mtx, offset=-1)
    a_win_by_1 = np.trace(prob_mtx, offset=1)
    
    ah0_h = ph / (ph + pa) if (ph + pa) > 0 else 0 # DNB
    ah_minus_1_h = (ph - h_win_by_1) / (1 - h_win_by_1) if (1 - h_win_by_1) > 0 else 0
    ah_minus_1_a = (pa - a_win_by_1) / (1 - a_win_by_1) if (1 - a_win_by_1) > 0 else 0
    
    o25 = prob_mtx[np.add.outer(np.arange(max_g), np.arange(max_g)) > 2.5].sum()
    
    return {
        "1": ph, "X": px, "2": pa, "O25": o25, "U25": 1-o25,
        "AH 0.0 (H)": ah0_h, "AH -0.5 (H)": ph, "AH -1.0 (H)": ah_minus_1_h,
        "AH 0.0 (A)": 1-ah0_h, "AH -0.5 (A)": pa, "AH -1.0 (A)": ah_minus_1_a
    }, prob_mtx

# --- 3. SIDEBAR COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; margin:0;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.7rem; color:#64748B;'>INSTITUTIONAL SYNDICATE BUILD</p>", unsafe_allow_html=True)
    bankroll = st.number_input("BANCA (€)", value=100.0)
    
    l_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94, "Champions League": 2}
    ln = st.selectbox("LIGA", list(l_map.keys()))
    
    fix = requests.get(f"https://{api_host}/fixtures", headers=headers, params={"date": date.today().strftime('%Y-%m-%d'), "league": l_map[ln], "season": "2025"}).json().get('response', [])
    if fix:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
        m_display = st.selectbox("JOGO DISPONÍVEL", list(m_map.keys()))
        m_id = m_map[m_display]
        m_sel = next(f for f in fix if f['fixture']['id'] == m_id)
    else: m_sel = None

    st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
    st.write("ODDS DO MERCADO (BET365)")
    c1, cx, c2 = st.columns(3)
    o1 = c1.number_input("Odd 1", value=2.00); ox = cx.number_input("Odd X", value=3.40); o2 = c2.number_input("Odd 2", value=3.50)
    
    st.write("ASIAN LINES")
    o_ah0 = st.number_input("AH 0.0 (H)", value=1.55)
    o_ah1 = st.number_input("AH -1.0 (H)", value=3.20)
    o_o25 = st.number_input("Over 2.5", value=1.90)
    
    execute = st.button("🚀 INICIAR ALPHA SCAN")

# --- 4. RESULTADOS INTEGRADOS ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:200px; opacity:0.2;'><h1>ORACLE V140</h1><p>Aguardando Injeção de Dados...</p></div>", unsafe_allow_html=True)
else:
    s = get_pro_stats(m_sel['teams']['home']['id'], l_map[ln])
    lh, la = (s['h_f']*s['a_a'])**0.5, (s['a_f']*s['h_a'])**0.5
    res, mtx = run_master_math(lh, la, -0.11, 0.12)
    
    st.markdown(f"<h2 style='margin-bottom:0; font-size:3rem;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#475569; font-weight:300;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h2>", unsafe_allow_html=True)

    col_res, col_chart = st.columns([1.1, 0.9])

    with col_res:
        mkts = [("WIN: "+m_sel['teams']['home']['name'], res["1"], o1), ("AH 0.0: "+m_sel['teams']['home']['name'], res["AH 0.0 (H)"], o_ah0), ("AH -1.0: "+m_sel['teams']['home']['name'], res["AH -1.0 (H)"], o_ah1), ("OVER 2.5", res["O25"], o_o25)]
        best = sorted([(n,p,b,(p*b)-1) for n,p,b in mkts], key=lambda x: x[3], reverse=True)[0]
        edge = best[3]; kelly = max(0, (edge/(best[2]-1))*0.5)
        color = "#00FF88" if edge > 0.08 else "#FFD700" if edge > 0.02 else "#EF4444"
        
        st.markdown(f"""<div class="pro-card" style="border-left-color: {color};">
            <span style="color:#64748B; font-size:0.7rem; font-weight:800;">RECOMENDAÇÃO ALPHA MASTER</span>
            <p class="bet-name">{best[0]}</p>
            <p style="margin:10px 0;">EDGE: <span class="edge-value" style="color:{color};">{edge:+.1%}</span> | STAKE: <b>{bankroll*kelly:.2f}€</b></p>
            <div class="ia-insight-card">
                <b>🤖 ANALISTA IA:</b> O modelo detetou uma ineficiência de {edge:.1%} no mercado. 
                Expectativa de {lh+la:.2f} golos totais. O score {np.unravel_index(mtx.argmax(), mtx.shape)[0]}-{np.unravel_index(mtx.argmax(), mtx.shape)[1]} 
                tem a maior densidade bivariada para este confronto.
            </div>
        </div>""", unsafe_allow_html=True)

    with col_chart:
        xr = np.arange(7)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name="Casa", fill='tozeroy', line_color='#00FF88', line_width=3))
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name="Fora", fill='tozeroy', line_color='#3B82F6', line_width=3))
        fig.update_layout(height=240, margin=dict(l=0,r=0,t=20,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)

    # TABELA DE MERCADOS PROFISSIONAIS (1X2 + ASIANS)
    st.markdown("### 📊 Mercados de Alta Liquidez")
    df = pd.DataFrame([
        ("Match Winner (1)", res["1"], o1), ("Draw (X)", res["X"], ox), ("Match Winner (2)", res["2"], o2),
        ("AH 0.0 (DNB)", res["AH 0.0 (H)"], o_ah0), ("AH -1.0 (Casa)", res["AH -1.0 (H)"], o_ah1),
        ("Over 2.5 Golos", res["O25"], o_o25)
    ], columns=["Mercado", "P", "B"])
    df["Fair"] = 1/df["P"]; df["Edge"] = (df["P"] * df["B"]) - 1
    
    def get_heatmap(e):
        if e > 0.10: return 'rgba(255, 215, 0, 0.2)' # Ouro
        if e > 0.03: return 'rgba(0, 255, 136, 0.15)' # Verde
        if e < 0: return 'rgba(239, 68, 68, 0.1)'    # Vermelho
        return 'rgba(255, 255, 255, 0.02)'

    fig_t = go.Figure(data=[go.Table(
        header=dict(values=['MERCADO', 'PROB.', 'ODD JUSTA', 'ODD CASA', 'ALPHA EDGE'], fill_color='#020617', align='left', font=dict(color='#94A3B8', size=11), height=40),
        cells=dict(values=[df.Mercado, df.P.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), df.B.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                   fill_color=[[get_heatmap(e) for e in df["Edge"]]], align='left', font=dict(color='white', size=13), height=35)
    )])
    fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=300, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_t, use_container_width=True)

    # GUIA DE CORES INSTITUCIONAL
    st.markdown(f"""
        <div style="font-size:0.8rem; color:#64748B; padding:15px; border:1px solid #1E293B; border-radius:8px;">
            <b style="color:#FFFFFF;">LEGENDAS DE VALOR:</b> &nbsp;&nbsp;
            <span style="color:#FFD700;">● OURO (Elite > 10%)</span> &nbsp;&nbsp;
            <span style="color:#00FF88;">● VERDE (Pro > 3%)</span> &nbsp;&nbsp;
            <span style="color:#EF4444;">● VERMELHO (Trap < 0%)</span>
        </div>
    """, unsafe_allow_html=True)
