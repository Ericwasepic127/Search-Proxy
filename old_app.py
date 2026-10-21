import os
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")  
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PROVIDERS = [
    {
        "name": "groq",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": GROQ_API_KEY,
        "models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "minimaxai/minimax-m2.7",
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "whisper-large-v3",
            "whisper-large-v3-turbo",
        ],
    },
    {
        "name": "gemini",
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "key_env": GEMINI_API_KEY,
        "models": [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            #"gemini-flash-latest",
            #"gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemma-4-31b-it",
            "gemma-4-26b-a4b-it",
        ],
    },
    {
        "name": "openrouter",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key_env": OPENROUTER_API_KEY,
        "models": [
            "openrouter/free",
        ],
    },
]

when = """<title>AI Proxy Server by Ericwasepic127</title>
<h1>This is AI Proxy Server by Ericwasepic127</h1>
<hr>
<p>Use POST to get API response</p>
<br>
<strong>Or else, you will end up here</strong>"""

app = Flask(__name__)
CORS(app)
max_limit = int(os.environ.get("LIMIT", "4"))
requests_count = 0

@app.route('/ready', methods=['GET'])
def ready():
     return "ok\n", 200

@app.route('/', methods=['POST', 'GET'])
def chat():
    global requests_count
    print("Devices count:", requests_count)
    if request.method == 'GET':
        return when, 200
    if requests_count >= max_limit:
        return jsonify({"error": "Server busy"}), 503
    requests_count += 1
    user_messages = request.json.get("messages")
    use = request.json.get("provider", os.environ.get("PROVIDER", "auto"))
    auto = use == "auto"
    model = request.json.get("model")
    if not user_messages or not isinstance(user_messages, list):
        requests_count -= 1
        return jsonify({"error": "A 'messages' array is required"}), 400
    if not auto and model:
        if use not in ["gemini", "openrouter", "groq"]:
           requests_count -= 1
           return jsonify({"error": "Provider %s not found" % use}), 500
        index = ["groq", "gemini", "openrouter"].index(use)
        PROVIDER = PROVIDERS[index]
        key = PROVIDER["key_env"]
        if not key:
            requests_count -= 1
            return jsonify({"error": "Missing API key for %s provider" % use}), 500
        url = PROVIDER["url"]
        if model not in PROVIDER["models"]:
             requests_count -= 1
             return jsonify({"error": "Model not found"}), 404
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": user_messages
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
            requests_count -= 1
            if "error" in response_data:
                return jsonify({"error": response_data["error"]["message"]}), response.status_code
            ai_response = response_data['choices'][0]['message']['content']
            return jsonify({"response": ai_response})
        except (BaseException, Exception) as e:
            requests_count -= 1
            return jsonify({"error": f"Internal proxy error: {str(e)}"}), 500
    elif auto:
         for p in PROVIDERS:
              url = p["url"]
              key = p["key_env"]
              name = p["name"]
              models = p["models"]
              error = None
              if not key:
                   continue
              headers = {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
              }
              for model in models:
                    print("Trying model: %s+%s" % (name, model))
                    payload = {
                         "model": model,
                         "messages": user_messages
                    }
                    try:
                      response = requests.post(url, headers=headers, json=payload)
                      response_data = response.json()
                      if response.status_code != 200 or "error" in response_data:
                         if response.status_code in [429, 503]:
                              continue
                         error = jsonify({"error": response_data["error"]["message"]}), response.status_code
                         print("Error:", response.json())
                         continue
                      ai_response = response_data['choices'][0]['message']['content']
                      requests_count -= 1
                      return jsonify({"response": ai_response, "used": f"{name}+{model}"})
                    except (BaseException, Exception) as e:
                      error = jsonify({"error": f"Internal proxy error: {str(e)}"}), 500
                      print("Error:", error)
         requests_count -= 1
         return error or (jsonify({"error": "no models available right now"}), 503)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443 if getattr(os, "getuid", lambda: 1000)() == 0 else os.environ.get("AI_PORT", 5000))
