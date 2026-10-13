from pathlib import Path
import json,re
w=Path('work');p=json.loads((w/'atlas-final.json').read_text(encoding='utf-8'))
terms=dict(l.split('=',1) for l in (w/'korean_terms.txt').read_text(encoding='utf-8').splitlines() if '=' in l)
phrases=dict(l.split('=',1) for l in (w/'korean_phrases.txt').read_text(encoding='utf-8').splitlines() if '=' in l)
phrasekeys=sorted(phrases,key=len,reverse=True);pat=re.compile(r'(?<![a-z])('+ '|'.join(re.escape(k) for k in phrasekeys)+r')(?![a-z])')
missing=set()
def trans(n):
 n=n.lower().strip()
 if n in phrases:return phrases[n]
 if ' of ' in n:
  a,b=n.split(' of ',1);return trans(b)+'의 '+trans(a)
 prefix=''
 if n.startswith(('right ','left ')):
  a,n=n.split(' ',1);prefix=terms[a]+' '
 placeholders={}
 def ph(m):
  key='§'+str(len(placeholders))+'§';placeholders[key]=phrases[m.group()];return key
 n=pat.sub(ph,n)
 def word(m):
  x=m.group();
  if x not in terms:missing.add(x)
  return terms.get(x,x)
 n=re.sub('[a-z]+',word,n)
 for a,b in placeholders.items():n=n.replace(a,b)
 n=n.replace(' ','').replace('근근','근').replace('뼈뼈','뼈').replace('연골연골','연골').replace('샘샘','샘')
 return prefix+n
p['namesKo']={d['name']:trans(d['name']) for d in p['catalog']}
assert not missing,missing
assert len(p['namesKo'])==len({d['name'] for d in p['catalog']})
for name,ko in p['namesKo'].items():assert re.search('[가-힣]',ko),(name,ko)
p['translationNote']='한국어는 용어 사전과 구성 규칙에 따른 탐색용 번역입니다. 영어 원명을 함께 제공합니다.'
(w/'atlas-final.json').write_text(json.dumps(p,separators=(',',':'),ensure_ascii=False),encoding='utf-8')
report={'catalog_entries':len(p['catalog']),'bilingual_names':len(p['namesKo']),'missing_terms':sorted(missing),'examples':{n:p['namesKo'][n] for n in ['heart','right kidney','left common carotid artery','right biceps brachii','brain'] if n in p['namesKo']}}
Path('outputs/anatomy/dist/bilingual-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))

