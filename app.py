import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

# Email configuration - Add these to your Render environment variables
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")  # Gmail SMTP
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USER = os.environ.get("EMAIL_USER", "dev@kwezy.com")   # Your email
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")        # App password
EMAIL_FROM_NAME = os.environ.get("EMAIL_FROM_NAME", "Kwezy Team")

def send_auto_reply_email(to_email, customer_name):
    """Send a professional auto-reply email to the customer"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Thank you for connecting with Kwezy!"
        msg['From'] = f"{EMAIL_FROM_NAME} <{EMAIL_USER}>"
        msg['To'] = to_email

        # Email content
        customer_first_name = customer_name.split()[0] if customer_name else "there"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none; }}
                .cta-button {{ display: inline-block; background: #667eea; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .highlight {{ background: #f0f7ff; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Thank You for Connecting with Kwezy!</h1>
                </div>
                
                <div class="content">
                    <p>Hi {customer_first_name},</p>
                    
                    <p>Thank you for reaching out to us! We're excited to connect with you and learn more about how we can help you achieve your goals.</p>
                    
                    <div class="highlight">
                        <strong>✅ Your message has been received!</strong><br>
                        We typically respond within 24 hours during business days.
                    </div>
                    
                    <p>Our team is reviewing your inquiry and will get back to you as soon as possible with a personalized response. In the meantime, feel free to:</p>
                    
                    <ul>
                        <li>🌐 Explore our website to learn more about our services</li>
                        <li>📱 Follow us on social media for updates and insights</li>
                        <li>📧 Reply to this email if you have any additional questions</li>
                    </ul>
                    
                    <p>We're looking forward to working with you and helping you succeed!</p>
                    
                    <p>Best regards,<br>
                    <strong>The Kwezy Team</strong><br>
                    📧 dev@kwezy.com</p>
                </div>
                
                <div class="footer">
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        This is an automated response. Please do not reply to this email directly.<br>
                        For immediate assistance, contact us at dev@kwezy.com
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version for compatibility
        text_content = f"""
        Hi {customer_first_name},

        Thank you for reaching out to Kwezy! We're excited to connect with you.

        ✅ Your message has been received!
        We typically respond within 24 hours during business days.

        Our team is reviewing your inquiry and will get back to you as soon as possible with a personalized response.

        Best regards,
        The Kwezy Team
        dev@kwezy.com

        ---
        This is an automated response. For immediate assistance, contact us at dev@kwezy.com
        """

        # Attach both HTML and text versions
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)

        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Auto-reply email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send auto-reply email to {to_email}: {str(e)}")
        return False

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
    print(f"🔍 Received request data: {data}")
    
    # Get data with better empty value handling
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    body = data.get("message", "").strip()
    
    # Log individual fields for debugging
    print(f"📋 Parsed fields - Name: '{name}', Email: '{email}', Message: '{body}'")

    if not body:
        print("❌ No message provided")
        return jsonify(success=False, message="Message is required"), 400

    try:
        # Create clean WhatsApp message format
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
            
        message_text += f"💬 Message: {body}"
        
        print(f"📱 Sending WhatsApp message: {message_text}")
            
        # Send WhatsApp message
        msg = client.messages.create(
            from_=twilio_from,
            to=whatsapp_to,
            body=message_text
        )
        
        # Send auto-reply email if email is provided
        email_sent = False
        if email and "@" in email:
            print(f"📧 Attempting to send auto-reply email to: {email}")
            email_sent = send_auto_reply_email(email, name)
        else:
            print("📧 No valid email provided, skipping auto-reply")
        
        # FIXED: Add proper CORS headers to response
        response_data = {
            "success": True, 
            "sid": msg.sid,
            "whatsapp_sent": True,
            "email_sent": email_sent,
            "message": f"WhatsApp sent successfully. Auto-reply email {'sent' if email_sent else 'not sent'}."
        }
        
        response = jsonify(response_data)
        response.headers.add("Access-Control-Allow-Origin", "https://kwezyhq.framer.website")
        return response
        
    except Exception as e:
        print(f"❌ Error processing request: {str(e)}")
        
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

# FIXED: Add test endpoint with CORS headers - accepts both GET and POST
@app.route("/test", methods=["GET", "POST"])
def test_endpoint():
    response = jsonify(
        status="success", 
        message="WhatsApp API is working",
        endpoint="https://whatsapp-api-rjd7.onrender.com/send-whatsapp",
        allowed_origin="https://kwezyhq.framer.website",
        method_used=request.method,
        email_configured=bool(EMAIL_USER and EMAIL_PASSWORD)
    )
    response.headers.add("Access-Control-Allow-Origin", "https://kwezyhq.framer.website")
    return response

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting server on port {port}")
    print(f"CORS enabled for: https://kwezyhq.framer.website")
    print(f"Email configured: {bool(EMAIL_USER and EMAIL_PASSWORD)}")
    app.run(host="0.0.0.0", port=port, debug=True)