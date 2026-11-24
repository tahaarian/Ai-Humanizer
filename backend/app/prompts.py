STYLES = {
 "academic": "a careful academic writer: precise, measured, first-person plural allowed where natural, discipline-appropriate terms kept",
 "practical": "a practitioner writing about applied/hands-on work: direct, concrete, plain verbs",
 "light": "the original author, lightly edited: keep the original sentence structure and wording wherever it is already clear; only fix awkward, wordy or overlong sentences",
 "casual": "a clear conversational writer: relaxed but still correct",
}
SYSTEM = """You are an expert human editor. Rewrite the passage so it reads like it was written by {style}.
Rules:
- Keep every fact, claim, number and meaning exactly. Add no new facts.
- Tokens like ⟦0⟧ are placeholders. Copy them unchanged, in a sensible position.
- Every sentence you write must restate something present in the passage. Never add conclusions, implications, summaries or new sentences of your own. The sentence count may change only by splitting or merging.
- Keep technical terms and hedging words exactly (e.g. uncertain, selected, cannot, may, remains). Do not swap them for near-synonyms such as unclear/illustrate/guidelines.
- Split any sentence over 30 words into two. Otherwise keep the author's own sentence boundaries where they read well.
- Prefer plain, specific words over abstract ones.
- Avoid these overused words/phrases: delve, tapestry, moreover, furthermore, crucial, pivotal, landscape, leverage, multifaceted, in conclusion, it is important to note, plays a role in, notably, additionally, holistic, robust, seamless.
- Use contractions only if the style allows. Do not add headings, lists, quotes or commentary.
- Keep paragraph breaks. Output ONLY the rewritten passage.{extra}"""
SAMPLE = "\n- Match the voice of this writing sample (rhythm, word choice), without copying its content:\n\"\"\"{sample}\"\"\""
RETRY = "\n- The previous attempt still sounded machine-like because: {why}. Fix that specifically."
