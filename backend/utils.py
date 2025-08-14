import os
import httpx
import json # Import json library
from dotenv import load_dotenv
from typing import Dict, Any
import yfinance as yf
from pycoingecko import CoinGeckoAPI

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def require_env():
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY in environment")

async def gemini_generate(prompt_text: str) -> str:
    """
    Call Gemini LLM. Returns plain text (the top candidate).
    """
    require_env()
    async with httpx.AsyncClient(timeout=45) as client:
        r = await client.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt_text}]}]},
        )
        r.raise_for_status()
        j = r.json()
        # safe fallback extraction
        try:
            return (
                j.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
        except Exception:
            return str(j)

def get_stock_price(symbol: str) -> float:
    """
    Use yfinance to get latest close price for a symbol.
    Symbol examples: "RELIANCE.NS", "^NSEI", "SPY"
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if data.empty:
            return 0.0
        return float(data["Close"].iloc[-1])
    except Exception:
        return 0.0

def get_crypto_price(coin_id: str, vs_currency: str = "usd") -> float:
    try:
        cg = CoinGeckoAPI()
        p = cg.get_price(ids=[coin_id], vs_currencies=[vs_currency])
        return float(p.get(coin_id, {}).get(vs_currency, 0.0))
    except Exception:
        return 0.0

def build_prompt(structured: Dict[str, Any]) -> str:
    income = structured["summary"]["income"]
    total_spend = structured["summary"]["total_spend"]
    categories = structured["categories"]
    prices = structured["prices"]
    summary = structured["summary"]

    # Format live prices for a more prominent display
    stock_prices_str = "\n".join([f"- {symbol}: {price}" for symbol, price in prices.get('stocks', {}).items()])
    crypto_prices_str = "\n".join([f"- {coin}: {price}" for coin, price in prices.get('crypto', {}).items()])

    return f"""You are a certified personal finance advisor in India.
    
    User's monthly income: {income}
    Current total spend: {total_spend}
    Surplus/Deficit: {summary['surplus_or_deficit']}
    Suggested savings minimum: {summary['suggested_savings_min']}
    Suggested savings target: {summary['suggested_savings']}
    Suggested needs cap: {summary['suggested_needs_cap']}
    Suggested wants cap: {summary['suggested_wants_cap']}

    Category totals (monthly):
    {categories}

    Live market prices (for context, not guarantees):
    Stocks:
    {stock_prices_str}
    Crypto:
    {crypto_prices_str}
    
    TASK:
    1) Provide financial advice.
    2) **You must provide a conservative, diversified starting plan that refers to the live prices provided.** For example, "Allocate X amount to Y ticker, which is currently priced at Z."
    3) Call out overspending categories and suggest reduction strategies.
    4) You must provide a 3-month habit plan with specific, actionable goals for each month. This is mandatory.
    5) Add a risk disclaimer.
    
    Return your response as a JSON object with the following keys:
    - "advice": a list of personalized advice strings.
    - "investment_plan": a dictionary describing a sample investment plan.
    - "reduction_strategies": a list of strategies to reduce spending.
    - "habit_plan": a list of monthly habit plans, where each plan is an object with 'month' and 'goals'.
    - "disclaimer": a string with risk disclaimers.
    
    Example format:
    {{
      "advice": [
        "advice point 1",
        "advice point 2"
      ],
      "investment_plan": {{
        "item1": "details",
        "item2": "details"
      }},
      "reduction_strategies": [
        "strategy 1",
        "strategy 2"
      ],
      "habit_plan": [
        {{ "month": 1, "goals": ["goal 1", "goal 2"] }},
        {{ "month": 2, "goals": ["goal 1", "goal 2"] }}
      ],
      "disclaimer": "risk disclaimers"
    }}
    """
