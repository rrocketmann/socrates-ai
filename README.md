# socrates-ai

The public site runs entirely in the browser with WebLLM. No API key. It loads on [GitHub Pages](https://rrocketmann.github.io/socrates-ai/).

The static app is in `web/`. Serve that folder locally:

```bash
python3 -m http.server 8000 -d web
```

The Flask app below still calls OpenAI if you want the server version.

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
