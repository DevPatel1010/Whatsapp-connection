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

# FIXED: Enable CORS with proper configuration
CORS(app, 
     origins=["https://kwezyhq.framer.website"], 
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Accept", "Authorization"])

# Twilio credentials + numbers from env-vars
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token  = os.environ["TWILIO_AUTH_TOKEN"]
twilio_from = os.environ["TWILIO_FROM"]        # e.g. whatsapp:+14155238886
whatsapp_to = os.environ["WHATSAPP_TO"]        # your phone in sandbox
client = Client(account_sid, auth_token)

@app.route("/")
def index():                     # LOCAL browser test only
    return send_from_directory(".", "index.html")

@app.route("/send-whatsapp", methods=["GET", "POST", "OPTIONS"])
def send_whatsapp():
    # FIXED: Handle preflight requests with proper headers
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "https://kwezyhq.framer.website")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Max-Age", "3600")
        return response, 200
    
    # For GET requests, return a simple status message
    if request.method == "GET":
        return jsonify(status="WhatsApp endpoint is active", message="Please use POST method to send messages")
    
    # Handle POST requests as before
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
        
        # FIXED: Add proper CORS headers to response
        response = jsonify(success=True, sid=msg.sid)
        response.headers.add("Access-Control-Allow-Origin", "https://kwezyhq.framer.website")
        return response
        
    except Exception as e:
        print(f"Error sending WhatsApp message: {str(e)}")
        
        # FIXED: Add proper CORS headers to error response
        response = jsonify(success=False, message=str(e))
        response.headers.add("Access-Control-Allow-Origin", "https://kwezyhq.framer.website")
        return response, 500

# Add a health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    response = jsonify(status="ok")
    response.headers.add("Access-Control-Allow-Origin", "https://kwezyhq.framer.website")
    return response

# FIXED: Add test endpoint with CORS headers
@app.route("/test", methods=["GET"])
def test_endpoint():
    response = jsonify(
        status="success", 
        message="WhatsApp API is working",
        endpoint="https://whatsapp-api-rjd7.onrender.com/send-whatsapp",
        allowed_origin="https://kwezyhq.framer.website"
    )
    response.headers.add("Access-Control-Allow-Origin", "https://kwezyhq.framer.website")
    return response

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting server on port {port}")
    print(f"CORS enabled for: https://kwezyhq.framer.website")
    app.run(host="0.0.0.0", port=port, debug=True)