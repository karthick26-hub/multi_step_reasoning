
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

for model in client.models.list():
    name = model.name or ""
    if "gemini" in name.lower():
        print(name)
