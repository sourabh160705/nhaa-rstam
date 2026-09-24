import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from app.analyzers.sentiment import TextSentimentAnalyzer
from app.analyzers.trauma_keywords import TraumaKeywordAnalyzer
from app.services.svi_engine import SVIEngine
from app.services.text_pipeline import TextPipeline
import asyncio

sa = TextSentimentAnalyzer()
ta = TraumaKeywordAnalyzer()
svi = SVIEngine()
tp = TextPipeline()

tests = [
    "I am very scared and in pain.",
    "They killed my brother and threatened to kill me too.",
    "I feel safe now. The police helped me. Justice was served.",
    "I was beaten and humiliated in front of the village. Nobody helped.",
    "Need information about filing an FIR.",
    "They gave death threat and want to rape my sister.",
    "I am just a little worried about the process.",
]

print("=== SENTIMENT SCORES ===")
for t in tests:
    r = sa.analyze(t)
    print(f"  [{r['sentiment_score']:+.3f} {r['sentiment_label']:>15}] {r['dominant_emotion']:>8} | {t}")

print()
print("=== TRAUMA SCORES ===")
for t in tests:
    r = ta.analyze(t)
    print(f"  [{r['keyword_density_score']:6.1f}] cats={len(r['categories_found'])} matches={len(r['matches'])} | {t}")

print()
print("=== FULL SVI SCORES (text-only) ===")
async def run():
    for t in tests:
        text_res = await tp.process(t)
        svi_res = svi.compute(voice_result=None, text_result=text_res)
        print(f"  SVI={svi_res['total_score']:5.1f}  Risk={svi_res['risk_level'].value:>10} | {t}")
        for c in svi_res['components']:
            print(f"         {c['name']:>20}: raw={c['raw_score']:5.1f}  w={c['weight']:.3f}  ws={c['weighted_score']:5.1f}")
        print()

asyncio.run(run())
