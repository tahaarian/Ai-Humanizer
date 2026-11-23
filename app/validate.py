import re
W = re.compile(r"[A-Za-z']+")
def length_ratio(a, b):
    la, lb = len(W.findall(a)), len(W.findall(b))
    return lb / la if la else 1
def keyword_overlap(a, b):
    ka = {w.lower() for w in W.findall(a) if len(w) > 5}
    kb = {w.lower() for w in W.findall(b)}
    return len(ka & kb) / len(ka) if ka else 1.0
def ok(orig, new):
    r = length_ratio(orig, new)
    return 0.6 <= r <= 1.4 and keyword_overlap(orig, new) >= 0.35
