
from flask import Flask, jsonify, request
from insights.fetcher import fetch_instagram_insights

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Instagram Insights API!"})

@app.route('/fetch-insights', methods=['POST'])
def fetch_insights():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username and password:
        fetch_instagram_insights(username, password)
        return jsonify({"message": "Insights fetched successfully!"}), 200
    return jsonify({"error": "Username and password required"}), 400

if __name__ == "__main__":
    app.run(debug=True)
