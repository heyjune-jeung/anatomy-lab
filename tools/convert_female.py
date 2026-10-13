from pathlib import Path
from collections import Counter
import json,struct,gzip,base64,re
import numpy as np

def read_glb(path):
 b=Path(path).read_bytes();assert b[:4]==b'glTF' and struct.unpack_from('<I',b,8)[0]==len(b);ln=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+ln]);pos=20+ln;bn,typ=struct.unpack_from('<II',b,pos);assert typ==0x004e4942;return j,memoryview(b)[pos+8:pos+8+bn]
def accessor(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];k={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);dt=np.dtype(dtype);stride=v.get('byteStride',dt.itemsize*k);return np.ndarray((a['count'],k),dtype=dt,buffer=b,offset=offset,strides=(stride,dt.itemsize)).copy()
def local(n):
 if 'matrix' in n:return np.array(n['matrix']).reshape(4,4).T
 r=np.eye(4);x,y,z,w=n.get('rotation',[0,0,0,1]);r[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]);r[:3,:3]=r[:3,:3]@np.diag(n.get('scale',[1,1,1]));r[:3,3]=n.get('translation',[0,0,0]);return r
def world_matrices(j):
 result={};paths={}
 def visit(i,parent,path):
  n=j['nodes'][i];m=parent@local(n);result[i]=m;paths[i]=path+[n['name']]
  for child in n.get('children',[]):visit(child,m,paths[i])
 for i in j['scenes'][j.get('scene',0)]['nodes']:visit(i,np.eye(4),[])
 return result,paths
fix={'jejenum':'jejunum','fibria':'fimbriae','eigth':'eighth','ucinate':'uncinate','heptopancreatic':'hepatopancreatic','hepataduodenal':'hepatoduodenal','ginviva':'gingiva','opthalmic':'ophthalmic','segmennt':'segment','epiglotic':'epiglottic','heschls':'heschl','schlemms':'schlemm','fugt':'fusiform gyrus','HTH':'hypothalamus'}
def name(raw):
 s=re.sub(r'^(VH_F_|Allen_)','',raw);side=None
 if s.endswith(('_L','_R')):side='left' if s[-1]=='L' else 'right';s=s[:-2]
 s=s.replace('_',' ').lower();s=re.sub(r'\bhth\b','hypothalamus',s)
 for a,b in fix.items():s=re.sub(r'\b'+a.lower()+r'\b',b.lower(),s)
 if s=='vh f':s='female human body'
 if side and not re.search(r'\b(left|right)\b',s):s=side+' '+s
 return s
systems=['골격·연골','근육·힘줄','동맥','정맥','신경계','소화계','호흡계','비뇨계','생식계','림프계','피부·감각','기타 구조','내분비계','심장 구조']
def category(raw,path):
 s=raw.lower();pth=' '.join(path).lower()
 if 'artery' in s or 'aorta' in s:return 2
 if 'vein' in s or 'vena' in s:return 3
 if any(k in s for k in ['thyroid','pituitary','adrenal','pineal']):return 12
 if 'integumentary_system' in pth:return 10
 if 'nervous_system' in pth:return 4
 if 'muscular_system' in pth:return 1
 if 'reproductive_system' in pth:return 8
 if 'digestive_system' in pth:return 5
 if 'urinary_system' in pth:return 7
 if 'circulatory_system' in pth:return 13
 if 'respiratory_system' in pth:return 6
 if 'lymphatic_system' in pth:return 9
 if 'skeletal_system' in pth or 'lower_limb' in pth:return 0
 return 11
