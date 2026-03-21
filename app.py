import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Advanced Institutional Configuration
st.set_page_config(
    page_title="STARLINE V117 - ELEGANT SOVEREIGN", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Sovereign Glassmorphism CSS (The White-Data Edition)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%);
        color: #FFFFFF; font-family: 'Plus Jakarta Sans', sans-serif; 
    }
    
    /* SIDEBAR: PURE GLASS & IVORY DATA */
    [data-testid="stSidebar"] { 
        background-color: rgba(255, 255, 255, 0.01) !important; 
        backdrop-filter: blur(40px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Input Styling - Branco Nítido e Elegante */
    [data-testid="stSidebar"] .stNumberInput input, 
    [data-testid="stSidebar"] .stTextInput input {
        background-color: rgba(255, 255, 255, 0.03) !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; /* BORDA CRISTAL ULTRA-FINA */
        color: #F8FAFC !important; /* IVORY SOFT DATA: Máxima Legibilidade com Leveza */
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 400 !important;
        border-radius: 6px !important;
        font-size: 0.95rem !important;
        transition: 0.3s all;
    }
    
    /* Input Focus State (Suave Glow) */
    [data-testid="stSidebar"] .stNumberInput input:focus {
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.05) !important;
    }

    /* Labels Sofisticadas */
    label { 
        font-size: 0.72rem !important; 
        font-weight: 700 !important; 
        color: #94A3B8 !important; 
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        margin-bottom: 8px !important;
    }

    /* O NOVO ADVISOR MINIMALISTA (O SELO) */
    .advisor-seal {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(255, 255, 255, 0.02) 100%);
        border-radius: 12px; padding: 20px 30px; border: 1px solid rgba(0, 255, 136, 0.4);
        display: inline-block; /* Tamanho ajustável ao conteúdo */
        text-align: center; margin-bottom: 30px;
    }
    .advisor-title { color: white; font-size: 2rem; font-weight: 900; letter-spacing: -1.5px; margin: 0; }
    .advisor-subtitle { color: #00FF88; font-size: 1.1rem; font-weight: 800; margin: 0; }

    /* Intel Cards */
    .intel-card {
        background: rgba(255, 255, 255, 0.03); border-radius: 16px; padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1); margin-top: 15px;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 900; 
        height: 4.8em; width: 100%; border-radius: 12px; border: none; text-transform: uppercase;
        letter-spacing: 3px; box-shadow: 0 15px 35px rgba(0, 255, 136, 0.25);
    }
    
    hr { border-top: 1px solid rgba(255, 255, 255, 0.08) !important; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: THE ELEGANT COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; font-size:26px; font-weight:800; letter-spacing:-1px;'>🏛️ ORACLE V117</h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='color:white; font-weight:800; margin-top:10px;'>01 // IDENTIFICATION</p>", unsafe_allow_html=True)
    h_n = st.text_input("HOME TEAM NAME", "VILLARREAL").upper()
    a_n = st.text_input("AWAY TEAM NAME", "REAL SOCIEDAD").upper()
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:white; font-weight:800;'>02 // PERFORMANCE (LAST 5 GAMES)</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    hgf = col1.number_input("HOME GOALS SCORED", 9.0)
    hga = col1.number_input("HOME GOALS CONCEDED", 7.0)
    agf = col2.number_input("AWAY GOALS SCORED", 12.0)
    aga = col2.number_input("AWAY GOALS CONCEDED", 10.0)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:white; font-weight:800;'>03 // MARKET QUOTES</p>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    m1 = c1.number_input("HOME WIN (1)", 1.90)
    mx = cx.number_input("DRAW (X)", 4.00)
    m2 = c2.number_input("AWAY WIN (2)", 3.35)
    
    st.caption("GOALS LADDER")
    col_o1, col_o2 = st.columns(2)
    o05 = col_o1.number_input("OVER 0.5 GOALS ODD", 1.05)
    o15 = col_o2.number_input("OVER 1.5 GOALS ODD", 1.16)
    o25 = col_o1.number_input("OVER 2.5 GOALS ODD", 1.33)
    o35 = col_o2.number_input("OVER 3.5 GOALS ODD", 1.78)
    
    st.caption("SPECIALS")
    m_ob = st.number_input("BOTH TEAMS TO SCORE (YES) ODD", 1.32)
    ah_h = st.number_input("ASIAN HANDICAP 0.0 (HOME) ODD", 1.33)
    ah_a = st.number_input("ASIAN HANDICAP 0.0 (AWAY) ODD", 1.85)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTE ALPHA SCAN")
    st.button("🗑️ RESET ENGINE", on_click=reset)

# --- RESULTS INTERFACE ---
if not run:
    st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.1;'><h1>ORACLE READY</h1><p>V117 Elegant Sovereign</p></div>", unsafe_allow_html=True)
else:
    # 3. MATH ENGINE: INSTITUTIONAL POISSON (V111+)
    lh = max(0.01, (hgf/5 * aga/5)**0.5)
    la = max(0.01, (agf/5 * hga/5)**0.5)
    
    sim_h = np.random.poisson(lh, 1000000)
    sim_a = np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    
    ph = np.mean(sim_h > sim_a); px = np.mean(sim_h == sim_a); pa = np.mean(sim_h < sim_a)
    norm = ph + px + pa; ph, px, pa = ph/norm, px/norm, pa/norm
    
    # AH 0.0 Calculation (Draw No Bet)
    p_ah0h = ph / (ph + pa); p_ah0a = pa / (ph + pa)

    # 4. RESULTS VISUALIZATION
    st.markdown(f"<h1 style='letter-spacing:-4px; font-size:60px; margin:0;'>{h_n} <span style='color:#00FF88; font-weight:300;'>vs</span> {a_n}</h1>", unsafe_allow_html=True)
    
    # Lista de Mercados Total (Recuperada)
    mkts = [
        ("WIN: "+h_n, ph, m1), ("WIN: "+a_n, pa, m2), ("DRAW (X)", px, mx),
        ("OVER 0.5 GOALS", np.mean(stot>0.5), o05), ("OVER 1.5 GOALS", np.mean(stot>1.5), o15), 
        ("OVER 2.5 GOALS", np.mean(stot>2.5), o25), ("OVER 3.5 GOALS", np.mean(stot>3.5), o35),
        ("BOTH TEAMS TO SCORE (YES)", np.mean((sim_h>0)&(sim_a>0)), m_ob),
        ("ASIAN HANDICAP 0.0: "+h_n, p_ah0h, ah_h), ("ASIAN HANDICAP 0.0: "+a_n, p_ah0a, ah_a)
    ]
    best = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts], key=lambda x: x[3], reverse=True)[0]

    # O NOVO ADVISOR: O SELO ALPHA
    st.markdown(f"""
        <div class="advisor-seal">
            <h1 class="advisor-title">{best[0]}</h1>
            <p class="advisor-subtitle">EDGE: {best[3]:+.1%} | PROB: {best[1]:.1%}</p>
        </div>
    """, unsafe_allow_html=True)

    # 5. MATRIX INFINITA (FULL HEIGHT)
    df = pd.DataFrame(mkts, columns=["Market", "Prob", "Odd"])
    df["Fair"] = 1/df["Prob"]; df["Edge"] = (df["Prob"] * df["Odd"]) - 1
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>MARKET</b>', '<b>CONFIDENCE</b>', '<b>FAIR ODD</b>', '<b>MARKET ODD</b>', '<b>ALPHA EDGE</b>'],
                    fill_color='#0A0A0A', align='center', font=dict(color='#64748B', size=11), height=45),
        cells=dict(values=[df.Market, df.Prob.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), 
                           df.Odd.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                   fill_color=[['rgba(0, 255, 136, 0.15)' if e > 0.1 else 'rgba(255,255,255,0.02)' for e in df.Edge]],
                   align='center', font=dict(color='white', size=14), height=40)
    )])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', height=(len(mkts)*40+60))
    st.plotly_chart(fig, use_container_width=True)

    # 6. ANALYTICS (HD GRAPHS)
    st.markdown("---")
    c1, c2 = st.columns([1.3, 0.7])
    with c1:
        xr = list(range(7))
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig_p.update_layout(title="POISSON DISTRIBUTION DENSITY", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=320)
        st.plotly_chart(fig_p, use_container_width=True)
    with c2:
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        st.write("**TOP PROBABLE SCORES**")
        for j in range(2, -1, -1):
            st.metric(f"SCORE {idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
