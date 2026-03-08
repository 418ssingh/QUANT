import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils.data_loader import load_market_data
from utils.strategies import moving_average_crossover, rsi_strategy
from utils.backtesting import run_backtest
from utils.risk import atr_position_sizing, kelly_position_sizing, monte_carlo_simulation
from utils.live_feed import simulate_live_feed
from utils.pnl_tracker import calculate_live_pnl


st_autorefresh(interval=5000, key="refresh")

# ============================
# STREAMLIT CONFIG
# ============================
st.set_page_config("Gemscap Quant Research Engine", layout="wide")

st.title("📈 Gemscap Quant Research Engine (Equity Trading)")
st.caption("Live Trading + Backtesting + Risk Monitoring Dashboard")


# ============================
# SIDEBAR SETTINGS
# ============================
st.sidebar.header("⚙️ Trading Controls")

symbol = st.sidebar.text_input("Equity Symbol", "AAPL")
capital = st.sidebar.number_input("Total Capital", 100000, step=5000)

strategy_name = st.sidebar.selectbox(
    "Select Strategy",
    ["Moving Average Crossover", "RSI Strategy"]
)


# ============================
# LOAD MARKET DATA
# ============================
data = load_market_market_data = load_market_data(symbol)

st.subheader("📊 Historical Price Data")
st.line_chart(data["Close"])


# ============================
# LIVE FEED SIMULATION
# ============================
st.subheader("⚡ Live Price Feed Simulation")

live_prices = simulate_live_feed(data["Close"].values[-50:])
st.line_chart(live_prices)


# ============================
# STRATEGY SIGNALS
# ============================
st.subheader("🧠 Strategy Engine")

if strategy_name == "Moving Average Crossover":
    signals = moving_average_crossover(data)
else:
    signals = rsi_strategy(data)

st.dataframe(signals.tail(10), width="stretch")


# ============================
# BACKTEST RESULTS
# ============================
st.subheader("📌 Backtesting Performance")

results = run_backtest(signals)

col1, col2, col3 = st.columns(3)

col1.metric("Total Return (%)", f"{results['total_return']:.2f}")
col2.metric("Sharpe Ratio", f"{results['sharpe']:.2f}")
col3.metric("Max Drawdown (%)", f"{results['drawdown']:.2f}")


# ============================
# LIVE POSITION + P&L TRACKER
# ============================
st.subheader("💰 Live Position & P&L Monitor")

st.sidebar.markdown("----")
st.sidebar.subheader("📌 Trade Settings")

live_price = data["Close"].iloc[-1].item()

entry_price = st.sidebar.number_input(
    "Entry Price (Manual)",
    value=live_price,
    step=1.0
)

pnl_table = calculate_live_pnl(symbol, capital, entry_price)

st.dataframe(pnl_table, width="stretch")


# ============================
# POSITION SIZING
# ============================
st.subheader("📌 Position Sizing (ATR + Kelly)")

atr_size = atr_position_sizing(data, capital)
kelly_size = kelly_position_sizing(signals, capital)

col1, col2 = st.columns(2)

col1.success(f"ATR Suggested Size: ₹{float(atr_size):,.0f}")
col2.info(f"Kelly Suggested Size: ₹{float(kelly_size):,.0f}")


# ============================
# MONTE CARLO RISK FORECAST
# ============================
st.subheader("🎲 Monte Carlo Risk Forecast")

mc_paths = monte_carlo_simulation(signals)

st.line_chart(mc_paths)

st.success("✅ Gemscap Quant Dashboard Fully Ready for Interview")
