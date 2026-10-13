from pathlib import Path
import base64,concurrent.futures,gzip,hashlib,json,shutil,subprocess,sys,urllib.request

root=Path.cwd();work=root/'work';site=root/'_site';work.mkdir(exist_ok=True);site.mkdir(exist_ok=True);(root/'outputs/anatomy/dist').mkdir(parents=True,exist_ok=True)
for p in (root/'tools').iterdir():
 if p.suffix in ['.py','.txt']:shutil.copy2(p,work/p.name)
base='https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/'
downloads={'bodyparts.zip':base+'isa_BP3D_4.0_obj_99.zip','names.txt':base+'isa_parts_list_e.txt','elements.txt':base+'isa_element_parts.txt','relations.txt':base+'isa_inclusion_relation_list.txt','partof-elements.txt':base+'partof_element_parts.txt','female.glb':'https://cdn.humanatlas.io/digital-objects/ref-organ/united-female/v1.5/assets/3d-vh-f-united.glb','female-v110.glb':'https://cdn.humanatlas.io/digital-objects/ref-organ/united-female/v1.10/assets/3d-vh-f-united.glb'}
def download(item):
 name,url=item;target=work/name
 if target.exists() and target.stat().st_size>100:return
 print('Downloading',name,flush=True)
 for attempt in range(3):
  try:
   urllib.request.urlretrieve(url,str(target)+'.download');Path(str(target)+'.download').replace(target);return
  except Exception:
   if attempt==2:raise
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(download,downloads.items()))
for script in ['convert_atlas.py','optimize_atlas.py','add_korean.py','convert_female.py','translate_female.py']:
 subprocess.run([sys.executable,str(work/script)],check=True)
for filename in ['index.html','atlas.js','style.css','README.md','LICENSE','.nojekyll']:shutil.copy2(root/filename,site/filename)
(site/'vendor').mkdir(exist_ok=True);(site/'data').mkdir(exist_ok=True)
for filename,url in {'three.module.js':'https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js','LICENSE.txt':'https://cdn.jsdelivr.net/npm/three@0.170.0/LICENSE'}.items():urllib.request.urlretrieve(url,site/'vendor'/filename)
for sex,filename,outname in [('male','atlas-final.json','atlas-data.json'),('female','female-final.json','female-data.json')]:
 data=json.loads((work/filename).read_text(encoding='utf-8'));binary=base64.b64decode(data.pop('binary'));gzip.decompress(binary);chunks=[]
 for i,offset in enumerate(range(0,len(binary),8*1024*1024)):
  name=f'data/{sex}-{i:02d}.bin';(site/name).write_bytes(binary[offset:offset+8*1024*1024]);chunks.append(name)
 data['binaryChunks']=chunks;data['binarySha256']=hashlib.sha256(binary).hexdigest();(site/outname).write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False),encoding='utf-8')
 assert hashlib.sha256(b''.join((site/name).read_bytes() for name in chunks)).hexdigest()==data['binarySha256']
 ids={m['id'] for m in data['meshes']}
 assert all(d['meshes'] and set(d['meshes'])<=ids for d in data['catalog'])
 print(sex,len(data['meshes']),'meshes;',len(data['catalog']),'named structures verified.',flush=True)
print('Site built in _site.',flush=True)

