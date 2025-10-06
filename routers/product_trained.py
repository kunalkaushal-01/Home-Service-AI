from fastapi import APIRouter, Depends, HTTPException,Form
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from config import get_db  
from typing import Dict,Optional,List,Any
# from utils.celery_new_task import process_json_data, manual_process_json
# from utils.faiss_utils import search
import google.generativeai as genai
import json
import logging
from google.api_core.exceptions import GoogleAPIError, ResourceExhausted
from models.user import Product,ChatbotResult
# from utils.celery_latest_task import chatbot_query
from uuid import uuid4, UUID
from sqlalchemy.dialects.postgresql import UUID
from data.agents import handle_smalltalk,route_query
import re
import json
from google import genai
from google.genai import types
import os


router = APIRouter(
    prefix="/products",
    tags=["Products Training"],
    
)

@router.post("/agent_chatbot")
def agent_chatbot(user_input: str = Form(...), user_id: Optional[str] = Form(None)):
    """
    Chatbot API that uses an agent to process user queries and return a JSON response.
    """
    try:
        # First, check for smalltalk
        bot_chat = handle_smalltalk(user_input)
        if bot_chat:
            return {
                "status": "success",
                "message": bot_chat,
                "user_id": user_id if user_id else str(uuid4())
            }

        # Otherwise, route query to the correct agent
        response = route_query(user_input)

        return {
            "status": "success",
            "message": response,
            "user_id": user_id if user_id else str(uuid4())
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


CONVERSATIONS = {}

def create_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)

def clean_json_output(text: str):
    """Remove markdown fences and extract clean JSON."""
    # Remove triple backticks and optional 'json'
    cleaned = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()
    # If still wrapped in ``` ... ``` blocks, remove them
    cleaned = re.sub(r"^```|```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
    return cleaned

# def ask_product_insights(client: genai.Client, title: str, brand: str, price: str, reviews: int, description: str):
#     grounding_tool = types.Tool(google_search=types.GoogleSearch())
#     config = types.GenerateContentConfig(tools=[grounding_tool])

#     query = f"""
#     Product details:
#     Title: {title}
#     Brand: {brand}
#     Price: {price}
#     Reviews: {reviews}
#     Description: {description}

#     Please return the answer ONLY as a JSON object with this format:
#     {{
#         "insights": "overall insights on pricing, reviews, and quality",
#         "average_price": "market price range",
#         "average_reviews": number,
#         "quality_summary": "summary of build quality, durability, performance"
#     }}
#     Do not add markdown fences or explanations.
#     """

#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=query,
#         config=config
#     )

#     raw_text = response.text
#     try:
#         clean_text = clean_json_output(raw_text)
#         return json.loads(clean_text)
#     except Exception:
#         return {"raw_output": raw_text}  # fallback if still not valid JSON

# def ask_product_insights(client: genai.Client, conversation_text: str):
#     grounding_tool = types.Tool(google_search=types.GoogleSearch())
#     config = types.GenerateContentConfig(tools=[grounding_tool])

#     query = f"""
#     You are a helpful product insights assistant.
#     Here is the conversation so far:
#     {conversation_text}

#     Please return the answer ONLY as a JSON object in this format:
#     {{
#         "insights": "overall insights on pricing, reviews, and quality",
#         "average_price": "market price range",
#         "average_reviews": number,
#         "pros": ["pro1", "pro2", "pro3"],
#         "cons": ["con1", "con2", "con3"],
#         "summary": "brief conversational response (under 100 words)"
#     }}
#     Do not include markdown fences or explanations.
#     """

#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=query,
#         config=config
#     )

#     raw_text = response.text
#     try:
#         clean_text = clean_json_output(raw_text)
#         return json.loads(clean_text)
#     except Exception:
#         return {"raw_output": raw_text}

def ask_product_insights(client: genai.Client, conversation_text: str):
    """Ask Gemini API for concise product insights with conversational context."""
    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(tools=[grounding_tool])

    prompt = f"""
    You are an intelligent assistant that helps users analyze product details and provide short, structured responses.

    Below is the ongoing conversation context:
    {conversation_text}

    Now, based on the latest product details provided, please respond ONLY in JSON with this exact structure:
    {{
        "rating": "<overall rating or sentiment out of 5>",
        "average_price": "<typical or market price range>",
        "pros": ["Top 3 pros only"],
        "cons": ["Top 3 cons only"],
        "summary": "<short conversational summary — no longer than 3 sentences>"
    }}

    Keep it concise and professional.
    Do not include markdown or explanations.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )

    raw_text = response.text
    try:
        clean_text = clean_json_output(raw_text)
        return json.loads(clean_text)
    except Exception:
        return {"raw_output": raw_text}

@router.post("/product-search")
def product_search(
    user_id: str = Form(...),
    title:str = Form(...),  
    description: str = Form(...),
    brand: str = Form(...),
    price: str = Form(...),
    reviews: int = Form(...)
    ):
    """
    Conversational Product Insights API
    - Each user_id maintains its own conversation history.
    - If the same user_id sends another request, the chat continues.
    """
    try:
        
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key is None:
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        client = create_client(api_key)
        if user_id not in CONVERSATIONS:
            CONVERSATIONS[user_id] = []
        user_message = f"Product details:\nTitle: {title}\nBrand: {brand}\nPrice: {price}\nReviews: {reviews}\nDescription: {description}"
        CONVERSATIONS[user_id].append({"role": "user", "content": user_message})
        # Convert history into text
        conversation_text = "\n".join(
            [f"{msg['role'].capitalize()}: {msg['content']}" for msg in CONVERSATIONS[user_id]]
        )
        result = ask_product_insights(client, conversation_text)
        CONVERSATIONS[user_id].append({"role": "assistant", "content": json.dumps(result)})
        # return {"status": "success", "data": result}
        return {
            "status": "success",
            "user_id": user_id,
            "data": result,
            "conversation_length": len(CONVERSATIONS[user_id])
        }
    except Exception as e:
        logging.error(f"Error fetching product insights: {e}")
        return {"status": "error", "message": str(e)}   
    




