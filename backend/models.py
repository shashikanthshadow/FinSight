from pydantic import BaseModel, Field
from typing import List, Optional

class ExpenseItem(BaseModel):
    name: str = Field(..., description="e.g., Rent, Groceries")
    amount: float = Field(..., ge=0)
    category: Optional[str] = Field(None, description="Optional pre-tag")

class AnalyzeRequest(BaseModel):
    income: float = Field(..., ge=0)
    expenses: List[ExpenseItem]

class AnalyzeResponse(BaseModel):
    categories: dict
    summary: dict
    prices: dict
    advice: str
