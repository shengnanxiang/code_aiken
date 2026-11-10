# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image
import os

d = r'C:\Users\Nan\Documents\GitHub\code_aiken\bromo\design'
for view in ['FRONT', 'BACK', 'TOP', 'BOTTOM', 'LEFT', 'RIGHT']:
    png = os.path.join(d, f'Bromo-{view}.png')
    svg = os.path.join(d, f'Bromo-{view}.svg')
    img = Image.open(png).convert('L')
    w, h = img.size
    # 统计暗像素（<128）占比，确认有真实线稿内容
    hist = img.histogram()
    dark = sum(hist[:128])
    total = w * h
    print(f'{view}: PNG {w}x{h}px, {os.path.getsize(png)//1024}KB, 暗像素占比 {dark/total*100:.2f}%, SVG {os.path.getsize(svg)//1024}KB')
