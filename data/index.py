# os.environ["GOOGLE_API_KEY"] = "AIzaSyD9-JNP-rXqU0KLkRO5YiLUBdAX7CmeNbM"

import os
import requests
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from sqlalchemy import text
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import SessionLocal, Base, engine

db = SessionLocal()
print(db,'get db')
query = text('SELECT id, "productTitle", "productDescription" FROM "DefaultProducts" LIMIT 10')
result = db.execute(query).fetchall()
print(result,'resultresultresult')

# GEMINI_API_KEY="AIzaSyBofbP27IxpERC1p0ENtfu18U1fEN2MUcI"
GEMINI_API_KEY="AIzaSyD9-JNP-rXqU0KLkRO5YiLUBdAX7CmeNbM"
# --- Tool Definition ---
@tool
def homeshow_api_search(query: str) -> str:
    """
    Searches the homeshow.ai API for products. 
    Input should be a string describing the product, e.g., "leather chairs" or "American Leather sofas".
    The function returns a formatted list of product titles and their descriptions.
    """
    api_url = "https://homeshow.ai/api/databaseproducts"
    try:
        response = requests.get(api_url)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json().get("data", {}).get("records", [])
        # 1. Extract price constraint if it exists
        price_limit = None
        price_match = re.search(r'less than \$?(\d+)', query.lower())
        if price_match:
            price_limit = float(price_match.group(1))
            # Remove the price part from the query for product matching
            query = re.sub(r'less than \$?(\d+)', '', query, flags=re.IGNORECASE).strip()
            
        # 2. Split the query into keywords
        keywords = query.lower().split()
        # Simple search logic: filter records where the query is in the product title or description.
        matching_products = []
        for record in data:
            product_title = record.get("productTitle", "").lower()
            product_description = record.get("productDescription", "").lower()
            product_brand = record.get("productBrandName", "").lower()
            product_sale_price = float(record.get("productSalePrice", 0.0))

            # Check if all keywords are present in either the title, description, or brand
            title_match = all(word in product_title for word in keywords)
            desc_match = all(word in product_description for word in keywords)
            brand_match = all(word in product_brand for word in keywords)
            
            # 3. Apply the filters
            # Check for keyword match first
            if not (title_match or desc_match or brand_match):
                continue
                
            # Then, check for price constraint if one was specified
            if price_limit is not None and product_sale_price >= price_limit:
                continue

            # If it passes all filters, add it to the list
            matching_products.append({
                "title": record.get("productTitle"),
                "brand": record.get("productBrandName"),
                "description": record.get("productDescription"),
                "sale_price": record.get("productSalePrice")
            })
        print(matching_products,'matching_productsmatching_productsmatching_products')      

        if not matching_products:
            return f"Sorry, I couldn't find any products related to '{query}'."
        
        # Format the results into a readable string for the agent.
        results_string = "Found the following products:\n\n"
        for i, product in enumerate(matching_products[:5]): # Limiting to 5 for brevity
            results_string += f"Product {i+1}:\n"
            results_string += f"  Title: {product['title']}\n"
            results_string += f"  Brand: {product['brand']}\n"
            results_string += f"  Price: ${product['sale_price']}\n"
            results_string += f"  Description: {product['description'][:100]}...\n\n"
        
        return results_string
    
    except requests.exceptions.RequestException as e:
        return f"Error connecting to the homeshow.ai API: {e}"

# --- Agent Setup ---
# Set up your Gemini API key as an environment variable
# os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY"

try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",google_api_key=GEMINI_API_KEY,max_output_tokens=4000) 
except KeyError:
    print("Please set your GOOGLE_API_KEY environment variable.")

# List of tools the agent can use
tools = [homeshow_api_search]

# Correct prompt template including all required variables
# prompt = PromptTemplate.from_template("""
#     You are an expert product assistant. You have access to the following tools: {tools}

#     Follow this exact format for your responses:
#     Question: the input question you must answer
#     Thought: you should always think about what to do
#     Action: the action to take, should be one of [{tool_names}]
#     Action Input: the input to the action
#     ... (this Thought/Action/Action Input can repeat N times)
#     Thought: I now know the final answer
#     Final Answer: the final answer to the original input question

#     Begin!
#     User: {input}
#     {agent_scratchpad}
# """)


prompt = PromptTemplate.from_template("""
You are an expert product assistant. You must strictly follow the reasoning and response format below.
You can only use the tools provided: {tools}.
Do not invent tools, actions, or information outside of what is given.
 
Your response format must always be exactly:
 
Question: the user’s question
Thought: reason about what needs to be done
Action: the chosen tool (must be one of [{tool_names}])
Action Input: the input/query you send to the tool
... (Repeat Thought/Action/Action Input as needed)
Thought: I now know the final answer
Final Answer: the clear and concise final answer to the user’s question
 
⚠️ Important:
- Only return the above format, nothing else.
- If a tool is required, always call it.
- If the answer can be given directly, still follow the format.
- If no relevant products are found, then you need to take action based on query keywords and relevant product attributes.
- Always provide the Final Answer in a complete markdown sentence.
 
Begin!
User: {input}
{agent_scratchpad}
""")


