import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date
import textwrap

# --- 1. CONFIGURAÇÃO DE DESIGN (OMNI PREMIUM) ---
st.set_page_config(page_title="ORACLE V140 - OMNI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    .stApp { background-color: #050810; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #020408 !important; border-right: 1px solid #1E293B !important; }
    
    .top-recommendation { 
        background: linear-gradient(90deg, #0B1120 0%, #050810 100%);
        border-radius: 12px; border: 1px solid #1E293B; border-left: 6px solid #00FF88; 
        padding: 25px 40px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;
    }
    .top-rec-title { font-size: 0.75rem; color: #94A3B8; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
    .top-rec-value { font-size: 2.2rem; font-weight: 800; color: #FFFFFF; margin: 0; line-height: 1; font-family: 'Inter', sans-serif; }
    .top-rec-odd { font-size: 2.2rem; font-weight: 800; color: #FFD700; margin: 0; line-height: 1; font-family: 'JetBrains Mono', monospace; }
    .top-rec-edge { font-size: 2.2rem; font-weight: 800; color: #00FF88; margin: 0; line-height: 1; font-family: 'JetBrains Mono', monospace; }
    
    .context-card { background: rgba(59, 130, 246, 0.05); border-radius: 10px; padding: 20px; border: 1px solid rgba(59, 130, 246, 0.2); border-left: 4px solid #3B82F6; margin-bottom: 20px; display: flex; justify-content: space-between;}
    .context-team { font-size: 0.9rem; color: #E2E8F0; line-height: 1.5; }
    
    .ai-box { background: rgba(0, 255, 136, 0.03); border-radius: 12px; padding: 25px; border: 1px solid rgba(0, 255, 136, 0.2); border-top: 3px solid #00FF88; height: 100%; }
    .chart-box { background: #0B1120; border-radius: 12px; padding: 20px; border: 1px solid #1E293B; height: 100%; border-top: 3px solid #94A3B8;}
    
    .stNumberInput label, .stSelectbox label { font-size: 0.70rem !important; color: #94A3B8 !important; font-weight: 700; text-transform: uppercase; }
    div.stButton > button { background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; font-weight: 800 !important; height: 3.8rem !important; border-radius: 8px !important; border: none !important; width: 100%; letter-spacing: 1px; transition: transform 0.2s; }
    div.stButton > button:hover { transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE API E MATEMÁTICA OMNI ---
api_key = "8171043bf0a322286bb127947dbd4041"
api_host = "v3.football.api-sports.io"
headers = {"x-apisports-key": api_key}

@st.cache_data(ttl=3600)
def get_pro_stats(team_id, league_id):
    try:
        r = requests.get(f"https://{api_host}/teams/statistics", headers=headers, params={"league": league_id, "season": "2025", "team": team_id}).json()
        stats = r.get('response', {})
        g = stats.get('goals', {})
        
        # Puxar dados reais de contexto (Forma e Defesa)
        form = stats.get('form', 'N/A')
        clean_sheets = stats.get('clean_sheet', {}).get('total', 0)
        matches_played = stats.get('fixtures', {}).get('played', {}).get('total', 1)
        cs_pct = (clean_sheets / matches_played) if matches_played > 0 else 0
        
        return {
            "h_f": float(g.get('for', {}).get('average', {}).get('home', 1.5)), 
            "h_a": float(g.get('against', {}).get('average', {}).get('home', 1.0)),
            "a_f": float(g.get('for', {}).get('average', {}).get('away', 1.2)), 
            "a_a": float(g.get('against', {}).get('average', {}).get('away', 1.3)),
            "form": form,
            "cs_pct": cs_pct
        }
    except: return {"h_f": 1.5, "h_a": 1.0, "a_f": 1.2, "a_a": 1.3, "form": "N/A", "cs_pct": 0}

@st.cache_data(ttl=1800)
def get_auto_odds(fixture_id):
    odds = {k: 0.0 for k in ["1","X","2","O15","U15","O25","U25","O35","U35","BTTS_Y","BTTS_N","AH_P15","AH_P05","AH_00","AH_M05","AH_M10","AH_M15"]}
    try:
        r = requests.get(f"https://{api_host}/odds", headers=headers, params={"fixture": fixture_id, "bookmaker": 8}).json()
        if r.get('response'):
            bets = r['response'][0]['bookmakers'][0]['bets']
            for bet in bets:
                if bet['name'] == 'Match Winner':
                    odds["1"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Home'), 0.0))
                    odds["X"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Draw'), 0.0))
                    odds["2"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Away'), 0.0))
                elif bet['name'] == 'Goals Over/Under':
                    odds["O15"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Over 1.5'), 0.0))
                    odds["U15"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Under 1.5'), 0.0))
                    odds["O25"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Over 2.5'), 0.0))
                    odds["U25"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Under 2.5'), 0.0))
                    odds["O35"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Over 3.5'), 0.0))
                    odds["U35"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Under 3.5'), 0.0))
                elif bet['name'] == 'Both Teams Score':
                    odds["BTTS_Y"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Yes'), 0.0))
                    odds["BTTS_N"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'No'), 0.0))
                elif bet['name'] == 'Asian Handicap':
                    for v in bet['values']:
                        if v['value'] == 'Home +1.5': odds["AH_P15"] = float(v['odd'])
                        elif v['value'] == 'Home +0.5': odds["AH_P05"] = float(v['odd'])
                        elif v['value'] == 'Home +0.0' or v['value'] == 'Home 0.0': odds["AH_00"] = float(v['odd'])
                        elif v['value'] == 'Home -0.5': odds["AH_M05"] = float(v['odd'])
                        elif v['value'] == 'Home -1.0': odds["AH_M10"] = float(v['odd'])
                        elif v['value'] == 'Home -1.5': odds["AH_M15"] = float(v['odd'])
    except: pass
    return odds

def run_master_math(lh, la, rho, boost, zip_factor=1.08):
    lh *= (1+boost); la *= (1-boost); max_g = 10
    prob_mtx = np.outer(poisson.pmf(np.arange(max_g), lh), poisson.pmf(np.arange(max_g), la))
    
    # Ajuste Dixon-Coles
    for x in range(2):
        for y in range(2):
            if x==0 and y==0: prob_mtx[x,y] *= (1-lh*la*rho)
            elif x==0 and y==1: prob_mtx[x,y] *= (1+lh*rho)
            elif x==1 and y==0: prob_mtx[x,y] *= (1+la*rho)
            elif x==1 and y==1: prob_mtx[x,y] *= (1-rho)
            
    # Ajuste Zero-Inflated Poisson (ZIP) para empates 0-0 frequentes
    prob_mtx[0,0] *= zip_factor
    prob_mtx /= prob_mtx.sum() 
    
    ph, px, pa = np.tril(prob_mtx, -1).sum(), np.trace(prob_mtx), np.triu(prob_mtx, 1).sum()
    h_win_1 = np.trace(prob_mtx, offset=-1)
    goals_sum = np.add.outer(np.arange(max_g), np.arange(max_g))
    
    return {
        "Vencedor Casa": ph, "Empate (X)": px, "Vencedor Fora": pa,
        "Mais de 1.5 Golos": prob_mtx[goals_sum > 1.5].sum(), "Menos de 1.5 Golos": prob_mtx[goals_sum < 1.5].sum() + prob_mtx[goals_sum == 1.5].sum(),
        "Mais de 2.5 Golos": prob_mtx[goals_sum > 2.5].sum(), "Menos de 2.5 Golos": prob_mtx[goals_sum < 2.5].sum() + prob_mtx[goals_sum == 2.5].sum(),
        "Mais de 3.5 Golos": prob_mtx[goals_sum > 3.5].sum(), "Menos de 3.5 Golos": prob_mtx[goals_sum < 3.5].sum() + prob_mtx[goals_sum == 3.5].sum(),
        "Ambas Marcam (Sim)": 1 - (prob_mtx[0, :].sum() + prob_mtx[:, 0].sum() - prob_mtx[0,0]), 
        "Ambas Marcam (Não)": prob_mtx[0, :].sum() + prob_mtx[:, 0].sum() - prob_mtx[0,0],
        "Handicap +1.5 (Casa)": 1 - np.triu(prob_mtx, 2).sum(), "Handicap +0.5 (Casa)": ph + px,
        "Empate Anula (Casa)": ph / (ph + pa) if (ph + pa) > 0 else 0, "Handicap -0.5 (Casa)": ph,
        "Handicap -1.0 (Casa)": (ph - h_win_1) / (1 - h_win_1) if (1 - h_win_1) > 0 else 0, "Handicap -1.5 (Casa)": np.tril(prob_mtx, -2).sum()
    }, prob_mtx

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; margin:0;'>🏛️ ORACLE V140</h2><br>", unsafe_allow_html=True)
    
    bankroll = st.number_input("💰 A TUA BANCA TOTAL (€)", value=100.0, step=10.0)
    
    l_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94, "Champions League": 2, "Serie A": 135}
    ln = st.selectbox("⚽ LIGA", list(l_map.keys()))
    
    fix = requests.get(f"https://{api_host}/fixtures", headers=headers, params={"date": date.today().strftime('%Y-%m-%d'), "league": l_map[ln], "season": "2025"}).json().get('response', [])
    if fix:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
        m_display = st.selectbox("JOGO", list(m_map.keys()))
        m_sel = next(f for f in fix if f['fixture']['id'] == m_map[m_display])
        with st.spinner('A puxar odds e estatísticas...'):
            auto_odds = get_auto_odds(m_sel['fixture']['id'])
    else: 
        m_sel = None; auto_odds = {k: 0.0 for k in ["1","X","2","O15","U15","O25","U25","O35","U35","BTTS_Y","BTTS_N","AH_P15","AH_P05","AH_00","AH_M05","AH_M10","AH_M15"]}

    st.markdown("<br>", unsafe_allow_html=True)
    execute = st.button("🚀 INICIAR ALPHA SCAN")

    with st.expander("⚙️ ODDS MANUAIS COMPLETAS"):
        st.write("Vencedor do Encontro")
        c1, c2, c3 = st.columns(3)
        o_1 = c1.number_input("1 (Casa)", value=auto_odds["1"], format="%.2f"); o_x = c2.number_input("X (Empate)", value=auto_odds["X"], format="%.2f"); o_2 = c3.number_input("2 (Fora)", value=auto_odds["2"], format="%.2f")
        
        st.write("Mercado de Golos")
        c4, c5 = st.columns(2)
        o_o15 = c4.number_input("Mais 1.5", value=auto_odds["O15"], format="%.2f"); o_u15 = c5.number_input("Menos 1.5", value=auto_odds["U15"], format="%.2f")
        o_o25 = c4.number_input("Mais 2.5", value=auto_odds["O25"], format="%.2f"); o_u25 = c5.number_input("Menos 2.5", value=auto_odds["U25"], format="%.2f")
        o_o35 = c4.number_input("Mais 3.5", value=auto_odds["O35"], format="%.2f"); o_u35 = c5.number_input("Menos 3.5", value=auto_odds["U35"], format="%.2f")
        
        st.write("Ambas Marcam")
        c6, c7 = st.columns(2)
        o_btts_y = c6.number_input("Sim", value=auto_odds["BTTS_Y"], format="%.2f"); o_btts_n = c7.number_input("Não", value=auto_odds["BTTS_N"], format="%.2f")
        
        st.write("Handicaps Asiáticos (Casa)")
        c8, c9 = st.columns(2)
        o_ahp15 = c8.number_input("AH +1.5", value=auto_odds["AH_P15"], format="%.2f"); o_ahp05 = c9.number_input("AH +0.5", value=auto_odds["AH_P05"], format="%.2f")
        o_ah0 = c8.number_input("Empate Anula", value=auto_odds["AH_00"], format="%.2f"); o_ahm05 = c9.number_input("AH -0.5", value=auto_odds["AH_M05"], format="%.2f")
        o_ahm1 = c8.number_input("AH -1.0", value=auto_odds["AH_M10"], format="%.2f"); o_ahm15 = c9.number_input("AH -1.5", value=auto_odds["AH_M15"], format="%.2f")

# --- 4. RESULTADOS (ESTRUTURA CASCATA) ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:180px;'><h1 style='opacity:0.1; font-size:4rem;'>ORACLE V140</h1><p style='color:#64748B;'>Terminal de Decisão Analítica.</p></div>", unsafe_allow_html=True)
else:
    s_home = get_pro_stats(m_sel['teams']['home']['id'], l_map[ln])
    s_away = get_pro_stats(m_sel['teams']['away']['id'], l_map[ln])
    
    lh, la = (s_home['h_f']*s_away['a_a'])**0.5, (s_away['a_f']*s_home['h_a'])**0.5
    res, mtx = run_master_math(lh, la, -0.11, 0.12, zip_factor=1.08) # Fator ZIP aplicado
    
    st.markdown(f"<h2 style='margin-bottom:10px; font-size:3.2rem; letter-spacing:-2px;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#475569; font-weight:300;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h2>", unsafe_allow_html=True)

    # PAINEL DE CONTEXTO REAL
    st.markdown(f"""
    <div class="context-card">
        <div class="context-team">
            <b style="color:#FFF;">🏠 {m_sel['teams']['home']['name']}</b><br>
            Forma Recente: <span style="color:#00FF88;">{s_home['form'][-5:] if s_home['form'] != 'N/A' else 'N/A'}</span><br>
            Clean Sheets: {s_home['cs_pct']:.0%} dos jogos
        </div>
        <div class="context-team" style="text-align:right;">
            <b style="color:#FFF;">✈️ {m_sel['teams']['away']['name']}</b><br>
            Forma Recente: <span style="color:#3B82F6;">{s_away['form'][-5:] if s_away['form'] != 'N/A' else 'N/A'}</span><br>
            Clean Sheets: {s_away['cs_pct']:.0%} dos jogos
        </div>
    </div>
    """, unsafe_allow_html=True)

    all_mkts = [
        ("Vencedor Casa", res["Vencedor Casa"], o_1), ("Empate (X)", res["Empate (X)"], o_x), ("Vencedor Fora", res["Vencedor Fora"], o_2),
        ("Mais de 1.5 Golos", res["Mais de 1.5 Golos"], o_o15), ("Menos de 1.5 Golos", res["Menos de 1.5 Golos"], o_u15),
        ("Mais de 2.5 Golos", res["Mais de 2.5 Golos"], o_o25), ("Menos de 2.5 Golos", res["Menos de 2.5 Golos"], o_u25),
        ("Mais de 3.5 Golos", res["Mais de 3.5 Golos"], o_o35), ("Menos de 3.5 Golos", res["Menos de 3.5 Golos"], o_u35),
        ("Ambas Marcam (Sim)", res["Ambas Marcam (Sim)"], o_btts_y), ("Ambas Marcam (Não)", res["Ambas Marcam (Não)"], o_btts_n),
        ("Handicap +1.5 (Casa)", res["Handicap +1.5 (Casa)"], o_ahp15), ("Handicap +0.5 (Casa)", res["Handicap +0.5 (Casa)"], o_ahp05),
        ("Empate Anula (Casa)", res["Empate Anula (Casa)"], o_ah0), ("Handicap -0.5 (Casa)", res["Handicap -0.5 (Casa)"], o_ahm05),
        ("Handicap -1.0 (Casa)", res["Handicap -1.0 (Casa)"], o_ahm1), ("Handicap -1.5 (Casa)", res["Handicap -1.5 (Casa)"], o_ahm15)
    ]
    
    valid_mkts = [(n,p,b,(p*b)-1) for n,p,b in all_mkts if b > 1.05]
    
    if len(valid_mkts) > 0:
        value_bets = [m for m in valid_mkts if m[3] > 0.02] 
        if value_bets:
            sweet_spot = [m for m in value_bets if 1.40 <= m[2] <= 3.50]
            best = sorted(sweet_spot, key=lambda x: x[3], reverse=True)[0] if sweet_spot else sorted(value_bets, key=lambda x: x[3], reverse=True)[0]
        else:
            best = sorted(valid_mkts, key=lambda x: x[1], reverse=True)[0]
            
        edge = best[3]; kelly = max(0, (edge/(best[2]-1)) * 0.50) 
        odd_justa = 1/best[1]
        
        st.markdown(f"""
        <div class="top-recommendation">
            <div><div class="top-rec-title">Aposta de Ouro (Sweet Spot)</div><div class="top-rec-value">{best[0]}</div></div>
            <div><div class="top-rec-title">Odd da Casa</div><div class="top-rec-odd">{best[2]:.2f}</div></div>
            <div><div class="top-rec-title">Lucro Extra (Vantagem)</div><div class="top-rec-edge">{edge:+.1%}</div></div>
            <div><div class="top-rec-title">Valor a Apostar</div><div class="top-rec-value" style="font-family:'JetBrains Mono'; color:#00FF88;">{bankroll*kelly:.2f}€</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='margin-top:10px; font-size:1.2rem; letter-spacing:-1px; color:#94A3B8;'>📋 TODAS AS APOSTAS AVALIADAS</h3>", unsafe_allow_html=True)
        
        df = pd.DataFrame(valid_mkts, columns=["Aposta", "Certeza", "OddCasa", "Vantagem"])
        df["OddReal"] = 1 / df["Certeza"]
        df = df.sort_values(by="Vantagem", ascending=False)
        colors_vantagem = ['#FFD700' if e > 0.10 else '#00FF88' if e > 0.02 else '#EF4444' for e in df["Vantagem"]]
        
        fig_t = go.Figure(data=[go.Table(
            columnorder = [1,2,3,4,5], columnwidth = [250, 100, 100, 100, 120],
            header=dict(
                values=['<b>A TUA APOSTA</b>', '<b>A NOSSA CERTEZA</b>', '<b>ODD REAL (CORRETA)</b>', '<b>ODD DA CASA</b>', '<b>LUCRO EXTRA</b>'], 
                fill_color='#020408', align=['left', 'center', 'center', 'center', 'center'], 
                font=dict(color='#64748B', size=11, family='Inter'), line_color='#1E293B', height=45
            ),
            cells=dict(
                values=[df.Aposta, df.Certeza.map('{:.1%}'.format), df.OddReal.map('{:.2f}'.format), df.OddCasa.map('{:.2f}'.format), df.Vantagem.map('{:+.1%}'.format)],
                fill_color='#0B1120', align=['left', 'center', 'center', 'center', 'center'], 
                font=dict(color=['#FFFFFF', '#E2E8F0', '#E2E8F0', '#E2E8F0', colors_vantagem], size=13, family='JetBrains Mono'), 
                line_color='#1E293B', height=40
            )
        )])
        fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=(len(df)*40)+50, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_t, use_container_width=True)

        # 4. FUNDO: IA E GRÁFICO (LADO A LADO)
        col_ai, col_chart = st.columns([1, 1])
        
        with col_ai:
            apostas_ouro = len(df[df['Vantagem'] > 0.10])
            apostas_verdes = len(df[(df['Vantagem'] > 0.02) & (df['Vantagem'] <= 0.10)])
            
            texto_ia = f"O modelo processou <b>{len(valid_mkts)} mercados</b>.<br><br>"
            if edge > 0.02:
                texto_ia += f"🎯 <b>VERDICTO:</b> A recomendação '{best[0]}' (odd {best[2]:.2f}) é o Ponto Rebuçado. Tem uma segurança matemática sólida e um lucro extra de {edge:.1%}. "
            else:
                texto_ia += f"⛔ <b>SEM VALOR CLARO:</b> As casas de apostas foram espertas neste jogo. A recomendação '{best[0]}' é apenas a menos má. Sugiro proteger o capital."
                
            if apostas_ouro > 0: texto_ia += f"<br><br>🚨 <b>Atenção:</b> Encontrei {apostas_ouro} apostas com erros graves (Ouro) na tabela. Analisa se o risco te compensa."

            st.markdown(f"""
            <div class="ai-box">
                <h4 style="margin:0 0 10px 0; color:#00FF88; font-size:1.1rem; text-transform:uppercase;">🤖 Assistente de Mesa</h4>
                <p style="color:#E2E8F0; font-size:0.95rem; margin:0; line-height:1.6;">{texto_ia}</p>
                <hr style="border-color: rgba(255,255,255,0.1); margin: 15px 0;">
                <span style="font-size:0.8rem; color:#94A3B8;"><b>Dica de Leitura da Tabela:</b> Só aposta quando a Odd da Casa for maior que a Odd Real (Ouro ou Verde). O Vermelho é armadilha.</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col_chart:
            st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
            xr = np.arange(7)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name="Ataque Casa", mode='lines+markers', fill='tozeroy', line=dict(color='#00FF88', width=3), marker=dict(size=8, color='#00FF88')))
            fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name="Ataque Fora", mode='lines+markers', fill='tozeroy', line=dict(color='#3B82F6', width=3), marker=dict(size=8, color='#3B82F6')))
            fig.update_layout(
                title=dict(text="📊 DISTRIBUIÇÃO DE GOLOS (POISSON)", font=dict(color="#94A3B8", size=13)),
                height=250, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#64748B"),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#64748B", tickformat=".0%"),
                legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
    else:
        st.warning("O robô não encontrou odds. Vai ao menu lateral (Engrenagem: Odds Manuais Completas) e insere os valores.")
