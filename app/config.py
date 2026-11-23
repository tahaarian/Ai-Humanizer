import os
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("HUMANIZER_MODEL", "qwen2.5:7b-instruct")
MAX_PASSES = int(os.getenv("MAX_PASSES", "2"))
TARGET_SCORE = float(os.getenv("TARGET_SCORE", "35"))  # AI-likeness score below this = done
MAX_WORDS = int(os.getenv("MAX_WORDS", "5000"))
