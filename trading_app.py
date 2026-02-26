"""
TRADING TERMINAL PRO - Versione Streamlit Cloud
Accessibile da qualsiasi telefono
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import pytz

# Configurazione pagina
st.set_page_config(
    page_title="Trading Pro",
    page_icon="??",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS per mobile
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
    }
    
    .main-title {
        background: linear-gradient(135deg, #1e1e1e, #2d2d2d);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    
    .main-title h1 {
        color: #00ff00;
        font-size: 28px;
        margin: 0;
    }
    
    .main-title p {
        color: #888;
        font-size: 12px;
        margin: 5px 0 0 0;
    }
    
    .session-card {
        background: #1e1e1e;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border-left: 4px solid #00ff00;
        font-size: 14px;
    }
    
    .price-card {
        background: #000;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        border: 2px solid #00ff00;
        margin: 20px 0;
        box-shadow: 0 0 20px rgba(0,255,0,0.2);
    }
    
    .price-value {
        font-size: 48px;
        font-weight: bold;
        color: #00ff00;
        font-family: monospace;
    }
    
    .signal-badge {
        display: inline-block;
        padding: 5px 20px;
        border-radius: 25px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .signal-buy {
        background: rgba(0,255,0,0.1);
        color: #00ff00;
        border: 1px solid #00ff00;
    }
    
    .signal-sell {
        background: rgba(255,0,0,0.1);
        color: #ff4444;
        border: 1px solid #ff4444;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin: 15px 0;
    }
    
    .metric-card {
        background: #1e1e1e;
        padding: 15px 5px;
        border-radius: 12px;
        text-align: center;
    }
    
    .metric-label {
        color: #888;
        font-size: 11px;
        margin-bottom: 5px;
    }
    
    .metric-value {
        color: #00ff00;
        font-size: 18px;
        font-weight: bold;
    }
    
    .levels-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin: 15px 0;
    }
    
    .level-card {
        background: #1e1e1e;
        padding: 12px 5px;
        border-radius: 12px;
        text-align: center;
    }
    
    .level-entry { color: #00ccff; font-size: 18px; font-weight: bold; }
    .level-tp { color: #00ff00; font-size: 18px; font-weight: bold; }
    .level-sl { color: #ff4444; font-size: 18px; font-weight: bold; }
    
    .info-footer {
        background: #1e1e1e;
        padding: 10px;
        border-radius: 10px;
        font-size: 11px;
        color: #666;
        text-align: center;
        margin-top: 20px;
    }
    
    .stButton > button {
        width: 100%;
        height: 50px;
        background: linear-gradient(90deg, #00ff00, #00cc00);
        color: black;
        font-weight: bold;
        font-size: 18px;
        border-radius: 25px;
        border: none;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class='main-title'>
    <h1>?? TRADING TERMINAL PRO</h1>
    <p>Analisi Multi-Asset in Tempo Reale</p>
</div>
""", unsafe_allow_html=True)

# Funzione sessioni mercato
def get_sessions_html():
    zones = {
        'Tokyo': 'Asia/Tokyo',
        'Londra': 'Europe/London',
        'New York': 'America/New_York',
        'Sydney': 'Australia/Sydney'
    }
    
    now = datetime.now(pytz.UTC)
    html = "<div class='session-card'>?? "
    
    for city, zone in zones.items():
        tz = pytz.timezone(zone)
        local = now.astimezone(tz)
        hour = local.hour
        
        if city == 'Tokyo':
            is_open = 0 <= hour < 9
        elif city == 'Sydney':
            is_open = 21 <= hour or hour < 6
        elif city == 'Londra':
            is_open = 8 <= hour < 17
        else:
            is_open = 13 <= hour < 22
            
        icon = '??' if is_open else '??'
        html += f"{icon}{city} {local.strftime('%H:%M')}  "
    
    html += "</div>"
    return html

st.markdown(get_sessions_html(), unsafe_allow_html=True)

# Input in colonne
col1, col2 = st.columns(2)

with col1:
    asset = st.selectbox(
        "?? ASSET",
        ["XAU/USD (Oro)", "EUR/USD", "GBP/USD", "BTC/USD", "ETH/USD", "S&P 500"]
    )

with col2:
    timeframe = st.selectbox(
        "?? TIMEFRAME",
        ["1h", "4h", "1d"]
    )

col1, col2 = st.columns(2)

with col1:
    capitale = st.number_input("?? Capitale (€)", value=1000, step=100)

with col2:
    rischio = st.slider("?? Rischio %", 0.1, 5.0, 1.0, 0.1)

