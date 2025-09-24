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


