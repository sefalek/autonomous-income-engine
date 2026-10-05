from __future__ import annotations
import json
from pathlib import Path
from .ai import generate_product_spec
from .product import build_product
from .research import collect
from .scoring import rank
from .state import load_json,save_json

ROOT=Path(__file__).resolve().parents[2]
CONFIG=json.loads((ROOT/'config'/'config.json').read_text(encoding='utf-8'))

def run()->None:
    opportunities=rank(collect(CONFIG['topics'],CONFIG['max_candidates']))
    save_json(str(ROOT/'state'/'opportunities.json'),opportunities)
    eligible=[x for x in opportunities if x['opportunity_score']>=CONFIG['min_opportunity_score']]
    if not eligible:
        print('No opportunity passed the threshold.'); return
    spec=generate_product_spec(eligible[:CONFIG['top_candidates_for_ai']])
    if not spec.get('title') or not spec.get('deliverables'): raise RuntimeError('Incomplete product specification')
    product_dir=build_product(spec,str(ROOT/'dist'))
    history=load_json(str(ROOT/'state'/'history.json'),[])
    history.append({'title':spec['title'],'price_usd':spec.get('price_usd'),'source_score':eligible[0]['opportunity_score'],'product_dir':str(product_dir.relative_to(ROOT))})
    save_json(str(ROOT/'state'/'history.json'),history[-100:])
    site=ROOT/'site'; site.mkdir(exist_ok=True)
    (site/'latest.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(spec,ensure_ascii=False,indent=2))

if __name__=='__main__': run()