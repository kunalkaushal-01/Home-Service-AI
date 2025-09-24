# agents.py
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits import create_sql_agent
from langchain.prompts import SystemMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.memory import ConversationBufferMemory
import re

# ✅ Load env
load_dotenv()
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))



DB_URL = os.getenv("DB_URL")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY",'AIzaSyD9-JNP-rXqU0KLkRO5YiLUBdAX7CmeNbM')
GEMINI_API_KEY = "AIzaSyD9-JNP-rXqU0KLkRO5YiLUBdAX7CmeNbM"
if not DB_URL or not GEMINI_API_KEY:
    raise RuntimeError("Please set DB_URL and GEMINI_API_KEY in .env (do NOT hardcode)")

engine = create_engine(DB_URL, pool_pre_ping=True)
db = SQLDatabase(engine)


# System prompts
system_message_products = SystemMessagePromptTemplate.from_template("""
You are HomeShow AI, a polite shopping assistant specialized in DefaultProducts.

Rules:
- Always answer politely and strictly in JSON format.
- Only show 2–3 relevant products with prices if available.
- Do not mention tables, database names, or SQL.
- Ask politely for clarification if query is ambiguous.
- If product info is missing, suggest checking with the seller.
- Always return a JSON response in this format:

{
  "products": [
    {"name": "Product1", "price": 100, "seller": "SellerA"},
    {"name": "Product2", "price": 150, "seller": "SellerB"}
  ]
}
""")


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

system_message_autos = SystemMessagePromptTemplate.from_template("""
    You are HomeShow AI, a polite assistant specialized in Auto listings.
    Rules:
    - Always return valid JSON only.
    - Do not expose tables or SQL.
    - JSON format:
    {
    "autos": [
        {"make": "string", "model": "string", "year": "int", "price": "float", "dealer": "string"}
    ]
    }
    """
    )


# ✅ LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.2,
    # max_output_tokens=4000
)

#Memory
memory_products = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
memory_services = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)


memory_autos = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True
)

# ✅ Agent (auto SQL generation)
agent_products  = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True,
    extra_prompt_messages=[system_message_products],
    agent_type="openai-tools",
    memory=memory_products,
)
agent_services  = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True,
    extra_prompt_messages=[system_message_services],
    agent_type="openai-tools",
    memory=memory_services,
)

agent_autos = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True,
    extra_prompt_messages=[system_message_autos],
    # agent_type="openai-tools",
    agent_type="zero-shot-react-description",
    memory=memory_autos,
)

from langchain.agents import AgentExecutor

agent_autos = AgentExecutor.from_agent_and_tools(
    agent=agent_autos.agent, 
    tools=agent_autos.tools,
    verbose=True,
    handle_parsing_errors=True
)

def sanitize_input(text: str) -> str:
    """
    Clean user input by removing unwanted characters.
    Removes: *, \, /, # (and extra spaces).
    """
    # Remove *, \, /, #
    cleaned = re.sub(r'[\*\\/#+]', '', text)
    # Collapse multiple spaces into one
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def handle_smalltalk(user_input: str) -> str | None:
    greetings = ["hi", "hello","Hello","Hi","hey", "how are you", "good morning","good afternoon", "good evening"]
    # Only trigger if input is SHORT and exactly a greeting
    clean = user_input.lower().strip()
    if clean in greetings:
        return "Hello, welcome to HomeShow AI! How can I assist you today?"
    return None



# Determine which agent to use based on keywords
def route_query(user_input: str) -> str:
    try:
        clean_inut = sanitize_input(user_input)
        product_keywords = ["buy", "price", "product", "appliance", "clothing", "electronics", "furniture", "lawn", "tools", "sports"]
        service_keywords = ["install", "repair", "delivery", "home service", "contractor", "tutor", "mechanic", "nurse", "trainer"]
        car_keywords = ["car", "auto", "vehicle", "dealer", "used car", "new car","Auto Insurance", "Car Loan", "Car Lease", "Car Warranty", "Car Rental", "Car Repair", "Car Maintenance", "Car Detailing", "Car Accessories","Car Parts", "Car Financing", "Car Trade-In", "Car Inspection", "Car Title", "Car Registration","Finance", "Insurance", "Lease", "Warranty", "Rental", "Repair", "Maintenance", "Detailing", "Accessories","Parts", "Trade-In", "Inspection", "Title", "Registration"]

        input_lower = clean_inut.lower()
        if any(word in input_lower for word in product_keywords):
            return agent_products.invoke({"input": user_input})["output"]
        elif any(word in input_lower for word in service_keywords):
            print("Routing to services agent")
            return agent_services.invoke({"input": user_input})["output"]
        elif any(word in input_lower for word in car_keywords):
            print("Routing to autos agent")
            return agent_autos.invoke({"input": user_input}).get("output") or agent_autos.invoke({"input": user_input})
        else:
            # Default to products if unclear
            return agent_products.invoke({"input": user_input})["output"]
        
    except Exception as e:
        return f"Sorry, Server is Busy Can you try after Some Time: {str(e)}"

