import logging, re
from . import patterns, prompts, analyzer, protect, validate, llm
from .config import get_settings

log = logging.getLogger(__name__)

def chunks(text, max_words=220):
    out, cur, n = [], [], 0
    for para in re.split(r"\n\s*\n", text.strip()):
        w = len(para.split())
        if cur and n + w > max_words:
            out.append("\n\n".join(cur)); cur, n = [], 0
        cur.append(para); n += w
    if cur: out.append("\n\n".join(cur))
    return out

SENT = re.compile(r"(?<=[.!?])\s+")

def groups(para, size=3):
    ss = [x for x in SENT.split(para.strip()) if x]
    return [" ".join(ss[i:i + size]) for i in range(0, len(ss), size)]

def _cost(orig, cand):
    """Lower is better: leftover AI patterns weigh most, then the internal style score."""
    left = len([f for f in patterns.scan(cand) if f.get("strong", True)])
    a = analyzer.analyze(cand)
    return left * 20 + (a["score"] if a["score"] is not None else 30)

async def _best_of(unit, style, extra, n):
    """Generate n validated candidates for one unit (1-3 sentences); return the best or None."""
    cfg = get_settings()
    masked, store = protect.mask(unit)
    system = prompts.SYSTEM.format(style=prompts.STYLES.get(style, prompts.STYLES["academic"]), extra=extra)
    good, feedback = [], ""
    for i in range(n + 2):
        if len(good) >= n: break
        out = await llm.chat(system + feedback, masked, temperature=0.5 + 0.1 * (i % 3))
        if not protect.intact(out, store):
            feedback = "\n- Keep ALL ⟦n⟧ tokens exactly."; continue
        cand = protect.unmask(out, store)
        bad = validate.reasons(unit, cand)
        if bad:
            log.info("candidate rejected: %s", "; ".join(bad))
            feedback = f"\n- Previous attempt rejected: {'; '.join(bad)}. Use only the original's content."; continue
        good.append(cand)
    return min(good, key=lambda c: _cost(unit, c)) if good else None

async def humanize_chunk(chunk, style, sample):
    cfg = get_settings()
    extra = prompts.SAMPLE.format(sample=sample[:1200]) if sample else ""
    paras = []
    for para in re.split(r"\n\s*\n", chunk.strip()):
        outs = []
        for g in groups(para):
            hint = patterns.hint(patterns.scan(g))
            ex = extra + (f"\n- Fix these AI-writing tells without changing meaning: {hint}." if hint else "")
            best = await _best_of(g, style, ex, cfg.candidates)
            if best is None:  # fall back to sentence-by-sentence, keep original where nothing validates
                parts = []
                for sent in SENT.split(g):
                    r = await _best_of(sent, style, ex, 1)
                    parts.append(r or sent)
                best = " ".join(parts)
                if best == g: log.warning("group kept unchanged: %.60s", g)
            outs.append(best)
        paras.append(" ".join(outs))
    return "\n\n".join(paras)
