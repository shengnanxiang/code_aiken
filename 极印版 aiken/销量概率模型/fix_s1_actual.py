# -*- coding: utf-8 -*-
"""批量更新 S1 实际数据：7,285/7,300 → 10,000（P5以下 → P18）"""
import io, os

BASE = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型"

# 文件 → 替换规则
updates = {
    "Ricotta回测报告.md": [
        ("| **S1**（极印 ¥1799） | 25,000（点预测） | 6,300 | ~7,300 | **模型右尾覆盖了实际 ✓**，内部点预测 P92 过于乐观 |",
         "| **S1**（极印 ¥1799） | 25,000（点预测） | 6,300 | **~10,000** | **模型 P50 更接近实际 ✓**，内部点预测 P92 过于乐观 |"),
        ("| **S1**（极印 ¥1799） | 25,000 | 6,300 | ~7,300 | **模型** ✓ |",
         "| **S1**（极印 ¥1799） | 25,000 | 6,300 | ~10,000 | **模型** ✓ |"),
    ],
    "新品概率模型_PM使用手册.md": [
        ("内部点预测 25,000 台位于事前分布 P92（模型当场就会预警「仅 8% 概率达成」），实际卖了约 7,300 台（P5 以下）。点预测错 3.4 倍，但分布把这两种可能都包含了。",
         "内部点预测 25,000 台位于事前分布 P92（模型当场就会预警「仅 8% 概率达成」），实际卖了约 10,000 台（P18）。点预测高估 2.5 倍；模型 P50=14,500，偏差 45%。分布把这两种可能都包含了。"),
    ],
    "v0.4_结果摘要.md": [
        ("实际宽口径 ~7,285 → **P5 以下**——验证分布悲观。",
         "实际首年 ~10,000 → **P18**——模型 P50=14,512 更接近实际（偏差 45%），内部 25,000 高估 2.5 倍。"),
    ],
}

for fname, rules in updates.items():
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print(f"[skip] {fname} 不存在")
        continue
    src = io.open(path, encoding="utf-8").read()
    changed = 0
    for old, new in rules:
        if old in src:
            src = src.replace(old, new)
            changed += 1
        else:
            print(f"[warn] {fname}: 未找到 「{old[:40]}...」")
    io.open(path, "w", encoding="utf-8").write(src)
    print(f"[done] {fname}: {changed}/{len(rules)} 处替换")

# 评审页 HTML（SVG 内嵌数字 + 文字）
path = os.path.join(BASE, "AiKen销量概率分布_评审页.html")
src = io.open(path, encoding="utf-8").read()
c1 = src.count("7,285") + src.count("7,300")
src = src.replace("实际宽口径 7,285", "实际首年 10,000")
src = src.replace("实际宽口径 ~7,300", "实际首年 ~10,000")
src = src.replace("实际（宽口径 ~7,300）落在 P5 以下，验证悲观", "实际（首年 ~10,000）落在 P18，模型 P50=14,500 更接近实际（偏差 45%）")
src = src.replace("实际（宽口径 ~7,300）落在 P5 以下，验证悲观。偏差根源：N 系（已留育产品类）参数对 S1（需教育品类）系统性高估约 2 倍——这直接决定了 AiKen 锚 S1 而非 N 系，并已转化为 v0.4 参数余量。",
                  "实际（首年 ~10,000）落在 P18——模型 P50=14,512 与实际偏差 45%，显著优于内部点预测（25,000=P92，高估 2.5 倍）。偏差根源：N 系（已留育产品类）参数对 S1（需教育品类）高估约 2 倍——这直接决定了 AiKen 锚 S1 而非 N 系，并已转化为 v0.4 参数余量。")
# SVG 里的标注
src = src.replace("实际宽口径 7,285", "实际首年 10,000")
src = src.replace(">P5 以下<", ">P18<")
c2 = src.count("7,285") + src.count("7,300")
io.open(path, "w", encoding="utf-8").write(src)
print(f"[done] 评审页 HTML: 替换前 {c1} 处旧值，替换后残留 {c2} 处")

print("\n全部更新完成")
