import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

DB_URL = os.getenv("DB_URL")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")    
GEMINI_API_KEY = "AIzaSyD9-JNP-rXqU0KLkRO5YiLUBdAX7CmeNbM"  

if not DB_URL or not GEMINI_API_KEY:
    raise RuntimeError("Please set DB_URL and GEMINI_API_KEY in .env")

engine = create_engine(DB_URL, pool_pre_ping=True)
db = SQLDatabase(engine)

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0,
    generation_config={"response_mime_type": "application/json"},
)
