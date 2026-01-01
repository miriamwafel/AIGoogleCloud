import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# Konfiguracja - używa ADC (Application Default Credentials)
# Na Google Cloud automatycznie używa konta serwisowego bez klucza API
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.environ.get("VERTEX_AI_LOCATION", "us-central1")

# Klient Vertex AI
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# Przechowuj historię czatu per użytkownik
chat_histories: dict[str, list] = {}


def get_chat_history(session_id: str) -> list:
    """Pobierz lub utwórz historię czatu."""
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    return chat_histories[session_id]


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
        history = get_chat_history(session_id)

        # Dodaj wiadomość użytkownika do historii
        history.append(types.Content(role="user", parts=[types.Part(text=message)]))

        # Wyślij do Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=history
        )

        # Dodaj odpowiedź do historii
        assistant_message = response.text
        history.append(types.Content(role="model", parts=[types.Part(text=assistant_message)]))

        return jsonify({"response": assistant_message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset():
    """Reset sesji czatu."""
    data = request.json
    session_id = data.get("session_id", "default")

    if session_id in chat_histories:
        del chat_histories[session_id]

    return jsonify({"status": "ok"})


@app.route("/health")
def health():
    """Health check dla Cloud Run."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
