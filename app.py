import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go

# 1. Advanced Institutional Configuration
st.set_page_config(
    page_title="STARLINE V140 - PURE SOVEREIGN", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Sovereign Elite CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;600;700&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #000000 95%);
        color: #FFFFFF; font-family: 'Inter', sans-serif; 
    }
    
    [data-testid="stSidebar"] { 
        background-color: rgba(255, 255, 255, 0.01) !important; 
        backdrop-filter: blur(45px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    [data-testid="stSidebar"] .stNumberInput input, 
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.96) !important;
        border: 1px solid rgba(0, 255, 136, 0.2) !important;
        color: #000000 !important; 
        font-family: 'Inter', sans-serif !important;
        font-weight: 300 !important; 
        font-size: 0.85rem !important;
        border-radius: 4px !important;
    }

    .advisor-seal {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
        border-radius: 12px; padding: 15px 25px; border: 1px solid rgba(0, 255, 136, 0.4);
        margin-bottom: 20px; display: inline-block;
    }
    
    .risk-card {
        background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 15px 25px;
        border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px;
    }

    .advisor-title { color: white; font-size: 1.6rem; font-weight: 700; margin: 0; letter-spacing: -1px; }
    .advisor-subtitle { color: #00FF88; font-size: 0.85rem; font-weight: 400; margin: 0; letter-spacing: 1px; }

    .intel-card {
        background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05); font-weight: 300; font-size: 0.85rem;
        margin-bottom: 10px;
    }

    label { font-size: 0.62rem !important; font-weight: 600 !important; color: #64748B !important; text-transform: uppercase; letter-spacing: 1.2px; }

    div.stButton > button {
        background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important;
        color: #000000 !important; font-weight: 700; 
        height: 4em; width: 100%; border-radius: 6px; border: none; text-transform: uppercase;
        letter-spacing: 2px; box-shadow: 0 10px 25px rgba(0, 255, 136, 0.1);
    }
    
    hr { border-top: 1px solid rgba(255, 255, 255, 0.03) !important; margin: 15px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

def reset():
    for key in list(st.session_state.keys()): del st.session_state[key]

# --- SIDEBAR COCKPIT ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; font-size:22px; font-weight:700;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='color:#475569; font-size:0.65rem; font-weight:700;'>01 // CONTEXT</p>", unsafe_allow_html=True)
    comp_type = st.selectbox("MATCH TYPE", ["LEAGUE / REGULAR", "CHAMPIONS / ELIMINATION"])
    h_score_1st, a_score_1st = 0, 0
    leg_type = "1st Leg"
    if comp_type == "CHAMPIONS / ELIMINATION":
        leg_type = st.radio("LEG SELECTION", ["1st Leg", "2nd Leg"])
        if leg_type == "2nd Leg":
            c1, c2 = st.columns(2)
            h_score_1st = c1.number_input("H-1st Leg", value=0, step=1, format="%d")
            a_score_1st = c2.number_input("A-1st Leg", value=0, step=1, format="%d")

    st.markdown("<hr>", unsafe_allow_html=True)
    h_n = st.text_input("HOME TEAM", "VILLARREAL").upper()
    a_n = st.text_input("AWAY TEAM", "REAL SOCIEDAD").upper()
    
    st.markdown("<hr>", unsafe_allow_html=True)
    col_gf, col_ga = st.columns(2)
    hgf = col_gf.number_input("H-GF (Last 5)", value=9, step=1, format="%d")
    hga = col_gf.number_input("H-GA (Last 5)", value=7, step=1, format="%d")
    agf = col_ga.number_input("A-GF (Last 5)", value=12, step=1, format="%d")
    aga = col_ga.number_input("A-GA (Last 5)", value=10, step=1, format="%d")

    st.markdown("<hr>", unsafe_allow_html=True)
    c1, cx, c2 = st.columns(3)
    m1 = c1.number_input("1", value=1.90); mx = cx.number_input("X", value=4.00); m2 = c2.number_input("2", value=3.35)
    
    st.write("GOALS LADDER")
    o15_i = st.number_input("O1.5", value=1.16); o25_i = st.number_input("O2.5", value=1.33); o35_i = st.number_input("O3.5", value=1.78)
    u15_i = st.number_input("U1.5", value=4.50); u25_i = st.number_input("U2.5", value=2.65); u35_i = st.number_input("U3.5", value=1.60)
    
    st.write("SPECIALS")
    m_ob = st.number_input("BTTS (YES)", value=1.32)
    ah_h = st.number_input("AH 0.0 (H)", value=1.33); ah_a = st.number_input("AH 0.0 (A)", value=1.85)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🚀 EXECUTE ALPHA SCAN")
    st.button("🗑️ RESET ENGINE", on_click=reset)

# --- RESULTS INTERFACE ---
if not run:
    st.markdown("<div style='text-align:center; padding-top:150px; opacity:0.1;'><h1>ORACLE V140</h1><p>PURE SOVEREIGN BUILD</p></div>", unsafe_allow_html=True)
else:
    # --- MATH ENGINE (EXACT PROBABILITY MATRIX) ---
    
    # 1. Cálculo Otimizado dos Lambdas (Expectativa de Golos)
    avg_hgf, avg_hga = hgf / 5.0, hga / 5.0
    avg_agf, avg_aga = agf / 5.0, aga / 5.0

    # Força de Ataque x Força de Defesa + Fator Casa (Home Advantage ~10%)
    lh = max(0.01, (avg_hgf * avg_aga)) * 1.10
    la = max(0.01, (avg_agf * avg_hga)) * 0.90

    # Lógica de Eliminatórias
    if comp_type == "CHAMPIONS / ELIMINATION" and leg_type == "2nd Leg":
        diff = h_score_1st - a_score_1st
        if diff < 0: lh *= (1 + abs(diff) * 0.12)
        elif diff > 0: la *= (1 + abs(diff) * 0.12)

    # 2. Construção da Matriz Exata de Poisson (0 a 9 golos)
    max_goals = 10
    hp = poisson.pmf(np.arange(max_goals), lh)
    ap = poisson.pmf(np.arange(max_goals), la)
    
    # Produto externo gera a matriz de todos os resultados possíveis
    prob_matrix = np.outer(hp, ap)
    prob_matrix /= prob_matrix.sum() # Normalização de segurança

    # 3. Cálculo Exato dos Mercados Principais (1X2)
    ph = np.tril(prob_matrix, -1).sum() # Vitória Casa 
    px = np.trace(prob_matrix)          # Empate 
    pa = np.triu(prob_matrix, 1).sum()  # Vitória Fora 

    # 4. Cálculo Exato de Golos (Over/Under)
    goals_sum_matrix = np.add.outer(np.arange(max_goals), np.arange(max_goals))
    
    o15_prob = prob_matrix[goals_sum_matrix > 1.5].sum()
    o25_prob = prob_matrix[goals_sum_matrix > 2.5].sum()
    o35_prob = prob_matrix[goals_sum_matrix > 3.5].sum()
    
    u15_prob = prob_matrix[goals_sum_matrix < 1.5].sum()
    u25_prob = prob_matrix[goals_sum_matrix < 2.5].sum()
    u35_prob = prob_matrix[goals_sum_matrix < 3.5].sum()

    # 5. Mercados Especiais
    btts_prob = prob_matrix[1:, 1:].sum() 
    ah_h_prob = ph / (ph + pa) if (ph + pa) > 0 else 0 
    ah_a_prob = pa / (ph + pa) if (ph + pa) > 0 else 0 

    # Realistic Confidence
    cv = np.sqrt(lh + la) / (lh + la) if (lh + la) > 0 else 1
    conf_score = max(50.0, min(99.9, 100 * (1 - (cv / 2))))

    st.markdown(f"<h1 style='letter-spacing:-3px; font-size:55px; margin:0; font-weight:700;'>{h_n} <span style='color:#00FF88; font-weight:300;'>vs</span> {a_n}</h1>", unsafe_allow_html=True)
    
    col_res, col_risk = st.columns([1.1, 0.9])
    
    # 6. Atualização da Lista de Mercados 
    mkts = [
        ("WIN: "+h_n, ph, m1), ("WIN: "+a_n, pa, m2), ("DRAW (X)", px, mx),
        ("O1.5 GOALS", o15_prob, o15_i), ("O2.5 GOALS", o25_prob, o25_i), ("O3.5 GOALS", o35_prob, o35_i),
        ("U1.5 GOALS", u15_prob, u15_i), ("U2.5 GOALS", u25_prob, u25_i), ("U3.5 GOALS", u35_prob, u35_i),
        ("BTTS (YES)", btts_prob, m_ob),
        ("AH 0.0: "+h_n, ah_h_prob, ah_h), ("AH 0.0: "+a_n, ah_a_prob, ah_a)
    ]
    best = sorted([(n, p, b, (p*b)-1) for n, p, b in mkts], key=lambda x: x[3], reverse=True)[0]
    kelly = max(0, (best[3] / (best[2] - 1)) * 0.5)

    with col_res:
        st.markdown(f"""<div class="advisor-seal"><h1 class="advisor-title">{best[0]}</h1><p class="advisor-subtitle">ALPHA EDGE: {best[3]:+.1%} | STAKE: {kelly:.1%}</p></div>""", unsafe_allow_html=True)
    with col_risk:
        st.markdown(f"""<div class="risk-card"><b style="color:#00FF88; letter-spacing:1px; font-size:0.65rem;">🛡️ STATISTICAL CONFIDENCE</b><h2 style="margin:5px 0; font-size:2rem; font-weight:700;">{conf_score:.1f}%</h2><p style="color:#64748B; font-size:0.75rem; margin:0;">HALF-KELLY MODEL ACTIVE</p></div>""", unsafe_allow_html=True)

    # IA TACTICS
    c_ins1, c_ins2 = st.columns(2)
    with c_ins1:
        st.markdown(f"""<div class="intel-card"><b style="color:#00FF88;">🧠 AI TACTICAL ANALYSIS</b><br>
        <span style="color:#CBD5E1; line-height:1.6;">Trend: <b>{"OPEN ATTACK" if (lh+la) > 2.6 else "DEFENSIVE BATTLE"}</b><br>
        Volatility: <b>{np.sqrt(lh+la):.2f}</b> | Signal: <b>Bivariate Corrected</b></span></div>""", unsafe_allow_html=True)
    with c_ins2:
        # Usa a matriz exata calculada acima para encontrar os resultados mais prováveis
        idx = np.unravel_index(np.argsort(prob_matrix.ravel())[-3:], prob_matrix.shape)
        st.markdown(f"""<div class="intel-card"><b style="color:#00FF88;">🎯 TOP SCORE PROBABILITIES</b><br>
        <span style="color:#CBD5E1;">1. {idx[0][2]}-{idx[1][2]} ({prob_matrix[idx[0][2], idx[1][2]]:.1%}) | 2. {idx[0][1]}-{idx[1][1]} ({prob_matrix[idx[0][1], idx[1][1]]:.1%})</span></div>""", unsafe_allow_html=True)

    # MATRIX WITH HEATMAP (FF8C00 ORANGE)
    df = pd.DataFrame(mkts, columns=["Market", "Prob", "Odd"])
    df["Fair"] = 1/df["Prob"]; df["Edge"] = (df["Prob"] * df["Odd"]) - 1
    row_colors = [['rgba(0, 255, 136, 0.15)' if e > 0.10 else 'rgba(255, 140, 0, 0.35)' if e > 0.05 else 'rgba(255, 255, 255, 0.01)' for e in df["Edge"]]]

    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>MARKET</b>', '<b>PROB</b>', '<b>FAIR</b>', '<b>BOOKIE</b>', '<b>EDGE</b>'], fill_color='#0A0A0A', align='center', font=dict(color='#475569', size=11), height=45),
        cells=dict(values=[df.Market, df.Prob.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), df.Odd.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                   fill_color=row_colors, align='center', font=dict(color='white', size=13), height=40))])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', height=(len(mkts)*42+60))
    st.plotly_chart(fig, use_container_width=True)

    # GRAPH & EXPLANATION
    xr = list(range(7))
    fig_p = go.Figure()
    fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, lh) for i in xr], name=h_n, fill='tozeroy', line_color='#00FF88', line_width=4))
    fig_p.add_trace(go.Scatter(x=xr, y=[poisson.pmf(i, la) for i in xr], name=a_n, fill='tozeroy', line_color='#3B82F6', line_width=4))
    fig_p.update_layout(title="POISSON DENSITY OVERLAP", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
    st.plotly_chart(fig_p, use_container_width=True)
    
    st.markdown(f"""<div class="intel-card"><b style="color:#00FF88;">🌐 ORACLE INSIGHTS // GRÁFICO:</b><br><span style="color:#CBD5E1; font-size:0.85rem; line-height:1.5;">O gráfico cruza as densidades ofensivas das duas equipas. A zona de interseção revela o equilíbrio estatístico. Picos desalinhados indicam vantagem táctica clara de um dos lados.</span></div>""", unsafe_allow_html=True)
