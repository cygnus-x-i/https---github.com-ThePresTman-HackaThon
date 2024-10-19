import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="C:\\Users\\TmanT\\OneDrive\\Desktop\\SMS Chatbot\\.venv\\api.env")

print(str(os.getenv("SIGNALWIRE_API_TOKEN")))