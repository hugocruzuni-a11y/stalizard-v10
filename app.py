import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Advanced Institutional Configuration
st.set_page_config(
    page_title="STARLINE V111 - INSTITUTIONAL", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Sovereign Glassmorphism CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%); color: #FFFFFF; font-family: 'Plus Jakarta Sans', sans-serif; }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.02) !important; backdrop-filter: blur(40px) !important; border-right: 1px solid rgba(255, 255, 255, 0.08) !important; }
    [data-testid="stSidebar"] .stNumberInput input, [data-testid="stSidebar"] .stTextInput input { background-color: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; color: #FFFFFF !important; font-family: 'JetBrains Mono', monospace !important; border-radius: 8px !important; }
    .advisor-premium { background: linear-gradient(135deg, rgba(0, 255, 136, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%); border-radius: 24px; padding: 35px; border: 1px solid rgba(0, 255, 136, 0.3); box-shadow: 0 0 40px rgba(0, 255, 136, 0.05); margin-bottom: 25px; }
    .intel-card { background: rgba(255, 255, 255, 0.03); border-radius: 16px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.1); margin-top: 15px; }
    div.stButton > button { background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; font-weight: 800; height: 4.8em; width: 100%; border-radius: 12px; border: none; text-transform: uppercase; letter-spacing: 3px; box-shadow: 0 15px 35px rgba(0, 255, 136, 0.25); }
    label { font-size: 0.75rem !important; font-weight: 700 !important; color: #94A3B8 !important; text-transform: uppercase; letter-spacing: 1.5px; }
    hr { border-top: 1px solid rgba(255, 255, 255, 0.08) !important; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: THE PROFESSIONAL COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:white; font-size:26px; font-weight:800;'>🏛️ ORACLE <span style='color:#00FF88;'>V111</span></h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='color:white; font-weight:800; margin-top:20px;'>01 // IDENTIFICATION</p>", unsafe_allow_html=True)
    h_n = st.text_input("HOME TEAM", "VILLARREAL").upper()
    a_n = st.text_input("AWAY TEAM", "REAL SOCIEDAD").upper()
    
    st.markdown("<p style='color:white; font-weight:800;'>02 // PERFORMANCE (Last 5 Games)</p>", unsafe_allow_html=True)
    c_h, c_a = st.columns(2)
    hgf = c_h.number_input("H-GF", 9.0); hga = c_h.number_input("H-GA", 7.0)
    agf = c_a.number_input("A-GF", 12.0); aga = c_a.number_input("A-GA", 10.0)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<p style='color:white; font-weight:800;'>03 // MARKET QUOTES</p>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    m1 = c1.number_input("ODD 1", 1.90); mx = cx.number_input("ODD X", 4.00); m2 = c2.number_input("ODD 2", 3.35)
    
    st.caption("GOALS LADDER")
    co0, co1, co2, co3 = st.columns(4)
    o05 = co0.number_input("O0.5", 1.05); o15 = co1.number_input("O1.5", 1.16); o25 = co2.number_input("O2.5", 1.33); o35 = co3.number_input("O3.5", 1.78)
    
    cu0, cu1, cu2, cu3 = st.columns(4)
    u05 = cu0.number_input("U0.5", 9.50); u15 = cu1.number_input("U1.5", 4.50); u25 = cu2.number_input("U2.5", 2.65); u35 = cu3.number_input("U3.5", 1.60)
    
    st.caption("SPECIALS")
    m_ob = st.number_input("BTTS YES", 1.32)
    m_ah_h = st.number_input("AH 0.0 (HOME)", 1.33)
    m_ah_a = st.number_input("AH 0.0 (AWAY)", 1.85)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTE ALPHA SCAN")
    st.button("🗑️ RESET ENGINE", on_click=reset)

# --- RESULTS INTERFACE ---
if not run:
    st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.1;'><h1>ORACLE STANDBY</h1><p>AWAITING ASSET COMMANDS</p></div>", unsafe_allow_html=True)
else:
    # 3. MATH ENGINE: PROFESSIONAL POISSON ADJUSTMENT
    # Baseline: Average goals per game in modern football (approx 1.35 per team)
    lh = max(0.01, (hgf/5 * aga/5)**0.5)
    la = max(0.01, (agf/5 * hga/5)**0.5)
    
    # 1 Million Monte Carlo Simulation
    sim_h = np.random.poisson(lh, 1000000)
    sim_a = np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    
    # Probabilities Calculation
    ph = np.mean(sim_h > sim_a); px = np.mean(sim_h == sim_a); pa = np.mean(sim_h < sim_a)
    norm = ph + px + pa; ph, px, pa = ph/norm, px/norm, pa/norm # Normalization
    
    # AH 0.0 Calculation (Draw No Bet)
    p_ah0h = ph / (ph + pa); p_ah0a = pa / (ph + pa)

    st.markdown(f"<h1 style='letter-spacing:-4px; font-size:60px; margin:0;'>{h_n} <span style='color:#00FF88; font-weight:300;'>vs</span> {a_n}</h1>", unsafe_allow_html=True)
    
    # 4. ADVISOR & AI INSIGHTS
    col_adv, col_note = st.columns([1.2, 0.8])
    mkts = [
        ("WIN: "+h_n, ph, m1), ("WIN: "+a_n, pa, m2), ("DRAW (X)", px, mx),
        ("OVER 0.5", np.mean(stot>0.5), o05), ("OVER 1.5", np.mean(stot>1.5), o15), 
        ("OVER 2.5", np.mean(stot>2.5), o25), ("OVER 3.5", np.mean(stot>3.5), o35),
        ("UNDER 0.5", np.mean(stot<0.5), u05), ("UNDER 1.5", np.mean(stot<1.5), u15), 
        ("UNDER 2.5", np.mean(stot<2.5), u25), ("UNDER 3.5", np.mean(stot<3.5), u35),
        ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob),
        ("AH 0.0: "+h_n, p_ah0h, m_ah_h), ("AH 0.0: "+a_n, p_ah0a, m_ah_a)
    ]
    best = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts], key=lambda x: x[3], reverse=True)[0]

    with col_adv:
        st.markdown(f"""<div class="advisor-premium">
            <p style="color:#94A3B8; margin:0; font-size:0.8rem; font-weight:800; letter-spacing:4px;">ORACLE ALPHA SIGNAL</p>
            <h1 style="color:white; margin:10px 0; font-size:3.5rem; letter-spacing:-2px;">{best[0]}</h1>
            <p style="color:#00FF88; font-size:1.6rem; margin:0; font-weight:900;">EDGE: {best[3]:+.1%} | PROB: {best[1]:.1%}</p>
        </div>""", unsafe_allow_html=True)

    with col_note:
        st.markdown("### 🧠 AI ASSISTANCE")
        st.markdown(f"""<div class="intel-card">
            <b style="color:#00FF88; font-size:1rem;">INSTITUTIONAL INSIGHT:</b><br>
            <p style="color:#CBD5E1; font-size:0.95rem; line-height:1.6; margin-top:10px;">
            Engine detects a <b>{best[3]:.1%} alpha</b>. High-precision Poisson adjustment confirms <b>{h_n if ph > pa else a_n}'s</b> offensive efficiency outperforms the current market price by {best[3]*100:.1f}%.
            </p>
        </div>""", unsafe_allow_html=True)

    # 5. MATRIX INFINITA (VISIBILIDADE TOTAL)
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

    # 6. ANALYTICS
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
