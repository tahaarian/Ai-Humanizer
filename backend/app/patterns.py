"""Rule-based detector of common AI-writing tells (after Wikipedia 'Signs of AI writing').
Returns explainable findings; used for UI feedback and to steer the rewrite prompt."""
import re

PATTERNS = [
 ("not_x_but_y", "Not X but Y", True, r"\b(?:it'?s|this is|that'?s)?\s*not (?:just|only|merely|simply)\b[^.]{0,80}\b(?:but|it'?s|—)", "State the point directly."),
 ("closer", "One-line closer", True, r"(?:^|(?<=[.!?]\s))(?:Let that sink in|That is the real win|This (?:highlights|underscores|shows) the importance of)[^.]*\.", "Cut the closer that only restates."),
 ("deep_saying", "Deep-sounding saying", True, r"\b(?:at its core|at the heart of|the true power of|in essence)\b", "Replace with the specific claim."),
 ("run_up", "Staged run-up", True, r"\b(?:let'?s dive in|here'?s the thing|the hard part is|it'?s worth noting that|it is important to note that|it is worth noting that)\b", "Remove the run-up; state the point."),
 ("no_one", "Arguing with no one", True, r"\b(?:this isn'?t (?:mainly )?about|I'?m not saying)\b", "Drop the unraised objection."),
 ("inflated", "Inflated significance", False, r"\b(?:pivotal|testament to|game-?changer|paradigm shift|ever-evolving|the future looks bright|marks? a (?:significant|new) (?:era|chapter))\b", "Keep the fact, drop the significance."),
 ("ai_words", "Overused AI words", False, r"\b(?:delve|tapestry|multifaceted|holistic|seamless(?:ly)?|myriad|paramount|intricate|realm of)\b", "Use plain words."),
 ("ing_tail", "Shallow -ing tail", False, r",\s(?:highlighting|underscoring|showcasing|reflecting|symbolizing|emphasizing|demonstrating)\b[^.]{0,80}\.", "Keep only what the source supports."),
 ("connector_open", "Stock sentence opener", False, r"(?:^|(?<=[.!?]\s))(?:Moreover|Furthermore|Additionally|In conclusion|Overall|Ultimately),", "Vary or drop the connector."),
 ("em_dash", "Many em dashes", False, None, "Use periods, commas or parentheses."),
 ("triad", "Forced triads", False, r"\b\w+, \w+,? and \w+\b", "Use the number of items the meaning needs."),
]

def scan(text: str) -> list[dict]:
    out = []
    for pid, name, strong, rx, fix in PATTERNS:
        if pid == "em_dash":
            n = text.count("—") + text.count(" -- ")
            if n >= 3: out.append({"id": pid, "name": name, "strong": strong, "count": n, "examples": [], "fix": fix})
            continue
        ms = [m.group(0).strip() for m in re.finditer(rx, text, re.I | re.M)]
        if pid == "triad" and len(ms) < 3: continue
        if ms: out.append({"id": pid, "name": name, "strong": strong, "count": len(ms), "examples": ms[:3], "fix": fix})
    return out

def hint(findings: list[dict]) -> str:
    if not findings: return ""
    return "; ".join(f"{f['name']} ({f['fix']})" for f in findings[:5])
