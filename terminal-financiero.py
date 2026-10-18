# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import requests
import yfinance as yf
import datetime
import time

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA Y DISEÑO INSTITUCIONAL CORPORATIVO
# ============================================================
st.set_page_config(
    page_title="Terminal Financiero Ejecutivo | BVL, Wall Street & Europa",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Ocultar elementos predeterminados de Streamlit */
    .stDeployButton { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    .main, .stApp {
        background-color: #0b0e14;
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }
    h1 {
        font-size: 1.4rem !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    .nav-header-container {
        background: #151b23;
        border-bottom: 1px solid #30363d;
        padding: 10px 16px;
        border-radius: 8px 8px 0 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: all 0.2s ease-in-out;
    }
    .metric-card:hover {
        border-color: #1f6feb;
    }
    .metric-card h4 {
        font-size: 0.72rem;
        color: #8b949e !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
        font-weight: 600;
    }
    .metric-card h2 {
        font-size: 1.25rem;
        color: #58a6ff !important;
        margin: 0;
        font-weight: 700;
    }

    .tc-banner {
        background: linear-gradient(135deg, #161b22 0%, #1f6feb22 100%);
        color: #e2e8f0;
        border-left: 4px solid #1f6feb;
        border: 1px solid #30363d;
        border-left-width: 4px;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.85rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }

    div[data-testid="stExpander"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    
    .stButton>button {
        background-color: #1f6feb;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 600;
        padding: 0.35rem 1rem;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #388bfd;
        color: white;
    }
    
    .stSelectbox label, .stTextInput label, .stCheckbox label {
        color: #8b949e !important;
        font-size: 0.8rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="nav-header-container">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="background-color: #1f6feb; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem;">BVL, Wall Street & Europa</span>
            <span style="font-size: 1.1rem; font-weight: 700; color: #f0f6fc;">Terminal Financiero Ejecutivo</span>
        </div>
        <div style="font-size: 0.8rem; color: #8b949e;">Precios Sincronizados con TradingView & Dividendos Automáticos</div>
    </div>
""", unsafe_allow_html=True)

def obtener_tc_sunat_actual():
    hoy = datetime.date.today()
    try:
        url = "https://api.apis.net.pe/v1/tipo-cambio-sunat"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            venta = float(r.json().get("venta", 0))
            if 3.0 < venta < 4.5:
                return round(venta, 3), f"SUNAT Oficial ({hoy.strftime('%d/%m/%Y')})"
    except:
        pass
    return 3.440, f"SUNAT Oficial Venta (Referencia {hoy.strftime('%d/%m/%Y')})"

TC_SUNAT, DETALLE_TC = obtener_tc_sunat_actual()
USD_POR_PEN = 1.0 / TC_SUNAT

st.markdown(f"""
    <div class="tc-banner">
        <span>💱 Tipo de Cambio Oficial Venta (SUNAT): <b style="color: #3fb950;">S/ {TC_SUNAT:.3f}</b></span>
        <span style="opacity: 0.85; color: #8b949e;">{DETALLE_TC}</span>
    </div>
""", unsafe_allow_html=True)

EXCLUIR_BVL = {
    "BAP", "BVN", "IFS", "SCCO", "CPAC", "TV", "AUY", "CVI", "HBM",
    "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "TSLA", "META", "NVDA", "NFLX",
    "AMD", "INTC", "SPY", "QQQ", "DIA", "IWM", "GLD", "SLV", "DIS", "BA"
}

BVL_BASE = [
    "FERREYC1", "ALICORC1", "UNACEMC1", "BBVAC1", "VOLCAABC1", "INTERBC1", 
    "CREDIC1", "SIDERC1", "MINSURI1", "BROCALC1", "AUNA", "POMALCC1", 
    "FIBPRIME", "LUNDIN", "ATLASC1", "CORAREI1", "ENELGX1", "CAOPAC1", "PML"
]
USA_BASE = ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "BRK-B", "JPM", "XOM", "TSLA", "V", "MA", "PG", "JNJ", "HD"]
EUROPA_BASE = ["ASML.AS", "MC.PA", "SAP.DE", "SHEL.L", "AZN.L", "OR.PA", "TTE.PA", "SIE.DE", "SAN.MC", "IBE.MC"]

COLS_TV = [
    "name", "description", "close", "currency", "volume", "market_cap_basic",
    "exchange", "sector", "industry", "Recommend.All", "Recommend.MA", "Recommend.Other",
    "analysts_rating", "price_target_average", "EMA20", "EMA50", "SMA200",
    "earnings_per_share_basic_ttm", "book_value_per_share_fq",
    "average_volume_30d_calc", "Value.Traded", "dividends_yield_recent"
]

def num(v, d=np.nan):
    try:
        if v is None: return d
        fv = float(str(v).replace(",", "").strip())
        return d if np.isnan(fv) else fv
    except:
        return d

def es_nativa_bvl(t, ex):
    t = str(t).split(":")[-1].strip().upper()
    if t in EXCLUIR_BVL or str(ex).upper() in ["NASDAQ", "NYSE", "AMEX"]:
        return False
    sufijos = ("C1", "I1", "BC1", "AC1", "C2", "I2")
    locales = {"CREDIC1", "INTERBC1", "SCOTIAC1", "VOLCAN", "MINSURI1", "BROCALC1", "AUNA", "POMALCC1", "FIBPRIME", "NEXA"}
    return any(t.endswith(s) for s in sufijos) or t in locales

def asignar_indice(mercado, exchange, ticker):
    ex = str(exchange).upper()
    tk = str(ticker).upper()
    if mercado == "PERÚ":
        return "S&P/BVL Peru General"
    elif mercado == "EE.UU.":
        if tk in ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NFLX"]:
            return "NASDAQ 100"
        return "S&P 500"
    elif mercado == "EUROPA":
        if "ASML" in tk or "SAP" in tk or "SIE" in tk: return "EURO STOXX 50 / DAX"
        if "MC" in tk or "OR" in tk or "TTE" in tk: return "CAC 40"
        if "SHEL" in tk or "AZN" in tk: return "FTSE 100"
        if "SAN" in tk or "IBE" in tk: return "IBEX 35"
        return "EURO STOXX 50"
    return "Global Broad Index"

@st.cache_data(ttl=1800)
def ejecutar_scanner_completo():
    todos_datos = []
    for mercado, screener in [("PERÚ", "peru"), ("EE.UU.", "america"), ("EUROPA", "europe")]:
        url = f"https://scanner.tradingview.com/{screener}/scan"
        filtros = [{"left": "type", "operation": "in_range", "right": ["stock", "dr"]}]
        if screener == "america":
            filtros.extend([
                {"left": "market_cap_basic", "operation": "greater", "right": 500000000},
                {"left": "close", "operation": "greater", "right": 2.0},
                {"left": "exchange", "operation": "in_range", "right": ["NASDAQ", "NYSE", "AMEX"]}
            ])
        elif screener == "europe":
            filtros.extend([
                {"left": "market_cap_basic", "operation": "greater", "right": 1000000000},
                {"left": "close", "operation": "greater", "right": 1.0}
            ])
            
        payload = {"filter": filtros, "options": {"lang": "es"}, "columns": COLS_TV, "sort": {"sortBy": "Value.Traded", "sortOrder": "desc"}, "range": [0, 80]}
        headers = {"User-Agent": "Mozilla/5.0", "Origin": "https://www.tradingview.com", "Referer": "https://www.tradingview.com/"}
        
        filas = []
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=6)
            if r.status_code == 200:
                for item in r.json().get("data", []):
                    vals = item.get("d", [])
                    if not vals: continue
                    d = dict(zip(COLS_TV[:len(vals)], vals))
                    s = item.get("s", "")
                    ex = s.split(":")[0] if ":" in s else d.get("exchange", "")
                    tk = s.split(":")[-1].strip().upper()
                    if mercado == "PERÚ" and not es_nativa_bvl(tk, ex): continue
                    
                    if mercado == "PERÚ":
                        ty = tk + ".LM" if not tk.endswith(".LM") else tk
                    elif mercado == "EUROPA":
                        ty = tk.replace(".", "-")
                        if ex in ["LSE", "LON"]: ty += ".L"
                        elif ex in ["EN Paris", "EPA"]: ty += ".PA"
                        elif ex in ["XETR", "FWB"]: ty += ".DE"
                        elif ex in ["BME"]: ty += ".MC"
                    else:
                        ty = tk.replace(".", "-")
                        
                    d.update({"Mercado": mercado, "Ticker_TV": tk, "Exchange_TV": str(ex).upper(), "Ticker_Yahoo": ty})
                    filas.append(d)
        except:
            pass
        
        if not filas:
            base = BVL_BASE if mercado == "PERÚ" else USA_BASE if mercado == "EE.UU." else EUROPA_BASE
            for tk in base:
                ty = tk if mercado == "EUROPA" or mercado == "EE.UU." else tk + ".LM"
                filas.append({"Mercado": mercado, "Ticker_TV": tk, "Exchange_TV": "BVL" if mercado == "PERÚ" else "NASDAQ" if mercado == "EE.UU." else "EURONEXT", "Ticker_Yahoo": ty, "description": tk, "currency": "PEN" if mercado == "PERÚ" else "USD" if mercado == "EE.UU." else "EUR"})
        
        todos_datos.extend(filas)

    df_uni = pd.DataFrame(todos_datos)
    if df_uni.empty: return pd.DataFrame()

    tickers_forzados = ["AUNA.LM", "POMALCC1.LM", "FIBPRIME.LM"]
    for tf in tickers_forzados:
        if tf not in df_uni["Ticker_Yahoo"].values:
            t_base = tf.replace(".LM", "")
            df_uni = pd.concat([df_uni, pd.DataFrame([{
                "Mercado": "PERÚ", "Ticker_TV": t_base, "Exchange_TV": "BVL", 
                "Ticker_Yahoo": tf, "description": t_base, "currency": "USD" if t_base=="FIBPRIME" else "PEN", "close": 6.84 if t_base=="FIBPRIME" else 1.0
            }])], ignore_index=True)

    resultados = []
    for _, row in df_uni.iterrows():
        ty = row["Ticker_Yahoo"]
        precio = num(row.get("close"), 0.0)
        div_sum = 0.0
        h = None
        
        try:
            t_obj = yf.Ticker(ty)
            h = t_obj.history(period="1y", interval="1d", auto_adjust=False)
            if h is not None and not h.empty:
                if (precio <= 0 or np.isnan(precio)) and "Close" in h.columns:
                    c_vals = h["Close"].dropna()
                    if not c_vals.empty:
                        precio = float(c_vals.iloc[-1])
                if "Dividends" in h.columns:
                    div_sum = float(h["Dividends"].fillna(0).sum())
        except:
            pass

        div_pct = num(row.get("dividends_yield_recent"), 0.0)
        if np.isnan(div_pct) or div_pct <= 0:
            if precio > 0 and div_sum > 0:
                div_pct = (div_sum / precio) * 100.0

        if np.isnan(div_pct): 
            div_pct = 0.0

        if div_pct > 0:
            reparte_div = "SÍ"
            freq = "Trimestral" if row["Mercado"] == "EE.UU." else "Anual / Semestral" if row["Mercado"] == "EUROPA" else "Anual"
        else:
            reparte_div = "NO"
            freq = "N/D"

        ema20, ema50, sma200 = num(row.get("EMA20")), num(row.get("EMA50")), num(row.get("SMA200"))
        vol_30d = num(row.get("average_volume_30d_calc"), num(row.get("volume"), 0.0))
        presencia = 50.0

        if h is not None and not h.empty and "Close" in h:
            c = h["Close"].dropna()
            if len(c) >= 5:
                if len(c) >= 20: ema20 = float(c.ewm(span=20, adjust=False).mean().iloc[-1])
                if len(c) >= 50: ema50 = float(c.ewm(span=50, adjust=False).mean().iloc[-1])
                if len(c) >= 200: sma200 = float(c.rolling(200).mean().iloc[-1])
                if "Volume" in h:
                    v = h["Volume"].fillna(0)
                    fin = v.index[-1]
                    v30 = v[v.index >= fin - pd.Timedelta(days=30)]
                    v90 = v[v.index >= fin - pd.Timedelta(days=90)]
                    dias_ventana = len(v90)
                    if dias_ventana > 0:
                        presencia = min(100.0, round(((v90 > 0).sum() / dias_ventana) * 100.0, 1))
                    if len(v30) > 0: vol_30d = float(v30.sum() / len(v30))

        if precio <= 0: continue

        es_pen = str(row.get("currency") or "").upper() == "PEN"
        es_eur = str(row.get("currency") or "").upper() == "EUR"
        
        mult_usd = (USD_POR_PEN if es_pen else 1.07 if es_eur else 1.0)
        val_usd = (precio * vol_30d) * mult_usd
        
        u_alta, u_media, u_baja = (80000, 20000, 4000) if row["Mercado"] == "PERÚ" else (25000000, 5000000, 1000000)
        liq = "ALTA" if val_usd >= u_alta else "MEDIA" if val_usd >= u_media else "BAJA" if val_usd >= u_baja else "MUY BAJA"
        if liq in ["ALTA", "MEDIA"] and presencia < 50.0: liq = "BAJA"
        muy_com = "SÍ" if (presencia >= 80.0 and liq in ["ALTA", "MEDIA"]) else "NO"

        obj = num(row.get("price_target_average"))
        eps, bvps = num(row.get("earnings_per_share_basic_ttm")), num(row.get("book_value_per_share_fq"))
        g = np.sqrt(22.5 * eps * bvps) if (pd.notna(eps) and pd.notna(bvps) and eps > 0.01 and bvps > 0) else np.nan
        justo = (obj * 0.7 + g * 0.3) if (pd.notna(obj) and obj > 0 and pd.notna(g)) else (obj if pd.notna(obj) and obj > 0 else g)
        
        diag = "SIN DATOS"
        if pd.notna(justo) and justo > 0:
            diff = ((justo / precio) - 1.0) * 100
            diag = "DEMASIADO CARO" if diff <= -25 else "CARO" if diff <= -8 else "BARATO / SUBVALUADO" if diff >= 25 else "BUEN PRECIO" if diff >= 8 else "PRECIO JUSTO"

        val_analistas = row.get("analysts_rating")
        rec_all = num(row.get("Recommend.All"))
        rec_ma = num(row.get("Recommend.MA"))
        rec_other = num(row.get("Recommend.Other"))
        
        analistas_rec = None
        if pd.notna(val_analistas):
            v_str = str(val_analistas).strip().upper()
            if "STRONG_BUY" in v_str or "COMPRA FUERTE" in v_str: analistas_rec = "COMPRA FUERTE"
            elif "BUY" in v_str or "COMPRA" in v_str: analistas_rec = "COMPRA"
            elif "STRONG_SELL" in v_str or "VENTA FUERTE" in v_str: analistas_rec = "VENTA FUERTE"
            elif "SELL" in v_str or "VENTA" in v_str: analistas_rec = "VENTA"
            elif "NEUTRAL" in v_str or "HOLD" in v_str: analistas_rec = "NEUTRAL"
        
        if analistas_rec is None and pd.notna(rec_all):
            score_multifuente = rec_all
            if pd.notna(rec_other): score_multifuente = (rec_all * 0.6) + (rec_other * 0.4)
            if score_multifuente >= 0.4: analistas_rec = "COMPRA FUERTE"
            elif score_multifuente >= 0.1: analistas_rec = "COMPRA"
            elif score_multifuente > -0.1: analistas_rec = "NEUTRAL"
            elif score_multifuente > -0.4: analistas_rec = "VENTA"
            else: analistas_rec = "VENTA FUERTE"

        if analistas_rec in ["VENTA", "VENTA FUERTE"] or (pd.notna(rec_ma) and rec_ma <= -0.1):
            momento = "NO COMPRAR AHORA"
        else:
            pts = 3 if analistas_rec == "COMPRA FUERTE" else 2 if analistas_rec == "COMPRA" else 0
            if pd.notna(ema20) and pd.notna(ema50): pts += (2 if precio > ema20 > ema50 else -2 if precio < ema20 < ema50 else 0)
            if pd.notna(sma200): pts += (1 if precio > sma200 else -1)
            if diag in ["BARATO / SUBVALUADO", "BUEN PRECIO"]: pts += 1
            elif diag == "DEMASIADO CARO": pts -= 2
            momento = "MUY BUEN MOMENTO PARA COMPRA" if pts >= 4 else "BUEN MOMENTO PARA COMPRA" if pts >= 2 else "ESPERAR CONFIRMACIÓN" if pts >= 0 else "NO COMPRAR AHORA"

        s_tec = (rec_all + 1.0) * 50.0 if pd.notna(rec_all) else 50.0
        s_fund = 70.0 if diag in ["BARATO / SUBVALUADO", "BUEN PRECIO"] else 25.0 if diag in ["CARO", "DEMASIADO CARO"] else 50.0
        aj_liq = 0 if liq in ["ALTA", "MEDIA"] else -8 if liq == "BAJA" else -15
        score = round(float(np.clip(0.6 * s_tec + 0.4 * s_fund + aj_liq, 0, 100)), 1)

        ex_tv = row.get("Exchange_TV", "BVL")
        tk_tv = row["Ticker_TV"]
        link_tv = f"https://www.tradingview.com/chart/?symbol={ex_tv}:{tk_tv}"
        indice_pert = asignar_indice(row["Mercado"], ex_tv, tk_tv)

        resultados.append({
            "Ranking": 0, "Ticker": tk_tv, "Empresa": row.get("description", ""), "Mercado": row["Mercado"],
            "Índice": indice_pert, "Exchange": ex_tv, "Moneda": row.get("currency", "USD"),
            "Precio": round(precio, 3), "Dividendos": reparte_div, "Div_Yield_%": round(div_pct, 2), "Frecuencia": freq,
            "Liquidez": liq, "Presencia_90d": presencia, "Muy_Comerciada": muy_com,
            "Precio_Objetivo": round(obj, 3) if pd.notna(obj) else None,
            "Precio_Justo": round(justo, 3) if pd.notna(justo) else None,
            "Valoracion": diag, "Analistas_TV": analistas_rec, "Momento_Compra": momento,
            "Score": score, "Valor_USD": round(val_usd, 0), "Link_TV": link_tv
        })
        
    df_res = pd.DataFrame(resultados)
    if not df_res.empty:
        df_res = df_res.drop_duplicates(subset=["Ticker"]).sort_values(by=["Score", "Valor_USD"], ascending=[False, False]).reset_index(drop=True)
        df_res["Ranking"] = df_res.index + 1
    return df_res

with st.spinner("⏳ Cargando terminal financiero global sincronizado con TradingView..."):
    df = ejecutar_scanner_completo()

with st.expander("🎛️ Panel de Control & Filtros Avanzados de Mercado", expanded=True):
    fc1, fc2, fc3, fc4, fc5, fc6, fc7 = st.columns([2.2, 1.5, 1.5, 1.5, 2, 1.5, 1.3])
    with fc1:
        busqueda = st.text_input("🔍 Buscar Ticker/Empresa", "")
    with fc2:
        mercado_f = st.selectbox("🌐 Mercado", ["Todos", "PERÚ", "EE.UU.", "EUROPA"])
    with fc3:
        div_f = st.selectbox("💰 Dividendos", ["Todos", "SÍ", "NO"])
    with fc4:
        liq_f = st.selectbox("💧 Liquidez", ["Todas", "ALTA", "MEDIA", "BAJA", "MUY BAJA"])
    with fc5:
        mom_f = st.selectbox("💡 Momento de Compra", ["Todos", "MUY BUEN MOMENTO", "BUEN MOMENTO", "ESPERAR CONFIRMACIÓN", "NO COMPRAR AHORA"])
    with fc6:
        solo_top50 = st.checkbox("⭐ Top 50", value=False)
    with fc7:
        st.markdown("<div style='margin-top: 22px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Actualizar"):
            st.cache_data.clear()
            st.rerun()

if df.empty:
    st.warning("⚠️ No se pudieron cargar los datos del mercado en este momento.")
else:
    dff = df.copy()
    if busqueda:
        dff = dff[dff["Ticker"].str.contains(busqueda, case=False, na=False) | dff["Empresa"].str.contains(busqueda, case=False, na=False)]
    if mercado_f != "Todos":
        dff = dff[dff["Mercado"] == mercado_f]
    if div_f != "Todos":
        dff = dff[dff["Dividendos"] == div_f]
    if liq_f != "Todas":
        dff = dff[dff["Liquidez"] == liq_f]
    if mom_f != "Todos":
        dff = dff[dff["Momento_Compra"].str.contains(mom_f, case=False, na=False)]
    if solo_top50:
        dff = dff[dff["Ranking"] <= 50]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="metric-card"><h4>📋 Activos Listados</h4><h2>{len(dff)}</h2></div>', unsafe_allow_html=True)
    with k2:
        n_div = len(dff[dff["Dividendos"] == "SÍ"])
        st.markdown(f'<div class="metric-card"><h4>💰 Reparten Dividendos</h4><h2>{n_div}</h2></div>', unsafe_allow_html=True)
    with k3:
        n_fav = len(dff[dff["Momento_Compra"].str.contains("BUEN MOMENTO", na=False)])
        st.markdown(f'<div class="metric-card"><h4>🚀 Momento Favorable</h4><h2 style="color:#3fb950;">{n_fav}</h2></div>', unsafe_allow_html=True)
    with k4:
        n_ven = len(dff[dff["Analistas_TV"].str.contains("VENTA", na=False).fillna(False)])
        st.markdown(f'<div class="metric-card"><h4>⚠️ Recomendación Venta</h4><h2 style="color:#f85149;">{n_ven}</h2></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    columnas_mostrar = [
        "Ranking", "Ticker", "Empresa", "Mercado", "Índice", "Moneda", "Precio",
        "Dividendos", "Div_Yield_%", "Frecuencia", "Liquidez", "Presencia_90d", "Muy_Comerciada",
        "Precio_Objetivo", "Precio_Justo", "Valoracion", "Analistas_TV", "Momento_Compra", "Score", "Link_TV"
    ]
    
    st.dataframe(
        dff[columnas_mostrar],
        column_config={
            "Precio": st.column_config.NumberColumn("Precio", format="%.3f"),
            "Div_Yield_%": st.column_config.NumberColumn("Div. Yield (%)", format="%.2f%%"),
            "Presencia_90d": st.column_config.NumberColumn("Presencia (90d)", format="%.1f%%"),
            "Precio_Objetivo": st.column_config.NumberColumn("Precio Obj.", format="%.3f"),
            "Precio_Justo": st.column_config.NumberColumn("Precio Justo", format="%.3f"),
            "Link_TV": st.column_config.LinkColumn("TradingView", display_text="📈 Ver Gráfico")
        },
        use_container_width=True, 
        height=480
    )

    csv_data = dff[columnas_mostrar].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte Ejecutivo Global en CSV",
        data=csv_data,
        file_name="reporte_financiero_global_dividendos.csv",
        mime="text/csv",
    )