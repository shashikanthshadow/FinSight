from collections import defaultdict
from typing import List, Dict
from .models import ExpenseItem

CATEGORY_KEYWORDS = {
    "Housing": ["rent", "mortgage", "emi", "hoa"],
    "Utilities": ["electric", "water", "gas", "internet", "wifi", "utility"],
    "Groceries": ["grocery", "groceries", "supermarket", "vegetable", "provision"],
    "Transport": ["fuel", "petrol", "diesel", "uber", "ola", "bus", "metro", "transport", "parking"],
    "Dining": ["restaurant", "dining", "food", "coffee", "takeout"],
    "Insurance": ["insurance", "premium"],
    "Healthcare": ["pharmacy", "medical", "doctor", "hospital", "medicine"],
    "Education": ["tuition", "course", "udemy", "coursera", "books", "stationery"],
    "Entertainment": ["movie", "netflix", "prime", "spotify", "game"],
    "Personal": ["clothes", "apparel", "salon", "gym", "fitness", "personal"],
    "Debt": ["loan", "debt", "credit card", "interest"],
    "Misc": [],
}

def infer_category(name: str) -> str:
    lower = (name or "").lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return cat
    return "Misc"

def categorize_expenses(expenses: List[ExpenseItem]) -> Dict[str, float]:
    buckets = defaultdict(float)
    for e in expenses:
        cat = e.category or infer_category(e.name)
        buckets[cat] += float(e.amount)
    return dict(buckets)

def budget_recommendation(income: float, cat_totals: Dict[str, float]) -> Dict[str, float]:
    needs_cats = {"Housing", "Utilities", "Groceries", "Healthcare", "Insurance", "Transport", "Debt"}
    wants_cats = {"Dining", "Entertainment", "Personal", "Education", "Misc"}

    needs_spend = sum(v for k, v in cat_totals.items() if k in needs_cats)
    wants_spend = sum(v for k, v in cat_totals.items() if k in wants_cats)
    total_spend = needs_spend + wants_spend

    suggested_savings_min = max(income * 0.2, 0.0)
    capacity = income - total_spend
    suggested_savings = max(suggested_savings_min, capacity * 0.5 + suggested_savings_min * 0.5) if income else 0.0
    suggested_savings = max(0.0, min(suggested_savings, max(income - needs_spend, 0.0)))

    return {
        "needs_current": round(needs_spend, 2),
        "wants_current": round(wants_spend, 2),
        "total_spend": round(total_spend, 2),
        "income": round(income, 2),
        "surplus_or_deficit": round(income - total_spend, 2),
        "suggested_savings": round(suggested_savings, 2),
        "suggested_needs_cap": round(income * 0.5, 2),
        "suggested_wants_cap": round(income * 0.3, 2),
        "suggested_savings_min": round(income * 0.2, 2),
    }
