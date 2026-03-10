from fastapi import FastAPI, HTTPException, Query
import uvicorn
import sys
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
import json

# Print startup messages
print("🚀 Starting Gemscap Trading API...", file=sys.stderr)
print("🌐 Server running at: http://localhost:8000", file=sys.stderr)
print("📚 API Documentation: http://localhost:8000/docs", file=sys.stderr)
print("📊 Health check: http://localhost:8000/health", file=sys.stderr)
print("📈 Trading endpoints: /stock/*, /screener/*, /portfolio/*", file=sys.stderr)
print("🛑 Press Ctrl+C to stop the server", file=sys.stderr)
print("-" * 50, file=sys.stderr)

# Create FastAPI app
app = FastAPI(
    title="Gemscap Trading API",
    description="Real-time equity trading API for Indian markets with analytics",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Nifty 50 stocks (Indian market)
NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "INFY.NS", "HINDUNILVR.NS", "ITC.NS", "SBIN.NS",
    "BHARTIARTL.NS", "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS",
    "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS",
    "BAJFINANCE.NS", "WIPRO.NS", "ONGC.NS", "NTPC.NS"
]

# Mock portfolio for demo
PORTFOLIO = [
    {"symbol": "RELIANCE.NS", "quantity": 10, "avg_price": 2450},
    {"symbol": "TCS.NS", "quantity": 5, "avg_price": 3500},
    {"symbol": "HDFCBANK.NS", "quantity": 8, "avg_price": 1650},
    {"symbol": "INFY.NS", "quantity": 12, "avg_price": 1500}
]

# ============ HELPER FUNCTIONS ============
def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    if len(prices) < period:
        return 50
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else 50

def calculate_moving_average(prices, window=20):
    """Calculate moving average"""
    if len(prices) < window:
        return prices.mean()
    return prices.rolling(window).mean().iloc[-1]

def calculate_bollinger_bands(prices, window=20):
    """Calculate Bollinger Bands"""
    if len(prices) < window:
        return {"upper": prices.mean(), "middle": prices.mean(), "lower": prices.mean()}
    sma = prices.rolling(window).mean()
    std = prices.rolling(window).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return {
        "upper": upper_band.iloc[-1],
        "middle": sma.iloc[-1],
        "lower": lower_band.iloc[-1]
    }

# ============ API ENDPOINTS ============
@app.get("/")
def read_root():
    """Root endpoint - API status"""
    return {
        "message": "Gemscap Trading API",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/docs": "Interactive API documentation",
            "/health": "Health check",
            "/stocks": "Get available stocks",
            "/stock/{symbol}/quote": "Get real-time quote",
            "/stock/{symbol}/history": "Get historical data",
            "/stock/{symbol}/analysis": "Get technical analysis",
            "/screener/momentum": "Screen momentum stocks",
            "/screener/oversold": "Screen oversold stocks",
            "/portfolio": "Get portfolio summary",
            "/portfolio/returns": "Calculate portfolio returns"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running"
    }

