import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz
import numpy as np

st.set_page_config(page_title="Trading Pro", page_icon="📱")

# CSS
st.markdown("""
<style>
    .stApp { background-color: #0d1117; }
    .price-box {
        background: #000;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #00ff00;
        margin: 20px 0;
    }
    .price {
        font-size: 48px;
        color: #00ff00;
        font-weight: bold;
        font-family: monospace;
    }
    .metric {
        background: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #333;
    }
    .metric-label {
        color: #888;
        font-size: 12px;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #00ff00;
        font-size: 24px;
        font-weight: bold;
    }
    .signal-buy {
        color: #00ff00;
        font-size: 20px;
        font-weight: bold;
    }
    .signal-sell {
        color: #ff4444;
        font-size: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("📱 Trading Terminal Pro")

# Input nella sidebar
with st.sidebar:
    st.header("⚙️ Controlli")
    
    asset = st.selectbox(
        "Asset",
        ["XAU/USD (Oro)", "EUR/USD", "GBP/USD", "BTC/USD", "ETH/USD", "S&P 500"]
    )
    
    timeframe = st.selectbox(
        "Timeframe",
        ["1h", "4h", "1d"]
    )
    
    capitale = st.number_input("Capitale (€)", value=1000, step=100)
    rischio = st.slider("Rischio %", 0.1, 5.0, 1.0, 0.1)

# Bottone analisi
if st.button("🚀 ANALIZZA", type="primary"):
    
    with st.spinner("📥 Scaricamento dati..."):
        
        try:
            # Mappa asset a simbolo
            symbols = {
                "XAU/USD (Oro)": "GC=F",
                "EUR/USD": "EURUSD=X",
                "GBP/USD": "GBPUSD=X",
                "BTC/USD": "BTC-USD",
                "ETH/USD": "ETH-USD",
                "S&P 500": "^GSPC"
            }
            
            symbol = symbols[asset]
            
            # Mappa timeframe a periodo
            period_map = {
                "1h": "5d",  # 5 giorni per dati orari
                "4h": "1mo", # 1 mese per 4 ore
                "1d": "3mo"  # 3 mesi per giornaliero
            }
            
            # Download dati con gestione migliore
            data = yf.download(
                symbol,
                period=period_map[timeframe],
                interval=timeframe,
                auto_adjust=True,
                progress=False
            )
            
            # Debug: mostra info dati
            st.write(f"📊 Dati scaricati: {len(data)} candele")
            
            # Verifica dati
            if data is None or len(data) == 0:
                st.error("❌ Nessun dato disponibile")
                st.stop()
            
            # Pulisci dati (rimuovi MultiIndex se presente)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Prezzo attuale
            current_price = float(data['Close'].iloc[-1])
            
            # Calcoli base
            high_20 = float(data['High'].tail(20).max())
            low_20 = float(data['Low'].tail(20).min())
            
            # Calcolo RSI
            try:
                close_prices = data['Close'].values
                deltas = np.diff(close_prices)
                seed = deltas[:14]
                up = seed[seed >= 0].sum()/14
                down = -seed[seed < 0].sum()/14
                rs = up/down if down != 0 else 100
                rsi = 100 - 100/(1+rs)
                
                for i in range(14, len(close_prices)-1):
                    delta = deltas[i-1]
                    if delta > 0:
                        upval = delta
                        downval = 0
                    else:
                        upval = 0
                        downval = -delta
                    
                    up = (up*13 + upval)/14
                    down = (down*13 + downval)/14
                    rs = up/down if down != 0 else 100
                    rsi = 100 - 100/(1+rs)
                
                current_rsi = rsi
            except:
                current_rsi = 50.0
            
            # Calcolo ATR
            try:
                high_low = data['High'] - data['Low']
                high_close = abs(data['High'] - data['Close'].shift(1))
                low_close = abs(data['Low'] - data['Close'].shift(1))
                tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                atr = float(tr.rolling(window=14).mean().iloc[-1])
            except:
                atr = (high_20 - low_20) * 0.1
            
            # Genera segnale
            if current_rsi > 50:
                signal = "BUY"
                signal_class = "signal-buy"
                entry = low_20 + (high_20 - low_20) * 0.382
                sl = entry - (atr * 1.5)
                tp = entry + (atr * 2)
            else:
                signal = "SELL"
                signal_class = "signal-sell"
                entry = high_20 - (high_20 - low_20) * 0.382
                sl = entry + (atr * 1.5)
                tp = entry - (atr * 2)
            
            # Calcolo lotti
            multiplier = 100 if "Oro" in asset or "BTC" in asset or "ETH" in asset else 100000
            dist_sl = abs(entry - sl)
            
            if dist_sl > 0:
                risk_amount = capitale * (rischio / 100)
                lotti = max(0.01, round(risk_amount / (dist_sl * multiplier), 2))
                actual_risk = lotti * dist_sl * multiplier
            else:
                lotti = 0.01
                actual_risk = 0
            
            # Metriche principali
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric">
                    <div class="metric-label">RSI</div>
                    <div class="metric-value">{current_rsi:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric">
                    <div class="metric-label">ATR</div>
                    <div class="metric-value">{atr:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric">
                    <div class="metric-label">RANGE</div>
                    <div class="metric-value">{(high_20-low_20):.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Price box con segnale
            st.markdown(f"""
            <div class="price-box">
                <div class="{signal_class}">{signal}</div>
                <div class="price">{current_price:.2f}</div>
                <div style="color:#888; margin-top:10px">{asset}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Livelli
            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"""
                <div class="metric">
                    <div class="metric-label">ENTRY</div>
                    <div style="color:#00ccff; font-size:20px; font-weight:bold">{entry:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"""
                <div class="metric">
                    <div class="metric-label">TP</div>
                    <div style="color:#00ff00; font-size:20px; font-weight:bold">{tp:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"""
                <div class="metric">
                    <div class="metric-label">SL</div>
                    <div style="color:#ff4444; font-size:20px; font-weight:bold">{sl:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Money management
            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"""
                <div class="metric">
                    <div class="metric-label">LOTTI</div>
                    <div class="metric-value">{lotti:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"""
                <div class="metric">
                    <div class="metric-label">RISCHIO €</div>
                    <div class="metric-value" style="color:#ff4444">{actual_risk:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[2]:
                rr = abs((tp - entry) / (sl - entry)) if sl != entry else 0
                st.markdown(f"""
                <div class="metric">
                    <div class="metric-label">R/R</div>
                    <div class="metric-value">{rr:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # GRAFICO CORRETTO
            st.subheader("📈 Grafico")

            # Prepara i dati per il grafico
            fig = go.Figure()

            # Candele
            fig.add_trace(go.Candlestick(
                x=data.index.tolist(),
                open=data['Open'].tolist(),
                high=data['High'].tolist(),
                low=data['Low'].tolist(),
                close=data['Close'].tolist(),
                name='Prezzo',
                increasing=dict(line=dict(color='#00ff00')),
                decreasing=dict(line=dict(color='#ff4444'))
            ))

            # Linee di livello
            fig.add_hline(
                y=entry,
                line_color='cyan',
                line_width=2,
                annotation_text=f'Entry {entry:.2f}',
                annotation_position='right'
            )

            fig.add_hline(
                y=tp,
                line_color='lime',
                line_dash='dash',
                line_width=1.5,
                annotation_text=f'TP {tp:.2f}',
                annotation_position='right'
            )

            fig.add_hline(
                y=sl,
                line_color='red',
                line_dash='dash',
                line_width=1.5,
                annotation_text=f'SL {sl:.2f}',
                annotation_position='right'
            )

            # Layout
            fig.update_layout(
                title=f'{asset} - {timeframe}',
                yaxis_title='Prezzo',
                template='plotly_dark',
                height=500,
                showlegend=False,
                margin=dict(l=50, r=50, t=50, b=50),
                xaxis_rangeslider_visible=True,  # Abilita lo slider per zoom
                xaxis=dict(
                    type='date',
                    rangeslider=dict(visible=True),
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label='1d', step='day', stepmode='backward'),
                            dict(count=7, label='1w', step='day', stepmode='backward'),
                            dict(count=1, label='1m', step='month', stepmode='backward'),
                            dict(step='all')
                        ])
                    )
                )
            )

            # Mostra il grafico
            st.plotly_chart(fig, use_container_width=True)

            # Info aggiuntive
            st.info(f"""
            📊 Ultime 20 candele:
            - Massimo: {high_20:.2f}
            - Minimo: {low_20:.2f}
            - Range: {(high_20-low_20):.2f}
            - Volume: {data['Volume'].iloc[-1] if 'Volume' in data.columns else 'N/A'}
            """)
            
        except Exception as e:
            st.error(f"❌ Errore: {str(e)}")
            st.exception(e)
