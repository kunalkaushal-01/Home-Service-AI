# utils/celery_task.py
from celery import Celery
import json
import os
import sys
import hashlib
from data.product import product_call_api  
from dotenv import load_dotenv
from bs4 import BeautifulSoup


load_dotenv()


# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import SessionLocal, Base, engine
from models.user import Product  # your existing model
# from utils.faiss_utils import add_texts, search, _index_dir  # add_texts is used below
from utils.faiss_utils import add_texts, search
from utils.chunker import product_to_chunks

# Initialize Celery app (assuming celery_config exists and is configured)
celery_app = Celery('json_processor')
celery_app.config_from_object('celery_config')

LAST_HASH_FILE = 'data/.last_hash'

def get_file_hash(file_path):
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return None

def has_file_changed(json_path):
    if not os.path.exists(json_path):
        return False

    current_hash = get_file_hash(json_path)
    if not current_hash:
        return False

    last_hash = None
    if os.path.exists(LAST_HASH_FILE):
        try:
            with open(LAST_HASH_FILE, 'r') as f:
                last_hash = f.read().strip()
        except Exception:
            pass

    if current_hash != last_hash:
        try:
            os.makedirs(os.path.dirname(LAST_HASH_FILE), exist_ok=True)
            with open(LAST_HASH_FILE, 'w') as f:
                f.write(current_hash)
        except Exception:
            pass
        print(f"🔄 File change detected! Hash changed from {last_hash} to {current_hash}")
        return True

    print("ℹ️ No file changes detected - file hash matches stored hash")
    return False


def to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes")
    return None

@celery_app.task(name='process_json_data')
def process_json_data():
    """Process JSON and save to DB + FAISS vector store"""
    try:
        print("🔄 Starting JSON processing task...")
        Base.metadata.create_all(bind=engine)

        get_resp = product_call_api()
        data = get_resp.get("data", {})
        records = data.get("records", [])

        db = SessionLocal()
        processed_count = 0
        updated_count = 0
        faiss_added = 0

        for record in records:
            try:
                # Extract fields from API
                brand = record.get("brand")
                categories = record.get("categories", [])
                domains = record.get("domains", [])
                features_dict = {f['key']: f['value'] for f in record.get("features", [])}
                print("feature_dict",features_dict)
                title = features_dict.get("Title", [""])[0]
                print(title,"title+++")
                description_html = features_dict.get("body html", [""])[0]
                description_text = BeautifulSoup(description_html, "html.parser").get_text(separator="\n").strip()
                print("description",description_text)
                tags = features_dict.get("tags", [])
                images = record.get("imageURLs", [])
                keys = record.get("keys", [])

                # Price info
                phone_price = record.get("prices", [])
                filtered_prices = [
                    {
                        "amountMin": price.get("amountMin"),
                        "amountMax": price.get("amountMax"),
                        "availability": to_bool(price.get("availability")),
                        "currency": price.get("currency")
                    } for price in phone_price
                ]

                most_recent_price_amount = record.get("mostRecentPriceAmount")
                most_recent_price_availability = to_bool(record.get("mostRecentPriceAvailability"))
                most_recent_price_currency = record.get("mostRecentPriceCurrency")
                most_recent_price_domain = record.get("mostRecentPriceDomain")
                most_recent_price_first_seen = record.get("mostRecentPriceFirstDateSeen")
                phone_name = record.get('name')

                # Check if product exists
                product_obj = db.query(Product).filter(Product.id == record['id']).first()
                if product_obj:
                    # Update existing product
                    product_obj.phone_name = phone_name
                    product_obj.brand = brand
                    product_obj.category = categories
                    product_obj.domains = domains
                    product_obj.title = title
                    product_obj.description = description_text
                    product_obj.tags = tags
                    product_obj.images = images
                    product_obj.keys = keys
                    product_obj.filtered_prices = filtered_prices
                    product_obj.most_recent_price_amount = most_recent_price_amount
                    product_obj.most_recent_price_availability = most_recent_price_availability
                    product_obj.most_recent_price_currency = most_recent_price_currency
                    product_obj.most_recent_price_domain = most_recent_price_domain
                    product_obj.most_recent_price_first_seen = most_recent_price_first_seen
                    product_obj.is_processed = False
                    updated_count += 1
                else:
                    # Create new product
                    product_obj = Product(
                        id=record['id'],
                        phone_name=phone_name,
                        brand=brand,
                        category=categories,
                        domains=domains,
                        title=title,
                        description=description_text,
                        tags=tags,
                        images=images,
                        keys=keys,
                        filtered_prices=filtered_prices,
                        most_recent_price_amount=most_recent_price_amount,
                        most_recent_price_availability=most_recent_price_availability,
                        most_recent_price_currency=most_recent_price_currency,
                        most_recent_price_domain=most_recent_price_domain,
                        most_recent_price_first_seen=most_recent_price_first_seen,
                        is_processed=False
                    )
                    db.add(product_obj)
                    db.flush()
                    processed_count += 1

                # Add to FAISS if not processed
                if not product_obj.is_processed:
                    chunks = product_to_chunks({
                        "id": record['id'],
                        "name": phone_name,
                        "category": categories,
                        "brand": brand,
                        "price": most_recent_price_amount,
                        "availability": most_recent_price_availability,
                        "features": str(features_dict),
                        "description": description_text
                    })
                    metas = [{
                        "id": str(record.get("id")),
                        "name": phone_name,
                        "brand": brand,
                        "price": most_recent_price_amount,
                        "category": categories
                    }]
                    try:
                        added = add_texts("products", chunks, metas)
                        faiss_added += added
                        product_obj.is_processed = True
                    except Exception as e:
                        print(f"❌ FAISS add failed for id {record.get('id')}: {e}")

            except Exception as e:
                print(f"❌ Error processing record {record.get('id', 'unknown')}: {e}")
                continue

        db.commit()
        total_processed = processed_count + updated_count
        result_msg = f"Processed: {total_processed} (New: {processed_count}, Updated: {updated_count}), FAISS added vectors: {faiss_added}"
        print(f"✅ {result_msg}")

        return {
            "status": "success",
            "new_products": processed_count,
            "updated_products": updated_count,
            "faiss_added": faiss_added,
            "message": result_msg
        }

    except Exception as e:
        try:
            db.rollback()
        except:
            pass
        error_msg = f"JSON processing failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}
    finally:
        try:
            db.close()
        except:
            pass


@celery_app.task(name='auto_process_json')
def auto_process_json():
    try:
        print("🤖 AUTO-PROCESSING: Checking for file changes...")
        json_path = os.path.join('data', 'products.json')
        if has_file_changed(json_path):
            print("📄 FILE CHANGED! Processing automatically...")
            result = process_json_data()
            return result
        else:
            return {"status": "no_changes", "message": "No file changes detected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task(name='manual_process_json')
def manual_process_json():
    return process_json_data()

@celery_app.task(name='get_products_count')
def get_products_count():
    try:
        db = SessionLocal()
        try:
            count = db.query(Product).count()
            unprocessed = db.query(Product).filter(Product.is_processed == False).count()
            return {"status": "success", "total_products": count, "unprocessed_products": unprocessed}
        finally:
            db.close()
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task(name='health_check')
def health_check():
    try:
        db = SessionLocal()
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"error: {e}"
        finally:
            db.close()
        json_path = os.path.join('data', 'products.json')
        json_exists = os.path.exists(json_path)
        json_status = "exists" if json_exists else "missing"
        return {"status": "success", "database": db_status, "json_file": json_status, "json_path": json_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}