# # ✅ Interactive loop
# if __name__ == "__main__":
#     while True:
#         query = input("You: ")
#         if query.lower() in ["exit", "quit"]:
#             break
#         bot_chat = handle_smalltalk(query)
#         if bot_chat:
#             print(bot_chat)
#             continue
#         response = route_query(query)
#         print(response)




#inprocess this code
# import os
# import sys
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_community.utilities import SQLDatabase
# from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
# from langchain_community.agent_toolkits import create_sql_agent
# from langchain.prompts import SystemMessagePromptTemplate
# from langchain.output_parsers import PydanticOutputParser
# from langchain.memory import ConversationBufferMemory
# from autos_agent import agent_autos
# from service_agent import agent_services
# from products_agent import agent_products
# import re

# # ✅ Load env
# load_dotenv()
# # sys.path.append(os.path.dirname(os.path.dirname(__file__)))



# DB_URL = os.getenv("DB_URL")
# # GEMINI_API_KEY = os.getenv("GEMINI_API_KEY",'AIzaSyD9-JNP-rXqU0KLkRO5YiLUBdAX7CmeNbM')
# GEMINI_API_KEY = "AIzaSyD9-JNP-rXqU0KLkRO5YiLUBdAX7CmeNbM"
# if not DB_URL or not GEMINI_API_KEY:
#     raise RuntimeError("Please set DB_URL and GEMINI_API_KEY in .env (do NOT hardcode)")

# engine = create_engine(DB_URL, pool_pre_ping=True)
# db = SQLDatabase(engine)
# from products_agent import agent_products
# from service_agent import agent_services


# def sanitize_input(text: str) -> str:
#     """
#     Clean user input by removing unwanted characters.
#     Removes: *, \, /, # (and extra spaces).
#     """
#     # Remove *, \, /, #
#     cleaned = re.sub(r'[\*\\/#+]', '', text)
#     # Collapse multiple spaces into one
#     cleaned = re.sub(r'\s+', ' ', cleaned)
#     return cleaned.strip()

# def handle_smalltalk(user_input: str) -> str | None:
#     greetings = ["hi", "hello", "hey", "how are you", "good morning", "good evening"]
#     # Only trigger if input is SHORT and exactly a greeting
#     clean = user_input.lower().strip()
#     if clean in greetings:
#         return "Hello, welcome to HomeShow AI! How can I assist you today?"
#     return None


# # Determine which agent to use based on keywords
# def route_query(user_input: str) -> str:
#     clean_inut = sanitize_input(user_input)
#     product_keywords = ["buy", "price", "product", "appliance", "clothing", "electronics", "furniture", "lawn", "tools", "sports"]
#     service_keywords = ["install", "repair", "delivery", "home service", "contractor", "tutor", "mechanic", "nurse", "trainer"]
#     car_keywords = ["car", "auto", "vehicle", "dealer", "used car", "new car","Auto Insurance", "Car Loan", "Car Lease", "Car Warranty", "Car Rental", "Car Repair", "Car Maintenance", "Car Detailing", "Car Accessories","Car Parts", "Car Financing", "Car Trade-In", "Car Inspection", "Car Title", "Car Registration","Finance", "Insurance", "Lease", "Warranty", "Rental", "Repair", "Maintenance", "Detailing", "Accessories","Parts", "Trade-In", "Inspection", "Title", "Registration"]
#     input_lower = clean_inut.lower()
#     if any(word in input_lower for word in product_keywords):
#         return agent_products.invoke({"input": user_input})["output"]
#     elif any(word in input_lower for word in service_keywords):
#         print("Routing to services agent")
#         return agent_services.invoke({"input": user_input})["output"]
#     elif any(word in input_lower for word in car_keywords):
#         print("Routing to autos agent")
#         return agent_autos.invoke({"input": user_input}).get("output") or agent_autos.invoke({"input": user_input})
#     else:
#         # Default to products if unclear
#         return agent_products.invoke({"input": user_input})["output"]

# # ✅ Interactive loop
# if __name__ == "__main__":
#     while True:
#         query = input("You: ")
#         if query.lower() in ["exit", "quit"]:
#             break
#         bot_chat = handle_smalltalk(query)
#         if bot_chat:
#             print(bot_chat)
#             continue
#         response = route_query(query)
#         print(response)

