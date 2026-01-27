# socrates-ai

Minimal Flask app exposing SOCRATES-AI chat UI.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run (dev)

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
export OPENAI_API_KEY=<your_key>
flask run
```

## Run (prod-ish)

```bash
export OPENAI_API_KEY=<your_key>
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```
