# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
import pymupdf, os

doc = pymupdf.open(r'C:\Users\Nan\Documents\GitHub\code_aiken\bromo\mf-2\ID ref\Jiyin-261104-6-views-open.pdf')
print('pages:', len(doc))

outdir = r'C:\Users\Nan\Documents\GitHub\code_aiken\bromo\design\_ref_render'
os.makedirs(outdir, exist_ok=True)
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=100)
    out = os.path.join(outdir, f'page{i+1}.png')
    pix.save(out)
    print('saved', out, pix.width, 'x', pix.height, os.path.getsize(out), 'bytes')

print('done')
