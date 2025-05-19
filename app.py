from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Allow ONLY your Framer domain in production
CORS(app, resources={r"/send-whatsapp": {"origins": "*"}})  # change "*" to your domain when live

# Twilio credentials from env-vars
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_from = os.getenv("TWILIO_FROM")          # whatsapp:+14155238886
whatsapp_to = os.getenv("WHATSAPP_TO")          # whatsapp:+91XXXXXXXXXX
client = Client(account_sid, auth_token)


@app.route("/send-whatsapp", methods=["POST"])
def send_whatsapp():
    data = request.json or {}
    message_body = data.get("message", "").strip()

    if not message_body:
        return jsonify(success=False, message="Message is required"), 400

    try:
        sms = client.messages.create(
            from_=twilio_from,
            to=whatsapp_to,
            body=message_body
        )
        return jsonify(success=True, sid=sms.sid)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
