import json,html
from pathlib import Path
import pymupdf
p=Path(__file__).parent/'outputs'
doc=json.loads((p/'GPIO_Button_Grove_MOSFET_LED_R1_1.json').read_text())
def tx(x,y,t,sz=12,col='#000080',anchor='start'):
 return f'<text x="{x}" y="{y}" font-size="{sz}" fill="{col}" font-family="Arial" text-anchor="{anchor}">{html.escape(t)}</text>'
def render(s):
 a=s.split('~');k=a[0]
 if k=='LIB':return ''.join(render(t) for t in s.split('#@$')[1:])
 if k in ['W','PL']:return f'<polyline points="{a[1]}" stroke="{a[2]}" stroke-width="1.3" fill="none"/>'
 if k=='T':return tx(a[2],a[3],a[12],float(a[7].replace('pt',''))*1.2,a[5])
 if k=='N':return tx(a[8],a[9],a[5],10.8,a[4])
 if k=='J':return f'<circle cx="{a[1]}" cy="{a[2]}" r="{a[3]}" fill="{a[4]}"/>'
 if k=='R':return f'<rect x="{a[1]}" y="{a[2]}" width="{a[5]}" height="{a[6]}" fill="none" stroke="{a[7]}"/>'
 if k=='E':return f'<ellipse cx="{a[1]}" cy="{a[2]}" rx="{a[3]}" ry="{a[4]}" fill="none" stroke="{a[5]}"/>'
 if k=='P':
  seg=s.split('^^');b=seg[2].split('~');v=f'<path d="{b[0]}" stroke="{b[1]}" fill="none"/>'
  for i in [3,4]:
   b=seg[i].split('~')
   if b[0]=='1':v+=tx(b[1],b[2],b[4],9,b[8],b[5])
  return v
 return ''
for sh in doc['schematics']:
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="750" viewBox="0 0 1200 750"><rect width="1200" height="750" fill="white"/>'+''.join(render(s) for s in json.loads(sh['dataStr'])['shape'])+'</svg>'
 path=p/(sh['title']+'.svg');path.write_text(svg)
 d=pymupdf.open(stream=svg.encode(),filetype='svg');d[0].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(str(p/(sh['title']+'.png')))
print('Rendered both schematic previews')
