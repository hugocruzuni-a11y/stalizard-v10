import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Institutional Configuration
st.set_page_config(
    page_title="STARLINE V102 - FULL SPECTRUM", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Cockpit Elite CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%);
        color: #FFFFFF; font-family: 'Inter', sans-serif; 
    }
    
    [data-testid="stSidebar"] { 
        background-color: #050505 !important; 
        border-right: 1px solid #1A1A1A;
    }
    
    .stNumberInput, .stTextInput {
        background-color: #0D1117 !important;
        border: 1px solid #30363D !important;
        border-radius: 4px !important;
        color: #00FF88 !important;
        font-family: 'JetBrains Mono', monospace;
    }

    .advisor-premium {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.05) 0%, rgba(0, 0, 0, 0.4) 100%);
        border-radius: 20px; padding: 30px; border: 1px solid #00FF88;
        box-shadow: 0 0 60px rgba(0, 255, 136, 0.1); margin-bottom: 20px;
    }

    div.stButton > button {
        background: #00FF88 !important; color: #000000 !important; font-weight: 900; 
        height: 4.5em; width: 100%; border-radius: 8px; border: none; text-transform: uppercase;
        letter-spacing: 2px; box-shadow: 0 8px 25px rgba(0, 255, 136, 0.3);
    }
    
    label { font-size: 0.65rem !important; font-weight: 900 !important; color: #64748B !important; text-transform: uppercase; }
    hr { border-top: 1px solid #1A1A1A !important; margin: 15px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: THE FULL-SPECTRUM COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:#FFFFFF; font-size:22px; font-weight:900;'>🏛️ COCKPIT <span style='color:#00FF88;'>V102</span></h2>", unsafe_allow_html=True)
    
    # 01. EQUIPAS
    st.markdown("<p style='color:#00FF88; font-size:0.7rem; font-weight:800; margin-top:10px;'>01 // ASSET DATA</p>", unsafe_allow_html=True)
    h_n = st.text_input("HOME TEAM", "HOME TEAM").upper()
    a_n = st.text_input("AWAY TEAM", "AWAY TEAM").upper()
    
    # 02. PERFORMANCE
    st.markdown("<p style='color:#00FF88; font-size:0.7rem; font-weight:800;'>02 // ATTACK/DEFENSE RATINGS</p>", unsafe_allow_html=True)
    c_h, c_a = st.columns(2)
    hgf = c_h.number_input("H-GF (Last 5)", 8.0); hga = c_h.number_input("H-GA (Last 5)", 10.0)
    agf = c_a.number_input("A-GF (Last 5)", 10.0); aga = c_a.number_input("A-GA (Last 5)", 12.0)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 03. MERCADOS (FULL SPECTRUM)
    st.markdown("<p style='color:#00FF88; font-size:0.7rem; font-weight:800;'>03 // MARKET QUOTES</p>", unsafe_allow_html=True)
    
    # 1X2
    c1, cx, c2 = st.columns(3)
    m1 = c1.number_input("ODD 1", 2.10); mx = cx.number_input("ODD X", 3.40); m2 = c2.number_input("ODD 2", 3.60)
    
    # OVER LADDER
    st.caption("GOALS: OVER")
    co0, co1, co2, co3 = st.columns(4)
    o05 = co0.number_input("O 0.5", 1.05); o15 = co1.number_input("O 1.5", 1.25); o25 = co2.number_input("O 2.5", 1.85); o35 = co3.number_input("O 3.5", 3.20)
    
    # UNDER LADDER
    st.caption("GOALS: UNDER")
    cu0, cu1, cu2, cu3 = st.columns(4)
    u05 = cu0.number_input("U 0.5", 9.50); u15 = cu1.number_input("U 1.5", 3.75); u25 = cu2.number_input("U 2.5", 1.95); u35 = cu3.number_input("U 3.5", 1.35)
    
    # SPECIALS
    st.caption("SPECIALS & HANDICAPS")
    cs1, cs2 = st.columns(2)
    m_ob_y = cs1.number_input("BTTS YES", 1.80); m_ob_n = cs2.number_input("BTTS NO", 2.00)
    
    ch1, ch2 = st.columns(2)
    m_ah0_h = ch1.number_input("AH 0.0 (H)", 1.50); m_ah0_a = ch2.number_input("AH 0.0 (A)", 2.50)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTE QUANTUM SCAN")
    st.button("🗑️ RESET ENGINE", on_click=reset)

# --- RESULTS INTERFACE ---
if not run:
    st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.3;'><h1>SYSTEM STANDBY</h1><p>AWAITING COCKPIT COMMANDS</p></div>", unsafe_allow_html=True)
else:
    # MOTOR DE SIMULAÇÃO (1M ITERAÇÕES)
    lh, la = max(0.01, ((hgf/5)*(aga/5))**0.5), max(0.01, ((agf/5)*(hga/5))**0.5)
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)
    p_ah0h, p_ah0a = ph/(ph+pa), pa/(ph+pa)

    # CONSTRUÇÃO DA LISTA DE MERCADOS COMPLETA
    mkts = [
        ("WIN: "+h_n, ph, m1), ("WIN: "+a_n, pa, m2), ("DRAW (X)", px, mx),
        ("OVER 0.5", np.mean(stot>0.5), o05), ("OVER 1.5", np.mean(stot>1.5), o15), 
        ("OVER 2.5", np.mean(stot>2.5), o25), ("OVER 3.5", np.mean(stot>3.5), o35),
        ("UNDER 0.5", np.mean(stot<0.5), u05), ("UNDER 1.5", np.mean(stot<1.5), u15), 
        ("UNDER 2.5", np.mean(stot<2.5), u25), ("UNDER 3.5", np.mean(stot<3.5), u35),
        ("BTTS: YES", np.mean((sim_h>0)&(sim_a>0)), m_ob_y), ("BTTS: NO", 1-np.mean((sim_h>0)&(sim_a>0)), m_ob_n),
        ("AH 0.0: "+h_n, p_ah0h, m_ah0_h), ("AH 0.0: "+a_n, p_ah0a, m_ah0_a)
    ]
    
    best = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts], key=lambda x: x[3], reverse=True)[0]

    # UI DE RESULTADOS (DESIGN VALIDADO)
    st.markdown(f"<h1 style='letter-spacing:-2px; margin:0;'>{h_n} vs {a_n}</h1>", unsafe_allow_html=True)
    
    c_adv, c_note = st.columns([1.2, 0.8])
    with c_adv:
        st.markdown(f"""<div class="advisor-premium">
            <p style="color:#64748B; margin:0; font-size:0.7rem; font-weight:800; letter-spacing:3px;">MASTER ALPHA SIGNAL</p>
            <h1 style="color:white; margin:5px 0; font-size:3rem;">{best[0]}</h1>
            <p style="color:#00FF88; font-size:1.3rem; margin:0; font-weight:800;">EDGE: {best[3]:+.1%} | PROB: {best[1]:.1%}</p>
        </div>""", unsafe_allow_html=True)

    # MATRIX INFINITA (Ajuste dinâmico para todos os mercados)
    df = pd.DataFrame(mkts, columns=["Market", "Prob", "Odd"])
    df["Fair"] = 1/df["Prob"]; df["Edge"] = (df["Prob"] * df["Odd"]) - 1
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>MARKET</b>', '<b>CONFIDENCE</b>', '<b>FAIR</b>', '<b>BOOKIE</b>', '<b>EDGE</b>'],
                    fill_color='#0A0A0A', align='center', font=dict(color='#64748B', size=11)),
        cells=dict(values=[df.Market, df.Prob.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), 
                           df.Odd.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                   fill_color=[['rgba(0, 255, 136, 0.15)' if e > 0.1 else 'rgba(255,255,255,0.02)' for e in df.Edge]],
                   align='center', font=dict(color='white', size=13), height=35)
    )])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', height=(len(mkts)*35+50))
    st.plotly_chart(fig, use_container_width=True)

    # ANALYTICS
    st.markdown("---")
    c1, c2 = st.columns([1.3, 0.7])
    with c1:
        xr = list(range(7))
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig_p.update_layout(title="POISSON FLOW", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
        st.plotly_chart(fig_p, use_container_width=True)
    with c2:
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        st.write("**TOP PROBABLE SCORES**")
        for j in range(2, -1, -1):
            st.metric(f"{idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
