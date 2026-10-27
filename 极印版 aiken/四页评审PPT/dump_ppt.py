# -*- coding: utf-8 -*-
"""读取用户修改后的 PPT，导出 slide 2-6 全部文本"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pptx import Presentation

PATH = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\AiKen_JY_SI^L0DO_261027.pptx"
OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\四页评审PPT\_ppt_slides_dump.txt"

p = Presentation(PATH)
lines = [f"total slides: {len(p.slides)}", ""]

def walk_shapes(shapes, depth=0):
    out = []
    for shape in shapes:
        if shape.shape_type == 6:  # group
            out += walk_shapes(shape.shapes, depth + 1)
            continue
        if shape.has_text_frame:
            txt = shape.text_frame.text.strip()
            if txt:
                out.append(("  " * depth) + txt)
        if shape.has_table:
            for row in shape.table.rows:
                cells = [c.text.strip() for c in row.cells]
                out.append(("  " * depth) + " | ".join(cells))
    return out

for i, s in enumerate(p.slides, 1):
    lines.append(f"{'='*60}")
    lines.append(f"SLIDE {i}")
    lines.append(f"{'='*60}")
    for t in walk_shapes(s.shapes):
        lines.append(t)
    lines.append("")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"written: {OUT}")
