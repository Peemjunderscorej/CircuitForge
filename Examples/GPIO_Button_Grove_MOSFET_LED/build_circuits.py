import json, uuid, zipfile
from pathlib import Path

OUT=Path(__file__).parent/'outputs'; OUT.mkdir(exist_ok=True)
counter=0
def uid():
 global counter
 counter+=1; return 'gge'+str(counter)
def text(x,y,s,size=10,mark='L',color='#000080'):
 return f'T~{mark}~{x}~{y}~0~{color}~Arial~{size}pt~~~~comment~{s}~1~start~{uid()}~0~'
def line(points,color='#A00000',kind='PL'):
 return f'{kind}~'+ ' '.join(str(v) for p in points for v in p)+f'~{color}~1~0~none~{uid()}~0'
def pin(n,x,y,ex,ey,name=None,show=False):
 rot=180 if ex>x else 0 if ex<x else 90 if ey>y else 270
 return f'P~show~0~{n}~{x}~{y}~{rot}~{uid()}~0^^{x}~{y}^^M {x} {y} L {ex} {ey}~#880000^^{int(show)}~{ex-5}~{ey+3}~0~{name or n}~end~Arial~8pt~#000080^^{int(show)}~{(x+ex)/2}~{(y+ey)/2-3}~0~{n}~start~Arial~7pt~#000080^^0~{ex}~{ey}^^0~M {ex} {ey}'
def comp(ref,val,x,y,parts,package='',tx=None,ty=None):
 tx=x+18 if tx is None else tx; ty=y-5 if ty is None else ty
 params=f'package`{package}`nameAlias`Value`spicePre`{ref.rstrip("0123456789")}`spiceSymbolName`{val}`'
 return f'LIB~{x}~{y}~{params}~0~0~{uid()}~~{uuid.uuid4().hex}~0~~yes~yes#@$'+'#@$'.join([text(tx,ty,ref,9,'P'),text(tx,ty+14,val,9,'N')]+parts)
def resistor(ref,val,x,y,h=False):
 if h:
  p=[pin(1,x-30,y,x-15,y),pin(2,x+30,y,x+15,y),line([(x-15,y),(x-12,y-5),(x-7,y+5),(x-2,y-5),(x+3,y+5),(x+8,y-5),(x+12,y+5),(x+15,y)])]
  return comp(ref,val,x,y,p,'R0603',x-18,y-28)
 p=[pin(1,x,y-30,x,y-15),pin(2,x,y+30,x,y+15),line([(x,y-15),(x-5,y-12),(x+5,y-7),(x-5,y-2),(x+5,y+3),(x-5,y+8),(x+5,y+12),(x,y+15)])]
 return comp(ref,val,x,y,p,'R0603')
def cap(ref,x,y,val='0.1uF'):
 return comp(ref,val,x,y,[pin(1,x,y-25,x,y-4),pin(2,x,y+25,x,y+4),line([(x-12,y-4),(x+12,y-4)]),line([(x-12,y+4),(x+12,y+4)])],'C0603')
def switch(ref,x,y):
 return comp(ref,'SW_PUSH / SPST',x,y,[pin(1,x,y-25,x,y-12),pin(3,x,y+25,x,y+12),line([(x,y+12),(x-12,y-10)]),line([(x-16,y-4),(x-7,y-4)]),f'E~{x}~{y-12}~2~2~#A00000~1~0~none~{uid()}~0',f'E~{x}~{y+12}~2~2~#A00000~1~0~none~{uid()}~0'],'SW-TH_4P-L6.0-W6.0-P4.50-LS6.1')  # pads 1-2 joined, 3-4 joined: symbol uses pins 1 and 3
def connector(ref,val,x,y,names):
 p=[f'R~{x-105}~{y-20}~~~85~{len(names)*25+15}~#A00000~1~0~none~{uid()}~0~']
 for n,name in enumerate(names,1):p.append(pin(n,x,y+(n-1)*25,x-20,y+(n-1)*25,name,True))
 return comp(ref,val,x,y,p,'',x-105,y-48)
