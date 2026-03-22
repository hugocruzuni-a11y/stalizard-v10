import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO DE DESIGN ---
st.set_page_config(page_title="ORACLE V140 - SIMPLIFIED", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #070A11; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1E293B !important; }
    
    .pro-card { background: #111827; border-radius: 12px; padding: 25px; border: 1px solid #1E293B; border-left: 6px solid #00FF88; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .bet-name { font-size: 2.2rem; font-weight: 800; color: #FFFFFF; margin: 0; line-height: 1.1; letter-spacing: -1px; }
    .edge-value { font-family: 'JetBrains Mono'; font-size: 1.4rem; color: #00FF88; font-weight: 700; }
    
    .ia-insight-card { background: rgba(0, 255, 136, 0.03); border-radius: 10px; padding: 20px; border: 1px dashed rgba(0, 255, 136, 0.3); margin-top: 15px; font-size: 0.95rem; line-height: 1.5; }
    .help-card { background: #1E293B; border-radius: 10px; padding: 15px; border-left: 4px solid #3B82F6; margin-bottom: 15px; }
    
    .stNumberInput label, .stSelectbox label, .stSlider label { font-size: 0.7rem !important; color: #94A3B8 !important; font-weight: 700; text-transform: uppercase; }
    div.stButton > button { background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; font-weight: 800 !important; height: 3.5rem !important; border-radius: 8px !important; border: none !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR LÓGICO (Fica igual, a matemática não muda) ---
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
    for x in range(2):
        for y in range(2):
            if x==0 and y==0: prob_mtx[x,y] *= (1-lh*la*rho)
            elif x==0 and y==1: prob_mtx[x,y] *= (1+lh*rho)
            elif x==1 and y==0: prob_mtx[x,y] *= (1+la*rho)
            elif x==1 and y==1: prob_mtx[x,y] *= (1-rho)
    prob_mtx[0,0] *= zip_factor
    prob_mtx /= prob_mtx.sum() 
    
    ph, px, pa = np.tril(prob_mtx, -1).sum(), np.trace(prob_mtx), np.triu(prob_mtx, 1).sum()
    h_win_1 = np.trace(prob_mtx, offset=-1); a_win_1 = np.trace(prob_mtx, offset=1)
    
    ah0_h = ph / (ph + pa) if (ph + pa) > 0 else 0
    ah_m1_h = (ph - h_win_1) / (1 - h_win_1) if (1 - h_win_1) > 0 else 0
    ah_m15_h = np.tril(prob_mtx, -2).sum()
    ah_p05_h = ph + px
    ah_p15_h = 1 - np.triu(prob_mtx, 2).sum()
    
    goals_sum = np.add.outer(np.arange(max_g), np.arange(max_g))
    o15 = prob_mtx[goals_sum > 1.5].sum(); u15 = 1 - o15
    o25 = prob_mtx[goals_sum > 2.5].sum(); u25 = 1 - o25
    o35 = prob_mtx[goals_sum > 3.5].sum(); u35 = 1 - o35
    
    btts_no = prob_mtx[0, :].sum() + prob_mtx[:, 0].sum() - prob_mtx[0,0]
    btts_yes = 1 - btts_no
    
    return {
        "Vencedor: Casa": ph, "Empate (X)": px, "Vencedor: Fora": pa,
        "Handicap +1.5 (Casa)": ah_p15_h, "Handicap +0.5 (Casa)": ah_p05_h, "Empate Anula (Casa)": ah0_h, "Handicap -0.5 (Casa)": ph, "Handicap -1.0 (Casa)": ah_m1_h, "Handicap -1.5 (Casa)": ah_m15_h,
        "Mais de 1.5 Golos": o15, "Menos de 1.5 Golos": u15, "Mais de 2.5 Golos": o25, "Menos de 2.5 Golos": u25, "Mais de 3.5 Golos": o35, "Menos de 3.5 Golos": u35,
        "Ambas Marcam (Sim)": btts_yes, "Ambas Marcam (Não)": btts_no
    }, prob_mtx

# --- 3. SIDEBAR (CONTROLO SIMPLIFICADO) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; margin:0;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    
    with st.expander("💸 O TEU DINHEIRO", expanded=True):
        bankroll = st.number_input("Quanto tens na Banca? (€)", value=100.0, step=10.0)
        st.markdown("<p style='font-size:0.7rem; color:#94A3B8;'>O modelo vai calcular quanto deves apostar para não ires à falência.</p>", unsafe_allow_html=True)
        k_mult = 0.50 # Fixo em Half-Kelly para simplificar (o melhor para a maioria)

    with st.expander("⚽ ESCOLHER O JOGO", expanded=True):
        l_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94, "Champions League": 2}
        ln = st.selectbox("Liga", list(l_map.keys()))
        
        fix = requests.get(f"https://{api_host}/fixtures", headers=headers, params={"date": date.today().strftime('%Y-%m-%d'), "league": l_map[ln], "season": "2025"}).json().get('response', [])
        if fix:
            m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
            m_display = st.selectbox("Jogo", list(m_map.keys()))
            m_sel = next(f for f in fix if f['fixture']['id'] == m_map[m_display])
        else: m_sel = None

    with st.expander("📝 INSERIR AS ODDS DA TUA CASA DE APOSTAS", expanded=False):
        st.write("Vencedor")
        c1, cx, c2 = st.columns(3)
        o_1 = c1.number_input("Casa (1)", value=2.00); o_x = cx.number_input("Empate (X)", value=3.40); o_2 = c2.number_input("Fora (2)", value=3.50)
        
        st.write("Vantagens (Handicaps para a Equipa da Casa)")
        c3, c4 = st.columns(2)
        o_ah0 = c3.number_input("Empate Anula", value=1.55); o_ahm1 = c4.number_input("Handicap -1.0", value=3.20)
        o_ahp05 = c3.number_input("Handicap +0.5", value=1.00); o_ahm15 = c4.number_input("Handicap -1.5", value=1.00)
        
        st.write("Golos Totais no Jogo")
        c5, c6 = st.columns(2)
        o_o25 = c5.number_input("Mais de 2.5", value=1.90); o_u25 = c6.number_input("Menos de 2.5", value=1.90)
        o_o15 = c5.number_input("Mais de 1.5", value=1.00); o_o35 = c6.number_input("Mais de 3.5", value=1.00)
        
        st.write("Ambas as Equipas Marcam?")
        c7, c8 = st.columns(2)
        o_btts_y = c7.number_input("Sim", value=1.85); o_btts_n = c8.number_input("Não", value=1.95)
        
    execute = st.button("🔍 PROCURAR DINHEIRO FÁCIL")

# --- 4. RESULTADOS (INTERFACE À PROVA DE TOTÓS) ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:150px;'><h1 style='opacity:0.2;'>ORACLE V140</h1><p style='color:#64748B;'>Escolhe o jogo e insere as odds no menu lateral.<br>O robô fará a matemática por ti.</p></div>", unsafe_allow_html=True)
else:
    s = get_pro_stats(m_sel['teams']['home']['id'], l_map[ln])
    lh, la = (s['h_f']*s['a_a'])**0.5, (s['a_f']*s['h_a'])**0.5
    res, mtx = run_master_math(lh, la, -0.11, 0.12, 1.05)
    
    st.markdown(f"<h2 style='margin-bottom:0; font-size:3.5rem;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#475569; font-weight:300;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h2>", unsafe_allow_html=True)

    col_res, col_chart = st.columns([1.1, 0.9])

    all_mkts = [
        ("Vencedor: Casa", res["Vencedor: Casa"], o_1), ("Empate (X)", res["Empate (X)"], o_x), ("Vencedor: Fora", res["Vencedor: Fora"], o_2),
        ("Handicap +0.5 (Casa)", res["Handicap +0.5 (Casa)"], o_ahp05), ("Empate Anula (Casa)", res["Empate Anula (Casa)"], o_ah0), 
        ("Handicap -1.0 (Casa)", res["Handicap -1.0 (Casa)"], o_ahm1), ("Handicap -1.5 (Casa)", res["Handicap -1.5 (Casa)"], o_ahm15),
        ("Mais de 1.5 Golos", res["Mais de 1.5 Golos"], o_o15), ("Mais de 2.5 Golos", res["Mais de 2.5 Golos"], o_o25), 
        ("Menos de 2.5 Golos", res["Menos de 2.5 Golos"], o_u25), ("Mais de 3.5 Golos", res["Mais de 3.5 Golos"], o_o35),
        ("Ambas Marcam: Sim", res["Ambas Marcam (Sim)"], o_btts_y), ("Ambas Marcam: Não", res["Ambas Marcam (Não)"], o_btts_n)
    ]
    
    valid_mkts = [(n,p,b,(p*b)-1) for n,p,b in all_mkts if b > 1.01]
    
    if len(valid_mkts) > 0:
        best = sorted(valid_mkts, key=lambda x: x[3], reverse=True)[0]
        edge = best[3]; kelly = max(0, (edge/(best[2]-1)) * k_mult)
        color = "#00FF88" if edge > 0.08 else "#FFD700" if edge > 0.02 else "#EF4444"
        
        # A MÁGICA DO TEXTO SIMPLES AQUI
        odd_justa = 1/best[1]
        
        with col_res:
            st.markdown(f"""<div class="pro-card" style="border-left-color: {color};">
                <span style="color:#64748B; font-size:0.75rem; font-weight:800;">A MELHOR APOSTA DETETADA</span>
                <p class="bet-name">{best[0]}</p>
                <div style="display:flex; gap:20px; margin:15px 0;">
                    <div><span style="color:#64748B; font-size:0.7rem;">O ERRO DA CASA (VANTAGEM)</span><br><span class="edge-value" style="color:{color};">{edge:+.1%}</span></div>
                    <div><span style="color:#64748B; font-size:0.7rem;">VALOR APOSTAR (SEGURO)</span><br><b style="font-size:1.4rem;">{bankroll*kelly:.2f}€</b></div>
                </div>
                
                <div class="ia-insight-card">
                    <b>🗣️ O QUE ISTO SIGNIFICA (EM PORTUGUÊS CLARO):</b><br>
                    A casa de apostas está a oferecer uma odd de <b>{best[2]}</b>. Isso significa que eles acham que isto é mais difícil de acontecer do que realmente é.<br><br>
                    O nosso robô fez as contas a todos os golos, e a Odd Justa (verdadeira) deveria ser apenas <b>{odd_justa:.2f}</b>.<br><br>
                    Como a casa está a pagar <b>{best[2]}</b> quando devia pagar <b>{odd_justa:.2f}</b>, eles estão a dar-te dinheiro grátis a longo prazo. Apostar os {bankroll*kelly:.2f}€ recomendados protege a tua banca enquanto aproveitas este erro.
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        with col_res: st.warning("Por favor, insira as odds no menu lateral esquerdo.")

    with col_chart:
        st.markdown(f"""
        <div class="help-card">
            <b>📚 O GUIA RÁPIDO DO APOSTADOR</b><br>
            <span style="font-size:0.8rem; color:#94A3B8;">
            <b>• Vantagem (Edge):</b> O quão "cega" está a casa de apostas. +10% de vantagem significa que ficas com mais 10% de lucro do que a matemática normal permitiria.<br>
            <b>• Odd Justa:</b> O preço real da aposta sem a margem de lucro da casa. Se a casa oferece MAIS do que a odd justa, tens uma aposta de valor.<br>
            <b>• Handicap -1.0:</b> A equipa tem de ganhar por 2 ou mais golos de diferença. Se ganhar só por 1 golo, o teu dinheiro é devolvido.
            </span>
        </div>
        """, unsafe_allow_html=True)

        xr = np.arange(7)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name="Ataque Casa", fill='tozeroy', line_color='#00FF88', line_width=3))
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name="Ataque Fora", fill='tozeroy', line_color='#3B82F6', line_width=3))
        fig.update_layout(title="Gráfico de Probabilidade de Golos", title_font_color="#64748B", height=200, margin=dict(l=0,r=0,t=30,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)

    # TABELA DINÂMICA SIMPLIFICADA
    st.markdown("### 📋 TODAS AS APOSTAS AVALIADAS")
    
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
            header=dict(values=['A TUA APOSTA', 'A NOSSA CERTEZA', 'ODD REAL (CORRETA)', 'ODD DA CASA (O ERRO)', 'VANTAGEM (LUCRO EXTRA)'], fill_color='#020617', align='left', font=dict(color='#94A3B8', size=11), height=40),
            cells=dict(values=[df.Mercado, df.P.map('{:.1%}'.format), df.Fair.map('{:.2f}'.format), df.B.map('{:.2f}'.format), df.Edge.map('{:+.1%}'.format)],
                       fill_color=[[get_heatmap(e) for e in df["Edge"]]], align='left', font=dict(color='white', size=13), height=35)
        )])
        fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=(len(df)*35)+60, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_t, use_container_width=True)
