from flask import Flask, request, jsonify

app = Flask(__name__)

# Home route
@app.route("/")
def home():
    return "backend is running"

# Test route
@app.route("/test")
def test():
    return "API is working!"

# Free AI route
@app.route("/ask", methods=["POST"])
def ask_ai():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_input = data["message"].lower()

    # Simple AI-like responses
    if "hello" in user_input:
        reply = "Hi! How can I help you?"
    elif "task" in user_input:
        reply = "You can add, delete, or view your tasks."
    elif "add task" in user_input:
        reply = "Task added successfully! (demo)"
    elif "bye" in user_input:
        reply = "Goodbye! Have a great day!"
    else:
        reply = "I'm a free AI. I understand simple messages for now."

    return jsonify({
        "response": reply
    })


# Run locally
if __name__ == "__main__":
    app.run(debug=True)
