from __future__ import annotations
import json
import os
import re
from typing import Any
import requests

MODEL=os.getenv('GEMINI_MODEL','gemini-3.7-flash')

def extract_json(text:str)->dict[str,Any]:
    text=text.strip()
    if text.startswith('```'):
        lines=text.splitlines()
        if lines and lines[0].startswith('```'): lines=lines[1:]
        if lines and lines[-1].startswith('```'): lines=lines[:-1]
        text='\n'.join(lines)
    return json.loads(text)

def generate_product_spec(signals:list[dict])->dict[str,Any]:
    key=os.getenv('GEMINI_API_KEY')
    if not key: return fallback(signals[0])
    prompt={
      'role':'You are a conservative digital-business product strategist.',
      'rules':['Do not invent evidence of demand.','Treat supplied signals as demand hints only.','Prefer useful, specific, non-generic products.','Avoid copyrighted material, trademarks and copied templates.','Choose a product one person can generate automatically.','Return JSON only.'],
      'schema':{'title':'string','problem':'string','target_customer':'string','product_type':'business_template|calculator|checklist|guide','deliverables':['string'],'price_usd':'number','sales_angle':'string','keywords':['string']},
      'signals':signals
    }
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    r=requests.post(url,params={'key':key},json={'contents':[{'parts':[{'text':json.dumps(prompt,ensure_ascii=False)}]}]},timeout=90)
    r.raise_for_status()
    return extract_json(r.json()['candidates'][0]['content']['parts'][0]['text'])

def fallback(signal:dict)->dict[str,Any]:
    title=(signal.get('title') or 'Practical Workflow Toolkit')[:80]
    return {'title':f'{title} - Practical Toolkit','problem':'A practical workflow problem identified from public demand signals.','target_customer':'People who need a repeatable, simple workflow.','product_type':'checklist','deliverables':['Implementation checklist','Quick-start guide','Tracking sheet'],'price_usd':12,'sales_angle':'Save time with a ready-to-use workflow.','keywords':re.findall(r'[A-Za-z]{4,}',title)[:8]}