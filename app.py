import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
import requests
import textwrap
from datetime import date
import plotly.graph_objects as go

# --- 1. CONFIGURAÇÃO DE DESIGN ---
st.set_page_config(page_title="ORACLE V140 - AUTOMATIZADO", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #0B0F19; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #070A11 !important; border-right: 1px solid #1E293B !important; }
    
    .pro-card { background: #111827; border-radius: 12px; padding: 25px; border: 1px solid #1E293B; border-left: 6px solid #00FF88; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .bet-name { font-size: 2.2rem; font-weight: 800; color: #FFFFFF; margin: 0; line-height: 1.1; letter-spacing: -1px; }
    .edge-value { font-size: 1.4rem; color: #00FF88; font-weight: 800; }
    
    .ia-insight-card { background: rgba(0, 255, 136, 0.05); border-radius: 8px; padding: 15px; border-left: 4px solid #00FF88; margin-top: 15px; font-size: 0.95rem; line-height: 1.5; color: #E2E8F0; }
    .help-card { background: #1E293B; border-radius: 8px; padding: 15px; border-left: 4px solid #3B82F6; margin-bottom: 15px; }
    
    .stNumberInput label, .stSelectbox label { font-size: 0.75rem !important; color: #94A3B8 !important; font-weight: 700; text-transform: uppercase; }
    div.stButton > button { background: linear-gradient(90deg, #00FF88 0%, #00BD63 100%) !important; color: #000000 !important; font-weight: 800 !important; height: 3.5rem !important; border-radius: 8px !important; border: none !important; width: 100%; transition: transform 0.2s; }
    div.stButton > button:hover { transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE API, ODDS AUTOMÁTICAS E MATEMÁTICA ---
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
    # Tenta ir buscar as odds à Bet365 (Bookmaker ID 8)
    odds = {"1": 1.0, "X": 1.0, "2": 1.0, "O25": 1.0, "U25": 1.0, "BTTS_Y": 1.0, "BTTS_N": 1.0}
    try:
        r = requests.get(f"https://{api_host}/odds", headers=headers, params={"fixture": fixture_id, "bookmaker": 8}).json()
        if r['response']:
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
    h_win_1 = np.trace(prob_mtx, offset=-1)
    ah0_h = ph / (ph + pa) if (ph + pa) > 0 else 0
    ah_m1_h = (ph - h_win_1) / (1 - h_win_1) if (1 - h_win_1) > 0 else 0
    
    goals_sum = np.add.outer(np.arange(max_g), np.arange(max_g))
    o25 = prob_mtx[goals_sum > 2.5].sum(); u25 = 1 - o25
    
    btts_no = prob_mtx[0, :].sum() + prob_mtx[:, 0].sum() - prob_mtx[0,0]
    btts_yes = 1 - btts_no
    
    return {
        "Vencedor: Casa": ph, "Empate (X)": px, "Vencedor: Fora": pa,
        "Empate Anula (Casa)": ah0_h, "Handicap -1.0 (Casa)": ah_m1_h,
        "Mais de 2.5 Golos": o25, "Menos de 2.5 Golos": u25,
        "Ambas Marcam (Sim)": btts_yes, "Ambas Marcam (Não)": btts_no
    }, prob_mtx

# --- 3. SIDEBAR (AUTO-ODDS INJECTED) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF88; margin:0;'>🏛️ ORACLE V140</h2>", unsafe_allow_html=True)
    
    bankroll = st.number_input("💰 A TUA BANCA (€)", value=100.0, step=10.0)
    
    l_map = {"Premier League": 39, "La Liga": 140, "Primeira Liga": 94, "Champions League": 2}
    ln = st.selectbox("⚽ LIGA", list(l_map.keys()))
    
    fix = requests.get(f"https://{api_host}/fixtures", headers=headers, params={"date": date.today().strftime('%Y-%m-%d'), "league": l_map[ln], "season": "2025"}).json().get('response', [])
    if fix:
        m_map = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f['fixture']['id'] for f in fix}
        m_display = st.selectbox("JOGO", list(m_map.keys()))
        m_sel = next(f for f in fix if f['fixture']['id'] == m_map[m_display])
        
        # Puxa as odds automáticas se existirem
        auto_odds = get_auto_odds(m_sel['fixture']['id'])
    else: 
        m_sel = None
        auto_odds = {"1": 1.0, "X": 1.0, "2": 1.0, "O25": 1.0, "U25": 1.0, "BTTS_Y": 1.0, "BTTS_N": 1.0}

    st.markdown("<hr style='border-color:#1E293B;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.7rem; color:#00FF88; font-weight:bold;'>🤖 ODDS AUTOMÁTICAS (CORRIGE SE NECESSÁRIO)</p>", unsafe_allow_html=True)
    
    c1, cx, c2 = st.columns(3)
    o_1 = c1.number_input("1 (Casa)", value=auto_odds["1"], format="%.2f")
    o_x = cx.number_input("X (Empate)", value=auto_odds["X"], format="%.2f")
    o_2 = c2.number_input("2 (Fora)", value=auto_odds["2"], format="%.2f")
    
    c3, c4 = st.columns(2)
    o_o25 = c3.number_input("Mais 2.5 Golos", value=auto_odds["O25"], format="%.2f")
    o_u25 = c4.number_input("Menos 2.5 Golos", value=auto_odds["U25"], format="%.2f")
    
    c5, c6 = st.columns(2)
    o_btts_y = c5.number_input("Ambas Sim", value=auto_odds["BTTS_Y"], format="%.2f")
    o_btts_n = c6.number_input("Ambas Não", value=auto_odds["BTTS_N"], format="%.2f")
    
    st.markdown("<br>", unsafe_allow_html=True)
    execute = st.button("🔍 PROCURAR DINHEIRO FÁCIL")

# --- 4. RESULTADOS (INTERFACE LIMPA E EXPLICATIVA) ---
if not execute or not m_sel:
    st.markdown("<div style='text-align:center; padding-top:150px;'><h1 style='opacity:0.2;'>ORACLE V140</h1><p style='color:#64748B;'>Escolhe o jogo. O robô irá preencher as odds sozinho e fazer as contas.</p></div>", unsafe_allow_html=True)
else:
    s = get_pro_stats(m_sel['teams']['home']['id'], l_map[ln])
    lh, la = (s['h_f']*s['a_a'])**0.5, (s['a_f']*s['h_a'])**0.5
    res, mtx = run_master_math(lh, la, -0.11, 0.12)
    
    st.markdown(f"<h2 style='margin-bottom:0; font-size:3.5rem;'>{m_sel['teams']['home']['name'].upper()} <span style='color:#475569; font-weight:300;'>vs</span> {m_sel['teams']['away']['name'].upper()}</h2>", unsafe_allow_html=True)

    col_res, col_chart = st.columns([1.1, 0.9])

    all_mkts = [
        ("Vencedor: Casa", res["Vencedor: Casa"], o_1), ("Empate (X)", res["Empate (X)"], o_x), ("Vencedor: Fora", res["Vencedor: Fora"], o_2),
        ("Mais de 2.5 Golos", res["Mais de 2.5 Golos"], o_o25), ("Menos de 2.5 Golos", res["Menos de 2.5 Golos"], o_u25),
        ("Ambas Marcam (Sim)", res["Ambas Marcam (Sim)"], o_btts_y), ("Ambas Marcam (Não)", res["Ambas Marcam (Não)"], o_btts_n)
    ]
    
    valid_mkts = [(n,p,b,(p*b)-1) for n,p,b in all_mkts if b > 1.01]
    
    if len(valid_mkts) > 0:
        best = sorted(valid_mkts, key=lambda x: x[3], reverse=True)[0]
        edge = best[3]; kelly = max(0, (edge/(best[2]-1)) * 0.50) # Half-Kelly fixo
        color = "#00FF88" if edge > 0.08 else "#FFD700" if edge > 0.02 else "#EF4444"
        odd_justa = 1/best[1]
        
        # Corrigido o bug do bloco branco usando textwrap.dedent para ignorar identações do Python
        html_card = f"""
        <div class="pro-card" style="border-left-color: {color};">
            <span style="color:#64748B; font-size:0.75rem; font-weight:800;">A MELHOR APOSTA DETETADA</span>
            <p class="bet-name">{best[0]}</p>
            <div style="display:flex; gap:20px; margin:15px 0;">
                <div><span style="color:#64748B; font-size:0.7rem;">O ERRO DA CASA (VANTAGEM)</span><br><span class="edge-value" style="color:{color};">{edge:+.1%}</span></div>
                <div><span style="color:#64748B; font-size:0.7rem;">VALOR APOSTAR (SEGURO)</span><br><b style="font-size:1.4rem;">{bankroll*kelly:.2f}€</b></div>
            </div>
            
            <div class="ia-insight-card">
                <b>🗣️ O QUE ISTO SIGNIFICA:</b><br>
                A casa de apostas acha que a odd correta é <b>{best[2]}</b>. Mas o nosso algoritmo, cruzando a força de ataque e defesa de ambas as equipas, sabe que a Odd Justa é apenas <b>{odd_justa:.2f}</b>.<br><br>
                Apostar nisto a longo prazo é como comprar uma nota de 10€ por 8€. 
            </div>
        </div>
        """
        with col_res: st.markdown(textwrap.dedent(html_card), unsafe_allow_html=True)
    else:
        with col_res: st.warning("Ainda não temos odds automáticas para este jogo. Insere os valores manualmente.")

    with col_chart:
        st.markdown(f"""
        <div class="help-card">
            <b>📚 O GUIA RÁPIDO DO APOSTADOR</b><br>
            <span style="font-size:0.8rem; color:#94A3B8;">
            <b>• Vantagem (Lucro Extra):</b> Mostra o quão errada está a casa de apostas. Valores verdes ou amarelos significam lucro garantido a longo prazo.<br>
            <b>• Odd Real (Certa):</b> É a odd sem a margem de lucro (o roubo) da casa. Se a casa te paga MAIS do que a Odd Real, tens de apostar.
            </span>
        </div>
        """, unsafe_allow_html=True)

        xr = np.arange(7)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=1), name="Ataque Casa", fill='tozeroy', line_color='#00FF88', line_width=3))
        fig.add_trace(go.Scatter(x=xr, y=mtx.sum(axis=0), name="Ataque Fora", fill='tozeroy', line_color='#3B82F6', line_width=3))
        fig.update_layout(title="Quem vai marcar mais golos?", title_font_color="#64748B", height=180, margin=dict(l=0,r=0,t=30,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)

    # TABELA NATIVA (MUITO MAIS LIMPA E INTUITIVA)
    st.markdown("### 📋 TODAS AS APOSTAS AVALIADAS")
    
    if len(valid_mkts) > 0:
        df = pd.DataFrame(valid_mkts, columns=["Aposta", "Nossa Certeza", "Odd da Casa", "Vantagem"])
        df["Odd Certa"] = 1 / df["Nossa Certeza"]
        df["Vantagem Num"] = df["Vantagem"] * 100 # Para pintar a cor
        
        # Reordenar colunas para leitura natural
        df = df[["Aposta", "Nossa Certeza", "Odd Certa", "Odd da Casa", "Vantagem Num"]]
        df = df.sort_values(by="Vantagem Num", ascending=False)
        
        # Formatar a tabela para ser ultra limpa no Streamlit
        st.dataframe(
            df,
            column_config={
                "Aposta": st.column_config.TextColumn("Qual é a Aposta?", width="medium"),
                "Nossa Certeza": st.column_config.ProgressColumn("Nossa Certeza (%)", format="%.1f%%", min_value=0, max_value=1),
                "Odd Certa": st.column_config.NumberColumn("Odd Real (Certa)", format="%.2f"),
                "Odd da Casa": st.column_config.NumberColumn("Odd da Casa", format="%.2f"),
                "Vantagem Num": st.column_config.NumberColumn("O Teu Lucro Extra", format="%+.1f%%")
            },
            hide_index=True,
            use_container_width=True
        )
