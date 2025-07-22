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
     origins=["https://www.kwezy.com"], 
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
        response.headers.add("Access-Control-Allow-Origin", "https://www.kwezy.com")
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
    print(f"🔍 Received request data: {data}")
    
    # Get data with better empty value handling
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    number = data.get("number", "").strip()
    body = data.get("message", "").strip()
    
    # Log individual fields for debugging
    print(f"📋 Parsed fields - Name: '{name}', Email: '{email}', Phone Number: '{number}', Message: '{body}'")

    if not body:
        print("❌ No message provided")
        return jsonify(success=False, message="Message is required"), 400

    try:
        # Create clean message format - only show provided values
        message_text = "📝 New Contact Form Submission\n\n"
        
        # Only add name if it's provided and not empty
        if name:
            message_text += f"👤 Name: {name}\n"
        else:
            message_text += "👤 Name: Not provided\n"
            
        # Only add email if it's provided and not empty  
        if email:
            message_text += f"📧 Email: {email}\n"
        else:
            message_text += "📧 Email: Not provided\n"

        # Only add phone number if it's provided and not empty  
        if number:
            message_text += f"📞 Phone: {number}\n"
        else:
            message_text += "📞 Phone: Not provided\n"
            
        message_text += f"💬 Message: {body}"
        
        print(f"📱 Sending WhatsApp message: {message_text}")
            
        msg = client.messages.create(
            from_=twilio_from,
            to=whatsapp_to,
            body=message_text
        )
        
        # FIXED: Add proper CORS headers to response
        response = jsonify(success=True, sid=msg.sid)
        response.headers.add("Access-Control-Allow-Origin", "https://www.kwezy.com")
        return response
        
    except Exception as e:
        print(f"Error sending WhatsApp message: {str(e)}")
        
        # FIXED: Add proper CORS headers to error response
        response = jsonify(success=False, message=str(e))
        response.headers.add("Access-Control-Allow-Origin", "https://www.kwezy.com")
        return response, 500

# Add a health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    response = jsonify(status="ok")
    response.headers.add("Access-Control-Allow-Origin", "https://www.kwezy.com")
    return response

# FIXED: Add test endpoint with CORS headers - accepts both GET and POST
@app.route("/test", methods=["GET", "POST"])
def test_endpoint():
    response = jsonify(
        status="success", 
        message="WhatsApp API is working",
        endpoint="https://whatsapp-api-rjd7.onrender.com/send-whatsapp",
        allowed_origin="https://www.kwezy.com",
        method_used=request.method
    )
    response.headers.add("Access-Control-Allow-Origin", "https://www.kwezy.com")
    return response

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting server on port {port}")
    print(f"CORS enabled for: https://www.kwezy.com")
    app.run(host="0.0.0.0", port=port, debug=True)