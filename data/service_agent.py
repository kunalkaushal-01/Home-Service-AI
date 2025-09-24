import os
import json
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import create_sql_agent
from langchain.prompts import SystemMessagePromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from base import llm,db


load_dotenv()

DB_URL = os.getenv("DB_URL")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY",'AIzaSyD9-JNP-rXqU0KLkRO5YiLUBdAX7CmeNbM')
GEMINI_API_KEY = "AIzaSyD9-JNP-rXqU0KLkRO5YiLUBdAX7CmeNbM"
if not DB_URL or not GEMINI_API_KEY:
    raise RuntimeError("Please set DB_URL and GEMINI_API_KEY in .env (do NOT hardcode)")

engine = create_engine(DB_URL, pool_pre_ping=True)
db = SQLDatabase(engine)


system_message_services = SystemMessagePromptTemplate.from_template("""
You are HomeShow AI, a polite assistant specialized in services.
Strictly follow these rules:

- Only return a valid JSON object.
- Do NOT include Markdown, bullet points (*), extra characters, or explanatory text.
- Do not mention tables, database names, or SQL.
- We do not share our users personal info (email, address, Mobile Number, etc.)
- The JSON must have the following structure:
{
  "providers": [
    {
      "companyName": "string",
      "address": "string",
      "phoneNumber": "string",
      "email": "string",
      "latitude": "float or null",
      "longitude": "float or null"
    }
  ]
}
- If a field is unknown, set it to null.
- If no providers match, return {"providers": []}.
""")

SERVICE_CATEGORIES = {
    "Home Services & Real Estate": ["Real Estate Agents", "Property Manager", "Home Inspector", "General Contractor", "Handyman"],
    "Appliances, Electronics & A/V": ["A/V Home Theatre", "Appliance Delivery", "Appliance Installation", "Appliance Repair", "Electronics Delivery"],
    "Furniture & Interior Design": ["Furniture Assembly", "Furniture Delivery", "Furniture Repair", "Interior Designer"],
    "Yard, Landscape & Exterior": ["Asphalt & Paving Services", "Deck & Patio Builders", "Fence Installation & Repair", "Fence Staining & Restoration", "Garage Door Repair"],
    "Licensed & Specialty Contractors": ["Cabinet Maker / Woodwork", "Carpentry", "Countertop Fabrication,Repair", "Drywall & Plastering", "Electrical"],
    "Home Help & Personal Care": ["Chiropractic", "Home Nurse / Medical Care", "Housekeeping", "In-Home Senior Care", "Junk Haul Away"],
    "Auto Services": ["Auto Detailing", "Auto Mechanic", "Driver / Chauffeur"],
    "Education & Wellness": ["Fitness Trainer (In-Home)", "Health & Wellness Coach", "Music Lessons", "Nutritionist / Dietician", "Tutoring / Education"]
}


memory_services = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent_services = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True,
    extra_prompt_messages=[system_message_services],
    agent_type="openai-tools",
    memory=memory_services,
)

def get_service_providers(subcategory: str, location: str = None):
    query = f"""
    SELECT T1."firstName", T1."lastName", T1.email, T1."mobileNumber",
           T2.address, T2.experience, T3."providerRating", T3."providerComment"
    FROM "ServiceUsers" AS T1
    JOIN "ServiceProfileDetails" AS T2 ON T1.id = CAST(T2.userid AS INTEGER)
    JOIN "ServiceReviews" AS T3 ON T1.id = CAST(T3."providerId" AS INTEGER)
    WHERE T2.subcategory = '{subcategory}'
    """
    if location:
        query += f" AND (T1.address ILIKE '%{location}%' OR T2.address ILIKE '%{location}%')"

    query += " ORDER BY T3.\"providerRating\" DESC LIMIT 3"
    result = engine.execute(query)
    providers = [dict(row) for row in result]
    return providers