from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean,JSON,Float
from datetime import datetime
from . import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True)
    phone_name = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    category = Column(JSON, nullable=True)   # store as list
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
    
    def to_dict(self):
        return {
            "id": self.id,
            "phone_name": self.phone_name,
            "brand": self.brand,
            "category": self.category,
            "domains": self.domains,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "images": self.images,
            "keys": self.keys,
            "filtered_prices": self.filtered_prices,
            "most_recent_price_amount": self.most_recent_price_amount,
            "most_recent_price_availability": self.most_recent_price_availability,
            "most_recent_price_currency": self.most_recent_price_currency,
            "most_recent_price_domain": self.most_recent_price_domain,
            "most_recent_price_first_seen": self.most_recent_price_first_seen,
            "is_processed": self.is_processed,
        }


class ChatbotResult(Base):
    __tablename__ = "chatbot_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(36), nullable=True)   # Just a plain integer, no FK
    title = Column(String(255))
    brand = Column(String(255))
    categories = Column(String(255))
    description = Column(Text)
    price = Column(String(50))
    url = Column(String(255))
    image = Column(String(255))