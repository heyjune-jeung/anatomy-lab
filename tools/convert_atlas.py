from pathlib import Path
from collections import defaultdict, Counter
import json, zipfile, struct, gzip, base64, re, math

w=Path('work'); out=Path('outputs/anatomy/dist');
names={}; reps={}
for line in (w/'names.txt').read_text(encoding='utf-8-sig').splitlines()[1:]:
    f=line.split('\t')
    if len(f)>=3:names[f[0]]=f[2]; reps[f[0]]=f[1]
elements=defaultdict(list)
for line in (w/'elements.txt').read_text(encoding='utf-8-sig').splitlines()[1:]:
    f=line.split('\t')
    if len(f)>=3:elements[f[0]].append(f[2]); names.setdefault(f[0],f[1])
parents=defaultdict(list)
for line in (w/'relations.txt').read_text(encoding='utf-8-sig').splitlines()[1:]:
    f=line.split('\t')
    if len(f)>=4:parents[f[2]].append(f[0]);names.setdefault(f[0],f[1]);names.setdefault(f[2],f[3])
systems=['골격·연골','근육·힘줄','동맥','정맥','신경계','소화계','호흡계','비뇨계','생식계','림프계','피부·감각','기타 구조']
def classify(n):
    n=n.lower()
    if any(x in n for x in ['artery','aorta','arterial']):return 2
    if any(x in n for x in ['vein','vena','venous','sinus of dura']):return 3
    if any(x in n for x in ['nerve','ganglion','brain','cerebr','spinal cord','thalam','medulla','pons','tract','caudate','putamen','pallid','ventricle of brain']):return 4
    if any(x in n for x in ['lymph','spleen','thymus']):return 9
    if any(x in n for x in ['kidney','renal','ureter','bladder','urethra']):return 7
    if any(x in n for x in ['testis','testes','prostat','penis','scrot','seminal','epidid','deferens','ovary','uter','vagina']):return 8
    if any(x in n for x in ['lung','bronch','trache','laryn','nasal','nose','pulmonary alveol']):return 6
    if any(x in n for x in ['stomach','intestin','colon','duoden','jejun','ileum','liver','hepatic lob','gallbladder','bile','pancrea','esophag','rectum','anal','appendix','tongue','saliv','pharynx','tooth','teeth','gingiv']):return 5
    if any(x in n for x in ['muscle','tendon','aponeuro','fascia']):return 1
    if any(x in n for x in ['skin','eye','retina','lens','cornea','iris','ear','cochlea','vestibul']):return 10
    if any(x in n for x in ['bone','cartilage','vertebra','rib','sternum','femur','tibia','fibula','humerus','radius','ulna','scapula','clavicle','pelvis','sacrum','coccy','phalan','phalanges','carpal','tarsal','patella','mandible','maxilla','skull','cranium','ligament','joint','menisc','calcane','talus','metacarp','metatars']):return 0
    return 11
def category(fid):
    c=classify(names.get(fid,''))
    if c!=11:return c
    todo=list(parents[fid]);seen={fid}
    for _ in range(25):
        nxt=[]
        for p in todo:
            if p in seen:continue
            seen.add(p);c=classify(names.get(p,''))
            if c!=11:return c
            nxt.extend(parents[p])
        todo=nxt
    return 11
z=zipfile.ZipFile(w/'bodyparts.zip'); files={Path(n).stem:n for n in z.namelist() if n.lower().endswith('.obj')}
physical=sorted({f for fs in elements.values() for f in fs if f in files})
print('Archive meshes:',len(files),'Physical meshes:',len(physical),flush=True)
owners=defaultdict(list)
for fid,fs in elements.items():
    for f in fs:owners[f].append(fid)
blob=bytearray();meshes=[];allmin=[float('inf')]*3;allmax=[float('-inf')]*3
for k,f in enumerate(physical):
    verts=[];idx=[]
    for line in z.read(files[f]).decode('utf-8').splitlines():
        if line.startswith('v '):verts.extend(float(v) for v in line.split()[1:4])
        elif line.startswith('f '):
            face=[int(v.split('/')[0])-1 for v in line.split()[1:]]
            for j in range(1,len(face)-1):idx.extend((face[0],face[j],face[j+1]))
    if not verts or not idx:continue
    if min(idx)<0 or max(idx)>=len(verts)//3:raise ValueError('invalid indices '+f)
    vo=len(blob);blob.extend(struct.pack('<%sf'%len(verts),*verts));io=len(blob);blob.extend(struct.pack('<%sI'%len(idx),*idx))
    lo=[min(verts[a::3]) for a in range(3)];hi=[max(verts[a::3]) for a in range(3)]
    for a in range(3):allmin[a]=min(allmin[a],lo[a]);allmax[a]=max(allmax[a],hi[a])
    own=min(owners[f],key=lambda x:len(elements[x])); n=names[own];cat=category(own)
    meshes.append({'id':f,'name':n,'fma':own,'category':cat,'vo':vo,'vc':len(verts),'io':io,'ic':len(idx),'center':[(lo[a]+hi[a])/2 for a in range(3)],'size':[hi[a]-lo[a] for a in range(3)]})
    if k%200==0:print(k,len(blob),flush=True)
available={m['id'] for m in meshes}
catalog=[{'id':fid,'name':names[fid],'category':category(fid),'meshes':sorted(set(f for f in fs if f in available))} for fid,fs in elements.items() if any(f in available for f in fs)]
payload={'meshes':meshes,'catalog':catalog,'systems':systems,'bounds':[allmin,allmax],'source':'BodyParts3D 4.0, 99% polygon reduction','binary':base64.b64encode(gzip.compress(blob,compresslevel=6)).decode()}
(w/'atlas-data.json').write_text(json.dumps(payload,separators=(',',':')),encoding='utf-8')
report={'physical_meshes':len(meshes),'named_structures':len(catalog),'triangles':sum(m['ic']//3 for m in meshes),'bounds':payload['bounds'],'systems':dict(Counter(systems[m['category']] for m in meshes)),'missing_element_files':sorted({f for fs in elements.values() for f in fs}-set(files)),'invalid_meshes':0}
(out/'atlas-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(report,ensure_ascii=False),flush=True)

