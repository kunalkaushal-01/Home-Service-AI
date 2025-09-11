import os
from dotenv import load_dotenv

load_dotenv()

# Load from environment variables
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Task settings
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True


beat_schedule = {
    'process-json-every-30sec': {
        'task': 'process_json_data', 
        'schedule': 30.0,
    },
}


# Task routing
# task_routes = {
#     'auto_process_json': {'queue': 'json_processing'},
#     'process_json_data': {'queue': 'json_processing'},
#     'manual_process_json': {'queue': 'json_processing'},
#     'get_products_count': {'queue': 'monitoring'},
#     'health_check': {'queue': 'monitoring'},
# }