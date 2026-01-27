import os
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    Response,
    stream_with_context,
    jsonify,
)
import openai

load_dotenv()

# Strip whitespace/newlines to avoid invalid auth header
api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
openai.api_key = api_key

# Pass explicit key to client to avoid relying on env formatting
client = openai.OpenAI(api_key=api_key)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    content = request.json["message"]
    
    # Store in Flask session or global for the stream endpoint
    global current_message
    current_message = content
    
    return jsonify(success=True)


@app.route("/stream", methods=["GET"])
def stream():
    def generate():
        global current_message
        
        system_prompt = """You are SOCRATES-AI, a philosophical guide inspired by the Socratic method.

Your purpose: To help users gain knowledge and understanding through thoughtful questioning, rather than simply providing answers.

Instructions:
1. Read the user's statement or question carefully
2. Identify underlying assumptions, gaps in reasoning, or areas for deeper exploration
3. Respond with 2-4 clarifying questions that:
   - Challenge assumptions
   - Encourage critical thinking
   - Guide the user toward their own insights
   - Explore different perspectives
4. Keep your tone curious, respectful, and encouraging
5. Do NOT provide direct answers unless the user has thoroughly explored the topic through questions
6. Help users think for themselves

Style:
- Ask genuine, thought-provoking questions
- Build upon the user's previous responses
- Guide discovery rather than lecture
- Be concise but meaningful"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": current_message}
        ]

        with client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
            temperature=0.7,
        ) as stream:
            for chunk in stream:
                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"
                if chunk.choices[0].finish_reason == "stop":
                    break

    return Response(stream_with_context(generate()), mimetype="text/event-stream")



