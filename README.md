![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red.svg)
![License](https://img.shields.io/badge/license-Research%20Only-yellow.svg)

# QUANT - Quantitative Trading Platform

A full-stack quantitative trading platform combining a **FastAPI backend** with an interactive **Streamlit frontend**, featuring a dedicated **Quant Research Engine** for strategy development, backtesting, and analysis.

---

## ✨ Features

### 📈 Quant Research Engine
- Strategy backtesting framework
- Performance metrics (Sharpe ratio, drawdown, win rate, profit factor)
- Multi-timeframe analysis support
- Swing structure detection
- Machine learning integration for probability modeling

### ⚡ FastAPI Backend
- RESTful API for trading operations
- Real-time and historical market data endpoints
- Strategy execution and management
- Request validation and error handling

### 🎨 Streamlit Frontend
- Interactive dashboard for strategy monitoring
- Real-time performance visualization
- Backtest result explorer
- Trade execution interface

---
```
## 🏗️ Project Structure
QUANT/
├── Full-Stack Trading Application (FastAPI Backend + Streamlit Frontend)/
│ ├── backend/ # FastAPI application
│ │ ├── main.py # API entry point
│ │ ├── routes/ # API endpoints
│ │ └── models/ # Pydantic models
│ ├── frontend/ # Streamlit dashboard
│ │ └── app.py # UI application
│ └── shared/ # Shared utilities
├── QUANT RESEARCH ENGINE/
│ ├── backtest/ # Backtesting engine
│ ├── strategies/ # Strategy implementations
│ ├── data/ # Data handling modules
│ └── metrics/ # Performance calculations
└── tests/ # Unit and integration tests
```
---

## 📋 Prerequisites

- Python 3.9 or higher
- pip package manager
- Git (optional)

---

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/418ssingh/QUANT.git
cd QUANT

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
🚀 Quick Start
1. Start the Backend Server
bash
cd Full-Stack\ Trading\ Application\ \(FastAPI\ Backend\ +\ Streamlit\ Frontend\)/backend
uvicorn main:app --reload --port 8000
API documentation available at: http://localhost:8000/docs

2. Launch Streamlit Frontend
bash
cd Full-Stack\ Trading\ Application\ \(FastAPI\ Backend\ +\ Streamlit\ Frontend\)/frontend
streamlit run app.py
Dashboard available at: http://localhost:8501

3. Run Quant Research Engine
bash
python QUANT\ RESEARCH\ ENGINE/backtest_runner.py
📊 API Endpoints
Method	Endpoint	Description
GET	/health	API health check
GET	/market/{symbol}	Get market data for symbol
POST	/strategy/run	Execute a backtest
GET	/strategy/{id}/results	Retrieve backtest results
GET	/strategy/list	List available strategies
📈 Example Usage
Running a Backtest via API
python
import requests

response = requests.post(
    "http://localhost:8000/strategy/run",
    json={
        "strategy": "swing_breakout",
        "symbol": "EURUSD",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "parameters": {
            "threshold": 0.003,
            "atr_period": 14
        }
    }
)

print(response.json())
Sample Response
json
{
    "total_return": 0.154,
    "sharpe_ratio": 1.82,
    "max_drawdown": -0.087,
    "win_rate": 0.58,
    "profit_factor": 1.45,
    "total_trades": 124
}
🧪 Running Tests
bash
pytest tests/
📝 To-Do / Roadmap
Real-time broker API integration

ML-based probability calculation engine

Risk management module

Docker containerization

Deployment to cloud (AWS/GCP)

Telegram bot for trade alerts

Multi-asset support

🤝 Contributing
Contributions, issues, and feature requests are welcome!

Fork the repository

Create your feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

📄 License
This project is for educational and research purposes only.

👤 Author
Shubham Singh

GitHub: @418ssingh

Email: 418ssingh@gmail.com

The quantitative trading community for inspiration

⚠️ Disclaimer
This platform is designed for research and educational purposes. It is not intended for live trading without thorough validation and proper risk management.
