# 📊 FinSight – AI-Powered Personal Finance Advisor

FinSight is an **AI-powered personal finance advisor** that helps users track expenses, categorize spending, set savings goals, and receive personalized budgeting & investment strategies.  
It integrates **real-time market data** and **structured LLM responses** for actionable financial insights.

---

## 🚀 Features

- **Expense Categorization** – Automatically assigns spending to categories (Housing, Utilities, Groceries, etc.)  
- **Budget Recommendations** – Calculates needs/wants caps and suggested savings targets  
- **LLM-Powered Advice** – Generates structured JSON financial plans using **Gemini 2.0 Flash API**  
- **Live Market Data** – Fetches real-time stock & crypto prices from **Yahoo Finance** and **CoinGecko**  
- **Interactive Frontend** – Add/remove expenses dynamically, view spending insights with **Chart.js** visualizations  
- **Risk Disclaimers & 3-Month Plan** – Ensures safe and structured investment strategies  

---

## 🛠️ Tech Stack

### **Backend**
- Python 3.10+, FastAPI  
- Gemini 2.0 Flash API (structured JSON output)  
- Yahoo Finance (`yfinance`) & CoinGecko API for market data  

### **Frontend**
- HTML, CSS, JavaScript  
- Chart.js for spending visualizations  

### **Other**
- Prompt engineering for LLM-controlled output  
- `.env` configuration for API keys  

---

## 📂 Project Structure
```bash 
finsight/
│── app.py                 # FastAPI backend entry point
│── agent.py               # Main financial analysis logic
│── finance_tools.py       # Expense categorization & budget calculation
│── utils.py               # Gemini API call & helper functions
│── static/
│   ├── index.html         # Frontend UI
│   ├── style.css          # Styling
│   └── script.js          # Interactive logic & charts
│── requirements.txt       # Dependencies
│── README.md              # Project documentation
```


⚡ Setup & Installation

Clone the Repository
```bash
git clone https://github.com/yourusername/finsight.git
cd finsight
```

Install Dependencies
```bash
pip install -r requirements.txt
```

Set Environment Variables
Create a .env file:
```bash
GEMINI_API_KEY=your_gemini_api_key
```


Run the Application
```bash
uvicorn app:app --reload
```

Open in Browser
Visit: http://127.0.0.1:8000


📊 Example Output

Example structured JSON from Gemini:
```bash
{
  "title": "Personalized Financial Plan",
  "overview": "This plan helps optimize your budget and grow wealth.",
  "income_spending": [
    {"label": "Monthly Income", "value": "₹45,3656"},
    {"label": "Current Spending", "value": "₹23,500"}
  ],
  "savings_goals": [
    {"label": "Minimum Savings", "value": "₹90,731"},
    {"label": "Target Savings", "value": "₹260,443"}
  ]
}

```
