from typing import Dict, List
import json

def product_to_chunks(p: Dict) -> List[str]:
    # Compose a compact, searchable text blob for the vector DB
    parts = [
        f"ID: {p.get('id')}",
        f"Name: {p.get('name')}",
        f"Phone Name: {p.get('phone_name', '')}",
        f"Category: {p.get('category')}",
        f"Brand: {p.get('brand')}",
        f"Domains: {', '.join(p.get('domains', []))}",
        f"Title: {p.get('title', '')}",
        f"Description: {p.get('description', '')}",
        f"Tags: {', '.join(p.get('tags', []))}",
        f"Images: {', '.join(p.get('images', []))}",
        f"Keys: {', '.join(p.get('keys', []))}",
        f"Filtered Prices: {json.dumps(p.get('filtered_prices', []))}",
        f"Most Recent Price Amount: {p.get('most_recent_price_amount')}",
        f"Most Recent Price Availability: {p.get('most_recent_price_availability')}",
        f"Most Recent Price Currency: {p.get('most_recent_price_currency')}",
        f"Most Recent Price Domain: {p.get('most_recent_price_domain')}",
        f"Most Recent Price First Seen: {p.get('most_recent_price_first_seen')}"
    ]
    text = "\n".join([x for x in parts if x])
    # For now one chunk per product (you can split long descriptions into many chunks)
    return [text]
