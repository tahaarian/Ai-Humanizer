"""LLM provider. Ollama-compatible; set LLM_URL to a Colab/GPU tunnel later, no code change."""
import httpx
from .config import get_settings

def _headers():
    k = get_settings().llm_api_key
    return {"Authorization": f"Bearer {k}"} if k else {}

async def chat(system: str, user: str, temperature: float = 0.9) -> str:
    s = get_settings()
    async with httpx.AsyncClient(timeout=s.llm_timeout, headers=_headers()) as c:
        r = await c.post(f"{s.llm_url}/api/chat", json={
            "model": s.llm_model, "stream": False,
            "options": {"temperature": temperature, "top_p": 0.95, "repeat_penalty": 1.1, "num_ctx": 4096}, "keep_alive": "30m",
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
        r.raise_for_status()
        return r.json()["message"]["content"].strip()

async def status() -> dict:
    s = get_settings()
    try:
        async with httpx.AsyncClient(timeout=3, headers=_headers()) as c:
            names = [m["name"] for m in (await c.get(f"{s.llm_url}/api/tags")).json().get("models", [])]
        return {"reachable": True, "model": s.llm_model, "model_installed": s.llm_model in names}
    except Exception:
        return {"reachable": False, "model": s.llm_model, "model_installed": False}
