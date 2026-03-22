import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date
import time

# --- 1. CONFIGURAÇÃO DE DESIGN (OMNI PREMIUM) ---
st.set_page_config(page_title="ORACLE V140 - HEDGE FUND BUILD", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    .stApp { background-color: #050810; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #020408 !important; border-right: 1px solid #1E293B !important; }
    
    /* Tabs Premium */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #64748B; font-weight: 800; font-size: 1.1rem; padding: 10px 20px; background: #0B1120; border-radius: 8px 8px 0 0; border: 1px solid #1E293B; border-bottom: none; }
    .stTabs [aria-selected="true"] { color: #00FF88 !important; background: #050810; border-top: 3px solid #00FF88; }
    
    .top-recommendation { background: linear-gradient(90deg, #0B1120 0%, #050810 100%); border-radius: 12px; border: 1px solid #1E293B; border-left: 6px solid #00FF88; padding: 25px 40px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; }
    .top-rec-title { font-size: 0.75rem; color: #94A3B8; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
    .top-rec-value { font-size: 2.2rem; font-weight: 800; color: #FFFFFF; margin: 0; line-height: 1; font-family: 'Inter', sans-serif; }
    .top-rec-odd { font-size: 2.2rem; font-weight: 800; color: #FFD700; margin: 0; line-height: 1; font-family: 'JetBrains Mono', monospace; }
    .top-rec-edge { font-size: 2.2rem; font-weight: 800; color: #00FF88; margin: 0; line-height: 1; font-family: 'JetBrains Mono', monospace; }
    
    .context-card { background: #0B1120; border-radius: 12px; padding: 20px; border: 1px solid #1E293B; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
    .team-name-context { font-size: 1.1rem; font-weight: 800; color: #FFF; margin-bottom: 10px; }
    .stats-text { font-size: 0.85rem; color: #94A3B8; margin-bottom: 3px; }
    
    .ai-box { background: rgba(0, 255, 136, 0.03); border-radius: 12px; padding: 25px; border: 1px solid rgba(0, 255, 136, 0.2); border-top: 3px solid #00FF88; height: 100%; }
    
    .stNumberInput label, .stSelectbox label { font-size: 0.70rem !important; color: #94A3B8 !important; font-weight: 700; text-transform: uppercase; }
    div.stButton > button { background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; font-weight: 800 !important; height: 3.8rem !important; border-radius: 8px !important; border: none !important; width: 100%; letter-spacing: 1px; transition: transform 0.2s; }
    div.stButton > button:hover { transform: translateY(-2px); }
    
    .portfolio-card { background: #0B1120; border-radius: 12px; padding: 25px; border: 1px solid #1E293B; border-top: 4px solid #FFD700; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE DADOS ---
api_key = "8171043bf0a322286bb127947dbd4041"
api_host = "v3.football.api-sports.io"
headers = {"x-apisports-key": api_key}

def format_form(form_str):
    if not form_str or form_str == 'N/A': return "<span style='color:#94A3B8;'>Sem dados</span>"
    html = ""
    for char in form_str[-5:]:
        if char == 'W': html += "<span style='color:#000; background:#00FF88; padding:2px 6px; border-radius:4px; margin-right:4px; font-weight:bold; font-size:0.75rem;'>V</span>"
        elif char == 'D': html += "<span style='color:#000; background:#FFD700; padding:2px 6px; border-radius:4px; margin-right:4px; font-weight:bold; font-size:0.75rem;'>E</span>"
        elif char == 'L': html += "<span style='color:#FFF; background:#EF4444; padding:2px 6px; border-radius:4px; margin-right:4px; font-weight:bold; font-size:0.75rem;'>D</span>"
    return html

@st.cache_data(ttl=3600)
def get_pro_stats(team_id, league_id):
    try:
        r = requests.get(f"https://{api_host}/teams/statistics", headers=headers, params={"league": league_id, "season": "2025", "team": team_id}).json()
        stats = r.get('response', {})
        g = stats.get('goals', {})
        form = stats.get('form', 'N/A')
        clean_sheets = stats.get('clean_sheet', {}).get('total', 0)
        matches = stats.get('fixtures', {}).get('played', {}).get('total', 1)
        return {
            "h_f": float(g.get('for', {}).get('average', {}).get('home', 1.5)), "h_a": float(g.get('against', {}).get('average', {}).get('home', 1.0)),
            "a_f": float(g.get('for', {}).get('average', {}).get('away', 1.2)), "a_a": float(g.get('against', {}).get('average', {}).get('away', 1.3)),
            "form": form, "cs_pct": (clean_sheets / matches) if matches > 0 else 0
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
                        elif v['value'] in ['Home +0.0', 'Home 0.0']: odds["AH_00"] = float(v['odd'])
                        elif v['value'] == 'Home -0.5': odds["AH_M05"] = float(v['odd'])
                        elif v['value'] == 'Home -1.0': odds["AH_M10"] = float(v['odd'])
                        elif v['value'] == 'Home -1.5': odds["AH_M15"] = float(v['odd'])
    except: pass
    return odds

def run_master_math(lh, la, rho, boost, zip_factor=1.05):
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
    h_win_1 = np.trace(prob_mtx, offset=-1); goals_sum = np.add.outer(np.arange(max_g), np.arange(max_g))
    
    return {
        "Vencedor Casa": ph, "Empate (X)": px, "Vencedor Fora": pa,
        "Mais de 1.5 Golos": prob_mtx[goals_sum > 1.5].sum(), "Menos de 1.5 Golos": prob_mtx[goals_sum < 1.5].sum() + prob_mtx[goals_sum == 1.5].sum(),
        "Mais de 2.5 Golos": prob_mtx[goals_sum > 2.5].sum(), "Menos de 2.5 Golos": prob_mtx[goals_sum < 2.5].sum() + prob_mtx[goals_sum == 2.5].sum(),
        "Mais de 3.5 Golos": prob_mtx[goals_sum > 3.5].sum(), "Menos de 3.5 Golos": prob_mtx[goals_sum < 3.5].sum() + prob_mtx[goals_sum == 3.5].sum(),
        "Ambas Marcam (Sim)": 1 - (prob_mtx[0, :].sum() + prob_mtx[:, 0].sum() - prob_mtx[0,0]), "Ambas Marcam (Não)": prob_mtx[0, :].sum() + prob_mtx[:, 0].sum() - prob_mtx[0,0],
        "Handicap +1.5 (Casa)": 1 - np.triu(prob_mtx, 2).sum(), "Handicap +0.5 (Casa)": ph + px,
        "Empate Anula (Casa)": ph / (ph + pa) if (ph + pa) > 0 else 0, "Handicap -0.5 (Casa)": ph,
        "Handicap -1.0 (Casa)": (ph - h_win_1) / (1 - h_win_1) if (1 - h_win_1) > 0 else 0, "Handicap -1.5 (Casa)": np.tril(prob_mtx, -2).sum()
    }, prob_mtx

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; margin:0;'>🏛️ ORACLE V140</h2><br>", unsafe_allow_html=True)
    bankroll = st.number_input("💰 A TUA BANCA TOTAL (€)", value=1000.0, step=50.0)
    
    l_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94, "Champions League": 2, "Serie A": 135}
    ln = st.selectbox("⚽ LIGA", list(l_map.keys()))
    
    fix_data = requests.get(f"https://{api_host}/fixtures", headers=headers, params={"date": date.today().strftime('%Y-%m-%d'), "league": l_map[ln], "season": "2025"}).json().get('response', [])
    
    if fix_data:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix_data}
        m_display = st.selectbox("JOGO (Apenas para Deep Dive)", list(m_map.keys()))
        m_sel = next(f for f in fix_data if f['fixture']['id'] == m_map[m_display])
        auto_odds = get_auto_odds(m_sel['fixture']['id'])
    else: 
        m_sel = None; auto_odds = {k: 0.0 for k in ["1","X","2","O15","U15","O25","U25","O35","U35","BTTS_Y","BTTS_N","AH_P15","AH_P05","AH_00","AH_M05","AH_M10","AH_M15"]}

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("⚙️ ODDS MANUAIS COMPLETAS (Opção Deep Dive)"):
        c1, c2, c3 = st.columns(3)
        o_1 = c1.number_input("1 (Casa)", value=auto_odds["1"]); o_x = c2.number_input("X (Emp)", value=auto_odds["X"]); o_2 = c3.number_input("2 (Fora)", value=auto_odds["2"])
        o_o25 = c1.number_input("Mais 2.5", value=auto_odds["O25"]); o_u25 = c2.number_input("Menos 2.5", value=auto_odds["U25"]); o_btts_y = c3.number_input("Ambas Sim", value=auto_odds["BTTS_Y"])
        # As odds de Handicap e Over/Under extra são geridas pela API
        
# --- 4. TABS (O CORAÇÃO DO SOFTWARE) ---
tab1, tab2 = st.tabs(["🔬 DEEP DIVE (ANÁLISE DE JOGO)", "🌍 ALPHA SCANNER (PORTFÓLIO GLOBAL)"])

with tab1:
    if not m_sel:
        st.markdown("<div style='text-align:center; padding-top:150px;'><h1 style='opacity:0.1; font-size:4rem;'>SEM JOGOS</h1></div>", unsafe_allow_html=True)
    else:
        s_h = get_pro_stats(m_sel['teams']['home']['id'], l_map[ln])
        s_a = get_pro_stats(m_sel['teams']['away']['id'], l_map[ln])
        lh, la = (s_h['h_f']*s_a['a_a'])**0.5, (s_a['a_f']*s_h['h_a'])**0.5
        res, mtx = run_master_math(lh, la, -0.11, 0.12)
        
        st.markdown(f"<h2 style='margin-bottom:10px; font-size:3.2rem; letter-spacing:-2px;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#475569; font-weight:300;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h2>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="context-card">
            <div><div class="team-name-context">🏠 {m_sel['teams']['home']['name']} (Casa)</div><div class="stats-text">Forma: {format_form(s_h['form'])}</div><div class="stats-text">Golos (Média): <b style="color:#FFF;">{s_h['h_f']:.2f}</b></div></div>
            <div style="text-align: right;"><div class="team-name-context">✈️ {m_sel['teams']['away']['name']} (Fora)</div><div class="stats-text">Forma: {format_form(s_a['form'])}</div><div class="stats-text">Golos (Média): <b style="color:#FFF;">{s_a['a_f']:.2f}</b></div></div>
        </div>
        """, unsafe_allow_html=True)

        # 17 Mercados Ativados no Deep Dive
        all_mkts = [
            ("Vencedor Casa", res["Vencedor Casa"], o_1), ("Empate (X)", res["Empate (X)"], o_x), ("Vencedor Fora", res["Vencedor Fora"], o_2),
            ("Mais de 1.5 Golos", res["Mais de 1.5 Golos"], auto_odds["O15"]), ("Menos de 1.5 Golos", res["Menos de 1.5 Golos"], auto_odds["U15"]),
            ("Mais de 2.5 Golos", res["Mais de 2.5 Golos"], o_o25), ("Menos de 2.5 Golos", res["Menos de 2.5 Golos"], o_u25),
            ("Mais de 3.5 Golos", res["Mais de 3.5 Golos"], auto_odds["O35"]), ("Menos de 3.5 Golos", res["Menos de 3.5 Golos"], auto_odds["U35"]),
            ("Ambas Marcam (Sim)", res["Ambas Marcam (Sim)"], o_btts_y), ("Ambas Marcam (Não)", res["Ambas Marcam (Não)"], auto_odds["BTTS_N"]),
            ("Handicap +1.5 (Casa)", res["Handicap +1.5 (Casa)"], auto_odds["AH_P15"]), ("Handicap +0.5 (Casa)", res["Handicap +0.5 (Casa)"], auto_odds["AH_P05"]),
            ("Empate Anula (Casa)", res["Empate Anula (Casa)"], auto_odds["AH_00"]), ("Handicap -0.5 (Casa)", res["Handicap -0.5 (Casa)"], auto_odds["AH_M05"]),
            ("Handicap -1.0 (Casa)", res["Handicap -1.0 (Casa)"], auto_odds["AH_M10"]), ("Handicap -1.5 (Casa)", res["Handicap -1.5 (Casa)"], auto_odds["AH_M15"])
        ]
        valid_mkts = [(n,p,b,(p*b)-1) for n,p,b in all_mkts if b > 1.05]
        
        if len(valid_mkts) > 0:
            value_bets = [m for m in valid_mkts if m[3] > 0.02] 
            if value_bets:
                safe_bets = [m for m in value_bets if 1.45 <= m[2] <= 3.50]
                if safe_bets: best = sorted(safe_bets, key=lambda x: x[1], reverse=True)[0]
                else: best = sorted(value_bets, key=lambda x: x[1], reverse=True)[0]
            else: best = sorted(valid_mkts, key=lambda x: x[1], reverse=True)[0]
            
            edge = best[3]; kelly = max(0, (edge/(best[2]-1)) * 0.50); odd_justa = 1/best[1]
            
            st.markdown(f"""
            <div class="top-recommendation">
                <div><div class="top-rec-title">Aposta de Ouro (Sweet Spot)</div><div class="top-rec-value">{best[0]}</div></div>
                <div><div class="top-rec-title">A Nossa Certeza</div><div class="top-rec-value" style="color:#00FF88;">{best[1]:.1%}</div></div>
                <div><div class="top-rec-title">Odd da Casa</div><div class="top-rec-odd">{best[2]:.2f}</div></div>
                <div><div class="top-rec-title">Valor a Apostar</div><div class="top-rec-value" style="font-family:'JetBrains Mono'; color:#00FF88;">{bankroll*kelly:.2f}€</div></div>
            </div>
            """, unsafe_allow_html=True)
            
            df = pd.DataFrame(valid_mkts, columns=["Aposta", "Certeza", "OddCasa", "Vantagem"])
            df["OddReal"] = 1 / df["Certeza"]
            df = df.sort_values(by="Vantagem", ascending=False)
            colors_v = ['#FFD700' if e > 0.10 else '#00FF88' if e > 0.02 else '#EF4444' for e in df["Vantagem"]]
            
            fig_t = go.Figure(data=[go.Table(
                columnorder = [1,2,3,4,5], columnwidth = [250, 100, 100, 100, 120],
                header=dict(values=['<b>MERCADO DA APOSTA</b>', '<b>NOSSA CERTEZA</b>', '<b>ODD REAL</b>', '<b>ODD CASA</b>', '<b>LUCRO EXTRA</b>'], fill_color='#0B1120', align='center', font=dict(color='#64748B', size=11), height=45),
                cells=dict(values=[df.Aposta, df.Certeza.map('{:.1%}'.format), df.OddReal.map('{:.2f}'.format), df.OddCasa.map('{:.2f}'.format), df.Vantagem.map('{:+.1%}'.format)], fill_color='#050810', align='center', font=dict(color=['#FFFFFF', '#E2E8F0', '#E2E8F0', '#E2E8F0', colors_v], size=13), height=40)
            )])
            fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=(len(df)*40)+50, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_t, use_container_width=True)

with tab2:
    st.markdown("<h2 style='font-size:2.5rem; letter-spacing:-1px;'>🌍 SCANNER GLOBAL DE MERCADO</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#94A3B8;'>O robô vai analisar todos os jogos de hoje na <b>{ln}</b>, avaliar os 17 mercados de cada um, cruzar com as odds da Bet365 e montar o teu portfólio de investimento diário focado no risco/recompensa ideal.</p>", unsafe_allow_html=True)
    
    if st.button("🔥 EXECUTAR VARREDURA GLOBAL (PORTFÓLIO)", key="scan_global"):
        if not fix_data:
            st.warning(f"Não há jogos agendados para hoje na {ln}.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            portfolio = []
            
            for i, f in enumerate(fix_data):
                home = f['teams']['home']['name']
                away = f['teams']['away']['name']
                fix_id = f['fixture']['id']
                
                status_text.text(f"A analisar os 17 mercados para {home} vs {away}...")
                
                s_h = get_pro_stats(f['teams']['home']['id'], l_map[ln])
                s_a = get_pro_stats(f['teams']['away']['id'], l_map[ln])
                odds = get_auto_odds(fix_id)
                
                # Só calcula se o mercado tiver odds reais da API
                if odds["1"] > 1.01:
                    lh, la = (s_h['h_f']*s_a['a_a'])**0.5, (s_a['a_f']*s_h['h_a'])**0.5
                    res, mtx = run_master_math(lh, la, -0.11, 0.12)
                    
                    # OS 17 MERCADOS VOLTAM PARA A VARREDURA GLOBAL
                    game_mkts = [
                        (f"{home} (Vencedor)", res["Vencedor Casa"], odds["1"]),
                        (f"Empate ({home} vs {away})", res["Empate (X)"], odds["X"]),
                        (f"{away} (Vencedor)", res["Vencedor Fora"], odds["2"]),
                        (f"Mais 1.5 Golos ({home} vs {away})", res["Mais de 1.5 Golos"], odds["O15"]),
                        (f"Menos 1.5 Golos ({home} vs {away})", res["Menos de 1.5 Golos"], odds["U15"]),
                        (f"Mais 2.5 Golos ({home} vs {away})", res["Mais de 2.5 Golos"], odds["O25"]),
                        (f"Menos 2.5 Golos ({home} vs {away})", res["Menos de 2.5 Golos"], odds["U25"]),
                        (f"Mais 3.5 Golos ({home} vs {away})", res["Mais de 3.5 Golos"], odds["O35"]),
                        (f"Menos 3.5 Golos ({home} vs {away})", res["Menos de 3.5 Golos"], odds["U35"]),
                        (f"Ambas Marcam: Sim ({home} vs {away})", res["Ambas Marcam (Sim)"], odds["BTTS_Y"]),
                        (f"Ambas Marcam: Não ({home} vs {away})", res["Ambas Marcam (Não)"], odds["BTTS_N"]),
                        (f"Handicap +1.5 ({home})", res["Handicap +1.5 (Casa)"], odds["AH_P15"]),
                        (f"Handicap +0.5 ({home})", res["Handicap +0.5 (Casa)"], odds["AH_P05"]),
                        (f"Empate Anula ({home})", res["Empate Anula (Casa)"], odds["AH_00"]),
                        (f"Handicap -0.5 ({home})", res["Handicap -0.5 (Casa)"], odds["AH_M05"]),
                        (f"Handicap -1.0 ({home})", res["Handicap -1.0 (Casa)"], odds["AH_M10"]),
                        (f"Handicap -1.5 ({home})", res["Handicap -1.5 (Casa)"], odds["AH_M15"])
                    ]
                    
                    for m_name, prob, odd in game_mkts:
                        # Sweet Spot Filter para o Portfólio (Valor real, odd mínima aceitável)
                        if odd > 1.40 and odd <= 3.50:
                            edge = (prob * odd) - 1
                            if edge > 0.05: # Ouro ou Verde Forte
                                kelly = max(0, (edge/(odd-1)) * 0.25)
                                portfolio.append({"Jogo/Aposta": m_name, "Certeza": prob, "Odd Casa": odd, "Lucro Extra": edge, "Kelly_Frac": kelly})
                
                progress_bar.progress((i + 1) / len(fix_data))
                time.sleep(0.5) 
                
            status_text.text("Varredura Concluída! A compilar Portfólio de Risco...")
            
            if len(portfolio) > 0:
                df_port = pd.DataFrame(portfolio)
                df_port = df_port.sort_values(by="Lucro Extra", ascending=False).head(5) 
                
                total_kelly = df_port["Kelly_Frac"].sum()
                if total_kelly > 0:
                    df_port["Stake (€)"] = (df_port["Kelly_Frac"] / total_kelly) * (bankroll * min(total_kelly, 0.20)) 
                else:
                    df_port["Stake (€)"] = 0
                    
                st.markdown(f"""
                <div class="portfolio-card">
                    <h3 style="margin-top:0; color:#FFD700;">💼 O TEU PORTFÓLIO DE INVESTIMENTO (TOP 5)</h3>
                    <p style="color:#94A3B8; font-size:0.9rem;">O sistema avaliou todos os jogos e handicaps possíveis. Estas são as {len(df_port)} apostas com erro crítico da casa. A tua banca de {bankroll}€ foi distribuída matematicamente para diluir o risco (Markowitz Portfolio Theory).</p>
                </div>
                """, unsafe_allow_html=True)
                
                fig_port = go.Figure(data=[go.Table(
                    columnorder = [1,2,3,4,5], columnwidth = [250, 100, 100, 100, 120],
                    header=dict(values=['<b>JOGO / APOSTA (MERCADOS TOTAIS)</b>', '<b>CERTEZA</b>', '<b>ODD CASA</b>', '<b>LUCRO EXTRA</b>', '<b>STAKE RECOMENDADA</b>'], fill_color='#020408', align='center', font=dict(color='#64748B', size=11), height=45),
                    cells=dict(values=[df_port["Jogo/Aposta"], df_port["Certeza"].map('{:.1%}'.format), df_port["Odd Casa"].map('{:.2f}'.format), df_port["Lucro Extra"].map('{:+.1%}'.format), df_port["Stake (€)"].map('{:.2f}€'.format)], fill_color='#0B1120', align='center', font=dict(color=['#FFFFFF', '#E2E8F0', '#E2E8F0', '#00FF88', '#FFD700'], size=13, family='JetBrains Mono'), height=45)
                )])
                fig_port.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=(len(df_port)*45)+50, paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_port, use_container_width=True)
            else:
                st.error("A varredura completa aos 17 mercados foi terminada. Nenhuma odd bateu a matemática com a margem de segurança de >5% de vantagem. Guarda a banca para amanhã.")
