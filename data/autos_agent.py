from langchain_community.agent_toolkits import create_sql_agent
from langchain.prompts import SystemMessagePromptTemplate
from langchain.memory import ConversationBufferMemory
from base import llm, db



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

memory_autos = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True
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