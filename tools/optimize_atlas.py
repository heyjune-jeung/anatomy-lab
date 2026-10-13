from pathlib import Path
from collections import defaultdict,Counter
import json,gzip,base64
import numpy as np
p=json.loads(Path('work/atlas-data.json').read_text(encoding='utf-8'));raw=gzip.decompress(base64.b64decode(p['binary']));packed=bytearray();worst=0
for m in p['meshes']:
    v=np.frombuffer(raw,dtype='<f4',count=m['vc'],offset=m['vo']).reshape(-1,3)
    lo=v.min(axis=0);span=v.max(axis=0)-lo
    q=np.rint((v-lo)/np.where(span>0,span,1)*65535).astype('<u2')
    err=np.max(np.abs(q.astype(np.float64)/65535*span+lo-v));worst=max(worst,float(err))
    ix=np.frombuffer(raw,dtype='<u4',count=m['ic'],offset=m['io']);dtype='<u2' if ix.max()<65536 else '<u4'
    while len(packed)%4:packed.append(0)
    m['vo']=len(packed);packed.extend(q.tobytes())
    while len(packed)%4:packed.append(0)
    m['io']=len(packed);packed.extend(ix.astype(dtype).tobytes());m['indexBytes']=2 if dtype=='<u2' else 4;m['min']=lo.tolist();m['span']=span.tolist()
physical={m['id'] for m in p['meshes']};catalog={d['id']:d for d in p['catalog']};extra=defaultdict(list);extra_names={}
for line in Path('work/partof-elements.txt').read_text(encoding='utf-8-sig').splitlines()[1:]:
    f=line.split('\t')
    if len(f)>=3:extra[f[0]].append(f[2]);extra_names[f[0]]=f[1]
missing={m for fs in extra.values() for m in fs}-physical
assert not missing, str(missing)
for fid,ms in extra.items():
    if fid in catalog:catalog[fid]['meshes']=sorted(set(catalog[fid]['meshes']+ms))
    else:
        n=extra_names[fid];existing=[m for m in p['meshes'] if m['id'] in ms];cats=Counter(m['category'] for m in existing);cat=cats.most_common(1)[0][0]
        catalog[fid]={'id':fid,'name':n,'category':cat,'meshes':sorted(set(ms))}
p['systems']+=['내분비계','심장 구조']
for d in catalog.values():
    if any(s in d['name'].lower() for s in ['thyroid','adrenal','pituitary','pineal','parathyroid']):d['category']=12
    if d['name']=='heart' or (d['category']==11 and any(s in d['name'] for s in ['heart','cardiac','atrium','ventricle'])):d['category']=13
for m in p['meshes']:
    d=catalog.get(m['fma'])
    if d:m['category']=d['category']
p['catalog']=list(catalog.values());p['binary']=base64.b64encode(gzip.compress(packed,6)).decode();p['quantized']=True
Path('work/atlas-final.json').write_text(json.dumps(p,separators=(',',':')),encoding='utf-8')
report=json.loads(Path('outputs/anatomy/dist/atlas-validation.json').read_text(encoding='utf-8'));report.update(named_structures=len(catalog),systems=dict(Counter(p['systems'][m['category']] for m in p['meshes'])),max_coordinate_quantization_error_mm=worst,missing_partof_files=list(missing),packed_bytes=len(packed))
Path('outputs/anatomy/dist/atlas-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False),flush=True)

