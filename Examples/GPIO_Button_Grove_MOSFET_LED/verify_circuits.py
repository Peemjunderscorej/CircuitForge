import json
from pathlib import Path
from collections import defaultdict
p=Path(__file__).parent/'outputs'
doc=json.loads((p/'GPIO_Button_Grove_MOSFET_LED_R1_1.json').read_text())
expected=[[
 {'J1.1','R1.2','R2.1'}, {'J1.2','R1.1'}, {'J1.3','J2.2','SW1.3','C1.2'}, {'J2.1','R2.2','SW1.1','C1.1'}
],[
 {'J3.1','R3.2','R4.1'}, {'J3.2','Q1.1','R6.1'}, {'J3.3','C3.1','R3.1','D1.2'}, {'J3.4','C3.2','C2.2','SW2.3','R6.2','Q1.2'}, {'R4.2','SW2.1','C2.1'}, {'D1.1','R5.1'}, {'R5.2','Q1.3'}
]]
report=[]
for i,sheet in enumerate(doc['schematics']):
 s=json.loads(sheet['dataStr'])['shape']; pins={}; labels={}; edges=[]
 for shape in s:
  a=shape.split('~')
  if a[0]=='W':
   v=list(map(float,a[1].split())); pts=list(zip(v[::2],v[1::2]));edges+=list(zip(pts,pts[1:]))
  elif a[0]=='N':labels[(float(a[1]),float(a[2]))]=a[5]
  elif a[0]=='LIB':
   sub=shape.split('#@$')[1:];ref=next(t.split('~')[12] for t in sub if t.startswith('T~P~'))
   for t in sub:
    if t.startswith('P~'):
     b=t.split('^^');conf=b[0].split('~');pins[ref+'.'+conf[3]]=tuple(map(float,b[1].split('~')))
 points=set(pins.values())|set(labels)|{p for e in edges for p in e};parent={p:p for p in points}
 def root(p):
  while parent[p]!=p:p=parent[p]
  return p
 def join(a,b):parent[root(a)]=root(b)
 for a,b in edges:
  for v in points:
   if (a[0]==b[0]==v[0] and min(a[1],b[1])<=v[1]<=max(a[1],b[1])) or (a[1]==b[1]==v[1] and min(a[0],b[0])<=v[0]<=max(a[0],b[0])):join(a,v)
 named={}
 for xy,n in labels.items():
  if n in named:join(xy,named[n])
  else:named[n]=xy
 actual=defaultdict(set)
 for pin,xy in pins.items():actual[root(xy)].add(pin)
 assert {frozenset(v) for v in actual.values()}=={frozenset(v) for v in expected[i]},(sheet['title'],actual)
 report.append(sheet['title']+': PASS - all component pin nets match design; no dangling component pins.')
 for k,v in actual.items():report.append('  '+next((n for xy,n in labels.items() if root(xy)==k),'internal')+': '+', '.join(sorted(v)))
report+=['','Checks performed on the editable EasyEDA source, before import.','Button: idle 3.3 V, pressed 3.3*1K/(10K+1K) = 0.30 V (logic LOW); pull-up current 0.30 mA.','Button RC: release (10K + 1K)*0.1uF = 1.1 ms; press 1K*0.1uF = 0.1 ms.','LED current approximately (3.3 - 2.0)/4K7 = 0.28 mA, neglecting the small MOSFET drop.','Not hardware-tested. Footprints are assigned in EasyEDA Pro only (see Footprints.txt), not in this source.']
(p/'Connectivity_Check.txt').write_text('\n'.join(report))
print('\n'.join(report))
