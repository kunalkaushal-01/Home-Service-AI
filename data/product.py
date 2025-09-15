import requests
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()



# def extract_keywords_regex(data):
#     # Extract words that are likely to be keywords (nouns, verbs, etc.)
#     # This pattern matches words with 3+ characters
#     keywords = re.findall(r'\b[a-zA-Z]{3,}\b', data.lower())
    
#     # Remove common stop words
#     stop_words = {'want', 'purchase', 'need', 'get', 'buy', 'find', 'looking', 'for', 'the', 'and', 'are'}
#     keywords = [word for word in keywords if word not in stop_words]
    
#     return keywords

# data = "top models of washingmachin"
# keywords = extract_keywords_regex(data)
# print(keywords)  # Output: ['iphone']
# if "washingmachin" in keywords:
#     print(keywords[2])
# else:
#     print('no')

def product_call_api():
    """
    Function to call an API using Bearer Token and return JSON response.
    """
    token = os.getenv("API_TOKEN")

    url = os.getenv("API_URL")
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
        "content-type": "application/json"
    }
    # product_name ='Iphone'
    product_name = ['iphone','washingmachine','laptop','lcd','tv']
    results = {}
    for prod in product_name:
        print(prod)
        payload = {"query": f"brand:{prod}"}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            results[prod] = {"status": "success", "data": data}
            # return {
            #     "status": "success",
            #     "data": data,
            # }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status": "error",
                "message": "HTTP error occurred",
                "details": str(http_err)
            }
        except requests.exceptions.ConnectionError as conn_err:
            return {
                "status": "error",
                "message": "Connection error occurred",
                "details": str(conn_err)
            }
        except requests.exceptions.Timeout as timeout_err:
            return {
                "status": "error",
                "message": "Request timed out",
                "details": str(timeout_err)
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status": "error",
                "message": "An error occurred",
                "details": str(req_err)
            }
    return results
# q = "washing machine"
# q = "iPhone 11"
# result = product_call_api(q)

# print(json.dumps(result, indent=4)) 