import os
from dotenv import load_dotenv
load_dotenv()
from celery_app import app
print("Broker:", app.conf.broker_url)
