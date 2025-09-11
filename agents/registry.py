# agents/registry.py
from agents.product_agent import ProductAgent

AGENTS = {
    "products": ProductAgent(),
    # "homes": HomeAgent(),
    # "autos": AutoAgent(),
    # "services": ServiceAgent(),
    # "events": EventAgent(),
}

DEFAULT = "products"

def get_agent(category: str):
    return AGENTS.get(category, AGENTS[DEFAULT])
