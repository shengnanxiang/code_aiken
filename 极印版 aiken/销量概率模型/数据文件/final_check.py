# -*- coding: utf-8 -*-
import json
with open(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\_finance_261027.json", encoding="utf-8") as f:
    d = json.load(f)
out = []
out.append("=== 分位表 sheet（内嵌版） ===")
for r in d.get("分位表", []):
    cells = [str(v)[:32] for v in r if v is not None and str(v).strip()]
    if cells:
        out.append(" | ".join(cells))
out.append("=== 财务读数 sheet ===")
for r in d.get("财务读数", []):
    cells = [str(v)[:36] for v in r if v is not None and str(v).strip()]
    if cells:
        out.append(" | ".join(cells))
out.append("=== Scenarios sheet ===")
for r in d.get("Scenarios", []):
    cells = [str(v)[:32] for v in r if v is not None and str(v).strip()]
    if cells:
        out.append(" | ".join(cells))
with open(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\_final_check.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("rows:", len(out))
