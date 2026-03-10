import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import requests
import time

# Page configuration
st.set_page_config(
    page_title="Gemscap Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# API Helper Functions
def check_api_status():
    """Check if FastAPI backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def fetch_from_api(endpoint, params=None):
    """Fetch data from FastAPI backend"""
    try:
        response = requests.get(f"http://localhost:8000{endpoint}", params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

def get_stock_data_simple(symbols, period):
    """Simple yfinance data fetch - NO API complications"""
    data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if not hist.empty:
                data[symbol] = hist
        except:
            pass
    return data

def main():
    # Check API status
    api_online = check_api_status()
    
    # Header
    st.markdown('<div class="main-header"><h1>📈 Gemscap Equity Trading Dashboard</h1></div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/stock-share.png", width=80)
        st.title("Controls")
        
        # Indian stocks list
        indian_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
            'INFY.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS',
            'KOTAKBANK.NS', 'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS',
            'MARUTI.NS', 'SUNPHARMA.NS', 'TITAN.NS', 'BAJFINANCE.NS'
        ]
        
        selected_stocks = st.multiselect(
            "Select Stocks",
            indian_stocks,
            default=['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']
        )
        
        period = st.selectbox(
            "Time Period",
            ['1d', '5d', '1mo', '3mo', '6mo', '1y'],
            index=2
        )
        
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
    
    # Main content
    if not selected_stocks:
        st.warning("Please select at least one stock from the sidebar")
        return
    
    # Fetch data - SIMPLE VERSION (no API complications)
    with st.spinner("Fetching market data..."):
        stock_data = get_stock_data_simple(selected_stocks, period)
    
    if not stock_data:
        st.error("Failed to fetch data. Please check your internet connection.")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Charts", "💼 Portfolio", "🚀 API Demo"])
    
    with tab1:
        # Market overview
        st.subheader("Market Overview")
        
        cols = st.columns(min(4, len(selected_stocks)))
        for idx, symbol in enumerate(selected_stocks[:4]):
            if symbol in stock_data:
                df = stock_data[symbol]
                if len(df) > 1: 
                    current = df['Close'].iloc[-1]
                    previous = df['Close'].iloc[-2]
                    change = ((current - previous) / previous) * 100
                    
                    with cols[idx]:
                        st.metric(
                            label=symbol.replace('.NS', ''),
                            value=f"₹{current:,.2f}",
                            delta=f"{change:.2f}%"
                        )
    
    with tab2:
        # Charts for each stock - SIMPLE FIXED VERSION
        for symbol in selected_stocks:
            if symbol in stock_data:
                df = stock_data[symbol]
                
                st.subheader(f"{symbol} - Price Chart")
                
                # Create SIMPLE chart - NO column name issues
                fig = go.Figure()
                
                # Use lowercase column names that definitely exist
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['Close'],
                    mode='lines',
                    name='Price',
                    line=dict(color='#3B82F6', width=2)
                ))
                
                # Add moving averages safely
                if len(df) > 20:
                    df['SMA_20'] = df['Close'].rolling(20).mean()
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['SMA_20'],
                        name='SMA 20',
                        line=dict(color='orange', width=1)
                    ))
                
                if len(df) > 50:
                    df['SMA_50'] = df['Close'].rolling(50).mean()
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['SMA_50'],
                        name='SMA 50',
                        line=dict(color='blue', width=1)
                    ))
                
                fig.update_layout(
                    title=f"{symbol} Price Chart",
                    yaxis_title="Price (₹)",
                    xaxis_title="Date",
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Portfolio tracker - SIMPLE VERSION
        st.subheader("Portfolio Tracker")
        
        # Sample portfolio data
        portfolio = [
            {'symbol': 'RELIANCE.NS', 'quantity': 10, 'avg_price': 2450},
            {'symbol': 'TCS.NS', 'quantity': 5, 'avg_price': 3500},
            {'symbol': 'HDFCBANK.NS', 'quantity': 8, 'avg_price': 1650}
        ]
        
        # Calculate P&L
        portfolio_df = []
        total_investment = 0
        total_current = 0
        
        for position in portfolio:
            symbol = position['symbol']
            if symbol in stock_data:
                current_price = stock_data[symbol]['Close'].iloc[-1]
                investment = position['quantity'] * position['avg_price']
                current_value = position['quantity'] * current_price
                pnl = current_value - investment
                pnl_percent = (pnl / investment) * 100
                
                portfolio_df.append({
                    'Stock': symbol.replace('.NS', ''),
                    'Qty': position['quantity'],
                    'Avg Price': f"₹{position['avg_price']:,.2f}",
                    'Current': f"₹{current_price:,.2f}",
                    'Investment': f"₹{investment:,.2f}",
                    'Current Value': f"₹{current_value:,.2f}",
                    'P&L': f"₹{pnl:,.2f}",
                    'Return %': f"{pnl_percent:.2f}%"
                })
                
                total_investment += investment
                total_current += current_value
        
        if portfolio_df:
            # Display portfolio table
            st.dataframe(pd.DataFrame(portfolio_df), use_container_width=True)
            
            # Summary metrics
            total_pnl = total_current - total_investment
            total_return = (total_pnl / total_investment) * 100 if total_investment > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Investment", f"₹{total_investment:,.2f}")
            col2.metric("Current Value", f"₹{total_current:,.2f}")
            col3.metric("Total P&L", f"₹{total_pnl:,.2f}")
            col4.metric("Return %", f"{total_return:.2f}%")
    
    with tab4:
        # API Demo Section
        st.subheader("FastAPI Backend Demo")
        
        if api_online:
            st.success("✅ FastAPI Backend is running on http://localhost:8000")
            
            # Test API buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Test Health"):
                    data = fetch_from_api("/health")
                    if data:
                        st.json(data)
            
            with col2:
                if st.button("Get Stock Quote"):
                    data = fetch_from_api("/stock/RELIANCE.NS/quote")
                    if data:
                        st.metric("RELIANCE", f"₹{data['price']:,.2f}", f"{data.get('change_percent', 0):.2f}%")
            
            with col3:
                if st.button("Get Momentum Stocks"):
                    data = fetch_from_api("/screener/momentum", {"limit": 3})
                    if data:
                        for stock in data.get("stocks", []):
                            st.write(f"**{stock['symbol']}**: {stock['signal']} (Score: {stock['score']})")
            
            # Show API documentation link
            st.markdown("""
            ### API Documentation
            - **Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
            - **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
            - **Stock Quote:** [http://localhost:8000/stock/RELIANCE.NS/quote](http://localhost:8000/stock/RELIANCE.NS/quote)
            """)
        else:
            st.error("❌ FastAPI Backend is not running")
            st.info("""
            To enable API features, start the backend:
            ```bash
            cd equity_dashboard
            python src/dashboard/main.py
            ```
            Then refresh this page.
            """)
    
    # Footer
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("Data source: Yahoo Finance | For demonstration purposes")

if __name__ == "__main__":
    main()