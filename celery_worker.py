import os 
from celery import Celery

from dotenv import load_dotenv


load_dotenv(".env")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery = Celery("tasks_app", 
             broker=CELERY_BROKER_URL, 
             backend=CELERY_RESULT_BACKEND,
             include=["tasks"] 
)
