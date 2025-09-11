from celery import Celery
import json
import os
import sys
import hashlib

# Add project root to path (same as your env.py approach)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import SessionLocal, Base, engine 
from models.user import Product

# Initialize Celery app
celery_app = Celery('json_processor')
celery_app.config_from_object('celery_config')

# File monitoring constants
LAST_HASH_FILE = 'data/.last_hash'  # ← UNCOMMENT THIS - it's needed!

def get_file_hash(file_path):
    """Get MD5 hash of file for change detection"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return None

def has_file_changed(json_path):
    """Check if JSON file has changed since last processing"""
    if not os.path.exists(json_path):
        return False
    
    current_hash = get_file_hash(json_path)
    if not current_hash:
        return False
    
    # Read last hash
    last_hash = None
    if os.path.exists(LAST_HASH_FILE):
        try:
            with open(LAST_HASH_FILE, 'r') as f:
                last_hash = f.read().strip()
        except Exception:
            pass
    
    # If changed, save new hash
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

@celery_app.task(name='process_json_data')
def process_json_data():
    """Process JSON file data and save to database"""
    try:
        print("🔄 Starting JSON processing task...")
        
        # Ensure tables exist using your existing Base
        Base.metadata.create_all(bind=engine)
        
        # Load JSON data
        json_path = os.path.join('data', 'products.json')
        print(f"📂 Reading JSON file: {json_path}")
        
        if not os.path.exists(json_path):
            return {"status": "error", "message": f"JSON file not found: {json_path}"}
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Database operations using your existing SessionLocal
        db = SessionLocal()
        processed_count = 0
        updated_count = 0
        
        try:
            products_data = data.get('products', [])
            print(f"📊 Found {len(products_data)} products in JSON file")
            print("🔍 Checking each product for new/updated records...")
            
            for product_data in products_data:
                try:
                    # Check if product exists
                    existing = db.query(Product).filter(Product.id == product_data['id']).first()
                    
                    if existing:
                        # Update existing product
                        print(f"🔄 Updating existing product ID: {product_data['id']} - {product_data['name']}")
                        existing.name = product_data['name']
                        existing.category = product_data['category']
                        existing.price = product_data['price']
                        existing.description = product_data['description']
                        existing.features = product_data.get('features', '')
                        existing.availability = product_data.get('availability', 'In Stock')
                        existing.brand = product_data.get('brand', '')
                        existing.is_processed = False  # Mark for reprocessing
                        updated_count += 1
                    else:
                        # Create new product
                        print(f"🆕 Adding NEW product ID: {product_data['id']} - {product_data['name']}")
                        new_product = Product(
                            id=product_data['id'],
                            name=product_data['name'],
                            category=product_data['category'],
                            price=product_data['price'],
                            description=product_data['description'],
                            features=product_data.get('features', ''),
                            availability=product_data.get('availability', 'In Stock'),
                            brand=product_data.get('brand', ''),
                            is_processed=False
                        )
                        db.add(new_product)
                        processed_count += 1
                        
                except Exception as e:
                    print(f"❌ Error processing product {product_data.get('id', 'unknown')}: {str(e)}")
                    continue
            
            # Commit all changes
            db.commit()
            
            total_processed = processed_count + updated_count
            result_msg = f"Successfully processed {total_processed} products (New: {processed_count}, Updated: {updated_count})"
            
            print(f"💾 Database commit successful!")
            print(f"📈 SUMMARY: {processed_count} new products added, {updated_count} products updated")
            print(f"✅ {result_msg}")
            
            return {
                "status": "success",
                "new_products": processed_count,
                "updated_products": updated_count,
                "total_processed": total_processed,
                "message": result_msg
            }
            
        except Exception as e:
            db.rollback()
            error_msg = f"Database operation failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {"status": "error", "message": error_msg}
            
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"JSON processing failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}

@celery_app.task(name='auto_process_json')
def auto_process_json():
    """Automatic processing - only when file changes (SMART)"""
    try:
        print("🤖 AUTO-PROCESSING: Checking for file changes...")
        json_path = os.path.join('data', 'products.json')
        
        if has_file_changed(json_path):
            print("📄 FILE CHANGED! Processing automatically...")
            result = process_json_data()
            print("🤖 AUTO-PROCESSING: Completed successfully")
            return result
        else:
            print("🤖 AUTO-PROCESSING: No changes detected - skipping processing")
            return {"status": "no_changes", "message": "No file changes detected"}
            
    except Exception as e:
        error_msg = f"Auto processing failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}

@celery_app.task(name='manual_process_json')
def manual_process_json():
    """Manual trigger for JSON processing"""
    print("👤 MANUAL PROCESSING: Triggered by user")
    result = process_json_data()
    print("👤 MANUAL PROCESSING: Completed")
    return result

@celery_app.task(name='get_products_count')
def get_products_count():
    """Get total number of products in database"""
    try:
        db = SessionLocal()
        try:
            count = db.query(Product).count()
            unprocessed = db.query(Product).filter(Product.is_processed == False).count()
            print(f"📊 Database stats - Total: {count}, Unprocessed: {unprocessed}")
            return {
                "status": "success", 
                "total_products": count,
                "unprocessed_products": unprocessed
            }
        finally:
            db.close()
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task(name='health_check')
def health_check():
    """Health check task to verify system is working"""
    try:
        print("🏥 HEALTH CHECK: Starting system verification...")
        
        # Check database connection
        db = SessionLocal()
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
            print("✅ Database connection: OK")
        except Exception as e:
            db_status = f"error: {str(e)}"
            print(f"❌ Database connection: FAILED - {str(e)}")
        finally:
            db.close()
        
        # Check JSON file
        json_path = os.path.join('data', 'products.json')
        json_exists = os.path.exists(json_path)
        json_status = "exists" if json_exists else "missing"
        
        if json_exists:
            print(f"✅ JSON file: Found at {json_path}")
        else:
            print(f"❌ JSON file: Missing at {json_path}")
        
        print("🏥 HEALTH CHECK: Completed")
        
        return {
            "status": "success",
            "database": db_status,
            "json_file": json_status,
            "json_path": json_path
        }
    except Exception as e:
        print(f"❌ HEALTH CHECK FAILED: {str(e)}")
        return {"status": "error", "message": str(e)}
