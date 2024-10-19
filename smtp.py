from flask import Flask, request, jsonify
import smtplib

app = Flask(__name__)

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_email_password'

# Function to send SMS via email
def send_sms_via_email(to_number, carrier, message):
    # Map carriers to email gateways
    carrier_gateways = {
        'att': 'txt.att.net',
        'verizon': 'vtext.com',
        'tmobile': 'tmomail.net',
        'mint': 'tmomail.net',
        # Add more carriers as needed
    }
    
    if carrier not in carrier_gateways:
        return False
    
    sms_gateway = carrier_gateways[carrier]
    to_email = f"{to_number}@{sms_gateway}"
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, message)
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

@app.route('/send-sms', methods=['POST'])
def send_sms():
    data = request.json
    to_number = data.get('to')
    carrier = data.get('carrier')
    message = data.get('message')

    if send_sms_via_email(to_number, carrier, message):
        return jsonify({"status": "Message sent"}), 200
    else:
        return jsonify({"error": "Failed to send message"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

