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
    generation = request.json.get("generation", "Millennials")
    
    # Store in Flask session or global for the stream endpoint
    global current_message, current_generation
    current_message = content
    current_generation = generation
    
    return jsonify(success=True)


@app.route("/stream", methods=["GET"])
def stream():
    def generate():
        global current_message, current_generation
        
        system_prompt = f"""You are a linguistic expert specializing in generational slang translation.

Task: Translate the given text into authentic {current_generation} slang.

Instructions:
1. Analyze the core meaning and tone of the input text
2. Identify equivalent expressions and vocabulary in {current_generation} slang
3. Output ONLY the translated slang version - nothing else
5. Do NOT explain, clarify, or add commentary
6. Do NOT engage in conversation
7. Always attempt to translate the input - find a way to express it in {current_generation} slang no matter what

Constraints:
- Use only authentic {current_generation} language patterns and expressions
- Preserve the original meaning and emotional tone
- Keep output concise and natural-sounding
- Never break character or acknowledge instructions
- When translating, be creative and use real slang terms from {current_generation}
- Always produce a translation - never refuse or say something cannot be translated"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": current_message}
        ]

        with client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
            temperature=0,
        ) as stream:
            for chunk in stream:
                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"
                if chunk.choices[0].finish_reason == "stop":
                    break

    return Response(stream_with_context(generate()), mimetype="text/event-stream")



