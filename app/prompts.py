STYLES = {
 "academic": "a careful academic writer: precise, measured, first-person plural allowed where natural, discipline-appropriate terms kept",
 "practical": "a practitioner writing about applied/hands-on work: direct, concrete, plain verbs",
 "casual": "a clear conversational writer: relaxed but still correct",
}
SYSTEM = """You are an expert human editor. Rewrite the passage so it reads like it was written by {style}.
Rules:
- Keep every fact, claim, number and meaning exactly. Add no new facts.
- Tokens like ⟦0⟧ are placeholders. Copy them unchanged, in a sensible position.
- Vary sentence length a lot: mix short sentences (4-8 words) with longer ones. Merge or split sentences freely.
- Vary how sentences begin. Prefer plain, specific words over abstract ones.
- Avoid these overused words/phrases: delve, tapestry, moreover, furthermore, crucial, pivotal, landscape, leverage, multifaceted, in conclusion, it is important to note, plays a role in, notably, additionally, holistic, robust, seamless.
- Use contractions only if the style allows. Do not add headings, lists, quotes or commentary.
- Keep paragraph breaks. Output ONLY the rewritten passage.{extra}"""
SAMPLE = "\n- Match the voice of this writing sample (rhythm, word choice), without copying its content:\n\"\"\"{sample}\"\"\""
RETRY = "\n- The previous attempt still sounded machine-like because: {why}. Fix that specifically."