# Create the agent executor
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# # --- Execution ---
if __name__ == "__main__":
    print("Welcome to the Homeshow.ai Product Assistant. Ask me about a product!")
    
    while True:
        user_query = input("Your query: ")
        if user_query.lower() in ["exit", "quit", "q"]:
            break
        
        response = agent_executor.invoke({"input": user_query})
        
        print("\n--- Agent Response ---")
        print(response['output'])
        print("---------------------\n")





# import os
# import requests
# import json
# import re
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.agents import create_react_agent, AgentExecutor
# from langchain.tools import tool
# from langchain_core.prompts import PromptTemplate

# # Set up your Gemini API key from environment variables
# # GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")
# GEMINI_API_KEY = "AIzaSyBofbP27IxpERC1p0ENtfu18U1fEN2MUcI"

# if not GEMINI_API_KEY:
#     print("Please set the GOOGLE_API_KEY environment variable.")
#     exit()

# try:
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash",
#         google_api_key=GEMINI_API_KEY,
#         max_output_tokens=2000
#     )
# except KeyError:
#     print("Please set your GOOGLE_API_KEY environment variable.")
#     exit()

# # --- Markdown Formatting Function ---
# def format_products_to_markdown(products: list) -> str:
#     """
#     Formats a list of product dictionaries into a Markdown string.
#     """
#     if not products:
#         return "I am sorry, I couldn't find any products that match your search criteria."
    
#     markdown_string = "### Found the following products:\n\n"
#     for i, product in enumerate(products):
#         markdown_string += f"**{product['title']}**\n"
#         markdown_string += f"| **Brand:** {product['brand']} | **Price:** ${product['sale_price']} |\n"
#         markdown_string += f"|---|---|\n"
#         markdown_string += f"| **Description:** {product['description'][:100]}... |\n"
#         markdown_string += "\n"
        
#     return markdown_string

# # --- Tool Definition ---
# @tool
# def homeshow_api_search(query: str) -> str:
#     """
#     Searches the homeshow.ai API for products. 
#     The function can handle queries with product names, brands, and price constraints (e.g., "less than $500").
#     It returns a formatted list of matching products in Markdown format.
#     """
#     api_url = "https://homeshow.ai/api/databaseproducts"
#     try:
#         response = requests.get(api_url)
#         response.raise_for_status() # Raise an exception for bad status codes
        
#         records = response.json().get("data", {}).get("records", [])
        
#         # 1. Extract price constraint if it exists
#         price_limit = None
#         price_match = re.search(r'less than \$?(\d+)', query.lower())
#         if price_match:
#             price_limit = float(price_match.group(1))
#             query = re.sub(r'less than \$?(\d+)', '', query, flags=re.IGNORECASE).strip()
            
#         # 2. Split the query into keywords
#         keywords = query.lower().split()
        
#         matching_products = []
#         for record in records:
#             product_title = record.get("productTitle", "").lower()
#             product_description = record.get("productDescription", "").lower()
#             product_brand = record.get("productBrandName", "").lower()
            
#             try:
#                 product_sale_price = float(record.get("productSalePrice", 0.0))
#             except (ValueError, TypeError):
#                 product_sale_price = 0.0

#             # Check if all keywords are present in the relevant fields
#             keyword_match = all(word in f"{product_title} {product_description} {product_brand}" for word in keywords)
            
#             if not keyword_match:
#                 continue
                
#             # Apply the price filter if one was specified
#             if price_limit is not None and product_sale_price >= price_limit:
#                 continue

#             matching_products.append({
#                 "title": record.get("productTitle"),
#                 "brand": record.get("productBrandName"),
#                 "description": record.get("productDescription"),
#                 "sale_price": record.get("productSalePrice")
#             })

#         return format_products_to_markdown(matching_products[:5])
    
#     except requests.exceptions.RequestException as e:
#         return f"An error occurred while connecting to the homeshow.ai API: {e}"

# # --- Agent Setup ---
# tools = [homeshow_api_search]

# prompt = PromptTemplate.from_template("""
#     You are an expert product assistant. You have access to the following tools: {tools}

#     Follow this exact format for your responses:
#     Question: the input question you must answer
#     Thought: you should always think about what to do
#     Action: the action to take, should be one of [{tool_names}]
#     Action Input: the input to the action
#     ... (this Thought/Action/Action Input can repeat N times)
#     Thought: I now know the final answer
#     Final Answer: the final answer to the original input question

#     Begin!
#     User: {input}
#     {agent_scratchpad}
# """)

# agent = create_react_agent(llm, tools, prompt)
# agent_executor = AgentExecutor(
#     agent=agent,
#     tools=tools,
#     verbose=True,
#     handle_parsing_errors=True
# )

x = [['x12','x23','x45','x67'],['x89','x90','x11','x12'],['x13','x14','x15','x16']]
z= []
# for i in x:
#     temp_raw = []
#     for j in i:
#         temp_call=''
#         for char in j:
#             if char.isnumeric():
#                 temp_call+=char
#         temp_raw.append(int(temp_call))
#     z.append(temp_raw)
# print(z,'zz')
                


