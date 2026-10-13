from pathlib import Path
import json,re

pairs={}
for line in Path('work/medical_name_pairs.txt').read_text(encoding='utf-8').splitlines():
 if '=' in line and not line.startswith('#'):
  new,clinical=line.split('=',1);pairs[new]=clinical
keys=sorted(pairs,key=len,reverse=True)
pattern=re.compile('|'.join(map(re.escape,keys)))
def clinical_name(text):
 return pattern.sub(lambda m:pairs[m.group()],text)
report={}
for filename in ['atlas-final.json','female-final.json']:
 path=Path('work')/filename;data=json.loads(path.read_text(encoding='utf-8'))
 original=data.get('namesKoAnatomical',data['namesKo']).copy();
 for en,old in list(original.items()):
  if 'thyroid cartilage' in en:original[en]=old.replace('갑상샘연골','방패연골')
  if 'thyroid artery' in en:original[en]=old.replace('갑상샘동맥','갑상동맥')
 data['namesKoAnatomical']=original.copy();labels={};aliases={};changed=0
 for en,full in original.items():
  primary=re.sub(r'\([^)]*\)','',full).strip();alternatives=re.findall(r'\(([^)]*)\)',full)
  # Keep an explicitly supplied modern synonym as the anatomical form.
  modern=primary
  if len(alternatives)==1 and primary in pairs.values() and alternatives[0] in pairs:modern=alternatives[0]
  clinical=clinical_name(modern);clinical=re.sub(r'^오른쪽\s*','우측 ',clinical);clinical=re.sub(r'^왼쪽\s*','좌측 ',clinical)
  label=clinical if clinical==modern else clinical+' ('+modern+')'
  labels[en]=label;aliases[en]=list(dict.fromkeys([clinical,modern,full,primary,*alternatives]))
  if clinical!=modern:changed+=1
 data['namesKo']=labels;data['namesKoAliases']=aliases
 if not any(d['name'] in ['thyroid gland','thyroid'] for d in data['catalog']):data['missingStructureHints']=[{'aliases':['갑상선','갑상샘','thyroid','thyroid gland'],'message':'이 원본에는 갑상선의 3D 모형이 없습니다. 갑상연골은 갑상선과 별개 구조입니다.'}]
 data['translationNote']='주요 구조는 임상·기존 용어와 해부학 용어를 함께 제공합니다. 세부 조합 명칭은 영문 원명과 대조가 필요하며, 전체 용어집 표준 검증을 완료한 것은 아닙니다.'
 path.write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False),encoding='utf-8')
 report[filename]={'names':len(labels),'paired_labels':changed}
Path('outputs/anatomy/dist/medical-terms-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report))

