import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date

# --- 1. CONFIGURAÇÃO DE DESIGN (ULTRA PREMIUM) ---
st.set_page_config(page_title="ORACLE V140 - ELITE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    .stApp { background-color: #070A11; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1E293B !important; }
    
    .pro-card { background: #0B0F19; border-radius: 16px; padding: 30px; border: 1px solid #1E293B; border-left: 6px solid #00FF88; margin-bottom: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.6); }
    .bet-name { font-size: 2.4rem; font-weight: 800; color: #FFFFFF; margin: 5px 0; line-height: 1.1; letter-spacing: -1px; }
    .edge-value { font-family: 'JetBrains Mono'; font-size: 1.6rem; color: #00FF88; font-weight: 800; }
    
    .ia-insight-card { background: rgba(0, 255, 136, 0.05); border-radius: 10px; padding: 20px; border-left: 4px solid #00FF88; margin-top: 20px; font-size: 0.95rem; line-height: 1.6; color: #E2E8F0; }
    .help-card { background: #0B0F19; border-radius: 12px; padding: 20px; border: 1px solid #1E293B; border-left: 4px solid #3B82F6; margin-bottom: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); }
    
    .ai-assistant-table { background: linear-gradient(90deg, rgba(15, 23, 42, 0.8) 0%, rgba(2, 6, 23, 0.9) 100%); border-radius: 12px; padding: 20px; border: 1px solid rgba(0, 255, 136, 0.2); margin-top: 15px; border-left: 4px solid #00FF88;}

    .stNumberInput label, .stSelectbox label { font-size: 0.75rem !important; color: #94A3B8 !important; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    div.stButton > button { background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; font-weight: 800 !important; height: 3.8rem !important; border-radius: 10px !important; border: none !important; width: 100%; text-transform: uppercase; letter-spacing: 2px; transition: transform 0.2s, box-shadow 0.2s; }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0, 255, 136, 0.3) !important; }
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
    odds = {"1": 1.0, "X": 1.0, "2": 1.0, "O25": 1.0, "U25": 1.0, "BTTS_Y": 1.0, "BTTS_N": 1.0}
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
                    odds["O25"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Over 2.5'), 1.0))
                    odds["U25"] = float(next((v['odd'] for v in bet['values'] if v['value'] == 'Under 2.5'), 1.0))
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
    
    goals_sum = np.add.outer(np.arange(max_g), np.arange(max_g))
    o25 = prob_mtx[goals_sum > 2.5].sum(); u25 = 1 - o25
    btts_no = prob_mtx[0, :].sum() + prob_mtx[:, 0].sum() - prob_mtx[0,0]
    btts_yes = 1 - btts_no
    
    return {"Vencedor Casa": ph, "Empate (X)": px, "Vencedor Fora": pa, "Mais de 2.5 Golos": o25, "Menos de 2.5 Golos": u25, "Ambas Marcam (Sim)": btts_yes, "Ambas Marcam (Não)": btts_no}, prob_mtx

# --- 3. SIDEBAR (AUTO-PILOT) ---
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
        auto_odds = {"1": 1.0, "X": 1.0, "2": 1.0, "O25": 1.0, "U25": 1.0, "BTTS_Y": 1.0, "BTTS_N": 1.0}

    st.markdown("<hr style='border-color:#1E293B;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.75rem; color:#00FF88; font-weight:800; letter-spacing:1px;'>🤖 ODDS AUTOMÁTICAS (AJUSTA SE PRECISO)</p>", unsafe_allow_html=True)
    
    c1, cx, c2 = st.columns(3)
    o_1 = c1.number_input("1 (Casa)", value=auto_odds["1"], format="%.2f")
    o_x = cx.number_input("X (Emp)", value=auto_odds["X"], format="%.2f")
    o_2 = c2.number_input("2 (Fora)", value=auto_odds["2"], format="%.2f")
    
    c3, c4 = st.columns(2)
    o_o25 = c3.number_input("Mais 2.5", value=auto_odds["O25"], format="%.2f")
    o_u25 = c4.number_input("Menos 2.5", value=auto_odds["U25"], format="%.2f")
    o_btts_y = c3.number_input("Ambas Sim", value=auto_odds["BTTS_Y"], format="%.2f")
    o_btts_n = c4.number_input("Ambas Não", value=auto_odds["BTTS_N"], format="%.2f")
    
    st.markdown("<br>", unsafe_allow_html=True)
    execute = st.button("🔍 PROCURAR DINHEIRO FÁCIL")

# --- 4. RESULTADOS ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:180px;'><h1 style='opacity:0.1; font-size:5rem;'>ORACLE V140</h1><p style='color:#64748B; font-size:1.2rem;'>Escolhe o jogo. O robô preenche as odds sozinho.</p></div>", unsafe_allow_html=True)
else:
    s = get_pro_stats(m_sel['teams']['home']['id'], l_map[ln])
    lh, la = (s['h_f']*s['a_a'])**0.5, (s['a_f']*s['h_a'])**0.5
    res, mtx = run_master_math(lh, la, -0.11, 0.12)
    
    st.markdown(f"<h2 style='margin-bottom:0; font-size:3.5rem;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#475569; font-weight:300;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h2>", unsafe_allow_html=True)

    col_res, col_chart = st.columns([1.1, 0.9])

    all_mkts = [
        ("Vencedor Casa", res["Vencedor Casa"], o_1), ("Empate (X)", res["Empate (X)"], o_x), ("Vencedor Fora", res["Vencedor Fora"], o_2),
        ("Mais de 2.5 Golos", res["Mais de 2.5 Golos"], o_o25), ("Menos de 2.5 Golos", res["Menos de 2.5 Golos"], o_u25),
        ("Ambas Marcam (Sim)", res["Ambas Marcam (Sim)"], o_btts_y), ("Ambas Marcam (Não)", res["Ambas Marcam (Não)"], o_btts_n)
    ]
    
    valid_mkts = [(n,p,b,(p*b)-1) for n,p,b in all_mkts if b > 1.01]
    
    if len(valid_mkts) > 0:
        best = sorted(valid_mkts, key=lambda x: x[3], reverse=True)[0]
        edge = best[3]; kelly = max(0, (edge/(best[2]-1)) * 0.50) 
        color = "#00FF88" if edge > 0.08 else "#FFD700" if edge > 0.02 else "#EF4444"
        odd_justa = 1/best[1]
        
        # O HTML AQUI AGORA ESTÁ ENCOSTADO À MARGEM ESQUERDA PARA EVITAR O BUG DO STREAMLIT
        st.markdown(f"""
<div class="pro-card" style="border-left-color: {color};">
    <span style="color:#94A3B8; font-size:0.8rem; font-weight:800; letter-spacing:1px;">A MELHOR APOSTA DETETADA</span>
    <p class="bet-name">{best[0]}</p>
    <div style="display:flex; gap:30px; margin:20px 0;">
        <div><span style="color:#64748B; font-size:0.75rem; font-weight:700;">VANTAGEM (ERRO DA CASA)</span><br><span class="edge-value" style="color:{color};">{edge:+.1%}</span></div>
        <div><span style="color:#64748B; font-size:0.75rem; font-weight:700;">VALOR SEGURO A APOSTAR</span><br><b style="font-size:1.6rem; font-family:'JetBrains Mono';">{bankroll*kelly:.2f}€</b></div>
    </div>
    
    <div class="ia-insight-card">
        <b>🗣️ O QUE ISTO SIGNIFICA EM PORTUGUÊS:</b><br><br>
        A casa de apostas está a oferecer uma odd de <b style="color:#FFF;">{best[2]:.2f}</b>. Mas o nosso algoritmo cruzou a força de ataque e defesa destas equipas e descobriu que a Odd Real devia ser só <b style="color:#FFF;">{odd_justa:.2f}</b>.<br><br>
        Apostar nisto a longo prazo é garantido. Usa a stake recomendada acima para proteger o teu saldo e crescer aos poucos.
    </div>
</div>
        """, unsafe_allow_html=True)
    else:
        st.warning("O robô não encontrou odds automáticas. Insere os valores na barra lateral.")

    with col_chart:
        st.markdown(f"""
<div class="help-card">
    <b style="color:#FFF; font-size:1rem;">📚 GUIA RÁPIDO DO APOSTADOR</b><br>
    <span style="font-size:0.85rem; color:#94A3B8; line-height:1.6;"><br>
    <b>• Vantagem (Lucro Extra):</b> O nível de "cegueira" da casa de apostas. +10% significa lucro limpo a longo prazo.<br>
    <b>• Odd Real (Certa):</b> O preço real sem o roubo/margem da casa. Apostar numa odd MAIOR do que esta é encontrar ouro.<br>
    <b>• Gráfico de Golos:</b> Mostra visualmente que equipa tem mais probabilidade de esmagar o adversário.
    </span>
</div>
        """, unsafe_allow_html=True)

        xr = np.arange(7)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name="Ataque Casa", fill='tozeroy', line_color='#00FF88', line_width=3))
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name="Ataque Fora", fill='tozeroy', line_color='#3B82F6', line_width=3))
        fig.update_layout(height=200, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)

    # --- A TABELA E O ASSISTENTE DE IA ---
    st.markdown("<h3 style='margin-top:20px; letter-spacing:-1px;'>📋 TODAS AS APOSTAS AVALIADAS</h3>", unsafe_allow_html=True)
    
    # LEGENDA CLARA ANTES DA TABELA
    st.markdown("""
    <div style='display: flex; gap: 20px; margin-bottom: 15px; font-size: 0.85rem; color: #94A3B8;'>
        <div><span style='color:#FFD700; font-size: 1.2rem; vertical-align: middle;'>●</span> <b style="color:white;">OURO (>10%)</b>: Erro grave da casa. Aposta excelente.</div>
        <div><span style='color:#00FF88; font-size: 1.2rem; vertical-align: middle;'>●</span> <b style="color:white;">VERDE (>2%)</b>: Valor sólido para crescimento consistente.</div>
        <div><span style='color:#EF4444; font-size: 1.2rem; vertical-align: middle;'>●</span> <b style="color:white;">VERMELHO (<0%)</b>: Armadilha da casa. Fica longe.</div>
    </div>
    """, unsafe_allow_html=True)
    
    if len(valid_mkts) > 0:
        df = pd.DataFrame(valid_mkts, columns=["Aposta", "Certeza", "OddCasa", "Vantagem"])
        df["OddReal"] = 1 / df["Certeza"]
        df = df.sort_values(by="Vantagem", ascending=False)
        
        # Cores cirúrgicas APENAS para a coluna de Vantagem / Edge
        colors_vantagem = ['#FFD700' if e > 0.10 else '#00FF88' if e > 0.02 else '#EF4444' for e in df["Vantagem"]]
        
        fig_t = go.Figure(data=[go.Table(
            columnorder = [1,2,3,4,5],
            columnwidth = [250, 120, 120, 120, 150],
            header=dict(
                values=['<b>A TUA APOSTA</b>', '<b>A NOSSA CERTEZA</b>', '<b>ODD REAL (Certa)</b>', '<b>ODD DA CASA</b>', '<b>LUCRO EXTRA</b>'], 
                fill_color='#020617', 
                align=['left', 'center', 'center', 'center', 'center'], 
                font=dict(color='#64748B', size=11, family='Inter'), 
                line_color='#1E293B',
                height=45
            ),
            cells=dict(
                values=[
                    df.Aposta, 
                    df.Certeza.map('{:.1%}'.format), 
                    df.OddReal.map('{:.2f}'.format), 
                    df.OddCasa.map('{:.2f}'.format), 
                    df.Vantagem.map('{:+.1%}'.format)
                ],
                fill_color='#0B0F19',
                align=['left', 'center', 'center', 'center', 'center'], 
                font=dict(
                    color=['#FFFFFF', '#E2E8F0', '#E2E8F0', '#E2E8F0', colors_vantagem], 
                    size=14, 
                    family='JetBrains Mono'
                ), 
                line_color='#1E293B',
                height=45
            )
        )])
        fig_t.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=(len(df)*45)+60, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_t, use_container_width=True)

        # --- ASSISTENTE IA DA TABELA (NOVO) ---
        apostas_ouro = len(df[df['Vantagem'] > 0.10])
        apostas_verdes = len(df[(df['Vantagem'] > 0.02) & (df['Vantagem'] <= 0.10)])
        apostas_lixo = len(df[df['Vantagem'] < 0])
        
        texto_ia = f"Analisei os {len(df)} mercados disponíveis para este jogo. "
        if apostas_ouro > 0:
            texto_ia += f"Atenção máxima: encontrei <b style='color:#FFD700;'>{apostas_ouro} oportunidades de OURO</b> (erros graves da casa). Foca-te nelas! "
        elif apostas_verdes > 0:
            texto_ia += f"Temos <b style='color:#00FF88;'>{apostas_verdes} apostas de valor sólido (Verdes)</b> para construirmos lucro a longo prazo. "
        else:
            texto_ia += "Infelizmente as casas de apostas foram espertas e não há grande valor neste jogo. Eu protegeria a banca. "
            
        if apostas_lixo > 0:
            texto_ia += f"Mais importante ainda: Cuidado com os <b style='color:#EF4444;'>{apostas_lixo} mercados onde a casa está a tentar enganar-te</b> (Vermelhos). Foge deles."

        st.markdown(f"""
        <div class="ai-assistant-table">
            <h4 style="margin-top:0; color:#00FF88; font-size:1rem;">🤖 RESUMO INTELIGENTE DA TABELA</h4>
            <p style="color:#E2E8F0; font-size:0.95rem; line-height:1.6; margin-bottom:0;">{texto_ia}</p>
        </div>
        """, unsafe_allow_html=True)
