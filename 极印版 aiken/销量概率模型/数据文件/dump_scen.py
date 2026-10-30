# -*- coding: utf-8 -*-
import json
with open(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\_finance_261027.json", encoding="utf-8") as f:
    d = json.load(f)
out = []
for name in ["Normal Secnario", "Best Secnario", "Worst Secnario"]:
    out.append(f"=== {name} ===")
    for r in d[name]:
        cells = [str(v)[:44] for v in r if v is not None and str(v).strip()]
        if not cells: continue
        line = " | ".join(cells)
        if any(k in line for k in ["模具","治具","研发NRE","测试","认证","汇总","Volumn","Revenue","GM%","Profit","ROI","Investment","CPU","毛利率","零售价","第一年销量"]):
            out.append(line)
with open(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\_scen_dump.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("rows:", len(out))
