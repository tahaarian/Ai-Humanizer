"""Heuristic stylometric analyzer: estimates how 'AI-like' a text reads and explains why.
It is a quality/style signal, NOT a guarantee about any external detector."""
import re, statistics

AI_PHRASES = [
 "delve", "tapestry", "moreover", "furthermore", "in conclusion", "it is important to note",
 "it is worth noting", "plays a crucial role", "a testament to", "in today's", "ever-evolving",
 "landscape", "multifaceted", "underscores", "pivotal", "comprehensive", "leverage", "seamless",
 "navigate the", "realm of", "in the realm", "foster", "intricate", "holistic", "robust",
 "shed light", "paves the way", "stands as", "endeavor", "myriad", "paramount", "notably",
 "additionally", "overall,", "ultimately,", "in summary",
]
SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(\[])")
WORD_RE = re.compile(r"[A-Za-z']+")

def sentences(text):
    return [s.strip() for s in SENT_RE.split(text.strip()) if s.strip()]

def analyze(text: str) -> dict:
    sents = sentences(text)
    words = WORD_RE.findall(text.lower())
    if len(words) < 30:
        return {"score": None, "signals": [], "note": "Need at least 30 words."}
    lens = [len(WORD_RE.findall(s)) for s in sents] or [0]
    mean = statistics.mean(lens)
    cv = (statistics.pstdev(lens) / mean) if mean else 0  # burstiness proxy
    ttr = len(set(words)) / len(words)
    low = text.lower()
    hits = {p: low.count(p) for p in AI_PHRASES if p in low}
    phrase_density = sum(hits.values()) / max(len(sents), 1)
    starters = [s.split()[0].lower() for s in sents if s.split()]
    starter_rep = 1 - len(set(starters)) / max(len(starters), 1)
    contractions = len(re.findall(r"\b\w+'(?:s|t|re|ve|ll|d|m)\b", low)) / max(len(sents), 1)
    avg_word = statistics.mean(len(w) for w in words)

    signals, score = [], 0.0
    def add(pts, msg):
        nonlocal score; score += pts; signals.append({"points": round(pts, 1), "message": msg})
    if cv < 0.35: add(25, f"Sentence lengths are very uniform (variation {cv:.2f}; humans typically >0.45).")
    elif cv < 0.45: add(10, f"Sentence lengths are somewhat uniform (variation {cv:.2f}).")
    if mean > 26: add(10, f"Average sentence is long ({mean:.0f} words).")
    if hits: add(min(30, 8 * sum(hits.values())), "AI-typical wording: " + ", ".join(sorted(hits)))
    if starter_rep > 0.35: add(10, "Many sentences start with the same word.")
    if contractions == 0 and len(sents) > 4: add(8, "No contractions; tone is stiff and impersonal.")
    if avg_word > 5.7: add(7, f"Long average word length ({avg_word:.1f}).")
    if ttr < 0.45 and len(words) > 150: add(5, "Low vocabulary variety.")
    return {"score": min(100, round(score)), "words": len(words), "sentences": len(sents),
            "metrics": {"burstiness": round(cv, 2), "avg_sentence_len": round(mean, 1),
                        "type_token_ratio": round(ttr, 2), "ai_phrases": hits},
            "signals": signals}
