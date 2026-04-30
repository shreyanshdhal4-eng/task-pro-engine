from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# OpenAI client (uses environment variable from Render)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Home route
@app.route("/")
def home():
    return "backend is running"

# Test route
@app.route("/test")
def test():
    return "API is working!"

# AI route (IMPORTANT)
@app.route("/ask", methods=["POST"])
def ask_ai():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400

        user_input = data["message"]

        # Call OpenAI
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=user_input
        )

        reply = response.output[0].content[0].text

        return jsonify({
            "response": reply
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run locally
if __name__ == "__main__":
    app.run(debug=True)
