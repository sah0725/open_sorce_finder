import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Placeholder for our AI agent logic
from agent import find_good_first_issues

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find-issues', methods=['POST'])
def find_issues():
    data = request.get_json()
    languages = data.get('languages', [])
    
    if not languages:
        return jsonify({"error": "Please select at least one language."}), 400

    # In a real scenario, you would call your agent here.
    issues = find_good_first_issues(languages)
    
    return jsonify(issues)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
