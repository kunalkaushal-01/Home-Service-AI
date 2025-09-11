from typing import Dict, Any, List
from utils.faiss_utils import search

def _format_hits(hits: List[Dict]) -> List[Dict[str, Any]]:
    out = []
    for h in hits:
        out.append({
            "text": h.get("text"),
            "metadata": h.get("metadata"),
            "score": h.get("score")
        })
    return out

def _synthesize_answer(hits: List[Dict]) -> str:
    if not hits:
        return "I couldn't find relevant information."
    lines = []
    for h in hits[:5]:
        md = h.get("metadata", {})
        name = md.get("name") or ""
        brand = md.get("brand") or ""
        price = md.get("price") or ""
        snippet = h.get("text", "").splitlines()[0]
        if name:
            lines.append(f"{name} ({brand}) — {price}")
        else:
            lines.append(snippet[:200])
    return "Here are top results:\n" + "\n".join(lines)

class BaseAgent:
    category = "base"

    def answer(self, query: str, top_k: int = 3) -> Dict:
        hits = search(self.category, query, k=top_k)
        return {
            "category": self.category,
            "hits": _format_hits(hits),
            "answer": _synthesize_answer(hits)
        }