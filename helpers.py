import requests, os
from dotenv import load_dotenv

load_dotenv()

def get_google_provider_cfg():
    return requests.get(os.getenv('GOOGLE_DISCOVERY_URL')).json()