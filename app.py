from flask import Flask, request, jsonify
from insights.fetcher import fetch_instagram_insights

app = Flask(__name__)

@app.route('/fetch-insights', methods=['POST'])
def fetch_insights():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        # Save CSV to `output` folder
        csv_file_path = fetch_instagram_insights(username, password, save_csv=True)
        return jsonify({"message": "Insights fetched successfully", "csv_file_path": csv_file_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
