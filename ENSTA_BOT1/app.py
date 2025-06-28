from flask import Flask, render_template, request, jsonify, redirect, make_response
import jwt
from chat import get_response
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)
CORS(app, resources={
    r"/predict": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "allow_headers": ["Authorization", "Content-Type"]
    }
})
app.config['SECRET_KEY'] = 'your_jwt_secret'  # Must match Node.js secret

# Connect to the  MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Database"]
messages_collection = db["messages"]

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return "Token expired"
    except jwt.InvalidTokenError:
        return "Invalid token"

@app.route("/dash.html")  
def dash():
    return render_template("dash.html")

@app.route('/chatbot', methods=['GET'])
def chatbot_get():
    # Check for token in URL parameters first
    token = request.args.get('token')
    
    # If no token in URL, check for token in cookies
    if not token:
        token = request.cookies.get('authToken')
    
    # If still no token, redirect to login
    if not token:
        print("❌ No token found")
        return redirect('http://localhost:8901')
    print(f"\n🔑 Current secret key: '{app.config['SECRET_KEY']}'")
    # Verify the token
    token_verification = verify_token(token)
    if isinstance(token_verification, str):  # <- FIXED INDENTATION
        print(f"🔴 Token verification failed: {token_verification}")  # Debug
        return redirect('http://localhost:8901')
    
    # Token is valid - render chatbot page
    response = make_response(render_template('base.html'))
    
    # Set the token as HTTP-only cookie for security
    response.set_cookie(
        'authToken', 
        token, 
        httponly=True, 
        secure=False  # True in production
    )
    print("🟢 Token valid - rendering base.html")
    return response

@app.route('/chatbot', methods=['POST'])
def chatbot_post():
    # For POST requests (if you have form submissions to this endpoint)
    token = request.cookies.get('authToken') or request.headers.get('Authorization')
    
    if token and token.startswith('Bearer '):
        token = token[7:]  # Strip 'Bearer ' prefix
    
    if not token or isinstance(verify_token(token), str):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Process POST data here if needed
    return jsonify({'status': 'success'})

@app.route('/predict', methods=['POST'])
def predict():
    # Get token from Authorization header or cookies
    token = None
    
    # Check Authorization header first
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]
    
    # Fallback to cookie if no header
    if not token:
        token = request.cookies.get('authToken')
    
    # Verify token
    if not token or isinstance(verify_token(token), str):
        return jsonify({'error': 'Unauthorized'}), 401
    
    decoded_token = verify_token(token)
    # Process chatbot prediction
    text = request.get_json().get('message')
    if not text:
        return jsonify({'error': 'No message provided'}), 400
    
    response = get_response(text)
    user_id = decoded_token["userId"]

    # Save user message
    messages_collection.insert_one({
        "userId": ObjectId(user_id),
        "sender": "user",
        "message": text,
        "timestamp": datetime.datetime.utcnow()
    })

    # Save bot response
    messages_collection.insert_one({
        "userId": ObjectId(user_id),
        "sender": "bot",
        "message": response,
        "timestamp": datetime.datetime.utcnow()
    })

    return jsonify({'answer': response})

@app.route('/')
def home():
    # Redirect to chatbot if already authenticated
    token = request.cookies.get('authToken')
    if token and not isinstance(verify_token(token), str):
        return redirect('/chatbot')
    return redirect('http://localhost:8901')

if __name__ == '__main__':
    app.run(port=5000, debug=True)