import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO SUPREME ---
st.set_page_config(
    page_title="ORACLE V140 - ULTIMATE LUXURY", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# CSS de Nível de Software de Investimento (Fintech Style)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { 
        background-color: #020617;
        background-image: radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.15) 0, transparent 50%), 
                          radial-gradient(at 50% 0%, rgba(16, 185, 129, 0.05) 0, transparent 50%);
        color: #F8FAFC; 
        font-family: 'Plus Jakarta Sans', sans-serif; 
    }
    
    /* Sidebar Luxury */
    [data-testid="stSidebar"] { 
        background-color: rgba(2, 6, 23, 0.7) !important; 
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Advisor Box - Redesenhada para Impacto Máximo */
    .luxury-card { 
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
        border-radius: 24px; 
        padding: 40px; 
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 40px 100px -20px rgba(0,0,0,0.5);
    }

    .recommendation-title {
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.3em;
        color: #10B981;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .main-bet {
        font-size: 4.5rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.04em;
        margin: 0;
        background: linear-gradient(to right, #FFFFFF, #94A3B8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Estatísticas Rápidas */
    .stat-badge {
        background: rgba(255, 255, 255, 0.05);
        padding: 10px 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stat-label { font-size: 0.65rem; color: #64748B; text-transform: uppercase; font-weight: 700; margin-bottom: 2px; }
    .stat-value { font-size: 1.2rem; font-weight: 800; font-family: 'JetBrains Mono'; }

    /* Estilo da Tabela de Luxo */
    .stTable { border: none !important; }
    
    /* Botão Scanner */
    div.stButton > button {
        background: #10B981 !important;
        color: #000000 !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        border-radius: 14px !important;
        border: none !important;
        height: 3.8rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div.stButton > button:hover { transform: translateY(-3px); box-shadow: 0 20px 40px -10px rgba(16, 185, 129, 0.4); }

    /* Badges de Lenda */
    .legend-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 0.6rem;
        font-weight: 800;
        margin-right: 10px;
        border: 1px solid rgba(255,255,255,0.1);
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

# --- 3. SIDEBAR (CONTROLO) ---
with st.sidebar:
    st.markdown("<h2 style='letter-spacing:-1px;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    bankroll = st.number_input("BANCA DISPONÍVEL (€)", value=100.0)
    
    league_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94}
    ln = st.selectbox("LIGA SELECCIONADA", list(league_map.keys()))
    
    fix = requests.get(f"https://{api_host}/fixtures", headers=headers, 
                       params={"date": date.today().strftime('%Y-%m-%d'), "league": league_map[ln], "season": "2025"}).json().get('response', [])
    
    if fix:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
        m_display = st.selectbox("CONFRONTO", list(m_map.keys()))
        m_sel = next(f for f in fix if f['fixture']['id'] == m_map[m_display])
    else: m_sel = None

    st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    o1 = c1.number_input("Odd 1", value=2.00)
    ox = cx.number_input("Odd X", value=3.40)
    o2 = c2.number_input("Odd 2", value=3.50)
    o_ah0 = st.number_input("Odd AH 0.0 (H)", value=1.55)
    o_o25 = st.number_input("Odd Over 2.5", value=1.95)
    
    execute = st.button("🚀 ALPHA SCAN")

# --- 4. ÁREA DE RESULTADOS ULTIMATE ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:250px; opacity:0.1;'><h1>ORACLE V140</h1><p>ULTIMATE LUXURY TERMINAL</p></div>", unsafe_allow_html=True)
else:
    s = fetch_stats(m_sel['teams']['home']['id'], league_map[ln])
    lh_f, la_f = (s['h_f']*s['a_a'])**0.5, (s['a_f']*s['h_a'])**0.5
    ph, px, pa, ah0, o25, mtx = run_math(lh_f, la_f, -0.11, 0.12)
    
    # Grid de Layout Principal
    col_left, col_right = st.columns([1.4, 0.6])

    with col_left:
        # Título do Confronto Estilo Noticiário de Finanças
        st.markdown(f"""
            <div style="margin-bottom: 40px;">
                <p style="color:#64748B; font-weight:800; font-size:0.7rem; letter-spacing:0.4em; text-transform:uppercase;">Live Analysis // {ln}</p>
                <h1 style="font-size: 4rem; line-height: 1; margin:0;">{m_sel['teams']['home']['name']} <span style="font-weight:300; color:#475569;">vs</span> {m_sel['teams']['away']['name']}</h1>
            </div>
        """, unsafe_allow_html=True)

        mkts = [("WIN: "+m_sel['teams']['home']['name'], ph, o1), ("AH 0.0: "+m_sel['teams']['home']['name'], ah0, o_ah0), ("OVER 2.5", o25, o_o25)]
        best = sorted([(n,p,b,(p*b)-1) for n,p,b in mkts], key=lambda x: x[3], reverse=True)[0]
        edge = best[3]; kelly = max(0, (edge/(best[2]-1))*0.5)
        color = "#10B981" if edge > 0.10 else "#F59E0B" if edge > 0.02 else "#EF4444"

        # Advisor Luxury Card
        st.markdown(f"""
            <div class="luxury-card">
                <div class="recommendation-title">Recomendação Alpha</div>
                <div class="main-bet">{best[0]}</div>
                <div style="display:flex; gap:40px; margin-top:30px;">
                    <div class="stat-badge">
                        <div class="stat-label">True Edge</div>
                        <div class="stat-value" style="color:{color};">{edge:+.1%}</div>
                    </div>
                    <div class="stat-badge">
                        <div class="stat-label">Sugerido (Half-Kelly)</div>
                        <div class="stat-value">{bankroll*kelly:.2f}€</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_right:
        # Gráfico de Poisson Redesenhado
        st.markdown("<br><br>", unsafe_allow_html=True)
        xr = np.arange(7)
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name=m_sel['teams']['home']['name'], fill='tozeroy', line_color='#10B981', line_width=4))
        fig_p.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name=m_sel['teams']['away']['name'], fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig_p.update_layout(
            height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            font_color="#64748B", margin=dict(l=0,r=0,t=0,b=0), 
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig_p, use_container_width=True)

    # Espaçamento
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Tabela de Mercados Estilo "Dark Trading"
    st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <h3 style="margin:0; letter-spacing:-1px;">Análise de Mercado Asiático</h3>
            <div>
                <span class="legend-tag" style="color:#10B981; background:rgba(16,185,129,0.1);">Elite (>10%)</span>
                <span class="legend-tag" style="color:#F59E0B; background:rgba(245,158,11,0.1);">Valor (>2%)</span>
                <span class="legend-tag" style="color:#EF4444; background:rgba(239,68,68,0.1);">Trap (<0%)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    df = pd.DataFrame([("Match Winner (1)", ph, o1), ("Empate (X)", px, ox), ("Match Winner (2)", pa, o2), ("AH 0.0 (DNB)", ah0, o_ah0), ("Over 2.5 Golos", o25, o_o25)], columns=["M", "P", "B"])
    df["F"] = 1/df["P"]; df["E"] = (df["P"] * df["B"]) - 1
    
    def get_c(e):
        if e > 0.10: return 'rgba(16, 185, 129, 0.08)'
        if e > 0.02: return 'rgba(245, 158, 11, 0.08)'
        if e < 0: return 'rgba(239, 68, 68, 0.08)'
        return 'rgba(255, 255, 255, 0.01)'

    fig_t = go.Figure(data=[go.Table(
        header=dict(values=['MERCADO', 'PROB.', 'ODD JUSTA', 'ODD CASA', 'ALPHA EDGE'], 
                    fill_color='#020617', align='left', font=dict(color='#64748B', size=11), height=50),
        cells=dict(values=[df.M, df.P.map('{:.1%}'.format), df.F.map('{:.2f}'.format), df.B.map('{:.2f}'.format), df.E.map('{:+.1%}'.format)],
                   fill_color=[[get_c(e) for e in df["E"]]], align='left', font=dict(color='white', size=14), height=50)
    )])
    fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=350, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_t, use_container_width=True)

    # Glossário - Agora em Grid Horizontal
    st.markdown("<br>", unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"""<div class="luxury-card" style="padding:20px; border-left:2px solid #10B981;">
            <p style="font-weight:800; color:#10B981; font-size:0.7rem; text-transform:uppercase;">🟡 Mercado de Elite</p>
            <p style="font-size:0.8rem; color:#94A3B8; margin:0;">Ineficiência crítica detetada. O risco é desproporcional à recompensa oferecida pela casa.</p>
        </div>""", unsafe_allow_html=True)
    with g2:
        st.markdown(f"""<div class="luxury-card" style="padding:20px; border-left:2px solid #F59E0B;">
            <p style="font-weight:800; color:#F59E0B; font-size:0.7rem; text-transform:uppercase;">🟢 Valor Profissional</p>
            <p style="font-size:0.8rem; color:#94A3B8; margin:0;">Território de lucro a longo prazo. Consistência em Edges positivos garante ROI positivo.</p>
        </div>""", unsafe_allow_html=True)
    with g3:
        st.markdown(f"""<div class="luxury-card" style="padding:20px; border-left:2px solid #EF4444;">
            <p style="font-weight:800; color:#EF4444; font-size:0.7rem; text-transform:uppercase;">🔴 Zona de Armadilha</p>
            <p style="font-size:0.8rem; color:#94A3B8; margin:0;">Preço inflacionado pela casa. O modelo indica fuga obrigatória destes mercados.</p>
        </div>""", unsafe_allow_html=True)