# Bottone analisi
if st.button("?? ANALIZZA ORA", type="primary"):
    
    with st.spinner("?? Scaricamento dati in corso..."):
        
        try:
            # Mappa asset a simbolo Yahoo Finance
            symbols = {
                "XAU/USD (Oro)": "GC=F",
                "EUR/USD": "EURUSD=X",
                "GBP/USD": "GBPUSD=X",
                "BTC/USD": "BTC-USD",
                "ETH/USD": "ETH-USD",
                "S&P 500": "^GSPC"
            }
            
            # Mappa timeframe a periodo
            period_map = {
                "1h": "1mo",
                "4h": "3mo",
                "1d": "6mo"
            }
            
            # Download dati
            data = yf.download(
                symbols[asset],
                period=period_map[timeframe],
                interval=timeframe,
                auto_adjust=True,
                progress=False
            )
            
            if not data.empty:
                # Prezzo attuale
                current_price = float(data['Close'].iloc[-1])
                
                # Calcoli base
                high_20 = float(data['High'].tail(20).max())
                low_20 = float(data['Low'].tail(20).min())
                
                # Calcola RSI semplice
                delta = data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs.iloc[-1])) if not pd.isna(rs.iloc[-1]) else 50
                
                # Genera segnale
                if rsi > 50:
                    signal = "BUY"
                    signal_class = "signal-buy"
                    entry = low_20 + (high_20 - low_20) * 0.382
                    sl = entry - ((high_20 - low_20) * 0.1)
                    tp = entry + ((high_20 - low_20) * 0.2)
                else:
                    signal = "SELL"
                    signal_class = "signal-sell"
                    entry = high_20 - (high_20 - low_20) * 0.382
                    sl = entry + ((high_20 - low_20) * 0.1)
                    tp = entry - ((high_20 - low_20) * 0.2)
                
                # Calcolo lotti
                multiplier = 100 if "Oro" in asset or "BTC" in asset else 100000
                dist_sl = abs(entry - sl)
                
                if dist_sl > 0:
                    risk_amount = capitale * (rischio / 100)
                    lotti = max(0.01, round(risk_amount / (dist_sl * multiplier), 2))
                    actual_risk = lotti * dist_sl * multiplier
                else:
                    lotti = 0.01
                    actual_risk = 0
                
                # Mostra prezzo e segnale
                st.markdown(f"""
                <div class='price-card'>
                    <div class='signal-badge {signal_class}'>{signal}</div>
                    <div class='price-value'>{current_price:,.2f}</div>
                    <div style='color:#888; margin-top:5px;'>{asset} | RSI: {rsi:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Metriche principali
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"<div class='metric-card'><div class='metric-label'>RSI</div><div class='metric-value'>{rsi:.1f}</div></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='metric-card'><div class='metric-label'>MAX 20gg</div><div class='metric-value'>{high_20:.2f}</div></div>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div class='metric-card'><div class='metric-label'>MIN 20gg</div><div class='metric-value'>{low_20:.2f}</div></div>", unsafe_allow_html=True)
                
                # Livelli trading
                st.markdown(f"""
                <div class='levels-grid'>
                    <div class='level-card'><div class='metric-label'>ENTRY</div><div class='level-entry'>{entry:.2f}</div></div>
                    <div class='level-card'><div class='metric-label'>TP</div><div class='level-tp'>{tp:.2f}</div></div>
                    <div class='level-card'><div class='metric-label'>SL</div><div class='level-sl'>{sl:.2f}</div></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Money management
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"<div class='metric-card'><div class='metric-label'>LOTTI</div><div class='metric-value'>{lotti:.2f}</div></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='metric-card'><div class='metric-label'>RISCHIO €</div><div class='metric-value'>{actual_risk:.2f}</div></div>", unsafe_allow_html=True)
                with col3:
                    rr = abs((tp - entry) / (sl - entry)) if sl != entry else 0
                    st.markdown(f"<div class='metric-card'><div class='metric-label'>R/R</div><div class='metric-value'>{rr:.2f}</div></div>", unsafe_allow_html=True)
                
                # Grafico
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                   vertical_spacing=0.05, row_heights=[0.7, 0.3])
                
                # Candele
                fig.add_trace(
                    go.Candlestick(
                        x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        increasing_line_color='#00ff00',
                        decreasing_line_color='#ff4444'
                    ),
                    row=1, col=1
                )
                
                # Linee di livello
                fig.add_hline(y=entry, line_color='cyan', line_width=2,
                            annotation_text=f'Entry {entry:.2f}', row=1, col=1)
                fig.add_hline(y=tp, line_color='lime', line_dash='dash',
                            annotation_text=f'TP {tp:.2f}', row=1, col=1)
                fig.add_hline(y=sl, line_color='red', line_dash='dash',
                            annotation_text=f'SL {sl:.2f}', row=1, col=1)
                
                # Volume
                if 'Volume' in data.columns:
                    volume_data = data['Volume'] if not isinstance(data['Volume'], pd.DataFrame) else data['Volume'].iloc[:, 0]
                    fig.add_trace(
                        go.Bar(x=data.index, y=volume_data, name='Volume', marker_color='#00ff00'),
                        row=2, col=1
                    )
                
                fig.update_layout(
                    template='plotly_dark',
                    height=500,
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Footer
                st.markdown(f"""
                <div class='info-footer'>
                    ?? Aggiornato: {datetime.now().strftime('%H:%M:%S')} | 
                    Range: {low_20:.2f} - {high_20:.2f}
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.error("? Nessun dato disponibile")
                
        except Exception as e:
            st.error(f"? Errore: {str(e)}")