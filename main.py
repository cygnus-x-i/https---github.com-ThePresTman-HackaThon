import os
from flask import Flask, request, jsonify
from signalwire.rest import Client as SignalWireClient
import requests 
from dotenv import load_dotenv
import time
from datetime import datetime
import csv

app = Flask(__name__)
load_dotenv(dotenv_path="C:\\Users\\TmanT\\OneDrive\\Desktop\\SMS Chatbot\\.venv\\api.env")
temp_conversations = {}
CONVERSATION_TIMEOUT = 60

# not all of these are API keys, but they are all hidden by the same class for simplicity.
 
SIGNALWIRE_PROJECT_ID = str(os.getenv("SIGNALWIRE_PROJECT_ID"))
SIGNALWIRE_API_TOKEN = str(os.getenv("SIGNALWIRE_API_TOKEN"))
SIGNALWIRE_SPACE_URL = str(os.getenv("SIGNALWIRE_SPACE_URL"))
SIGNALWIRE_PHONE_NUMBER = str(os.getenv("SIGNALWIRE_PHONE_NUMBER"))
OPENAI_API_KEY = str(os.getenv("OPENAI_API_KEY"))
OLLAMA_API_URL = str(os.getenv("OLLAMA_API_URL"))

# SignalWire client
client = SignalWireClient(SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN, signalwire_space_url=SIGNALWIRE_SPACE_URL)

@app.route('/sms', methods=['POST'])
def sms_reply():
    # Get incoming message and the sender's number
    incoming_msg = request.form.get('Body')
    from_number = request.form.get('From')

    # Check if the user requested to save or delete
    if incoming_msg.lower() == 'delete':
        try:
            os.remove(f"C:\\Users\\TmanT\\OneDrive\\Desktop\\SMS Chatbot\\{from_number}.csv")
            remove = "Your data has been deleted."
        except:
            remove = "Removal failed, please try again."
        # del temp_conversations[from_number]
        message = client.messages.create(
        from_=SIGNALWIRE_PHONE_NUMBER,
        to=from_number,
        body=remove
    )
        return jsonify({"status": "Your data has been deleted."}), 200

    elif incoming_msg.lower() == 'save':
        if from_number in temp_conversations:
            conversation_data = temp_conversations[from_number]
            log_to_csv(from_number, conversation_data['incoming_msg'], conversation_data['reply_text'])
            del temp_conversations[from_number]
        return jsonify({"status": "Your data has been saved."}), 200
    
    # Send the incoming message to Mistral 7B for a response
    reply_text = get_mistral_response(gen_prompt(incoming_msg))
    
    # Send Mistral 7B's response back as an SMS via SignalWire
    message = client.messages.create(
        from_=SIGNALWIRE_PHONE_NUMBER,
        to=from_number,
        body=reply_text
    )
    
    log(from_number, incoming_msg, reply_text)
    ai_memory(incoming_msg, reply_text)
    log_to_csv(from_number, incoming_msg, reply_text)
    return jsonify({"status": "Message Sent"}), 200

def get_mistral_response(prompt):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        data = {    
            "model": "gpt-3.5-turbo",  # Use GPT-3.5-turbo model
            "messages": [{"role": "user", "content": prompt}],  # Format for messages
        }
        response = requests.post(OLLAMA_API_URL, headers=headers, json=data)
        
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
    if message == "quit":
        with open("C:\\Users\\TmanT\\OneDrive\\Desktop\\SMS Chatbot\\.venv\\log.txt", "w") as file:
            file.write("")
            file.flush()
    with open("C:\\Users\\TmanT\\OneDrive\\Desktop\\SMS Chatbot\\.venv\\log.txt", "a") as file:
        file.write(f"{datetime.now()}: {phone_number}\nMessage in: \n{message}\nMessage out:\n{message_out}\n\n")
        file.flush()

def ai_memory(user, response):
    with open("C:\\Users\\TmanT\\OneDrive\\Desktop\\SMS Chatbot\\.venv\\memory.txt", 'a') as file:
        file.write(f"User: {user}\nYour Response: {response}\n\n")
        file.flush()

def gen_prompt(user):
    # Generates a complete prompt based on previous questions during this session
    with open("C:\\Users\\TmanT\\OneDrive\\Desktop\\SMS Chatbot\\.venv\\memory.txt", 'r') as file:
        return file.read() + f"\nUser:{user}"
    
def log_to_csv(phone_number, incoming_message, bot_response):
    # Define the CSV file name based on the phone number
    file_name = f"{phone_number}.csv"

    # Check if the file exists. If it doesn't, create it and write the header
    file_exists = os.path.isfile(file_name)

    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Write header only if the file didn't exist
            writer.writerow(['Phone Number', 'Incoming Text', 'Received Time', 'Bot Response', 'Response Time'])

        # Get current timestamps
        received_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        response_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Write the received data
        writer.writerow([phone_number, incoming_message, received_time, bot_response, response_time])
    
    print(f"Data logged to {file_name}")
        # file.write(f"{datetime.now()}: {phone_number}\nMessage in: \n{message}\nMessage out:\n{message_out}\n\n")
        # file.flush()
    
if __name__ == '__main__':
    app.run(debug=True)
