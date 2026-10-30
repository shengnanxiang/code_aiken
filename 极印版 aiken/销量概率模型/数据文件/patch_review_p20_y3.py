# -*- coding: utf-8 -*-
"""修补 make_review_slide_699.py：三年分布图锚也改为 P20/P50/P90"""
import io

p = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\make_review_slide_699.py"
src = io.open(p, encoding="utf-8").read()

# 三年图：P10 竖线改为 P20·Worst
src = src.replace(
    '''    marks=[(pct(y3,10), "P10", "#C0392B", "4 3"),
           (pct(y3,50), "P50", "#111", "4 3"),
           (pct(y3,90), "P90", "#7A4FA0", "4 3")],''',
    '''    marks=[(pct(y3,20), "P20·Worst", "#C0392B", "4 3"),
           (pct(y3,50), "P50·Normal", "#111", "4 3"),
           (pct(y3,90), "P90·Best", "#7A4FA0", "4 3")],''')

# 三年 nums 行：P10 → P20·Worst
src = src.replace(
    '''      <div class="nums">P10 <b>__Y3_P10__</b> ｜ P50 <b>__Y3_P50__</b> ｜ P90 <b>__Y3_P90__</b></div>''',
    '''      <div class="nums">P20·Worst <b>__Y3_P20__</b> ｜ P50·Normal <b>__Y3_P50__</b> ｜ P90·Best <b>__Y3_P90__</b></div>''')

# 替换段：加 __Y3_P20__
src = src.replace(
    '''    .replace("__Y3_P10__", f"{pct(y3,10)/1e4:.1f}万")''',
    '''    .replace("__Y3_P20__", f"{pct(y3,20)/1e4:.1f}万")
    .replace("__Y3_P10__", f"{pct(y3,10)/1e4:.1f}万")''')

io.open(p, "w", encoding="utf-8").write(src)
print("patched OK (三年 P20)")
