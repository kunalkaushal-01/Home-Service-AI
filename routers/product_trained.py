# routers/product_trained.py
from fastapi import APIRouter, Depends, HTTPException,Form
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from config import get_db  
from typing import Dict,Optional,List,Any
from utils.celery_new_task import process_json_data, manual_process_json
from utils.faiss_utils import search
import google.generativeai as genai
import json
import logging
from google.api_core.exceptions import GoogleAPIError, ResourceExhausted
from models.user import Product,ChatbotResult
from utils.celery_latest_task import chatbot_query
from uuid import uuid4, UUID
from sqlalchemy.dialects.postgresql import UUID


router = APIRouter(
    prefix="/products",
    tags=["Products Training"],
)


genai.configure(api_key="AIzaSyDd1RJgBs2p573iam4qGs62QOJbTNkoocQ")
model = genai.GenerativeModel("gemini-1.5-pro")

class AskRequest(BaseModel):
    q: str
    brand: Optional[str] = None
    category: str
    k: int = 3
    keywords: Optional[List[str]] = None 

@router.get("/test")
def test_products(db=Depends(get_db)):
    return {"message": "Products route is working fine!", "db_connection": str(db)}

@router.post("/ingest-now")
def ingest_now():
    # trigger manual ingestion synchronously
    res = manual_process_json.apply().get()  # uses celery task wrapper
    return res

from data.product import product_call_api
# @router.get("/ask")
# def ask_products(q: Optional[str] = None, k: int = 3):
#     if not q:
#         raise HTTPException(status_code=400, detail="query param 'q' required")

#     try:
#         # Get top search results from FAISS
#         hits = search("products", q, k=k)

#         # Convert hits to JSON context
#         context = "\n".join([json.dumps(hit["metadata"], indent=2) for hit in hits])

#         # Build restricted prompt
#         prompt = f"""
#         You are a product assistant. Use only the following product data to answer:

#         {context}

#         Question: {q}
#         If the answer is not found in the data, reply:
#         "Sorry, I don’t have information about that."
#         """

#         # Call Gemini
#         response = model.generate_content(prompt)

#         return {
#             "query": q,
#             "answer": response.text,
#             "metadata": hits[0]["metadata"] if hits else None
#         }

#     except ResourceExhausted as e:  # 429 quota limit error
#         logging.error(f"Quota exceeded: {e}")
#         raise HTTPException(
#             status_code=429,
#             detail="Quota exceeded. Please try again later or check your billing."
#         )
#     except GoogleAPIError as e:  # Any Gemini API error
#         logging.error(f"Gemini API error: {e}")
#         raise HTTPException(
#             status_code=502,
#             detail="Upstream Gemini API error. Please try again later."
#         )
#     except Exception as e:  # Fallback for 500 errors
#         logging.exception("Unexpected server error")
#         raise HTTPException(
#             status_code=500,
#             detail="Internal server error. Please try again later."
#         )


@router.post("/chatbot")
def chatbot(
    user_input: str = Form(..., description="User query"),
    user_id: Optional[str] = Form(None, description="User ID (UUID, optional for first request)"),
    db: Session = Depends(get_db)
):
    """
    Chatbot API that takes form-data and queries Weaviate with hybrid search.
    - First request: Send only user_input, get UUID in response
    - Subsequent requests: Send user_input + user_id (UUID from first response)
    """
    try:
        # Generate UUID if not provided (first request)
        is_first_request = not user_id or user_id == "string"
        if is_first_request:
            user_id = str(uuid4()) 
            print(f"Generated new UUID: {user_id}") 
            return {
                "status": "success",
                "message": "Welcome to home AI service, how may I help?",
                "user_id": user_id,
                "is_welcome": True
            }
        else:
            # Validate UUID format for subsequent requests
            try:
                UUID(user_id) 
                print(f"Using existing UUID: {user_id}")
            except ValueError:
                return {"status": "error", "message": "Invalid UUID format"}
        
        # Process the query (same for both first and subsequent requests)
        results = chatbot_query(user_input, limit=1)
        if not results:  # <--- Handle empty results
            return {
                "status": "success",
                "message": "Sorry, we could not find the product.",
                "results": [],
                "user_id": user_id,
                "is_welcome": False
            }
        # if results:
        result = results[0]
        chatbot_entry = ChatbotResult(
            user_id=user_id,
            title=result.get("title"),
            brand=result.get("brand"),
            categories=",".join(result.get("categories", [])),
            description=result.get("description"),
            price=result.get("price"),
            url=result.get("url"),
            image=result.get("image"),
        )
        db.add(chatbot_entry)
        db.commit()
        db.refresh(chatbot_entry)
        
        return {
            "status": "success",
            "results": results if results else [],
            "user_id": user_id ,
            "is_welcome": False
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}



@router.get("/chatbot/history/{user_id}")
def get_chat_history(user_id: str, db: Session = Depends(get_db)):
    """
    Get all chat history for a specific user_id
    """
    try:
        # Validate UUID format
        UUID(user_id)
        
        # Get all chats for this user
        chats = db.query(ChatbotResult).filter(ChatbotResult.user_id == user_id).all()
        
        chat_history = []
        for chat in chats:
            chat_history.append({
                "id": chat.id,
                "title": chat.title,
                "brand": chat.brand,
                "categories": chat.categories.split(",") if chat.categories else [],
                "description": chat.description,
                "price": chat.price,
                "url": chat.url,
                "image": chat.image
            })
        
        return {
            "status": "success",
            "user_id": user_id,
            "chat_count": len(chat_history),
            "chat_history": chat_history
        }
    
    except ValueError:
        return {"status": "error", "message": "Invalid UUID format"}
    except Exception as e:
        return {"status": "error", "message": str(e)}




#List of brand and category
@router.get("/products/brand-category")
def get_brand_category(db: Session = Depends(get_db)):
    results = db.query(Product.brand, Product.category).all()
    return [
        {"brand": brand, "category": category}
        for brand, category in results
    ]