from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Customer:
full_name: str
email: Optional[str] = None
phone: Optional[str] = None


@dataclass
class Vehicle:
make: str
model: str
version: str
year: int


@dataclass
class Pricing:
list_price: float
discounts: List[str]
trade_in_value: float
extras: List[str]


@dataclass
class Finance:
plan_name: str
apr: float
months: int


@dataclass
class Warranty:
name: str
months: int


@dataclass
class Quote:
customer: Customer
vehicle: Vehicle
pricing: Pricing
finance: Finance
warranty: Warranty
meta: Dict[str, str]
notes: Optional[str] = None


@dataclass
class Contract:
quote: Quote
special_terms: str
legal_block: str
rendered_md: str
rendered_pdf_path: Optional[str] = None
