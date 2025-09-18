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
    product_name ='Iphone'
    # product_name = ['iphone','washingmachine','laptop','lcd','tv']
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



# def product_api():
#     """
#     Function to call an API using Bearer Token and return JSON response.
#     """
#     token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvM2hraWsyNzh4Nzc4aXhuM2VvYWlhajAxNWtzYXYyNSIsImlzcyI6ImRhdGFmaW5pdGkuY28ifQ.cZT95YwKxZUptEmXqpz1X7y5WU4RNGf_JGHTxLsxbvBFcLQ0DvPlJnj0T7Ujr8mfi7sknX92oKCeSylvdaBT0radCNFiP7jkGuhBrv_b27ksOMbpkz8gao9lwAh4e3X6m93kpfvkABVrO0p6fmB8bjX4HDZYK3Mwp1--n5h_GvH0BcMc4CO1449YcfO9zyTBy0OU6LmDwnq6KS_Xi_UJqit4R3w820YABfNeU8_7vNvjhxCrm6gRTg60Lc8I9Y5-IQ4nobFqYbsKR1-jLrosSxq-ItLBvwG3Z45u4HocOF4D5gL_Jihi20yOG0tCELXc1HbAFdPJmF2hzEQAnIQrsydMmZFCPKyxCTyukFsgRZ67PhoNfH3fcYFazO4ENDBliqKfQS6hVkAOziPKCbpfXBRB_JAkRMLLGgF5Qg5Ixe_CEGaNAeB51AzSOi31IrpNWQsDdoaJB0udEhO4FkTk9njYYIu4iS1FLRhdh2eKxxF0Gq4dcWQrYpwSs3--SoRkQsTL9lDpOIggYF593yMBQjLRPNkPiVqMt2HPAiCWgAo8zGaQ0wfLgD0m_wRJMfAS8Tmp9pR-I28HPsUUt2q-OQauYKkH3gYMjyWsIO4HgzmI25jh4x_Ynq0gI-SKJKk0xZPVpulcIpb7nOWfzy_maWUUkKstTMr1B02WsoFQBmY"

#     url = "https://api.datafiniti.co/v4/products/search"
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "accept": "application/json",
#         "content-type": "application/json"
#     }
#     product_name ='Iphone'
#     print(product_name)
#     payload = {
#         "query": f"brand:{product_name}",
#         "format": "json",
#         "num_records": 10
#     }

#     try:
#         print("1")
#         response = requests.post(url, headers=headers, json=payload)
#         response.raise_for_status()
#         data = response.json()
#         print(len(data),'data')
#         return {
#             "status": "success",
#             "data": data,
#         }
#     except requests.exceptions.HTTPError as http_err:
#         return {
#             "status": "error",
#             "message": "HTTP error occurred",
#             "details": str(http_err)
#         }
#     except requests.exceptions.ConnectionError as conn_err:
#         return {
#             "status": "error",
#             "message": "Connection error occurred",
#             "details": str(conn_err)
#         }
#     except requests.exceptions.Timeout as timeout_err:
#         return {
#             "status": "error",
#             "message": "Request timed out",
#             "details": str(timeout_err)
#         }
#     except requests.exceptions.RequestException as req_err:
#         return {
#             "status": "error",
#             "message": "An error occurred",
#             "details": str(req_err)
#         }

# print(product_api(),'?????')


#old code working fine
# def product_call_api():
#     """
#     Function to call an API using Bearer Token and return JSON response.
#     """
#     token = os.getenv("API_TOKEN")

#     url = os.getenv("API_URL")
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "accept": "application/json",
#         "content-type": "application/json"
#     }
#     product_name ='Iphone'
#     print(product_name)
#     payload = {"query": f"brand:{product_name}",}

#     try:
#         response = requests.post(url, headers=headers, json=payload)
#         response.raise_for_status()
#         data = response.json()
#         print(data)
#         return {
#             "status": "success",
#             "data": data,
#         }
#     except requests.exceptions.HTTPError as http_err:
#         return {
#             "status": "error",
#             "message": "HTTP error occurred",
#             "details": str(http_err)
#         }
#     except requests.exceptions.ConnectionError as conn_err:
#         return {
#             "status": "error",
#             "message": "Connection error occurred",
#             "details": str(conn_err)
#         }
#     except requests.exceptions.Timeout as timeout_err:
#         return {
#             "status": "error",
#             "message": "Request timed out",
#             "details": str(timeout_err)
#         }
#     except requests.exceptions.RequestException as req_err:
#         return {
#             "status": "error",
#             "message": "An error occurred",
#             "details": str(req_err)
#         }

# def product_call_api(product_name, color=None, category=None):
#     """
#     Function to call an API using Bearer Token with multiple query parameters.
#     """
#     token = os.getenv("API_TOKEN")
#     url = os.getenv("API_URL")

#     headers = {
#         "Authorization": f"Bearer {token}",
#         "accept": "application/json",
#         "content-type": "application/json"
#     }

#     # Start with the mandatory product name query
#     queries = [f"brand:{product_name}"]

