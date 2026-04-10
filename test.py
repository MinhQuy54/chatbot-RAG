from google import genai
import os
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv('API_KEY'))
for i in client.models.list():
    print (i)