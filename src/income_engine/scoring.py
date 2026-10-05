from __future__ import annotations
import math
import re

PAIN_WORDS={'problem':8,'how':3,'guide':4,'template':7,'tool':6,'alternative':5,'workflow':6,'automation':8,'excel':8,'checklist':7,'calculator':8,'cost':5,'save':4,'mistake':7,'struggle':8,'need':5,'best':2,'software':4}

def score_signal(item: dict) -> float:
    text=f"{item.get('title','')} {item.get('summary','')}".lower()
    words=re.findall(r'[a-z0-9]+',text)
    pain=min(35,sum(PAIN_WORDS.get(w,0) for w in words))
    length=min(15,max(0,len(words)-5)*1.2)
    source=8 if item.get('source')=='reddit' else 5
    engagement=min(20,math.log1p(float(item.get('score_hint') or 0))*4)
    return round(min(100,20+pain+length+source+engagement),2)

def rank(items:list[dict])->list[dict]:
    out=[]
    for item in items:
        x=dict(item)
        x['opportunity_score']=score_signal(x)
        out.append(x)
    return sorted(out,key=lambda x:x['opportunity_score'],reverse=True)