#     # Add optional parameters to the query list if they exist
#     if color:
#         queries.append(f"tags:{color}")  # Assuming 'tags' field is used for color
#     if category:
#         queries.append(f"categories:{category}")

#     # Join all queries with " AND " to form the final query string
#     payload_query = " AND ".join(queries)
#     payload = {"query": payload_query}

#     print(f"Calling API with payload: {payload}")

#     try:
#         response = requests.post(url, headers=headers, json=payload)
#         response.raise_for_status()
#         data = response.json()
#         print(data)
#         return {
#             "status": "success",
#             "data": data,
#         }
#     except requests.exceptions.HTTPError as http_err:
#         return {
#             "status": "error",
#             "message": "HTTP error occurred",
#             "details": str(http_err)
#         }
#     except requests.exceptions.RequestException as req_err:
#         return {
#             "status": "error",
#             "message": "An error occurred",
#             "details": str(req_err)
#         }
# print('check latest api call',product_call_api(product_name='iPhone XS | X'))


# # def product_call_api():
# #     token = os.getenv("API_TOKEN")
# #     url = "https://api.client.com/products"  # Replace with actual API URL
# #     headers = {
# #         "Authorization": f"Bearer {token}",
# #         "accept": "application/json",
# #         "content-type": "application/json"
# #     }

# #     # Example query parameters
# #     params = {
# #         "brand": "iPhone",
# #         "color": "black",
# #         "max_price": 10000,
# #         "title": "Pro",
# #         "page": 1,
# #         "limit": 1
# #     }

# #     try:
# #         response = requests.get(url, headers=headers, params=params)
# #         response.raise_for_status()
# #         data = response.json()
# #         return {"status": "success", "data": data}
# #     except requests.exceptions.RequestException as e:
# #         return {"status": "error", "message": "Request failed", "details": str(e)}

# # print(product_call_api())


# import google.generativeai as genai
# import json

# genai.configure(api_key="AIzaSyD9-JNP-rXqU0KLkRO5YiLUBdAX7CmeNbM")
# models = genai.list_models()
# print(models)


# model = genai.GenerativeModel("gemini-2.0-flash-exp")

# # get_api_response =product_call_api()
# # print('get api response',get_api_response)

# prompt = """
# Generate JSON only. 
# I want search filters for iPhone under 10000 INR and color black.
# Do not add explanations, markdown, or text. Only return valid JSON.
# """

# response = model.generate_content(prompt)

# # Clean response text (remove ```json ``` wrappers if present)
# raw_text = response.text.strip()
# if raw_text.startswith("```"):
#     raw_text = raw_text.split("```")[1]  # remove code fences
#     raw_text = raw_text.replace("json", "", 1).strip()

# # Parse JSON safely
# try:
#     data = json.loads(raw_text)
#     filters_from_prompt = data.get("filters", {})
#     print("✅ Parsed JSON from prompt:", filters_from_prompt)
# except json.JSONDecodeError:
#     print("❌ Failed to parse JSON from prompt. Using default empty filters.")
#     filters_from_prompt = {}
# # Get API response
# get_api_response = product_call_api()  # Your existing API call
# print("✅ API Response:", get_api_response)

# records = get_api_response.get('data', {}).get('records', [])

# # Build Gemini-compatible filters dynamically
# gemini_filters = {
#     "filters": {
#         "price": {"max": None, "currency": "INR"},
#         "color": [],
#         "brand": [],
#         "model": []
#     }
# }

# for record in records:
#     # Price (take minimum or maximum depending on your logic)
#     price = record.get("mostRecentPriceAmount")
#     if price:
#         # Example: set max price from API response
#         if gemini_filters["filters"]["price"]["max"] is None:
#             gemini_filters["filters"]["price"]["max"] = price
#         else:
#             gemini_filters["filters"]["price"]["max"] = min(price, gemini_filters["filters"]["price"]["max"])
    
#     # Color
#     if record.get("color"):
#         gemini_filters["filters"]["color"].append(record["color"])
    
#     # Brand
#     if record.get("brand"):
#         gemini_filters["filters"]["brand"].append(record["brand"])
    
#     # Model (assuming model is part of record or categories)
#     if record.get("model"):
#         gemini_filters["filters"]["model"].append(record["model"])
#     elif record.get("categories"):
#         gemini_filters["filters"]["model"].append(record["categories"][0])  # fallback example

# # Remove duplicates
# for key in ["color", "brand", "model"]:
#     gemini_filters["filters"][key] = list(set(gemini_filters["filters"][key]))

# print("✅ Gemini Filters Ready:", json.dumps(gemini_filters, indent=4))

# # Now you can pass gemini_filters to Gemini API if needed
# gemini_response = model.generate_content(
#     json.dumps(gemini_filters)  # send filters as JSON input
# )

# print("✅ Gemini API Response:", gemini_response.text)
    
# # q = "washing machine"
# # q = "iPhone 11"
# # result = product_call_api(q)

# # print(json.dumps(result, indent=4)) 