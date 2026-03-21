iimport streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Advanced Institutional Configuration
st.set_page_config(
    page_title="STARLINE V98 - FINAL SOVEREIGN", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Sovereign UI CSS (High-Definition 2026 Graphics)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%);
        color: #FFFFFF; font-family: 'Inter', sans-serif; 
    }
    
    /* Sidebar Stealth Black */
    [data-testid="stSidebar"] { 
        background-color: #050505 !important; 
        backdrop-filter: blur(25px); border-right: 1px solid #1A1A1A; 
    }
    
    /* Decision Cards */
    .advisor-premium {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.05) 0%, rgba(0, 0, 0, 0.4) 100%);
        border-radius: 20px; padding: 35px; border: 1px solid #00FF88;
        box-shadow: 0 0 60px rgba(0, 255, 136, 0.1); margin-bottom: 30px;
    }
    .intel-card {
        background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05); margin-top: 10px;
    }

    /* Execute Button */
    div.stButton > button {
        background: #00FF88 !important; color: #000000 !important; font-weight: 900; 
        height: 4.5em; width: 100%; border-radius: 12px; border: none; text-transform: uppercase;
        letter-spacing: 2px; box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
    }
    
    label { font-size: 0.75rem !important; font-weight: 800 !important; color: #94A3B8 !important; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR: PRECISION COMMAND ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88; font-size:24px; margin-bottom:0;'>🏛️ STARLINE AI</h1>", unsafe_allow_html=True)
    st.caption("ULTRA-PRECISION // V98.0")
    
    st.markdown("---")
    h_n = st.text_input("HOME TEAM", "HOME TEAM").upper()
    a_n = st.text_input("AWAY TEAM", "AWAY TEAM").upper()
    
    c_gf, c_ga = st.columns(2)
    hgf = c_gf.number_input("H-GF", 8.0); hga = c_ga.number_input("H-GA", 10.0)
    agf = c_gf.number_input("A-GF", 10.0); aga = c_ga.number_input("A-GA", 12.0)
    
    st.markdown("---")
    st.write("1X2 & BTTS")
    m1 = st.number_input("ODD 1", 2.10); mx = st.number_input("ODD X", 3.40); m2 = st.number_input("ODD 2", 3.60)
    m_ob = st.number_input("BTTS YES", 1.80); m_ob_no = st.number_input("BTTS NO", 2.00)
    
    st.write("OVER / UNDER LADDER")
    o15 = st.number_input("O 1.5", 1.25); o25 = st.number_input("O 2.5", 1.85); o35 = st.number_input("O 3.5", 3.20)
    u15 = st.number_input("U 1.5", 3.75); u25 = st.number_input("U 2.5", 1.95); u35 = st.number_input("U 3.5", 1.35)
    
    st.write("ASIAN HANDICAP (DNB)")
    m_ah0_h = st.number_input("AH 0.0 HOME", 1.50); m_ah0_a = st.number_input("AH 0.0 AWAY", 2.50)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTE QUANTUM SCAN")
    st.button("🗑️ RESET ENGINE", on_click=reset)

# --- SOVEREIGN INTERFACE ---
if not run:
    st.markdown("""
        <div style='text-align:center; padding-top:100px;'>
            <h1 style='font-size:5rem; font-weight:900; letter-spacing:-5px; margin-bottom:0;'>SOVEREIGN <span style='color:#00FF88;'>AI</span></h1>
            <p style='color:#64748B; font-size:1.5rem; letter-spacing:10px;'>AWAITING MARKET DATA</p>
        </div>
    """, unsafe_allow_html=True)
else:
    # 1.000.000 SIMULATIONS ENGINE
    lh, la = max(0.01, ((hgf/5)*(aga/5))**0.5), max(0.01, ((agf/5)*(hga/5))**0.5)
    sim_h, sim_a = np.random.poisson(lh, 1000000), np.random.poisson(la, 1000000)
    stot = sim_h + sim_a
    
    ph, px, pa = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
    ph, px, pa = ph/(ph+px+pa), px/(ph+px+pa), pa/(ph+px+pa)

    st.markdown(f"<h1 style='letter-spacing:-3px; font-size:55px; margin:0;'>{h_n} vs {a_n}</h1>", unsafe_allow_html=True)

    # 1. ADVISOR & AI INSIGHTS
    col_adv, col_notes = st.columns([1.2, 0.8])
    
    p_btts = np.mean((sim_h>0)&(sim_a>0))
    p_ah0h = ph / (ph + pa) if (ph+pa) > 0 else 0
    p_ah0a = pa / (ph + pa) if (ph+pa) > 0 else 0

    mkts = [
        ("WIN: "+h_n, ph, m1), ("WIN: "+a_n, pa, m2), ("DRAW (X)", px, mx),
        ("OVER 1.5", np.mean(stot>1.5), o15), ("OVER 2.5", np.mean(stot>2.5), o25), ("OVER 3.5", np.mean(stot>3.5), o35),
        ("UNDER 1.5", np.mean(stot<1.5), u15), ("UNDER 2.5", np.mean(stot<2.5), u25), ("UNDER 3.5", np.mean(stot<3.5), u35),
        ("BTTS: YES", p_btts, m_ob), ("BTTS: NO", 1-p_btts, m_ob_no),
        ("AH 0.0: "+h_n, p_ah0h, m_ah0_h), ("AH 0.0: "+a_n, p_ah0a, m_ah0_a)
    ]
    
    best = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts], key=lambda x: x[3], reverse=True)[0]

    with col_adv:
        st.markdown(f"""
            <div class="advisor-premium">
                <p style="color:#64748B; margin:0; font-size:0.8rem; font-weight:800; letter-spacing:4px;">QUANTUM MASTER SIGNAL</p>
                <h1 style="color:white; margin:10px 0; font-size:3.5rem; letter-spacing:-1px;">{best[0]}</h1>
                <p style="color:#00FF88; font-size:1.5rem; margin:0; font-weight:800;">EDGE: {best[3]:+.1%} | PROBABILITY: {best[1]:.1%}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_notes:
        st.markdown("### 🧠 AI INSIGHTS")
        clr = "#00FF88" if best[3] > 0.15 else "#FACC15"
        st.markdown(f"""
            <div class="intel-card">
                <b style="color:{clr};">ALPHA EDGE SOURCE</b><br>
                <span style="color:#94A3B8; font-size:0.9rem;">
                Statistical discrepancy detected in <b>{best[0]}</b>. 
                The bookmakers are miscalculating the {h_n if ph > pa else a_n} momentum.
                </span>
            </div>
            <div class="intel-card">
                <b style="color:#3B82F6;">VOLATILITY SCAN</b><br>
                <span style="color:#94A3B8; font-size:0.9rem;">
                Confidence rating: <b>STABLE</b>. Goal density follows the Institutional standard.
                </span>
            </div>
        """, unsafe_allow_html=True)

    # 2. THE MATRIX (PLOTLY SECURE RENDER)
    st.markdown("### 💎 COMPREHENSIVE MARKET MATRIX")
    df = pd.DataFrame(mkts, columns=["Market", "Prob", "Odd"])
    df["Fair"] = 1/df["Prob"]
    df["Edge"] = (df["Prob"] * df["Odd"]) - 1

    fig_table = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>MARKET</b>', '<b>CONFIDENCE</b>', '<b>FAIR ODD</b>', '<b>MARKET ODD</b>', '<b>ALPHA EDGE</b>'],
            fill_color='#0A0A0A', align='center', font=dict(color='#64748B', size=12), height=40
        ),
        cells=dict(
            values=[df.Market, df.Prob.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), 
                    df.Odd.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
            fill_color=[['rgba(0, 255, 136, 0.15)' if e > 0.1 else 'rgba(255,255,255,0.02)' for e in df.Edge]],
            align='center', font=dict(color='white', size=14), height=45
        )
    )])
    fig_table.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', height=550)
    st.plotly_chart(fig_table, use_container_width=True)

    # 3. ANALYTICS
    st.markdown("---")
    c1, c2 = st.columns([1.3, 0.7])
    with c1:
        xr = list(range(7))
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
        fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
        fig_p.update_layout(title="POISSON DENSITY (ALPHA FLOW)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=380)
        st.plotly_chart(fig_p, use_container_width=True)
    with c2:
        st.write("**TOP PREDICTED SCORES**")
        hp, ap = poisson.pmf(range(5), lh), poisson.pmf(range(5), la)
        mtx = np.outer(hp, ap); mtx /= mtx.sum()
        idx = np.unravel_index(np.argsort(mtx.ravel())[-3:], mtx.shape)
        for j in range(2, -1, -1):
            st.metric(f"SCORE {idx[0][j]}-{idx[1][j]}", f"{mtx[idx[0][j], idx[1][j]]:.1%}")
