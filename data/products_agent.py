from langchain_community.agent_toolkits import create_sql_agent
from langchain.prompts import SystemMessagePromptTemplate
from langchain.memory import ConversationBufferMemory
from base import llm, db



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

memory_products = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True
)

agent_products = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True,
    extra_prompt_messages=[system_message_products],
    agent_type="openai-tools",
    memory=memory_products,
)