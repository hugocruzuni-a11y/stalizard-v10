import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Advanced Institutional Configuration
st.set_page_config(
    page_title="STARLINE V107 - UNBREAKABLE", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Luxury Glassmorphism CSS (The Final Polish)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%);
        color: #FFFFFF; font-family: 'Plus Jakarta Sans', sans-serif; 
    }
    
    [data-testid="stSidebar"] { 
        background-color: rgba(255, 255, 255, 0.02) !important; 
        backdrop-filter: blur(35px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    .stNumberInput input, .stTextInput input {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #00FF88 !important;
        font-family: 'JetBrains Mono', monospace !important;
        border-radius: 8px !important;
    }

    .advisor-premium {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(255, 255, 255, 0.02) 100%);
        border-radius: 20px; padding: 30px; border: 1px solid rgba(0, 255, 136, 0.4);
        box-shadow: 0 0 40px rgba(0, 255, 136, 0.05); margin-bottom: 25px;
    }
    .intel-card {
        background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08); margin-top: 10px;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 800; 
        height: 4.5em; width: 100%; border-radius: 10px; border: none; text-transform: uppercase;
        letter-spacing: 2px; box-shadow: 0 10px 30px rgba(0, 255, 136, 0.3);
    }
    
    label { font-size: 0.7rem !important; font-weight: 800 !important; color: #94A3B8 !important; text-transform: uppercase; letter-spacing: 1px; }
    hr { border-top: 1px solid rgba(255, 255, 255, 0.05) !important; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: THE GLASS COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:white; font-size:24px;'>🏛️ ORACLE <span style='color:#00FF88;'>V107</span></h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='color:white; font-weight:800; margin-top:15px;'>01 // ASSETS</p>", unsafe_allow_html=True)
    h_n = st.text_input("HOME TEAM", "VILLARREAL").upper()
    a_n = st.text_input("AWAY TEAM", "REAL SOCIEDAD").upper()
    
    st.markdown("<p style='color:white; font-weight:800;'>02 // PERFORMANCE (Last 5)</p>", unsafe_allow_html=True)
    c_h, c_a = st.columns(2)
    hgf = c_h.number_input("H-GF", 9.0); hga = c_h.number_input("H-GA", 7.0)
    agf = c_a.number_input("A-GF", 12.0); aga = c_a.number_input("A-GA", 10.0)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<p style='color:white; font-weight:800;'>03 // MARKET QUOTES</p>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    m1 = c1.number_input("ODD 1", 1.90); mx = cx.number_input("ODD X", 4.00); m2 = c2.number_input("ODD 2", 3.35)
    
    st.caption("GOALS LADDER (OVER)")
    co0, co1, co2, co3 = st.columns(4)
    o05 = co0.number_input("O0.5", 1.05); o15 = co1.number_input("O1.5", 1.16); o25 = co2.number_input("O2.5", 1.33); o35 = co3.number_input("O3.5", 1.78)
    
    st.caption("GOALS LADDER (UNDER)")
    cu0, cu1, cu2, cu3 = st.columns(4)
    u05 = cu0.number_input("U0.5", 9.50); u15 = cu1.number_input("U1.5", 4.50); u25 = cu2.number_input("U2.5", 2.65); u35 = cu3.number_input("U3.5", 1.60)
    
    st.caption("SPECIALS")
    m_ob_y = st.number_input("BTTS YES", 1.32)
    m_ah0_h = st.number_input("AH 0.0 (H)", 1.33)
    m_ah0_a = st.number_input("AH 0.0 (A)", 1.85)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTE ALPHA SCAN")
    st.button("🗑️ RESET ENGINE", on_click=reset)

# --- RESULTS INTERFACE ---
if not run:
    st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.1;'><h1>ORACLE READY</h1><p>V107 SOVEREIGN BUILD</p></div>", unsafe_allow_html=True)
else:
    # ENGINE 1M SIMS
    lh, la = max(0.01, ((hgf/5)*(aga/5))**0.5), max(0.01, ((agf/5)*(hga/5))**0.5)
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    norm = ph+px+pa; ph, px, pa = ph/norm, px/norm, pa/norm

    st.markdown(f"<h1 style='letter-spacing:-4px; font-size:60px; margin:0;'>{h_n} <span style='color:#00FF88; font-weight:300;'>vs</span> {a_n}</h1>", unsafe_allow_html=True)
    
    col_adv, col_note = st.columns([1.2, 0.8])
    
    mkts = [
        ("WIN: "+h_n, ph, m1), ("WIN: "+a_n, pa, m2), ("DRAW (X)", px, mx),
        ("OVER 0.5", np.mean(stot>0.5), o05), ("OVER 1.5", np.mean(stot>1.5), o15), 
        ("OVER 2.5", np.mean(stot>2.5), o25), ("OVER 3.5", np.mean(stot>3.5), o35),
        ("UNDER 0.5", np.mean(stot<0.5), u05), ("UNDER 1.5", np.mean(stot<1.5), u15), 
        ("UNDER 2.5", np.mean(stot<2.5), u25), ("UNDER 3.5", np.mean(stot<3.5), u35),
        ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob_y),
        ("AH 0.0: "+h_n, ph/(ph+pa), m_ah0_h), ("AH 0.0: "+a_n, pa/(ph+pa), m_ah0_a)
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
            <b style="color:#00FF88;">QUANTUM INSIGHT:</b><br>
            <span style="color:#CBD5E1; font-size:0.95rem;">
            Analysis detects <b>{best[3]:.1%} alpha</b> in {best[0]}. Discrepancy between Poisson density 
            and market pricing indicates high-value institutional entry.
            </span>
        </div>""", unsafe_allow_html=True)

    # MATRIX INFINITA (Fixed Plotly Logic)
    df = pd.DataFrame(mkts, columns=["Market", "Prob", "Odd"])
    df["Fair"] = 1/df["Prob"]; df["Edge"] = (df["Prob"] * df["Odd"]) - 1
    
    # Secure Color Logic
    edge_colors = ['rgba(0, 255, 136, 0.15)' if e > 0.1 else 'rgba(255,255,255,0.02)' for e in df["Edge"]]

    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>MARKET</b>', '<b>CONFIDENCE</b>', '<b>FAIR</b>', '<b>BOOKIE</b>', '<b>EDGE</b>'],
                    fill_color='#0A0A0A', align='center', font=dict(color='#64748B', size=11), height=45),
        cells=dict(values=[df.Market, df.Prob.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), 
                           df.Odd.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                   fill_color=[edge_colors],
                   align='center', font=dict(color='white', size=14), height=35)
    )])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', height=(len(mkts)*35+60))
    st.plotly_chart(fig, use_container_width=True)

    # ANALYTICS
    st.markdown("---")
    c1, c2 = st.columns([1.3, 0.7])
    with c1:
        xr = list(range(7))
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig_p.update_layout(title="POISSON DENSITY CURVES", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=320)
        st.plotly_chart(fig_p, use_container_width=True)
    with c2:
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        st.write("**TOP PROBABLE SCORES**")
        for j in range(2, -1, -1):
            st.metric(f"SCORE {idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
