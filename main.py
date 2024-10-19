import os
from flask import Flask, request, jsonify
from signalwire.rest import Client as SignalWireClient
import requests 
from dotenv import load_dotenv
import time
from datetime import datetime
from api import api

app = Flask(__name__)
load_dotenv()

# not all of these are API keys, but they are all hidden by the same class for simplicity.

SIGNALWIRE_PROJECT_ID = api()
SIGNALWIRE_PROJECT_ID.pick_key(1)
SIGNALWIRE_API_TOKEN = api()
SIGNALWIRE_API_TOKEN.pick_key(2)
SIGNALWIRE_SPACE_URL = api()
SIGNALWIRE_SPACE_URL.pick_key(3)
SIGNALWIRE_PHONE_NUMBER = api()
SIGNALWIRE_PHONE_NUMBER.pick_key(4)
OPENAI_API_KEY = api()
OPENAI_API_KEY.pick_key(5)
OLLAMA_API_URL = api()
OLLAMA_API_URL.pick_key(6)



# SignalWire client
client = SignalWireClient(SIGNALWIRE_PROJECT_ID._key, SIGNALWIRE_API_TOKEN._key, signalwire_space_url=SIGNALWIRE_SPACE_URL._key)

@app.route('/sms', methods=['POST'])
def sms_reply():
    # Get incoming message and the sender's number
    incoming_msg = request.form.get('Body')
    from_number = request.form.get('From')
    
    # Send the incoming message to Mistral 7B for a response
    reply_text = get_mistral_response(incoming_msg)
    
    # Send Mistral 7B's response back as an SMS via SignalWire
    message = client.messages.create(
        from_=SIGNALWIRE_PHONE_NUMBER._key,
        to=from_number,
        body=reply_text
    )
    
    log(from_number, incoming_msg, reply_text)
    return jsonify({"status": "Message Sent"}), 200

def get_mistral_response(prompt):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY._key}"
        }
        data = {    
            "model": "gpt-3.5-turbo",  # Use GPT-3.5-turbo model
            "messages": [{"role": "user", "content": prompt}],  # Format for messages
        }
        response = requests.post(OLLAMA_API_URL._key, headers=headers, json=data)
        
        # Check for errors
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code}. Response: {response.text}"

        if response.headers.get('Content-Type') == 'application/json':
            response_json = response.json()
            return response_json.get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I couldn't generate a response.") #no errors, returns chatbot output
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
