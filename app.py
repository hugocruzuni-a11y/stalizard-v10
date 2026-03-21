import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO DE INTERFACE (ESTÉTICA BLOOMBERG) ---
st.set_page_config(
    page_title="ORACLE V140 - SYNDICATE TERMINAL", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# CSS Profissional: Foco em Tipografia e Espaçamento
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;600;700;800&display=swap');
    
    /* Fundo Escuro Profundo Neutro */
    .stApp { 
        background-color: #0A0D14; 
        color: #E2E8F0; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Sidebar Sobria */
    [data-testid="stSidebar"] { 
        background-color: #06080C !important; 
        border-right: 1px solid #1E293B !important; 
    }

    /* Advisor Box - Compacta e Directa */
    .advisor-seal { 
        background: #111827; 
        border-radius: 8px; 
        padding: 20px 25px; 
        border: 1px solid #1E293B;
        border-left: 5px solid #10B981; 
        margin-bottom: 20px;
    }

    /* Tipografia de Decisão */
    .recommendation-label { font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.1em; }
    .main-bet { font-size: 2.8rem; font-weight: 800; color: #FFFFFF; margin: 5px 0; line-height: 1; letter-spacing: -0.03em; }
    .alpha-edge { font-family: 'Roboto Mono', monospace; font-size: 1.25rem; font-weight: 700; color: #10B981; }

    /* Inputs e Labels de Dados */
    .stNumberInput label, .stSelectbox label, .stSlider label { 
        font-size: 0.7rem !important; 
        font-weight: 600 !important;
        color: #94A3B8 !important; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
    }
    .stNumberInput input, .stSelectbox div { background-color: #111827 !important; border: 1px solid #1E293B !important; color: #FFFFFF !important; }

    /* Botão de Comando */
    div.stButton > button {
        background: #10B981 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        border-radius: 6px !important;
        border: none !important;
        height: 3.2rem !important;
        transition: background 0.2s ease !important;
    }
    div.stButton > button:hover { background: #059669 !important; }

    /* Guia de Performance */
    .performance-card {
        background: rgba(255, 255, 255, 0.01);
        border-radius: 8px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE LÓGICA (Mantida) ---
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

# --- 3. SIDEBAR (PAINEL DE DADOS) ---
with st.sidebar:
    st.markdown("<h3 style='margin:0; font-family:Roboto Mono;'>ORACLE V140</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.7rem; color:#64748B; margin-bottom:20px;'>SYNDICATE TERMINAL</p>", unsafe_allow_html=True)
    bankroll = st.number_input("BANCA (€)", value=100.0)
    
    st.markdown("<hr style='border:1px solid #1E293B; margin:10px 0;'>", unsafe_allow_html=True)
    league_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94}
    ln = st.selectbox("LIGA", list(league_map.keys()))
    
    fix = requests.get(f"https://{api_host}/fixtures", headers=headers, 
                       params={"date": date.today().strftime('%Y-%m-%d'), "league": league_map[ln], "season": "2025"}).json().get('response', [])
    
    if fix:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
        m_display = st.selectbox("JOGO", list(m_map.keys()))
        m_sel = next(f for f in fix if f['fixture']['id'] == m_map[m_display])
    else: m_sel = None

    st.markdown("<hr style='border:1px solid #1E293B; margin:10px 0;'>", unsafe_allow_html=True)
    st.write("MERCADO (BET365)")
    c1, cx, c2 = st.columns(3)
    o1 = c1.number_input("Odd 1", value=2.00)
    ox = cx.number_input("Odd X", value=3.40)
    o2 = c2.number_input("Odd 2", value=3.50)
    o_ah0 = st.number_input("Odd AH 0.0 (H)", value=1.55)
    o_o25 = st.number_input("Odd Over 2.5", value=1.95)
    
    execute = st.button("🚀 EXECUTE ALPHA SCAN")

# --- 4. ÁREA DE RESULTADOS SYNDICATE ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:200px; opacity:0.1;'><h1>ORACLE V140</h1><p>Terminal Status: Ready // Waiting for Command</p></div>", unsafe_allow_html=True)
else:
    s = fetch_stats(m_sel['teams']['home']['id'], league_map[ln])
    lh_f, la_f = (s['h_f']*s['a_a'])**0.5, (s['a_f']*s['h_a'])**0.5
    ph, px, pa, ah0, o25, mtx = run_math(lh_f, la_f, -0.11, 0.12)
    
    # Header do Jogo
    st.markdown(f"""
        <div style="margin-bottom: 30px;">
            <p style="color:#64748B; font-weight:600; font-size:0.75rem; text-transform:uppercase;">Live Analysis // {ln.upper()}</p>
            <h1 style="font-size: 3.5rem; line-height: 1; margin:0;">{m_sel['teams']['home']['name']} <span style="font-weight:300; color:#475569;">vs</span> {m_sel['teams']['away']['name']}</h1>
        </div>
    """, unsafe_allow_html=True)

    col_res, col_info = st.columns([1, 1])

    with col_res:
        mkts = [("WIN: "+m_sel['teams']['home']['name'], ph, o1), ("AH 0.0: "+m_sel['teams']['home']['name'], ah0, o_ah0), ("OVER 2.5", o25, o_o25)]
        best = sorted([(n,p,b,(p*b)-1) for n,p,b in mkts], key=lambda x: x[3], reverse=True)[0]
        edge = best[3]; kelly = max(0, (edge/(best[2]-1))*0.5)
        color = "#10B981" if edge > 0.08 else "#F59E0B" if edge > 0.02 else "#EF4444"
        
        # Advisor Seal - Sobrio e Profissional
        st.markdown(f"""
            <div class="advisor-seal" style="border-left-color: {color};">
                <p class="recommendation-label">Alpha Recommendation</p>
                <p class="main-bet">{best[0]}</p>
                <div style="display:flex; gap:30px; margin-top:15px;">
                    <div><p style="color:#64748B; font-size:0.6rem; margin:0;">ALPHA EDGE</p><b class="alpha-edge" style="color:{color};">{edge:+.1%}</b></div>
                    <div><p style="color:#64748B; font-size:0.6rem; margin:0;">SUGERIDO (HALF-KELLY)</p><b style="font-family:Roboto Mono; font-size:1.25rem; color:#FFFFFF;">{bankroll*kelly:.2f}€</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_info:
        # Tabela de Mercados Estilo "Dark Trading"
        st.markdown("### 📊 Market Matrix")
        df = pd.DataFrame([("Match Winner (1)", ph, o1), ("Empate (X)", px, ox), ("Match Winner (2)", pa, o2), ("AH 0.0 (DNB)", ah0, o_ah0), ("Over 2.5 Golos", o25, o_o25)], columns=["M", "P", "B"])
        df["F"] = 1/df["P"]; df["E"] = (df["P"] * df["B"]) - 1
        
        def get_c(e):
            if e > 0.10: return 'rgba(16, 185, 129, 0.15)'
            if e > 0.02: return 'rgba(245, 158, 11, 0.15)'
            if e < 0: return 'rgba(239, 68, 68, 0.15)'
            return 'rgba(255, 255, 255, 0.02)'

        fig_t = go.Figure(data=[go.Table(
            header=dict(values=['MERCADO', 'PROB.', 'ODD JUSTA', 'ODD CASA', 'EDGE'], 
                        fill_color='#020617', align='center', font=dict(color='#64748B', size=11, family='Inter')),
            cells=dict(values=[df.M, df.P.map('{:.1%}'.format), df.F.map('{:.2f}'.format), df.B.map('{:.2f}'.format), df.E.map('{:+.1%}'.format)],
                       fill_color=[[get_c(e) for e in df["E"]]], align='center', font=dict(color='white', size=13, family='Roboto Mono'), height=30)
        )])
        fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=250, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_t, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Guia de Performance e Cores (Frio e Técnico)
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"""<div class="performance-card">
            <b style="color:#10B981; font-family:Roboto Mono;">[🟢 ELITE VALUE]</b><br>
            <p style="font-size:0.8rem; color:#94A3B8; margin:0;">Edge superior a 8%. Ineficiência crítica detetada. Risco desproporcional à recompensa.</p>
        </div>""", unsafe_allow_html=True)
    with g2:
        st.markdown(f"""<div class="performance-card">
            <b style="color:#F59E0B; font-family:Roboto Mono;">[🟡 PRO VALUE]</b><br>
            <p style="font-size:0.8rem; color:#94A3B8; margin:0;">Edge entre 2% e 8%. Valor profissional sólido para crescimento de banca sustentável.</p>
        </div>""", unsafe_allow_html=True)
    with g3:
        st.markdown(f"""<div class="performance-card">
            <b style="color:#EF4444; font-family:Roboto Mono;">[🔴 TRAP ZONE]</b><br>
            <p style="font-size:0.8rem; color:#94A3B8; margin:0;">Edge negativo. O modelo indica que a odd oferecida é uma armadilha matemática.</p>
        </div>""", unsafe_allow_html=True)
