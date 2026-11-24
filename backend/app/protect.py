"""Mask things the rewriter must never alter: citations, numbers w/ units, URLs, equations."""
import re
PATTERNS = [
 r"https?://\S+",
 r"\[[0-9,\s\-–]+\]",                                   # [1], [2-4]
 r"\((?:[A-Z][A-Za-z\-]+(?: et al\.)?(?:,| and| &)?[^()]{0,40}\d{4}[a-z]?)\)",  # (Smith et al., 2020)
 r"\b[A-Z][A-Za-z]*[A-Z]\b",                           # acronyms (AUC, mRNA)
 r"\$[^$]+\$",                                          # inline latex
 r"\b\d+(?:[.,]\d+)?\s?(?:%|[A-Za-zµ°]{1,4}\b)?",       # numbers+units
]
RX = re.compile("|".join(f"(?:{p})" for p in PATTERNS))

def mask(text):
    store = {}
    def sub(m):
        k = f"⟦{len(store)}⟧"; store[k] = m.group(0); return k
    return RX.sub(sub, text), store

def unmask(text, store):
    for k, v in store.items(): text = text.replace(k, v)
    return text

def intact(rewritten, store):
    return all(k in rewritten for k in store)
