from typing import Dict, Any, List
from langsmith import Client as LangSmithClient
import os
import json
import re

from .finance_tools import categorize_expenses, budget_recommendation
from .utils import get_stock_price, get_crypto_price, build_prompt, gemini_generate

# LangSmith client (optional)
ls_client = None
if os.getenv("LANGSMITH_API_KEY"):
    try:
        ls_client = LangSmithClient(api_key=os.getenv("LANGSMITH_API_KEY"))
    except Exception:
        ls_client = None

# Defaults (change to your preferred tickers)
DEFAULT_STOCKS = ["^NSEI", "^BSESN"]  # Nifty 50, Sensex
DEFAULT_CRYPTO = ["bitcoin", "ethereum"]

async def run_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    income: float = float(payload["income"])
    expenses: List[Dict[str, Any]] = payload["expenses"]

    # Normalize and categorize
    normalized = []
    for x in expenses:
        normalized.append(type("Expense", (), {"name": x.get("name",""), "amount": x.get("amount",0), "category": x.get("category")}))

    categories = categorize_expenses(normalized)
    summary = budget_recommendation(income, categories)

    # Fetch live prices
    stocks_prices = {s: round(get_stock_price(s), 2) for s in DEFAULT_STOCKS}
    crypto_prices = {c: round(get_crypto_price(c), 2) for c in DEFAULT_CRYPTO}
    prices = {"stocks": stocks_prices, "crypto": crypto_prices}

    structured = {"categories": categories, "summary": summary, "prices": prices}
    prompt = build_prompt(structured)
    
    # Get the raw response from Gemini
    raw_advice = await gemini_generate(prompt)

    # Try to parse the JSON response
    try:
        # Clean the response to ensure it's a valid JSON object
        clean_raw_advice = raw_advice.strip()
        # Find the first and last curly braces to isolate the JSON
        match = re.search(r"\{.*\}", clean_raw_advice, re.DOTALL)
        if match:
            clean_raw_advice = match.group(0)

        advice_json = json.loads(clean_raw_advice)
        advice = advice_json.get("advice", [])
        investment_plan = advice_json.get("investment_plan", {})
        reduction_strategies = advice_json.get("reduction_strategies", [])
        habit_plan = advice_json.get("habit_plan", [])
        disclaimer = advice_json.get("disclaimer", "")
        
        # Combine the structured advice into a readable string with Markdown formatting
        advice_string = "## Personalized Financial Advice\n"
        advice_string += "\n".join([f"* {item}" for item in advice])
        
        advice_string += "\n\n## Conservative Diversified Starting Plan\n"
        advice_string += investment_plan.get("overview", "") + "\n"
        for section, details in investment_plan.items():
            if section != "overview":
                advice_string += f"\n* **{section.replace('_', ' ').title()}**: \n"
                if isinstance(details, dict):
                    for key, value in details.items():
                        advice_string += f"  * {key}: {value}\n"
                else:
                    advice_string += f"  * {details}\n"

        advice_string += "\n## Overspending Categories and Reduction Strategies\n"
        advice_string += "\n".join([f"* {item}" for item in reduction_strategies])
        
        advice_string += "\n\n## 3-Month Habit Plan\n"
        # Check if habit_plan is not empty and then loop
        if habit_plan:
            for month_plan in habit_plan:
                if 'month' in month_plan and 'goals' in month_plan:
                    advice_string += f"* **Month {month_plan['month']}**: {', '.join(month_plan['goals'])}\n"
        else:
            advice_string += "* No specific 3-month plan was generated. This may be due to the data provided.\n"
            
        advice_string += "\n\n## Risk Disclaimers\n"
        advice_string += disclaimer

    except json.JSONDecodeError as e:
        # If parsing fails, use a clean fallback message
        print(f"JSON Decode Error: {e}")
        advice_string = "I apologize, but I was unable to generate a structured financial plan at this time. Please try again."

    result = {"categories": categories, "summary": summary, "prices": prices, "advice": advice_string}

    # Log to LangSmith if configured
    if ls_client:
        try:
            ls_client.log_event("smartbudget_run", {"input": payload, "structured": structured, "prompt": prompt[:8000], "advice": advice_string[:8000]})
        except Exception:
            pass

    return result
