import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date
import textwrap

# --- 1. CONFIGURAÇÃO DE DESIGN (COMPACTO E PREMIUM) ---
st.set_page_config(page_title="ORACLE V140 - ELITE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    .stApp { background-color: #070A11; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1E293B !important; }
    
    /* Cartão Principal mais compacto */
    .pro-card { background: #0B0F19; border-radius: 12px; padding: 20px; border: 1px solid #1E293B; border-left: 5px solid #00FF88; margin-bottom: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
    .bet-name { font-size: 1.8rem; font-weight: 800; color: #FFFFFF; margin: 0; line-height: 1.2; letter-spacing: -0.5px; }
    .edge-value { font-family: 'JetBrains Mono'; font-size: 1.3rem; color: #00FF88; font-weight: 800; }
    
    .ia-insight-card { background: rgba(0, 255, 136, 0.05); border-radius: 8px; padding: 12px 15px; border-left: 3px solid #00FF88; margin-top: 15px; font-size: 0.85rem; line-height: 1.5; color: #E2E8F0; }
    .help-card { background: #0B0F19; border-radius: 10px; padding: 15px; border: 1px solid #1E293B; border-left: 3px solid #3B82F6; margin-bottom: 15px; font-size: 0.85rem;}
    
    .ai-assistant-table { background: linear-gradient(90deg, rgba(15, 23, 42, 0.8) 0%, rgba(2, 6, 23, 0.9) 100%); border-radius: 10px; padding: 15px 20px; border: 1px solid rgba(0, 255, 136, 0.2); margin-top: 15px; border-left: 4px solid #00FF88;}

    .stNumberInput label, .stSelectbox label { font-size: 0.7rem !important; color: #94A3B8 !important; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    div.stButton > button { background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; font-weight: 800 !important; height: 3.2rem !important; border-radius: 8px !important; border: none !important; width: 100%; text-transform: uppercase; letter-spacing: 1px; transition: transform 0.2s; }
    div.stButton > button:hover { transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE API E MATEMÁTICA ---
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

@st.cache_data(ttl=1800)
def get_auto_odds(fixture_id):
    odds = {"1": 1.0, "X": 1.0, "2": 1.0, "O15": 1.0, "O25": 1.0, "O35": 1.0, "U15": 1.0, "U25": 1.0, "U35": 1.0, "BTTS_Y": 1.0, "BTTS_N": 1.0}
    try:
        r = requests.get(f"https://{api_host}/odds", headers=headers, params={"fixture": fixture_id, "bookmaker": 8}).json()
        if r.get('response'):
            bets = r['response'][0]['bookmakers'][0]['bets']
            for bet in bets:
                if bet['name'] == 'Match Winner':
                    odds["1"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Home'), 1.0))
                    odds["X"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Draw'), 1.0))
                    odds["2"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Away'), 1.0))
                elif bet['name'] == 'Goals Over/Under':
                    odds["O15"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Over 1.5'), 1.0))
                    odds["U15"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Under 1.5'), 1.0))
                    odds["O25"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Over 2.5'), 1.0))
                    odds["U25"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Under 2.5'), 1.0))
                    odds["O35"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Over 3.5'), 1.0))
                    odds["U35"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Under 3.5'), 1.0))
                elif bet['name'] == 'Both Teams Score':
                    odds["BTTS_Y"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Yes'), 1.0))
                    odds["BTTS_N"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'No'), 1.0))
    except: pass
    return odds

def run_master_math(lh, la, rho, boost):
    lh *= (1+boost); la *= (1-boost); max_g = 10
    prob_mtx = np.outer(poisson.pmf(np.arange(max_g), lh), poisson.pmf(np.arange(max_g), la))
    for x in range(2):
        for y in range(2):
            if x==0 and y==0: prob_mtx[x,y] *= (1-lh*la*rho)
            elif x==0 and y==1: prob_mtx[x,y] *= (1+lh*rho)
            elif x==1 and y==0: prob_mtx[x,y] *= (1+la*rho)
            elif x==1 and y==1: prob_mtx[x,y] *= (1-rho)
    prob_mtx /= prob_mtx.sum() 
    
    ph, px, pa = np.tril(prob_mtx, -1).sum(), np.trace(prob_mtx), np.triu(prob_mtx, 1).sum()
    
    # Asian Handicaps
    h_win_1 = np.trace(prob_mtx, offset=-1)
    ah_p15_h = 1 - np.triu(prob_mtx, 2).sum()
    ah_p05_h = ph + px
    ah0_h = ph / (ph + pa) if (ph + pa) > 0 else 0
    ah_m05_h = ph
    ah_m1_h = (ph - h_win_1) / (1 - h_win_1) if (1 - h_win_1) > 0 else 0
    ah_m15_h = np.tril(prob_mtx, -2).sum()

    # Goals
    goals_sum = np.add.outer(np.arange(max_g), np.arange(max_g))
    o15 = prob_mtx[goals_sum > 1.5].sum(); u15 = 1 - o15
    o25 = prob_mtx[goals_sum > 2.5].sum(); u25 = 1 - o25
    o35 = prob_mtx[goals_sum > 3.5].sum(); u35 = 1 - o35
    
    btts_no = prob_mtx[0, :].sum() + prob_mtx[:, 0].sum() - prob_mtx[0,0]
    btts_yes = 1 - btts_no
    
    return {
        "Vencedor Casa": ph, "Empate (X)": px, "Vencedor Fora": pa, 
        "Handicap +1.5 (Casa)": ah_p15_h, "Handicap +0.5 (Casa)": ah_p05_h, "Empate Anula (Casa)": ah0_h, 
        "Handicap -0.5 (Casa)": ah_m05_h, "Handicap -1.0 (Casa)": ah_m1_h, "Handicap -1.5 (Casa)": ah_m15_h,
        "Mais de 1.5 Golos": o15, "Menos de 1.5 Golos": u15,
        "Mais de 2.5 Golos": o25, "Menos de 2.5 Golos": u25,
        "Mais de 3.5 Golos": o35, "Menos de 3.5 Golos": u35,
        "Ambas Marcam (Sim)": btts_yes, "Ambas Marcam (Não)": btts_no
    }, prob_mtx

# --- 3. SIDEBAR (COMPLETA) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; margin:0;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    bankroll = st.number_input("💰 A TUA BANCA (€)", value=100.0, step=10.0)
    
    l_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94, "Champions League": 2, "Serie A": 135}
    ln = st.selectbox("⚽ LIGA", list(l_map.keys()))
    
    fix = requests.get(f"https://{api_host}/fixtures", headers=headers, params={"date": date.today().strftime('%Y-%m-%d'), "league": l_map[ln], "season": "2025"}).json().get('response', [])
    if fix:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
        m_display = st.selectbox("JOGO", list(m_map.keys()))
        m_sel = next(f for f in fix if f['fixture']['id'] == m_map[m_display])
        auto_odds = get_auto_odds(m_sel['fixture']['id'])
    else: 
        m_sel = None
        auto_odds = {"1": 1.0, "X": 1.0, "2": 1.0, "O15": 1.0, "O25": 1.0, "O35": 1.0, "U15": 1.0, "U25": 1.0, "U35": 1.0, "BTTS_Y": 1.0, "BTTS_N": 1.0}

    st.markdown("<hr style='border-color:#1E293B; margin: 10px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.7rem; color:#00FF88; font-weight:800;'>🤖 ODDS (PREENCHIMENTO AUTO)</p>", unsafe_allow_html=True)
    
    with st.expander("Vencedor do Encontro", expanded=True):
        c1, cx, c2 = st.columns(3)
        o_1 = c1.number_input("1", value=auto_odds["1"], format="%.2f")
        o_x = cx.number_input("X", value=auto_odds["X"], format="%.2f")
        o_2 = c2.number_input("2", value=auto_odds["2"], format="%.2f")
    
    with st.expander("Mercado de Golos", expanded=False):
        c3, c4 = st.columns(2)
        o_o15 = c3.number_input("Mais 1.5", value=auto_odds["O15"], format="%.2f")
        o_u15 = c4.number_input("Menos 1.5", value=auto_odds["U15"], format="%.2f")
        o_o25 = c3.number_input("Mais 2.5", value=auto_odds["O25"], format="%.2f")
        o_u25 = c4.number_input("Menos 2.5", value=auto_odds["U25"], format="%.2f")
        o_o35 = c3.number_input("Mais 3.5", value=auto_odds["O35"], format="%.2f")
        o_u35 = c4.number_input("Menos 3.5", value=auto_odds["U35"], format="%.2f")
        o_btts_y = c3.number_input("Ambas Sim", value=auto_odds["BTTS_Y"], format="%.2f")
        o_btts_n = c4.number_input("Ambas Não", value=auto_odds["BTTS_N"], format="%.2f")

    with st.expander("Handicaps Asiáticos (Casa)", expanded=False):
        c5, c6 = st.columns(2)
        o_ahp15 = c5.number_input("AH +1.5", value=1.00, format="%.2f")
        o_ahp05 = c6.number_input("AH +0.5", value=1.00, format="%.2f")
        o_ah0 = c5.number_input("Empate Anula", value=1.00, format="%.2f")
        o_ahm05 = c6.number_input("AH -0.5", value=1.00, format="%.2f")
        o_ahm1 = c5.number_input("AH -1.0", value=1.00, format="%.2f")
        o_ahm15 = c6.number_input("AH -1.5", value=1.00, format="%.2f")
    
    st.markdown("<br>", unsafe_allow_html=True)
    execute = st.button("🔍 PROCURAR DINHEIRO FÁCIL")

# --- 4. RESULTADOS ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:180px;'><h1 style='opacity:0.1; font-size:4rem;'>ORACLE V140</h1><p style='color:#64748B;'>Escolhe o jogo na barra lateral.</p></div>", unsafe_allow_html=True)
else:
    s = get_pro_stats(m_sel['teams']['home']['id'], l_map[ln])
    lh, la = (s['h_f']*s['a_a'])**0.5, (s['a_f']*s['h_a'])**0.5
    res, mtx = run_master_math(lh, la, -0.11, 0.12)
    
    st.markdown(f"<h2 style='margin-bottom:0; font-size:3rem; letter-spacing:-1px;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#475569; font-weight:300;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h2>", unsafe_allow_html=True)

    # REEQUILÍBRIO DO LAYOUT: 50% / 50%
    col_res, col_chart = st.columns([1, 1])

    all_mkts = [
        ("Vencedor Casa", res["Vencedor Casa"], o_1), ("Empate (X)", res["Empate (X)"], o_x), ("Vencedor Fora", res["Vencedor Fora"], o_2),
        ("Handicap +1.5 (Casa)", res["Handicap +1.5 (Casa)"], o_ahp15), ("Handicap +0.5 (Casa)", res["Handicap +0.5 (Casa)"], o_ahp05),
        ("Empate Anula (Casa)", res["Empate Anula (Casa)"], o_ah0), ("Handicap -0.5 (Casa)", res["Handicap -0.5 (Casa)"], o_ahm05),
        ("Handicap -1.0 (Casa)", res["Handicap -1.0 (Casa)"], o_ahm1), ("Handicap -1.5 (Casa)", res["Handicap -1.5 (Casa)"], o_ahm15),
        ("Mais de 1.5 Golos", res["Mais de 1.5 Golos"], o_o15), ("Menos de 1.5 Golos", res["Menos de 1.5 Golos"], o_u15),
        ("Mais de 2.5 Golos", res["Mais de 2.5 Golos"], o_o25), ("Menos de 2.5 Golos", res["Menos de 2.5 Golos"], o_u25),
        ("Mais de 3.5 Golos", res["Mais de 3.5 Golos"], o_o35), ("Menos de 3.5 Golos", res["Menos de 3.5 Golos"], o_u35),
        ("Ambas Marcam (Sim)", res["Ambas Marcam (Sim)"], o_btts_y), ("Ambas Marcam (Não)", res["Ambas Marcam (Não)"], o_btts_n)
    ]
    
    valid_mkts = [(n,p,b,(p*b)-1) for n,p,b in all_mkts if b > 1.01]
    
    if len(valid_mkts) > 0:
        best = sorted(valid_mkts, key=lambda x: x[3], reverse=True)[0]
        edge = best[3]; kelly = max(0, (edge/(best[2]-1)) * 0.50) 
        color = "#00FF88" if edge > 0.08 else "#FFD700" if edge > 0.02 else "#EF4444"
        odd_justa = 1/best[1]
        
        st.markdown(f"""
<div class="pro-card" style="border-left-color: {color};">
    <span style="color:#94A3B8; font-size:0.75rem; font-weight:800; letter-spacing:1px;">A MELHOR APOSTA</span>
    <p class="bet-name">{best[0]}</p>
    <div style="display:flex; gap:20px; margin:15px 0;">
        <div><span style="color:#64748B; font-size:0.7rem; font-weight:700;">LUCRO EXTRA</span><br><span class="edge-value" style="color:{color};">{edge:+.1%}</span></div>
        <div><span style="color:#64748B; font-size:0.7rem; font-weight:700;">VALOR SEGURO</span><br><b style="font-size:1.4rem; font-family:'JetBrains Mono';">{bankroll*kelly:.2f}€</b></div>
    </div>
    <div class="ia-insight-card">
        <b>🗣️ O QUE ISTO SIGNIFICA:</b><br>
        A casa oferece <b style="color:#FFF;">{best[2]:.2f}</b>, mas a Odd Real devia ser <b style="color:#FFF;">{odd_justa:.2f}</b>. É lucro garantido a longo prazo.
    </div>
</div>
        """, unsafe_allow_html=True)
    else:
        with col_res: st.warning("Insere odds válidas na barra lateral.")

    with col_chart:
        st.markdown(f"""
<div class="help-card">
    <b style="color:#FFF; font-size:0.95rem;">📚 GUIA RÁPIDO DO APOSTADOR</b><br>
    <span style="font-size:0.8rem; color:#94A3B8; line-height:1.5;"><br>
    <b>• Lucro Extra:</b> +10% significa lucro limpo a longo prazo.<br>
    <b>• Odd Real:</b> O preço sem o roubo da casa. Aposta se a casa pagar mais.<br>
    <b>• Gráfico:</b> Mostra a probabilidade de golos de cada equipa.
    </span>
</div>
        """, unsafe_allow_html=True)

        xr = np.arange(7)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name="Ataque Casa", fill='tozeroy', line_color='#00FF88', line_width=3))
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name="Ataque Fora", fill='tozeroy', line_color='#3B82F6', line_width=3))
        fig.update_layout(height=180, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)

    # --- TABELA DE LUXO ---
    st.markdown("<h3 style='margin-top:10px; font-size:1.5rem; letter-spacing:-1px;'>📋 TODAS AS APOSTAS AVALIADAS</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='display: flex; gap: 20px; margin-bottom: 10px; font-size: 0.8rem; color: #94A3B8;'>
        <div><span style='color:#FFD700; font-size: 1rem; vertical-align: middle;'>●</span> <b style="color:white;">OURO (>10%)</b>: Erro grave da casa.</div>
        <div><span style='color:#00FF88; font-size: 1rem; vertical-align: middle;'>●</span> <b style="color:white;">VERDE (>2%)</b>: Valor sólido.</div>
        <div><span style='color:#EF4444; font-size: 1rem; vertical-align: middle;'>●</span> <b style="color:white;">VERMELHO (<0%)</b>: Armadilha.</div>
    </div>
    """, unsafe_allow_html=True)
    
    if len(valid_mkts) > 0:
        df = pd.DataFrame(valid_mkts, columns=["Aposta", "Certeza", "OddCasa", "Vantagem"])
        df["OddReal"] = 1 / df["Certeza"]
        df = df.sort_values(by="Vantagem", ascending=False)
        
        colors_vantagem = ['#FFD700' if e > 0.10 else '#00FF88' if e > 0.02 else '#EF4444' for e in df["Vantagem"]]
        
        fig_t = go.Figure(data=[go.Table(
            columnorder = [1,2,3,4,5], columnwidth = [220, 100, 100, 100, 120],
            header=dict(
                values=['<b>A TUA APOSTA</b>', '<b>A NOSSA CERTEZA</b>', '<b>ODD REAL</b>', '<b>ODD DA CASA</b>', '<b>LUCRO EXTRA</b>'], 
                fill_color='#020617', align=['left', 'center', 'center', 'center', 'center'], 
                font=dict(color='#64748B', size=10, family='Inter'), line_color='#1E293B', height=35
            ),
            cells=dict(
                values=[df.Aposta, df.Certeza.map('{:.1%}'.format), df.OddReal.map('{:.2f}'.format), df.OddCasa.map('{:.2f}'.format), df.Vantagem.map('{:+.1%}'.format)],
                fill_color='#0B0F19', align=['left', 'center', 'center', 'center', 'center'], 
                font=dict(color=['#FFFFFF', '#E2E8F0', '#E2E8F0', '#E2E8F0', colors_vantagem], size=13, family='JetBrains Mono'), 
                line_color='#1E293B', height=35
            )
        )])
        fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=(len(df)*35)+40, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_t, use_container_width=True)

        # --- ASSISTENTE IA ---
        apostas_ouro = len(df[df['Vantagem'] > 0.10])
        apostas_verdes = len(df[(df['Vantagem'] > 0.02) & (df['Vantagem'] <= 0.10)])
        apostas_lixo = len(df[df['Vantagem'] < 0])
        
        texto_ia = f"Analisei {len(df)} mercados. "
        if apostas_ouro > 0: texto_ia += f"Foca-te nas <b style='color:#FFD700;'>{apostas_ouro} apostas de OURO</b>! "
        elif apostas_verdes > 0: texto_ia += f"Tens <b style='color:#00FF88;'>{apostas_verdes} apostas Verdes</b> para lucro seguro. "
        else: texto_ia += "Não há grande valor aqui. Fica quieto. "
        if apostas_lixo > 0: texto_ia += f"Ignora as <b style='color:#EF4444;'>{apostas_lixo} armadilhas (Vermelho)</b>."

        st.markdown(f"""
        <div class="ai-assistant-table">
            <h4 style="margin:0 0 5px 0; color:#00FF88; font-size:0.9rem;">🤖 RESUMO DA TABELA</h4>
            <p style="color:#E2E8F0; font-size:0.85rem; margin:0;">{texto_ia}</p>
        </div>
        """, unsafe_allow_html=True)
