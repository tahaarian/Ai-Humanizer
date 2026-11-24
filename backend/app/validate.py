import re
W = re.compile(r"[A-Za-z']+")
def length_ratio(a, b):
    la, lb = len(W.findall(a)), len(W.findall(b))
    return lb / la if la else 1
def keyword_overlap(a, b):
    ka = {w.lower()[:6] for w in W.findall(a) if len(w) > 5}
    kb = {w.lower()[:6] for w in W.findall(b)}
    return len(ka & kb) / len(ka) if ka else 1.0
HEDGES = ["uncertain", "unclear", "selected", "cannot", "may", "might", "suggest", "limited", "preliminary",
          "retrospective", "heterogeneous", "guidance", "demonstrate", "remains"]
SPLIT = re.compile(r"(?<=[.!?])\s+")
def hedges_missing(a, b):
    """Hedge/key terms present in `a` but absent (by prefix) from `b`."""
    la, lb = a.lower(), b.lower()
    return [h for h in HEDGES if re.search(rf"\b{h}", la) and not re.search(rf"\b{h}", lb)]
def hedges_kept(a, b):
    return not hedges_missing(a, b)
def invented(orig, new):
    """Sentences in `new` whose content words mostly don't appear in `orig` => fabricated claim."""
    ko = {w.lower()[:6] for w in W.findall(orig) if len(w) > 4}
    bad = []
    for s in SPLIT.split(new.strip()):
        kw = [w.lower()[:6] for w in W.findall(s) if len(w) > 4]
        if len(kw) >= 4 and sum(k in ko for k in kw) / len(kw) < 0.5: bad.append(s)
    return bad
def ok(orig, new):
    if invented(orig, new) or not hedges_kept(orig, new): return False
    r = length_ratio(orig, new)
    return 0.6 <= r <= 1.4 and keyword_overlap(orig, new) >= 0.35

def reasons(orig, new):
    """Why `ok` would reject `new` (empty list = accepted)."""
    out = []
    if invented(orig, new): out.append("added sentence with new content")
    miss = hedges_missing(orig, new)
    if miss: out.append("hedge or key term dropped: " + ", ".join(miss))
    r = length_ratio(orig, new)
    if not 0.6 <= r <= 1.4: out.append(f"length changed too much ({r:.2f}x)")
    if keyword_overlap(orig, new) < 0.35: out.append("meaning drifted (low keyword overlap)")
    return out
