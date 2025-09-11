from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime,JSON,Float
from typing import Optional, List
from datetime import datetime
from sqlalchemy.sql import func
from pydantic import BaseModel
from config import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True)
    phone_name = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    category = Column(JSON, nullable=True)  # store as list
    domains = Column(JSON, nullable=True)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)  # cleaned text
    tags = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)
    keys = Column(JSON, nullable=True)
    filtered_prices = Column(JSON, nullable=True)
    
    most_recent_price_amount = Column(Float, nullable=True)
    most_recent_price_availability = Column(Boolean, nullable=True)
    most_recent_price_currency = Column(String, nullable=True)
    most_recent_price_domain = Column(String, nullable=True)
    most_recent_price_first_seen = Column(String, nullable=True)
    
    is_processed = Column(Boolean, default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "phone_name": "iPhone 15 Pro",
                "brand": "Apple",
                "category": ["Smartphones"],
                "domains": ["amazon.com", "flipkart.com"],
                "title": "Apple iPhone 15 Pro (128GB, Blue Titanium)",
                "description": "Latest iPhone with A17 Pro chip and ProMotion display.",
                "tags": ["iPhone", "Smartphone", "Flagship"],
                "images": [
                    "https://example.com/image1.jpg",
                    "https://example.com/image2.jpg"
                ],
                "keys": ["A17 Pro chip", "6.1-inch display", "128GB storage"],
                "filtered_prices": [
                    {
                        "amount": 999.99,
                        "currency": "USD",
                        "domain": "amazon.com",
                        "availability": True,
                        "first_seen": "2024-09-01"
                    }
                ],
                "most_recent_price_amount": 999.99,
                "most_recent_price_availability": True,
                "most_recent_price_currency": "USD",
                "most_recent_price_domain": "amazon.com",
                "most_recent_price_first_seen": "2024-09-01",
                "is_processed": False
            }
        }


class ProductResponseSchema(BaseModel):
    """Schema for returning product details from DB/API"""
    id: str
    phone_name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[List[str]] = None
    domains: Optional[List[str]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    keys: Optional[List[str]] = None
    filtered_prices: Optional[List[dict]] = None
    most_recent_price_amount: Optional[float] = None
    most_recent_price_availability: Optional[bool] = None
    most_recent_price_currency: Optional[str] = None
    most_recent_price_domain: Optional[str] = None
    most_recent_price_first_seen: Optional[str] = None
    is_processed: bool = False
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ProductListSchema(BaseModel):
    """Schema for a list of products"""
    products: List[ProductResponseSchema]

class ProductCountSchema(BaseModel):
    """Schema for returning product counts (for monitoring/health checks)"""
    status: str
    total_products: int
    unprocessed_products: int