@app.get("/stocks")
def get_available_stocks():
    """Get list of available stocks"""
    return {
        "market": "NSE India",
        "count": len(NIFTY_50),
        "stocks": NIFTY_50,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stock/{symbol}/quote")
async def get_stock_quote(symbol: str):
    """Get real-time stock quote"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")
        
        return {
            "symbol": symbol,
            "price": float(hist["Close"].iloc[-1]),
            "open": float(hist["Open"].iloc[-1]),
            "high": float(hist["High"].iloc[-1]),
            "low": float(hist["Low"].iloc[-1]),
            "volume": int(hist["Volume"].iloc[-1]),
            "previous_close": float(hist["Close"].iloc[-2]) if len(hist) > 1 else float(hist["Close"].iloc[-1]),
            "change": float(hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) if len(hist) > 1 else 0,
            "change_percent": float(((hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2] * 100) if len(hist) > 1 else 0),
            "currency": info.get("currency", "INR"),
            "market_cap": info.get("marketCap", 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching {symbol}: {str(e)}")

@app.get("/stock/{symbol}/history")
async def get_stock_history(
    symbol: str,
    period: str = Query("1mo", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y"),
    interval: str = Query("1d", description="Interval: 1m, 5m, 15m, 30m, 1h, 1d, 1wk")
):
    """Get historical stock data with technical indicators"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No historical data for {symbol}")
        
        # Calculate technical indicators
        hist["SMA_20"] = hist["Close"].rolling(20).mean()
        hist["SMA_50"] = hist["Close"].rolling(50).mean()
        hist["RSI"] = hist["Close"].diff()
        
        # Convert to list for JSON response
        data = []
        for idx, row in hist.iterrows():
            data.append({
                "timestamp": idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
                "sma_20": float(row["SMA_20"]) if not pd.isna(row["SMA_20"]) else None,
                "sma_50": float(row["SMA_50"]) if not pd.isna(row["SMA_50"]) else None
            })
        
        # Calculate summary statistics
        returns = hist["Close"].pct_change().dropna()
        
        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "start_date": hist.index[0].isoformat() if hasattr(hist.index[0], 'isoformat') else str(hist.index[0]),
            "end_date": hist.index[-1].isoformat() if hasattr(hist.index[-1], 'isoformat') else str(hist.index[-1]),
            "data": data,
            "count": len(data),
            "summary": {
                "start_price": float(hist["Close"].iloc[0]),
                "end_price": float(hist["Close"].iloc[-1]),
                "total_return": float((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100),
                "average_volume": int(hist["Volume"].mean()),
                "volatility": float(returns.std() * (252 ** 0.5) * 100) if not returns.empty else 0,
                "max_price": float(hist["High"].max()),
                "min_price": float(hist["Low"].min())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history for {symbol}: {str(e)}")

@app.get("/stock/{symbol}/analysis")
async def get_stock_analysis(symbol: str, period: str = "3mo"):
    """Get technical analysis for a stock"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if len(hist) < 20:
            raise HTTPException(status_code=400, detail="Insufficient data for analysis")
        
        prices = hist["Close"]
        
        # Calculate indicators
        rsi = calculate_rsi(prices)
        sma_20 = calculate_moving_average(prices, 20)
        sma_50 = calculate_moving_average(prices, 50)
        bb = calculate_bollinger_bands(prices)
        
        # Generate signals
        current_price = prices.iloc[-1]
        signals = []
        
        if current_price > sma_20 and rsi > 50:
            signals.append("BULLISH_TREND")
        if current_price < sma_20 and rsi < 50:
            signals.append("BEARISH_TREND")
        if rsi > 70:
            signals.append("OVERBOUGHT")
        if rsi < 30:
            signals.append("OVERSOLD")
        if current_price < bb["lower"]:
            signals.append("BB_OVERSOLD")
        if current_price > bb["upper"]:
            signals.append("BB_OVERBOUGHT")
        
        return {
            "symbol": symbol,
            "current_price": float(current_price),
            "indicators": {
                "rsi": float(rsi),
                "sma_20": float(sma_20),
                "sma_50": float(sma_50),
                "bb_upper": float(bb["upper"]),
                "bb_middle": float(bb["middle"]),
                "bb_lower": float(bb["lower"])
            },
            "signals": signals,
            "recommendation": "BUY" if "OVERSOLD" in signals else "SELL" if "OVERBOUGHT" in signals else "HOLD",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error for {symbol}: {str(e)}")

@app.get("/screener/momentum")
async def momentum_screener(limit: int = Query(10, description="Number of stocks to return")):
    """Screen stocks based on momentum strategy"""
    results = []
    
    for symbol in NIFTY_50[:15]:  # Check first 15 for speed
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if len(hist) > 20:
                current_price = hist["Close"].iloc[-1]
                sma_20 = hist["Close"].rolling(20).mean().iloc[-1]
                rsi = calculate_rsi(hist["Close"])
                volume_avg = hist["Volume"].rolling(10).mean().iloc[-1]
                current_volume = hist["Volume"].iloc[-1]
                
                # Momentum criteria
                score = 0
                if current_price > sma_20:
                    score += 2
                if 50 < rsi < 70:  # Mildly bullish
                    score += 1
                if current_volume > volume_avg * 1.5:
                    score += 1
                
                if score >= 2:  # At least 2 criteria met
                    results.append({
                        "symbol": symbol,
                        "price": float(current_price),
                        "sma_20": float(sma_20),
                        "rsi": float(rsi),
                        "volume_ratio": float(current_volume / volume_avg) if volume_avg > 0 else 0,
                        "score": score,
                        "signal": "BUY" if score >= 3 else "WATCH"
                    })
        except:
            continue
    
    # Sort by score and limit results
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "strategy": "momentum",
        "count": len(results[:limit]),
        "stocks": results[:limit],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/screener/oversold")
async def oversold_screener(limit: int = Query(5, description="Number of stocks to return")):
    """Screen oversold stocks (potential buying opportunities)"""
    results = []
    
    for symbol in NIFTY_50[:15]:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if len(hist) > 14:
                current_price = hist["Close"].iloc[-1]
                rsi = calculate_rsi(hist["Close"])
                
                if rsi < 35:  # Oversold condition
                    results.append({
                        "symbol": symbol,
                        "price": float(current_price),
                        "rsi": float(rsi),
                        "signal": "STRONG_BUY" if rsi < 30 else "BUY",
                        "timestamp": datetime.now().isoformat()
                    })
        except:
            continue
    
    results.sort(key=lambda x: x["rsi"])  # Sort by most oversold
    
    return {
        "strategy": "oversold",
        "count": len(results[:limit]),
        "stocks": results[:limit],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/portfolio")
async def get_portfolio():
    """Get current portfolio with live values"""
    portfolio_data = []
    total_investment = 0
    total_current = 0
    
    for position in PORTFOLIO:
        try:
            ticker = yf.Ticker(position["symbol"])
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                current_price = hist["Close"].iloc[-1]
                investment = position["quantity"] * position["avg_price"]
                current_value = position["quantity"] * current_price
                pnl = current_value - investment
                pnl_percent = (pnl / investment) * 100 if investment > 0 else 0
                
                portfolio_data.append({
                    "symbol": position["symbol"],
                    "quantity": position["quantity"],
                    "avg_price": position["avg_price"],
                    "current_price": float(current_price),
                    "investment": float(investment),
                    "current_value": float(current_value),
                    "pnl": float(pnl),
                    "pnl_percent": float(pnl_percent),
                    "status": "PROFIT" if pnl > 0 else "LOSS"
                })
                
                total_investment += investment
                total_current += current_value
        except:
            continue
    
    total_pnl = total_current - total_investment
    total_pnl_percent = (total_pnl / total_investment * 100) if total_investment > 0 else 0
    
    return {
        "portfolio": portfolio_data,
        "summary": {
            "total_investment": float(total_investment),
            "total_current_value": float(total_current),
            "total_pnl": float(total_pnl),
            "total_pnl_percent": float(total_pnl_percent),
            "return_status": "PROFIT" if total_pnl > 0 else "LOSS",
            "count": len(portfolio_data)
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/portfolio/returns")
async def calculate_portfolio_returns(days: int = Query(30, description="Period for returns calculation")):
    """Calculate portfolio returns over a period"""
    portfolio_returns = []
    
    for position in PORTFOLIO:
        try:
            ticker = yf.Ticker(position["symbol"])
            hist = ticker.history(period=f"{days+5}d")
            
            if len(hist) > days:
                start_price = hist["Close"].iloc[0]
                end_price = hist["Close"].iloc[-1]
                return_pct = ((end_price - start_price) / start_price) * 100
                
                portfolio_returns.append({
                    "symbol": position["symbol"],
                    "start_price": float(start_price),
                    "end_price": float(end_price),
                    "return_percent": float(return_pct),
                    "days": days
                })
        except:
            continue
    
    avg_return = np.mean([r["return_percent"] for r in portfolio_returns]) if portfolio_returns else 0
    
    return {
        "period_days": days,
        "returns": portfolio_returns,
        "average_return": float(avg_return),
        "best_performer": max(portfolio_returns, key=lambda x: x["return_percent"]) if portfolio_returns else None,
        "worst_performer": min(portfolio_returns, key=lambda x: x["return_percent"]) if portfolio_returns else None,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )