import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from twilio.rest import Client
from dotenv import load_dotenv

# ── LOCAL TESTING ONLY ────────────────────────────────────────────────
if os.getenv("FLASK_ENV") != "production":
    load_dotenv()                      # pulls vars from .env when you run locally
# ──────────────────────────────────────────────────────────────────────

app = Flask(__name__)
# Enable CORS for all routes to make sure the API is accessible
CORS(app)

# Twilio credentials + numbers from env-vars
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token  = os.environ["TWILIO_AUTH_TOKEN"]
twilio_from = os.environ["TWILIO_FROM"]        # e.g. whatsapp:+14155238886
whatsapp_to = os.environ["WHATSAPP_TO"]        # your phone in sandbox
client = Client(account_sid, auth_token)

@app.route("/")
def index():                     # LOCAL browser test only
    return send_from_directory(".", "index.html")

@app.route("/send-whatsapp", methods=["POST"])
def send_whatsapp():
    data = request.json or {}
    
    # Log incoming request data for debugging
    print(f"Received request data: {data}")
    
    name = data.get("name", "")
    email = data.get("email", "")
    body = data.get("message", "").strip()

    if not body:
        return jsonify(success=False, message="Message is required"), 400

    try:
        # Include name and email in the message if provided
        message_text = body
        if name:
            message_text = f"From: {name}\n{message_text}"
        if email:
            message_text = f"{message_text}\nContact: {email}"
            
        msg = client.messages.create(
            from_=twilio_from,
            to=whatsapp_to,
            body=message_text
        )
        return jsonify(success=True, sid=msg.sid)
    except Exception as e:
        print(f"Error sending WhatsApp message: {str(e)}")
        return jsonify(success=False, message=str(e)), 500

# Add a health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(status="ok")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