def mosfet(ref,x,y):
 p=[pin(1,x-40,y,x-15,y,'G',True),pin(3,x+10,y-40,x+10,y-17,'D',True),pin(2,x+10,y+40,x+10,y+17,'S',True),line([(x-15,y-17),(x-15,y+17)]),line([(x-9,y-17),(x-9,y-7)]),line([(x-9,y-4),(x-9,y+4)]),line([(x-9,y+7),(x-9,y+17)]),line([(x-9,y-14),(x+10,y-14),(x+10,y-17)]),line([(x-9,y+14),(x+10,y+14),(x+10,y+17)]),line([(x-9,y),(x+10,y),(x+10,y+14)]),line([(x+1,y-4),(x-7,y),(x+1,y+4),(x+1,y-4)])]
 return comp(ref,'BSS138',x,y,p,'SOT-23',x+32,y-8)
def led(ref,x,y):
 p=[pin(2,x,y-25,x,y-8,'A'),pin(1,x,y+25,x,y+8,'K'),line([(x-9,y-8),(x+9,y-8),(x,y+8),(x-9,y-8)]),line([(x-10,y+8),(x+10,y+8)]),line([(x+13,y-6),(x+24,y-17),(x+19,y-16)]),line([(x+20,y+1),(x+31,y-10),(x+26,y-9)])]
 return comp(ref,'RED LED',x,y,p,'LED0603',x+40,y-5)
class Sheet:
 def __init__(self,title,num):
  self.title=title; self.s=[]
  self.s+=[text(60,55,title,18),text(60,80,'3.3 V logic | Editable schematic | Rev 1.1 | 2026-10-04',10),line([(50,95),(1150,95)],'#808080'),text(60,720,f'Sheet {num}/2 - GPIO Button and Grove MOSFET LED',9)]
 def add(self,*s):self.s.extend(s)
 def wire(self,*pts):self.add(line(pts,'#008800','W'))
 def net(self,x,y,name):self.add(f'N~{x}~{y}~0~#0000FF~{name}~{uid()}~start~{x+3}~{y-5}~Arial~9pt~0')
 def dot(self,x,y):self.add(f'J~{x}~{y}~2.5~#008800~{uid()}~0')
 def gnd(self,x,y):
  self.net(x,y,'GND');self.add(line([(x-10,y),(x+10,y)],'#000000'),line([(x-6,y+4),(x+6,y+4)],'#000000'),line([(x-2,y+8),(x+2,y+8)],'#000000'))
 def power(self,x,y):self.net(x,y,'+3V3')
 def data(self):return {'head':{'docType':'1','editorVersion':'6.5.51','newgId':True,'c_para':{'Prefix Start':'1'}},'canvas':'CA~1200~800~#FFFFFF~yes~#CCCCCC~5~1200~800~line~5~pixel~5~0~0','shape':self.s,'BBox':{'x':40,'y':35,'width':1130,'height':710},'colors':{}}

# Rev 1.1: topology and values follow the Cytron Maker Pi RP2040 (sheet 2 PUSH BUTTONS,
# sheet 3 DIGITAL IO STATUS LEDS) and Maker Pi Pico (sheet 2 IO LEDS) reference schematics.
def button(s,x,sig,r_pull,r_ser,sw,c,raw=None):
 # +3V3 - 10K - signal node - 1K - (switch || 0.1uF) - GND, as Maker Pi RP2040 R19/R20/S3/C26
 s.add(resistor(r_pull,'10K',x,190),resistor(r_ser,'1K',x,290),switch(sw,x,385),cap(c,x+150,385))
 s.wire((x,145),(x,160));s.power(x,145)
 s.wire((x,220),(x,240));s.wire((x,240),(x,260));s.wire((x,240),(x+120,240));s.dot(x,240);s.net(x+120,240,sig)
 s.wire((x,320),(x,340));s.wire((x,340),(x,360));s.wire((x,340),(x+150,340));s.wire((x+150,340),(x+150,360));s.dot(x,340)
 if raw:s.net(x+60,340,raw)
 s.wire((x,410),(x,475));s.gnd(x,475);s.wire((x+150,410),(x+150,475));s.gnd(x+150,475)

