import httpx, re
from . import config, prompts, analyzer, protect, validate

async def _chat(system, user, temperature=0.9):
    async with httpx.AsyncClient(timeout=600) as c:
        r = await c.post(f"{config.OLLAMA_URL}/api/chat", json={
            "model": config.MODEL, "stream": False,
            "options": {"temperature": temperature, "top_p": 0.95, "repeat_penalty": 1.1},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
        r.raise_for_status()
        return r.json()["message"]["content"].strip()

def chunks(text, max_words=220):
    out, cur, n = [], [], 0
    for para in re.split(r"\n\s*\n", text.strip()):
        w = len(para.split())
        if cur and n + w > max_words:
            out.append("\n\n".join(cur)); cur, n = [], 0
        cur.append(para); n += w
    if cur: out.append("\n\n".join(cur))
    return out

async def humanize_chunk(chunk, style, sample):
    masked, store = protect.mask(chunk)
    extra = prompts.SAMPLE.format(sample=sample[:1200]) if sample else ""
    best = chunk
    for attempt in range(config.MAX_PASSES + 1):
        system = prompts.SYSTEM.format(style=prompts.STYLES.get(style, prompts.STYLES["academic"]), extra=extra)
        out = await _chat(system, masked)
        if not protect.intact(out, store):
            extra += "\n- You dropped placeholders last time. Keep ALL ⟦n⟧ tokens."; continue
        cand = protect.unmask(out, store)
        if not validate.ok(chunk, cand): continue
        best = cand
        a = analyzer.analyze(cand)
        if a["score"] is None or a["score"] <= config.TARGET_SCORE: break
        why = "; ".join(s["message"] for s in a["signals"][:3])
        extra = extra.split("\n- The previous")[0] + prompts.RETRY.format(why=why)
    return best

async def humanize(text, style="academic", sample=""):
    parts = [await humanize_chunk(c, style, sample) for c in chunks(text)]
    return "\n\n".join(parts)
