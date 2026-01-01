import os
from flask import Flask, render_template, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession

app = Flask(__name__)

# Konfiguracja Vertex AI - używa ADC (Application Default Credentials)
# Na Google Cloud automatycznie używa konta serwisowego bez klucza API
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.environ.get("VERTEX_AI_LOCATION", "us-central1")

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Użyj Gemini - dostępny przez Vertex AI
model = GenerativeModel("gemini-1.5-flash")

# Przechowuj sesje czatu per użytkownik (w produkcji użyj Redis/DB)
chat_sessions: dict[str, ChatSession] = {}


def get_chat_session(session_id: str) -> ChatSession:
    """Pobierz lub utwórz sesję czatu."""
    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat()
    return chat_sessions[session_id]


@app.route("/")
def index():
    """Strona główna z interfejsem czatu."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Endpoint API do wysyłania wiadomości."""
    data = request.json
    message = data.get("message", "")
    session_id = data.get("session_id", "default")

    if not message:
        return jsonify({"error": "Brak wiadomości"}), 400

    try:
        chat_session = get_chat_session(session_id)
        response = chat_session.send_message(message)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset():
    """Reset sesji czatu."""
    data = request.json
    session_id = data.get("session_id", "default")

    if session_id in chat_sessions:
        del chat_sessions[session_id]

    return jsonify({"status": "ok"})


@app.route("/health")
def health():
    """Health check dla Cloud Run."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