s1=Sheet('GPIO Push-Button or Switch Input',1)
s1.add(connector('J1','GPIO HEADER (2.54mm)',215,245,['GPIO_IN','3V3','GND']))
for y,net in [(245,'GPIO_IN'),(270,'+3V3'),(295,'GND')]:s1.wire((215,y),(280,y));s1.net(280,y,net)
s1.add(connector('J2','EXTERNAL SWITCH (optional)',250,420,['SW_RAW','GND']))
s1.wire((250,420),(330,420));s1.net(330,420,'SW_RAW');s1.wire((250,445),(330,445));s1.net(330,445,'GND')
button(s1,520,'GPIO_IN','R1','R2','SW1','C1','SW_RAW')
s1.add(text(60,555,'Operation: released / open = HIGH; pressed / closed = LOW.',11),text(60,580,'R1 10K pull-up gives the idle level. R2 1K is in series with the switch; C1 0.1uF is across the switch.',10),text(60,603,'Same network as Maker Pi RP2040 sheet 2 PUSH BUTTONS (R19 10K, R20 1K, S3, C26 0.1uF).',10),text(60,626,'J2 accepts a dry-contact switch in parallel with SW1. Configure the MCU pin as an input.',10),text(60,649,'References: Maker Pi RP2040 sheet 2; Maker Pi Pico sheet 1; ETT ET-ESP32 LAB V1 input switch block.',9),text(60,671,'Added to the reference: J1 header, optional J2. 3.3 V only. SW1 uses switch pins 1 and 3; pads 2 and 4 unmapped - verify 1 and 3 are opposite contacts before wiring.',9))

s2=Sheet('GROVE_4P_Button MOSFET_LED',2)
s2.add(connector('J3','GROVE 4P / 2.0mm keyed',210,205,['BTN_N','LED_CTL','3V3','GND']))
for y,net in [(205,'BTN_N'),(230,'LED_CTL'),(255,'+3V3'),(280,'GND')]:s2.wire((210,y),(285,y));s2.net(285,y,net)
s2.add(cap('C3',190,410));s2.wire((190,355),(190,385));s2.power(190,355);s2.wire((190,435),(190,475));s2.gnd(190,475)
button(s2,470,'BTN_N','R3','R4','SW2','C2')
# +3V3 - LED - 4K7 - BSS138 drain; gate driven directly as Maker Pi DS3/R28/Q6; gate pull-down 100K instead of the reference 3M3 (LED_CTL is a cable signal)
s2.add(led('D1',960,180),resistor('R5','4K7',960,255),mosfet('Q1',950,370),resistor('R6','100K',875,435))
s2.wire((960,135),(960,155));s2.power(960,135);s2.wire((960,205),(960,225));s2.wire((960,285),(960,330));s2.wire((960,410),(960,495));s2.gnd(960,495)
s2.wire((760,370),(875,370));s2.net(760,370,'LED_CTL');s2.wire((875,370),(910,370));s2.wire((875,370),(875,405));s2.dot(875,370);s2.wire((875,465),(875,495));s2.gnd(875,495)
s2.add(text(60,555,'Grove cable: 1 yellow = BTN_N | 2 white = LED_CTL | 3 red = 3.3 V | 4 black = GND',11),text(60,580,'Button is active LOW (pressed = LOW). LED_CTL HIGH lights D1; R6 100K keeps Q1 off while the MCU pin floats.',10),text(60,603,'Q1 BSS138: pin 1 gate, pin 2 source, pin 3 drain. LED current is about (3.3 V - 2.0 V) / 4K7 = 0.28 mA.',10),text(60,626,'C3 0.1uF is the Grove port supply decoupling, as on the Maker Pi Grove ports. 3.3 V supply and signals only.',10),text(60,649,'References: Maker Pi RP2040 sheets 2-3 (buttons, Grove ports, IO status LEDs); Maker Pi Pico sheets 1-2.',9),text(60,671,'Values follow the Cytron references (10K / 1K / 0.1uF button, LED + 4K7 + BSS138) except R6: 100K instead of 3M3.',9),text(60,692,'Grove pin order above is explicit (Cytron symbols number differently). SW2 uses switch pins 1 and 3; pads 2 and 4 unmapped - verify 1 and 3 are opposite contacts before wiring.',9))

NAME='GPIO_Button_Grove_MOSFET_LED_R1_1'
sheets=[s1,s2]
project={'editorVersion':'6.5.51','docType':'5','title':NAME,'description':'Two 3.3 V circuits following the Cytron Maker Pi reference schematics.','colors':{},'schematics':[{'docType':'1','title':s.title.replace(' ','_'),'description':'','dataStr':json.dumps(s.data())} for s in sheets]}
(OUT/(NAME+'.json')).write_text(json.dumps(project,indent=2),encoding='utf8')
with zipfile.ZipFile(OUT/(NAME+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:z.write(OUT/(NAME+'.json'),NAME+'.json')
print('Created EasyEDA editable source:',[(s.title,len(s.s)) for s in sheets])
