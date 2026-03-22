import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO DE ALTA FIDELIDADE ---
st.set_page_config(page_title="ORACLE V140 PRO - SYNDICATE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #070A11; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1E293B !important; }
    
    .pro-card { background: #111827; border-radius: 12px; padding: 25px; border: 1px solid #1E293B; border-left: 6px solid #00FF88; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .bet-name { font-size: 2.2rem; font-weight: 800; color: #FFFFFF; margin: 0; line-height: 1.1; letter-spacing: -1px; }
    .edge-value { font-family: 'JetBrains Mono'; font-size: 1.4rem; color: #00FF88; font-weight: 700; }
    
    .ia-insight-card { background: rgba(0, 255, 136, 0.03); border-radius: 10px; padding: 15px; border: 1px dashed rgba(0, 255, 136, 0.3); margin-top: 15px; font-size: 0.85rem; }
    
    .stNumberInput label, .stSelectbox label, .stSlider label { font-size: 0.7rem !important; color: #94A3B8 !important; font-weight: 700; text-transform: uppercase; }
    div.stButton > button { background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; font-weight: 800 !important; height: 3.5rem !important; border-radius: 8px !important; border: none !important; width: 100%; }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] { background-color: #070A11; }
    .stTabs [data-baseweb="tab"] { color: #64748B; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #00FF88 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR QUANTITATIVO DE ALTO NÍVEL ---
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

def run_master_math(lh, la, rho, boost, zip_factor):
    lh *= (1+boost); la *= (1-boost); max_g = 10
    prob_mtx = np.outer(poisson.pmf(np.arange(max_g), lh), poisson.pmf(np.arange(max_g), la))
    
    # Dixon-Coles Adjustment
    for x in range(2):
        for y in range(2):
            if x==0 and y==0: prob_mtx[x,y] *= (1-lh*la*rho)
            elif x==0 and y==1: prob_mtx[x,y] *= (1+lh*rho)
            elif x==1 and y==0: prob_mtx[x,y] *= (1+la*rho)
            elif x==1 and y==1: prob_mtx[x,y] *= (1-rho)
            
    # Zero-Inflated Poisson (ZIP) Adjustment para 0-0
    prob_mtx[0,0] *= zip_factor
    prob_mtx /= prob_mtx.sum() # Normalize
    
    ph, px, pa = np.tril(prob_mtx, -1).sum(), np.trace(prob_mtx), np.triu(prob_mtx, 1).sum()
    
    # Asian Handicaps
    h_win_1 = np.trace(prob_mtx, offset=-1); a_win_1 = np.trace(prob_mtx, offset=1)
    
    ah0_h = ph / (ph + pa) if (ph + pa) > 0 else 0
    ah_m1_h = (ph - h_win_1) / (1 - h_win_1) if (1 - h_win_1) > 0 else 0
    ah_m15_h = np.tril(prob_mtx, -2).sum()
    ah_p05_h = ph + px
    ah_p15_h = 1 - np.triu(prob_mtx, 2).sum()
    
    # Goals Matrix
    goals_sum = np.add.outer(np.arange(max_g), np.arange(max_g))
    o15 = prob_mtx[goals_sum > 1.5].sum(); u15 = 1 - o15
    o25 = prob_mtx[goals_sum > 2.5].sum(); u25 = 1 - o25
    o35 = prob_mtx[goals_sum > 3.5].sum(); u35 = 1 - o35
    
    # BTTS
    btts_no = prob_mtx[0, :].sum() + prob_mtx[:, 0].sum() - prob_mtx[0,0]
    btts_yes = 1 - btts_no
    
    return {
        "1": ph, "X": px, "2": pa,
        "AH +1.5 (H)": ah_p15_h, "AH +0.5 (H)": ah_p05_h, "AH 0.0 (H)": ah0_h, "AH -0.5 (H)": ph, "AH -1.0 (H)": ah_m1_h, "AH -1.5 (H)": ah_m15_h,
        "O1.5": o15, "U1.5": u15, "O2.5": o25, "U2.5": u25, "O3.5": o35, "U3.5": u35,
        "BTTS (Sim)": btts_yes, "BTTS (Não)": btts_no
    }, prob_mtx

# --- 3. SIDEBAR (CONTROLO MÁXIMO) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; margin:0;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    
    with st.expander("💼 GESTÃO DE BANCA E RISCO", expanded=True):
        bankroll = st.number_input("Banca Total (€)", value=100.0, step=10.0)
        kelly_fraction = st.selectbox("Estratégia Kelly", [("Quarter-Kelly (Conservador)", 0.25), ("Half-Kelly (Padrão)", 0.50), ("Full-Kelly (Agressivo)", 1.0)], index=1)
        k_mult = kelly_fraction[1]

    with st.expander("📡 DADOS E JOGO", expanded=True):
        l_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94, "Champions League": 2}
        ln = st.selectbox("Liga", list(l_map.keys()))
        
        fix = requests.get(f"https://{api_host}/fixtures", headers=headers, params={"date": date.today().strftime('%Y-%m-%d'), "league": l_map[ln], "season": "2025"}).json().get('response', [])
        if fix:
            m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
            m_display = st.selectbox("Jogo", list(m_map.keys()))
            m_sel = next(f for f in fix if f['fixture']['id'] == m_map[m_display])
        else: m_sel = None

    with st.expander("⚙️ OVERRIDE TÁCTICO (MANUAL xG)", expanded=False):
        use_manual_xg = st.checkbox("Ignorar API e usar xG Manual")
        man_xg_h = st.number_input("xG Casa", value=1.50, step=0.1)
        man_xg_a = st.number_input("xG Fora", value=1.20, step=0.1)
        zip_factor = st.slider("Fator ZIP (Ajuste de 0-0)", 1.0, 1.3, 1.05, help="Inflaciona a probabilidade do 0-0 para refletir o futebol moderno.")

    with st.expander("📈 ODD INJECTION (MERCADOS)", expanded=False):
        st.write("Match Odds")
        c1, cx, c2 = st.columns(3)
        o_1 = c1.number_input("1", value=2.00); o_x = cx.number_input("X", value=3.40); o_2 = c2.number_input("2", value=3.50)
        
        st.write("Asian Handicaps (Casa)")
        c3, c4 = st.columns(2)
        o_ah0 = c3.number_input("AH 0.0", value=1.55); o_ahm1 = c4.number_input("AH -1.0", value=3.20)
        o_ahp05 = c3.number_input("AH +0.5", value=1.00); o_ahm15 = c4.number_input("AH -1.5", value=1.00)
        
        st.write("Golos e BTTS")
        c5, c6 = st.columns(2)
        o_o25 = c5.number_input("Over 2.5", value=1.90); o_u25 = c6.number_input("Under 2.5", value=1.90)
        o_o15 = c5.number_input("Over 1.5", value=1.00); o_o35 = c6.number_input("Over 3.5", value=1.00)
        o_btts_y = c5.number_input("BTTS Sim", value=1.85); o_btts_n = c6.number_input("BTTS Não", value=1.95)
        
    execute = st.button("🚀 INICIAR ALPHA SCAN")

# --- 4. RESULTADOS E INTERFACE ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:200px; opacity:0.2;'><h1>ORACLE V140 PRO</h1><p>Terminal Institucional Aguardando Dados...</p></div>", unsafe_allow_html=True)
else:
    # Lógica de injeção de xG Manual ou API
    if use_manual_xg:
        lh, la = man_xg_h, man_xg_a
    else:
        s = get_pro_stats(m_sel['teams']['home']['id'], l_map[ln])
        lh, la = (s['h_f']*s['a_a'])**0.5, (s['a_f']*s['h_a'])**0.5
        
    res, mtx = run_master_math(lh, la, -0.11, 0.12, zip_factor)
    
    st.markdown(f"<h2 style='margin-bottom:0; font-size:3rem;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#475569; font-weight:300;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h2>", unsafe_allow_html=True)

    col_res, col_chart = st.columns([1.1, 0.9])

    # Compilação de todos os mercados ativos (Odd > 1.01)
    all_mkts = [
        ("Vencedor: Casa", res["1"], o_1), ("Empate (X)", res["X"], o_x), ("Vencedor: Fora", res["2"], o_2),
        ("AH +0.5 (Casa)", res["AH +0.5 (H)"], o_ahp05), ("AH 0.0 (DNB)", res["AH 0.0 (H)"], o_ah0), 
        ("AH -1.0 (Casa)", res["AH -1.0 (H)"], o_ahm1), ("AH -1.5 (Casa)", res["AH -1.5 (H)"], o_ahm15),
        ("Over 1.5 Golos", res["O1.5"], o_o15), ("Over 2.5 Golos", res["O2.5"], o_o25), 
        ("Under 2.5 Golos", res["U2.5"], o_u25), ("Over 3.5 Golos", res["O3.5"], o_o35),
        ("Ambas Marcam (Sim)", res["BTTS (Sim)"], o_btts_y), ("Ambas Marcam (Não)", res["BTTS (Não)"], o_btts_n)
    ]
    
    # Filtra mercados em que o utilizador não inseriu odds (<= 1.01)
    valid_mkts = [(n,p,b,(p*b)-1) for n,p,b in all_mkts if b > 1.01]
    
    if len(valid_mkts) > 0:
        best = sorted(valid_mkts, key=lambda x: x[3], reverse=True)[0]
        edge = best[3]; kelly = max(0, (edge/(best[2]-1)) * k_mult)
        color = "#00FF88" if edge > 0.08 else "#FFD700" if edge > 0.02 else "#EF4444"
        
        with col_res:
            st.markdown(f"""<div class="pro-card" style="border-left-color: {color};">
                <span style="color:#64748B; font-size:0.7rem; font-weight:800;">TOP ALPHA EDGE (MELHOR VALOR)</span>
                <p class="bet-name">{best[0]}</p>
                <p style="margin:10px 0;">EDGE: <span class="edge-value" style="color:{color};">{edge:+.1%}</span> | STAKE SUGERIDA: <b>{bankroll*kelly:.2f}€</b></p>
                <div class="ia-insight-card">
                    <b>🤖 ORACLE INSIGHT:</b> λ Casa ({lh:.2f}) vs λ Fora ({la:.2f}). 
                    A ineficiência deste mercado bate os <b>{edge:.1%}</b> de EV positivo. 
                    Gestão de risco adaptada usando {kelly_fraction[0]}.
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        with col_res: st.warning("Por favor, insira pelo menos uma odd válida no menu lateral.")

    with col_chart:
        xr = np.arange(7)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name="Casa", fill='tozeroy', line_color='#00FF88', line_width=3))
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name="Fora", fill='tozeroy', line_color='#3B82F6', line_width=3))
        fig.update_layout(height=240, margin=dict(l=0,r=0,t=20,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)

    # TABELA DINÂMICA COMPLETA DE MERCADOS
    st.markdown("### 📊 ALL MARKETS QUANT MATRIX")
    
    if len(valid_mkts) > 0:
        df = pd.DataFrame(valid_mkts, columns=["Mercado", "P", "B", "Edge"])
        df["Fair"] = 1/df["P"]
        df = df.sort_values(by="Edge", ascending=False)
        
        def get_heatmap(e):
            if e > 0.10: return 'rgba(255, 215, 0, 0.2)' 
            if e > 0.03: return 'rgba(0, 255, 136, 0.15)' 
            if e < 0: return 'rgba(239, 68, 68, 0.1)'    
            return 'rgba(255, 255, 255, 0.02)'

        fig_t = go.Figure(data=[go.Table(
            header=dict(values=['MERCADO', 'PROB. MODELO', 'ODD JUSTA', 'ODD CASA', 'ALPHA EDGE'], fill_color='#020617', align='left', font=dict(color='#94A3B8', size=11), height=40),
            cells=dict(values=[df.Mercado, df.P.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), df.B.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                       fill_color=[[get_heatmap(e) for e in df["Edge"]]], align='left', font=dict(color='white', size=13), height=35)
        )])
        fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=(len(df)*35)+60, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_t, use_container_width=True)
