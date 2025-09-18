import os
import requests
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from sqlalchemy import text
# from langchain.agents.react.prompt import REACT_PROMPT
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# from config import SessionLocal, Base, engine
from sqlalchemy import create_engine

# GEMINI_API_KEY="AIzaSyD9-JNP-rXqU0KLkRO5YiLUBdAX7CmeNbM"
GEMINI_API_KEY="AIzaSyBofbP27IxpERC1p0ENtfu18U1fEN2MUcI"

engine = create_engine(
    "postgresql+psycopg2://",
    connect_args={
        "user": "postgres",
        "password": "P)OoHY@6FGVH&t",
        "host": "3.228.47.36",
        "port": 9211,
        "dbname": "thehomeshow_db"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("✅ Connected")


# def homeshow_api_search(query: str) -> str:
#     """Searches The Home Show database for products matching the query."""
#     if not query.strip().lower().startswith("select"):
#         return "Only select query are allowed"
#     db = SessionLocal()
#     # print(db,'get db')
#     query = text('SELECT id, "productTitle", "productDescription" , "productRegularPrice","productImages","comp_price_market","color_code_description" FROM "DefaultProducts" LIMIT 10')
#     result = db.execute(query).fetchall()
#     print(result,'resultresultresult')
#     for row in result:
#         obj = {}
#         obj['id'] = row[0]
#         obj['productTitle'] = row[1]
#         obj['productDescription'] = row[2]
#         obj['productRegularPrice'] = row[3]
#         obj['productImages'] = row[4]
#         obj['comp_price_market'] = row[5]
#         obj['color_code_description'] = row[6]
#         print(obj,'objobjobjobj')

# print(homeshow_api_search("lawn mower"))

# @tool
# def run_sql(query: str) -> str:
#     """
#     Run a SQL query on the DefaultProducts table and return results.
#     Only SELECT queries are allowed.
#     """
#     query = query.strip().strip("```").replace("sql", "").strip()

#     if not query.lower().startswith("select"):
#         return "❌ Only SELECT queries are allowed."

#     db = SessionLocal()
#     try:
#         result = db.execute(text(query)).fetchall()
#         return [dict(row._mapping) for row in result]
#         # return str(result)
#     except Exception as e:
#         return f"❌ Error running query: {e}"
#     finally:
#         db.close()

# @tool()
# def run_sql(query: str) -> str:
#     """
#     Run a SQL query on the DefaultProducts table and return results.
#     Only SELECT queries are allowed.
#     """
#     query = query.strip().strip("```").replace("sql", "").strip()

#     if not query.lower().startswith("select"):
#         return "❌ Only SELECT queries are allowed."

#     db = SessionLocal()
#     try:
#         result = db.execute(text(query)).fetchall()
#         db.close()

#         if not result:
#             return "✅ No results found. Final Answer."

#         # Format the result nicely for the agent
#         rows = [dict(row._mapping) for row in result]
#         return f"✅ Query executed successfully. Final Answer:\n{json.dumps(rows, indent=2)}"

#     except Exception as e:
#         db.close()
#         return f"❌ Error running query: {e}"

# # -----------------------------
# # 3. Setup Gemini LLM
# # -----------------------------
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",google_api_key=GEMINI_API_KEY) 

# # -----------------------------
# # 4. Agent Setup
# # -----------------------------
# tools = [run_sql]

# # prompt = PromptTemplate.from_template("""
# # You are a helpful assistant that generates **one SQL query** for a PostgreSQL database and returns the results in plain text. 

# # The table is "DefaultProducts".
# # Allowed fields: 
# # - id
# # - "productTitle"
# # - "productDescription"
# # - "productRegularPrice"
# # - "productImages"
# # - "comp_price_market"
# # - "color_code_description"

# # TOOLS:
# # {tools}

# # You can use these tools: {tool_names}.

# # ⚠️ Rules:
# # - Generate only ONE SQL query to answer the user question.
# # - Do NOT loop or repeat queries.
# # - Do NOT use markdown, triple backticks, or ```sql.
# # - Use plain SQL only.
# # - Always filter out rows where "productRegularPrice" = 0 (unless user explicitly asks for them).
# # - After the query runs, return the results in a clean, human-readable format (list with id, title, and price).
# # - If no results are found, just say "No matching products found."

# # Output format:
# # Thought: Describe reasoning briefly
# # Action: run_sql
# # Action Input: SELECT ...;

# # {agent_scratchpad}

# # User Question: {input}
# # """)
# prompt = PromptTemplate.from_template("""
# You are a helpful assistant that generates **exactly one SQL query** for a PostgreSQL database and returns the results in plain text.
 
# The table is "DefaultProducts".
# Allowed fields:
# - id
# - "productTitle"
# - "productDescription"
# - "productRegularPrice"
# - "productImages"
# - "comp_price_market"
# - "color_code_description"
 
# TOOLS:
# {tools}
 
# You can use these tools: {tool_names}.
 
# ⚠️ CRITICAL RULES:
# - Generate EXACTLY ONE SQL query to answer the user question.
# - NEVER loop, repeat, or generate multiple queries.
# - NEVER use markdown, triple backticks, or ```sql formatting.
# - Use plain SQL only - no explanations before or after.
# - Always filter out rows where "productRegularPrice" = 0 (unless user explicitly asks for them).
# - Return results in clean, human-readable format: "ID: X, Title: Y, Price: Z"
# - After ovservation which record you find out then five the ist result in final answer and return the response.
# - When the tool returns a result with 'Final Answer', stop reasoning and return it to the user.
# - If no results found, respond with: "No matching products found."
# - DO NOT ask follow-up questions or request clarification.
 
# OUTPUT FORMAT (follow exactly):
# Thought: [Brief one-sentence reasoning]
# Action: run_sql
# Action Input: SELECT ...;
 
# {agent_scratchpad}
 
# User Question: {input}
# """)


# agent = create_react_agent(llm, tools, prompt)
# agent_executor = AgentExecutor(
#     agent=agent,
#     tools=tools,
#     verbose=True,
#     handle_parsing_errors=True
# )

# # -----------------------------
# # 5. Test Query
# # -----------------------------
# user_question = "Find me a french door stainless steel refrigerator under $2000"
# response = agent_executor.invoke({"input": user_question})

# print("🔎 Gemini Response:", response)
# print(response['output'])


# from langchain.agents import create_react_agent, AgentExecutor
# from langchain_core.tools import tool
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import PromptTemplate
# from sqlalchemy import text
# import json
# import threading
# import time
# from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
# import re

# @tool()
# def run_sql(query: str) -> str:
#     """
#     Run a SQL query on the DefaultProducts table and return results.
#     Only SELECT queries are allowed.
#     """
#     query = query.strip().strip("```").replace("sql", "").strip()

#     if not query.lower().startswith("select"):
#         return "❌ Only SELECT queries are allowed."

#     db = SessionLocal()
    
#     try:
#         result = db.execute(text(query)).fetchall()
#         db.close()

#         if not result:
#             return "No matching products found."

#         # Format results exactly as requested
#         formatted_results = []
#         products  = []
#         for row in result[:5]:
#             row_dict = dict(row._mapping) if hasattr(row, '_mapping') else dict(row)
#         #     formatted_results.append(f"ID: {row_dict.get('id', 'N/A')}, Title: {row_dict.get('productTitle', 'N/A')}, Price: ${row_dict.get('productRegularPrice', 'N/A')}")
            
#         # return "\n".join(formatted_results)
#             product = {
#                 "id": row_dict.get('id'),
#                 "title": row_dict.get('productTitle'),
#                 "description": row_dict.get('productDescription', 'No description available'),
#                 "price": float(row_dict.get('productRegularPrice') or 0),
#                 "images": row_dict.get('productImages', ''),
#                 "color": row_dict.get('color_code_description', '')
#             }
#             products.append(product)
#         print(products,'productsproductsproducts')
#         return json.dumps({
#             "status": "success", 
#             "count": len(products),
#             "products": products
#         }, indent=2)

#     except Exception as e:
#         db.close()
#         # Handle case sensitivity error specifically
#         if "does not exist" in str(e).lower():
#             return f"❌ Table not found. Error: {e}\nPlease check if table name should be quoted or has different case."
#         return f"❌ Error running query: {e}"

# # Setup Gemini LLM with lower temperature
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     google_api_key=GEMINI_API_KEY,
#     temperature=0
# )


# prompt = PromptTemplate.from_template("""
# You are a SQL assistant that generates EXACTLY ONE query and returns JSON results.

# Database: "DefaultProducts" table
# Fields: id, "productTitle", "productDescription", "productRegularPrice", "productImages", "comp_price_market", "color_code_description"

# TOOLS: {tools}
# TOOL NAMES: {tool_names}

# CRITICAL RULES:
# 1. Generate EXACTLY ONE SQL query only
# 2. ALWAYS use quoted table name: "DefaultProducts"
# 3. ALWAYS include "productDescription" in SELECT for full product info
# 4. Always exclude products with "productRegularPrice" = 0
# 5. After getting results, immediately provide Final Answer as JSON

# RESPONSE FORMAT:
# Thought: I need to search for products with descriptions
# Action: run_sql  
# Action Input: SELECT id, "productTitle", "productDescription", "productRegularPrice", "productImages", "color_code_description" FROM "DefaultProducts" WHERE ... AND "productRegularPrice" != 0

# After getting observation, immediately respond with:
# Final Answer: [JSON results from the tool]

# {agent_scratchpad}

# User Question: {input}
# """)

# # Configure agent with strict controls
# tools = [run_sql]
# agent = create_react_agent(llm, tools, prompt)

# agent_executor = AgentExecutor(
#     agent=agent,
#     tools=tools,
#     verbose=False,
#     handle_parsing_errors=True,
#     max_iterations=2,  # Only allow 2 iterations maximum
#     early_stopping_method="force",
#     return_intermediate_steps=False
# )

# #  Simple function for one question at a time
# def ask_question(question: str):
#     print(f"🔍 Question: {question}")
#     try:
#         print("inside 1st try")
#         response = agent_executor.invoke({"input": question})
#         result = response.get('output', 'No output found')
#         try:
#             json_result = json.loads(result)
#             print("✅ JSON Response:",json_result)
            
#             return json_result
#         except json.JSONDecodeError:
#             print("✅ Response:")
#             print(result)
#             return result
#     except Exception as e:
#         # error_msg = f"❌ Error: {str(e)}"
#         # print(error_msg)
#         # print("\n" + "="*60)
#         # return error_msg
#         error_result = {"status": "error", "message": str(e)}
#         print(f"❌ Error: {json.dumps(error_result, indent=2)}")
#         return error_result

# # Use it like this - ONE QUESTION AT A TIME
# if __name__ == "__main__":
#     # Ask your question
#     ask_question("Find me a french door stainless steel refrigerator under $2000")
    



from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from sqlalchemy import text
import json

# -------------------------
# SQL TOOL
# -------------------------
@tool()
def run_sql(query: str) -> str:
    """
    Run a SQL query on the DefaultProducts table and return results.
    Only SELECT queries are allowed.
    """
    query = query.strip().strip("```").replace("sql", "").strip()

    if not query.lower().startswith("select"):
        return "❌ Only SELECT queries are allowed."

    db = SessionLocal()
    try:
        result = db.execute(text(query)).fetchall()
        products = []

        for row in result[:5]:
            row_dict = dict(row._mapping) if hasattr(row, '_mapping') else dict(row)
            product = {
                "id": row_dict.get("id"),
                "title": row_dict.get("productTitle"),
                "description": row_dict.get("productDescription", "No description available"),
                "price": float(row_dict.get("productRegularPrice") or 0),
                "images": row_dict.get("productImages", ""),
                "color": row_dict.get("color_code_description", "")
            }
            products.append(product)

        db.close()

        if not products:
            return json.dumps({"status": "success", "count": 0, "products": []}, indent=2)

        return json.dumps({
            "status": "success",
            "count": len(products),
            "products": products
        }, indent=2)

    except Exception as e:
        db.close()
        if "does not exist" in str(e).lower():
            return f"❌ Table not found. Error: {e}\nPlease check if table name should be quoted or has different case."
        return f"❌ Error running query: {e}"


# -------------------------
# LLM SETUP
# -------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0
)

# Simplified prompt
prompt = PromptTemplate.from_template("""
You are a SQL assistant that generates EXACTLY ONE query and returns JSON results.

Database: "DefaultProducts" table
Fields: id, "productTitle", "productDescription", "productRegularPrice", "productImages", "color_code_description"

TOOLS: {tools}
TOOL NAMES: {tool_names}

CRITICAL RULES:
1. Generate EXACTLY ONE SQL query only
2. ALWAYS use quoted table name: "DefaultProducts"
3. ALWAYS include "productDescription" in SELECT for full product info
4. Always exclude products with "productRegularPrice" = 0
5. After getting results, immediately provide Final Answer as JSON

RESPONSE FORMAT:
Thought: I need to search for products with descriptions
Action: run_sql  
Action Input: SELECT id, "productTitle", "productDescription", "productRegularPrice", "productImages", "color_code_description" 
             FROM "DefaultProducts" WHERE ... AND "productRegularPrice" != 0

After getting observation, immediately respond with:
Final Answer: [JSON results from the tool]

{agent_scratchpad}

User Question: {input}
""")

# Agent
tools = [run_sql]
agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False,
    handle_parsing_errors=True,
    max_iterations=3,
    early_stopping_method="force",
    return_intermediate_steps=False
)


# -------------------------
# ASK QUESTION FUNCTION
# -------------------------
def ask_question(question: str):
    print(f"🔍 Question: {question}")
    try:
        response = agent_executor.invoke({"input": question})
        result = response.get("output", "No output found")

        # Handle "Final Answer:" prefix
        if isinstance(result, str) and result.startswith("Final Answer:"):
            result = result.replace("Final Answer:", "").strip()

        try:
            json_result = json.loads(result)
            print("✅ JSON Response:", json_result)
            return json_result
        except json.JSONDecodeError:
            print("✅ Raw Response:", result)
            return result

    except Exception as e:
        error_result = {"status": "error", "message": str(e)}
        print(f"❌ Error: {json.dumps(error_result, indent=2)}")
        return error_result


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    ask_question("Find me a french door stainless steel refrigerator under $2000")
