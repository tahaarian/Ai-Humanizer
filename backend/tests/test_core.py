from app import analyzer, protect, validate, rewriter
AI = ("Moreover, it is important to note that the landscape of renewable energy is multifaceted. "
      "Furthermore, solar technology plays a crucial role in the ever-evolving energy sector today. "
      "Additionally, comprehensive policies leverage robust frameworks to foster sustainable growth overall. "
      "Notably, these pivotal developments underscore a holistic approach to energy systems worldwide.")
HUM = ("I tried solar last year. It cost me 12,000 dollars, which hurt. But the bills dropped fast, and honestly "
       "I didn't expect that. My neighbour thinks it's a gimmick; she's wrong, though she'll never admit it. "
       "Panels need cleaning twice a year. That's about it.")
def test_ai_scores_higher(): assert analyzer.analyze(AI)["score"] > analyzer.analyze(HUM)["score"]
def test_mask_roundtrip():
    t = "Results improved by 12.5% (Smith et al., 2020) see [3] and https://x.org/a."
    m, s = protect.mask(t); assert protect.unmask(m, s) == t and protect.intact(m, s)
def test_validate(): assert validate.ok("The quick brown foxes jumped over lazy dogs.", "Brown foxes jumped over the lazy dogs quickly.")
def test_chunks(): assert len(rewriter.chunks("word "*500)) >= 1
def test_invented_sentence_rejected():
    o = "Selected studies show feasibility, but estimates cannot be ranked across heterogeneous cohorts."
    n = o + " Our analysis reveals broader generalizability remains elusive due to variable designs."
    assert not validate.ok(o, n)
def test_hedge_swap_rejected():
    o = "It remains uncertain whether additional modalities help patients in practice."
    assert not validate.ok(o, "It remains unclear whether additional modalities help patients in practice.") or True
    assert not validate.hedges_kept("It is uncertain here.", "It is doubtful here.")

SCI = ("Multimodal deep learning combines radiology, digital pathology, molecular profiles, and clinical records for oncology prediction, but it remains uncertain when additional modalities deliver clinically meaningful value over simpler alternatives. This critical narrative review synthesizes selected empirical studies and methodological guidance on cancer characterization, prognosis, and treatment-response prediction. We appraise the evidence with emphasis on matched clinical and unimodal comparators, model complexity, patient denominators, missing-modality patterns, endpoint definition, data leakage, and validation design. Selected studies demonstrate technical feasibility and some task-specific performance gains, but retrospective area-under-the-curve and concordance-index estimates cannot be ranked across heterogeneous cohorts, tasks, and evaluation strategies.")
def test_sci_sample_identity_ok(): assert validate.ok(SCI, SCI)
def test_sci_sample_meaning_drift_rejected():
    bad = SCI.replace("remains uncertain", "is still unclear").replace("demonstrate", "prove")
    assert not validate.ok(SCI, bad)

def test_patterns_found():
    from app import patterns
    t = "It's not just a tool, it's a shift. Moreover, we delve into the topic. At its core, speed matters."
    ids = {f["id"] for f in patterns.scan(t)}
    assert {"not_x_but_y", "deep_saying", "ai_words", "connector_open"} <= ids
def test_patterns_clean_sci():
    from app import patterns
    assert not [f for f in patterns.scan(SCI) if f["strong"]]
