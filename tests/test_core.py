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
