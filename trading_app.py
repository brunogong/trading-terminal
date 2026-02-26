import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

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
    }
    .metric {
        background: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("📱 Trading Terminal Pro")

# Input nella sidebar
with st.sidebar:
    st.header("⚙️ Controlli")
    
    asset = st.selectbox(
        "Asset",
        ["XAU/USD (Oro)", "EUR/USD", "GBP/USD", "BTC/USD"]
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
                "BTC/USD": "BTC-USD"
            }
            
            # Download dati
            data = yf.download(
                symbols[asset],
                period="1mo",
                interval=timeframe,
                auto_adjust=True,
                progress=False
            )
            
            # Verifica dati - CORREZIONE IMPORTANTE
            if data is None or len(data) == 0:
                st.error("❌ Nessun dato disponibile")
                st.stop()
            
            # Prezzo attuale
            current_price = float(data['Close'].iloc[-1])
            
            # Calcoli base
            high_20 = float(data['High'].tail(20).max())
            low_20 = float(data['Low'].tail(20).min())
            
            # Calcolo RSI semplice (senza pandas_ta)
            try:
                close_prices = data['Close']
                delta = close_prices.diff()
                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            except:
                current_rsi = 50.0
            
            # Calcolo ATR semplice
            try:
                high_low = data['High'] - data['Low']
                high_close = (data['High'] - data['Close'].shift()).abs()
                low_close = (data['Low'] - data['Close'].shift()).abs()
                tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                atr = float(tr.rolling(window=14).mean().iloc[-1])
            except:
                atr = (high_20 - low_20) * 0.1
            
            # Genera segnale
            if current_rsi > 50:
                signal = "BUY"
                signal_color = "#00ff00"
                entry = low_20 + (high_20 - low_20) * 0.382
                sl = entry - (atr * 1.5)
                tp = entry + (atr * 2)
            else:
                signal = "SELL"
                signal_color = "#ff4444"
                entry = high_20 - (high_20 - low_20) * 0.382
                sl = entry + (atr * 1.5)
                tp = entry - (atr * 2)
            
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
            
            # Mostra risultati
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric">
                    <div style="color:#888">RSI</div>
                    <div style="color:#00ff00; font-size:24px">{current_rsi:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric">
                    <div style="color:#888">ATR</div>
                    <div style="color:#00ff00; font-size:24px">{atr:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric">
                    <div style="color:#888">RANGE</div>
                    <div style="color:#00ff00; font-size:24px">{(high_20-low_20):.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Price box
            st.markdown(f"""
            <div class="price-box">
                <div style="color:{signal_color}; font-size:20px; margin-bottom:10px">{signal}</div>
                <div class="price">{current_price:.2f}</div>
                <div style="color:#888; margin-top:10px">{asset}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Livelli
            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"""
                <div class="metric">
                    <div style="color:#888">ENTRY</div>
                    <div style="color:#00ccff; font-size:20px">{entry:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"""
                <div class="metric">
                    <div style="color:#888">TP</div>
                    <div style="color:#00ff00; font-size:20px">{tp:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"""
                <div class="metric">
                    <div style="color:#888">SL</div>
                    <div style="color:#ff4444; font-size:20px">{sl:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Money management
            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"""
                <div class="metric">
                    <div style="color:#888">LOTTI</div>
                    <div style="color:#00ff00; font-size:20px">{lotti:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"""
                <div class="metric">
                    <div style="color:#888">RISCHIO €</div>
                    <div style="color:#ff4444; font-size:20px">{actual_risk:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[2]:
                rr = abs((tp - entry) / (sl - entry)) if sl != entry else 0
                st.markdown(f"""
                <div class="metric">
                    <div style="color:#888">R/R</div>
                    <div style="color:#00ff00; font-size:20px">{rr:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Grafico
            fig = go.Figure()
            
            # Candele
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                increasing_line_color='#00ff00',
                decreasing_line_color='#ff4444'
            ))
            
            # Linee di livello
            fig.add_hline(y=entry, line_color='cyan', line_width=2,
                         annotation_text=f'Entry {entry:.2f}')
            fig.add_hline(y=tp, line_color='lime', line_dash='dash',
                         annotation_text=f'TP {tp:.2f}')
            fig.add_hline(y=sl, line_color='red', line_dash='dash',
                         annotation_text=f'SL {sl:.2f}')
            
            fig.update_layout(
                template='plotly_dark',
                height=400,
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Info
            st.info(f"📊 Range 20gg: {low_20:.2f} - {high_20:.2f}")
            
        except Exception as e:
            st.error(f"❌ Errore: {str(e)}")
            st.exception(e)  # Mostra dettagli errore
