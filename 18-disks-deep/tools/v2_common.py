from __future__ import annotations
import csv, gzip, hashlib, io, json, os, shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path

LANES={
 'd12': {'model':'dodecagon','seed':'centered','L':2,'face':1,'va':'E','vb':'N'},
 '24A': {'model':'24gon','seed':'lattice','L':2,'sites':'0,1','velocities':'E,S'},
 '24B': {'model':'24gon','seed':'lattice','L':2,'sites':'0,1','velocities':'W,N'},
}

def atomic_text(path:Path, text:str):
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_name('.'+path.name+'.next'); tmp.write_text(text,encoding='utf-8'); os.replace(tmp,path)
def atomic_json(path:Path,obj): atomic_text(path,json.dumps(obj,indent=2,sort_keys=True)+'\n')
def read_json(path:Path): return json.loads(path.read_text(encoding='utf-8'))
def sha256(path:Path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def block_info(path:Path):
 with tarfile.open(path,'r:gz') as tf:
  names=[n for n in tf.getnames() if n.endswith('/BLOCK.json')]
  if len(names)!=1: raise RuntimeError(f'bad block archive {path}')
  return json.load(tf.extractfile(names[0]))
def extract_end_state(path:Path,out:Path):
 with tarfile.open(path,'r:gz') as tf:
  names=[n for n in tf.getnames() if n.endswith('/end_state.json')]
  if len(names)!=1: raise RuntimeError(f'bad block archive {path}')
  data=tf.extractfile(names[0]).read()
 atomic_text(out,data.decode())
def blocks(root:Path,lane:str):
 d=root/'blocks'/lane
 vals=[]
 if d.exists():
  for p in sorted(d.glob('*.block.tar.gz')):
   try: vals.append((block_info(p),p))
   except Exception: pass
 return sorted(vals,key=lambda x:int(x[0]['start']['step']))
def contiguous_frontier(root:Path,lane:str):
 vals=blocks(root,lane); prev=0; accepted=[]
 for meta,p in vals:
  if int(meta['start']['step'])!=prev: break
  prev=int(meta['end']['step']); accepted.append((meta,p))
 return prev,accepted
