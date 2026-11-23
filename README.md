# Ai-Humanizer
Local web tool that rewrites English (academic/practical) text so it reads naturally, using a **local LLM via Ollama**. No data leaves your machine.

## Run
```
ollama pull qwen2.5:7b-instruct      # or set HUMANIZER_MODEL
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000     # open http://localhost:8000
pytest
```
## Pipeline
parse (txt/md/docx/pdf) → chunk → mask citations/numbers/URLs → local-LLM rewrite (style + optional user writing sample) → validate (placeholders, length, keyword overlap) → stylometric analyzer → retry with targeted feedback if still AI-like → unmask.

The score is an internal style signal (burstiness, AI-typical wording, uniformity); it does not guarantee any external detector's result. Use responsibly and follow your institution's AI-disclosure rules.
