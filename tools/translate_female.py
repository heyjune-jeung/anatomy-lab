from pathlib import Path
import json
# Reuse the same curated compositional translation rules as the male atlas.
code=Path('work/add_korean.py').read_text(encoding='utf-8');code=code[:code.index("p['namesKo']")];code=code.replace("terms=dict(","terms=dict(",1)
ns={};exec(code,ns)
for fn,key in [('female_korean_terms.txt','terms'),('female_korean_phrases.txt','phrases')]:ns[key].update(dict(l.split('=',1) for l in Path('work/'+fn).read_text(encoding='utf-8').splitlines() if '=' in l))
import re
ns['phrasekeys']=sorted(ns['phrases'],key=len,reverse=True);ns['pat']=re.compile(r'(?<![a-z])('+'|'.join(re.escape(k) for k in ns['phrasekeys'])+r')(?![a-z])')
p=json.loads(Path('work/female-final.json').read_text(encoding='utf-8'));p['namesKo']={d['name']:ns['trans'](d['name']) for d in p['catalog']};assert not ns['missing'],ns['missing']
p['coverageNote']='여성 원본의 전체 964개 모형을 포함합니다. 남성 데이터와 세부 모델링 범위가 다르며, 원본에 없는 두개골·갈비뼈·팔뼈 등은 표시되지 않습니다.'
p['translationNote']='한국어는 용어 사전과 구성 규칙에 따른 탐색용 번역입니다. 영어 원명을 함께 제공합니다.'
Path('work/female-final.json').write_text(json.dumps(p,separators=(',',':'),ensure_ascii=False),encoding='utf-8');print('Translated female catalog:',len(p['catalog']))