j,b=read_glb('work/female-v110.glb');world,paths=world_matrices(j);old,ob=read_glb('work/female.glb');ow,op=world_matrices(old)
packed=bytearray();meshes=[];node_meshes={};mn=np.full(3,np.inf);mx=np.full(3,-np.inf);max_error=0;triangles=0
def add_mesh(n,i,src,binbuf,matrix,path,prefix):
 global packed,mn,mx,max_error,triangles
 verts=[];indices=[];count=0
 for primitive in src['meshes'][n['mesh']]['primitives']:
  assert primitive.get('mode',4)==4;v=accessor(src,binbuf,primitive['attributes']['POSITION']);ix=accessor(src,binbuf,primitive['indices']).ravel().astype(np.uint32);assert ix.max()<len(v)
  verts.append(v);indices.append(ix+count);count+=len(v)
 v=np.concatenate(verts).astype(np.float64);ix=np.concatenate(indices);v=v@matrix[:3,:3].T+matrix[:3,3]
 v=v[:,[0,2,1]]*np.array([1000,-1000,1000]);v=v.astype('<f4')
 # Weld exactly coincident positions; every source triangle is retained.
 unique,reverse=np.unique(v,axis=0,return_inverse=True);ix=reverse[ix].astype(np.uint32);v=unique
 lo=v.min(0);span=v.max(0)-lo;q=np.rint((v-lo)/np.where(span>0,span,1)*65535).astype('<u2');err=np.max(np.abs(q.astype(np.float64)/65535*span+lo-v));max_error=max(max_error,float(err))
 while len(packed)%4:packed.append(0)
 vo=len(packed);packed.extend(q.tobytes())
 while len(packed)%4:packed.append(0)
 io=len(packed);dt='<u2' if len(v)<65536 else '<u4';packed.extend(ix.astype(dt).tobytes());mid=prefix+str(i);nm=name(n['name']);cat=category(n['name'],path)
 m={'id':mid,'name':nm,'fma':'HRA_'+prefix+str(i),'category':cat,'vo':vo,'vc':v.size,'io':io,'ic':len(ix),'indexBytes':2 if dt=='<u2' else 4,'min':lo.tolist(),'span':span.tolist(),'center':(lo+span/2).tolist(),'size':span.tolist(),'sourceNode':n['name']};meshes.append(m);mn=np.minimum(mn,lo);mx=np.maximum(mx,lo+span);triangles+=len(ix)//3;return mid
for i,n in enumerate(j['nodes']):
 if 'mesh' in n:node_meshes[i]=[add_mesh(n,i,j,b,world[i],paths[i],'F110_')]
 if i%150==0:print('Converted nodes',i,flush=True)
def descendants(i):
 if i in node_meshes:return node_meshes[i]
 result=[]
 for ch in j['nodes'][i].get('children',[]):result+=descendants(ch)
 node_meshes[i]=result;return result
catalog=[]
for i,n in enumerate(j['nodes']):
 ms=descendants(i)
 if ms:catalog.append({'id':'HRA_F110_'+str(i),'name':name(n['name']),'category':category(n['name'],paths[i]),'meshes':ms,'sourceNode':n['name']})
supplement=[]
for i,n in enumerate(old['nodes']):
 if 'mesh' in n and ('_ischium_' in n['name'] or '_pubis_' in n['name']):
  mid=add_mesh(n,i,old,ob,ow[i],op[i],'F15_');supplement.append(mid);catalog.append({'id':'HRA_F15_'+str(i),'name':name(n['name']),'category':0,'meshes':[mid],'sourceNode':n['name']})
  for d in catalog:
   if d['sourceNode'] in ['VH_F','VH_F_skeletal_system','VH_F_pelvic_girdle']:d['meshes'].append(mid)
assert len(supplement)==8
# Restore convenient compound selections for the supplemented bones.
for side in ['left','right']:
 for bone in ['pubis','ischium']:
  ms=[m['id'] for m in meshes if side in m['name'] and bone in m['name']]
  catalog.append({'id':'HRA_group_'+side+'_'+bone,'name':side+' '+bone,'category':0,'meshes':ms})
data={'meshes':meshes,'catalog':catalog,'systems':systems,'bounds':[mn.tolist(),mx.tolist()],'source':'Human Reference Atlas / Visible Human Female v1.10 (+ 8 pelvic meshes from v1.5)','binary':base64.b64encode(gzip.compress(packed,6)).decode(),'quantized':True,'sex':'female','coordinateUnit':'mm','license':'CC BY 4.0','sourceUrl':'https://humanatlas.io/3d-reference-library'}
Path('work/female-final.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8');report={'source_meshes':len(j['meshes']),'included_meshes':len(meshes),'supplemented_pelvic_meshes':len(supplement),'named_structures':len(catalog),'triangles':triangles,'max_coordinate_quantization_error_mm':max_error,'bounds':data['bounds'],'systems':dict(Counter(systems[m['category']] for m in meshes))};Path('outputs/anatomy/dist/female-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)

