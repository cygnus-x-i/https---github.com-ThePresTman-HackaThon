import os
from flask import Flask, request, jsonify
from signalwire.rest import Client as SignalWireClient
import requests 
from dotenv import load_dotenv
import time
from datetime import datetime

app = Flask(__name__)
load_dotenv()

SIGNALWIRE_PROJECT_ID = 'c999ec5e-fab9-4360-8326-3825ffcb3fb9'
SIGNALWIRE_API_TOKEN = 'PTb5ae26a882762022a798154a1efa7f5e5a9ddce08994b6c3'
SIGNALWIRE_SPACE_URL = 'test1928u.signalwire.com'
SIGNALWIRE_PHONE_NUMBER = '+12068288235'
OPENAI_API_KEY = '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'
OLLAMA_API_URL = 'https://api.openai.com/v1/chat/completions'

# SignalWire client
client = SignalWireClient(SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN, signalwire_space_url=SIGNALWIRE_SPACE_URL)

@app.route('/sms', methods=['POST'])
def sms_reply():
    # Get incoming message and the sender's number
    incoming_msg = request.form.get('Body')
    from_number = request.form.get('From')
    
    # Send the incoming message to Mistral 7B for a response
    reply_text = get_mistral_response(incoming_msg)
    
    # Send Mistral 7B's response back as an SMS via SignalWire
    message = client.messages.create(
        from_=SIGNALWIRE_PHONE_NUMBER,
        to=from_number,
        body=reply_text
    )
    
    log(from_number, incoming_msg, reply_text)
    return jsonify({"status": "Message Sent"}), 200

def get_mistral_response(prompt):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"  # Your OpenAI API key
        }
        data = {    
            "model": "gpt-3.5-turbo",  # Use GPT-4 model
            "messages": [{"role": "user", "content": prompt}],  # Format for messages
        }
        response = requests.post(OLLAMA_API_URL, headers=headers, json=data)
        
        # Check for errors
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code}. Response: {response.text}"

        if response.headers.get('Content-Type') == 'application/json':
            response_json = response.json()
            return response_json.get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I couldn't generate a response.")
        else:
            return f"Unexpected response format: {response.text}"
    
    except Exception as e:
        return f"Error: {str(e)}"

def log(phone_number, message, message_out):
    with open("C:\\Users\\TmanT\\OneDrive\\Desktop\\SMS Chatbot\\.venv\\log.txt", "a") as file:
        file.write(f"{datetime.now()}: {phone_number}\nMessage in: \n{message}\nMessage out:\n{message_out}\n\n")
        file.flush()

if __name__ == '__main__':
    app.run(debug=True)
