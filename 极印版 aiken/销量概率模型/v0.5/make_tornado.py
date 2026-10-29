# -*- coding: utf-8 -*-
"""生成龙卷风图 HTML（敏感性检验可视化）"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import json

with open(r"C:\Users\Nan\AppData\Local\Temp\tornado_data.json", encoding="utf-8") as f:
    D = json.load(f)

base1, base3 = D["base1"], D["base3"]
rows = D["rows"]  # [label, pess1, opt1, swing1, pess3, opt3, swing3]

def tornado_svg(rows, base, w=760, title_unit="台", ymax=None):
    rows_sorted = sorted(rows, key=lambda r: r[3])  # 按 swing1 升序，最长的在最后（顶部）
    n = len(rows_sorted)
    rh = 34
    label_w = 130
    val_w = 150
    h = n * rh + 70
    ml, mr = label_w, val_w
    x0, x1_ = ml, w - mr
    # x 轴范围
    lo_min = min(r[1] for r in rows_sorted) * 0.96
    hi_max = max(r[2] for r in rows_sorted) * 1.04
    def X(v): return x0 + (v - lo_min) / (hi_max - lo_min) * (x1_ - x0)
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    # 基线竖线
    bx = X(base)
    P.append(f'<line x1="{bx:.1f}" y1="30" x2="{bx:.1f}" y2="{h-36}" stroke="#111" stroke-width="2" stroke-dasharray="6 4"/>')
    P.append(f'<text x="{bx:.1f}" y="22" text-anchor="middle" font-size="10.5" fill="#111" font-weight="bold">基线 P50 = {base:,.0f}{title_unit}</text>')
    # 条形
    for i, (label, pess, opt, swing, *_ ) in enumerate(rows_sorted):
        y = 40 + i * rh
        # 悲观臂（左，红）
        P.append(f'<rect x="{X(pess):.1f}" y="{y:.1f}" width="{X(base)-X(pess):.1f}" height="{rh*0.55:.1f}" fill="#C0392B" fill-opacity="0.75" rx="2"/>')
        # 乐观臂（右，绿）
        P.append(f'<rect x="{X(base):.1f}" y="{y:.1f}" width="{X(opt)-X(base):.1f}" height="{rh*0.55:.1f}" fill="#00A5A5" fill-opacity="0.72" rx="2"/>')
        # 标签
        P.append(f'<text x="{ml-8}" y="{y+rh*0.38:.1f}" text-anchor="end" font-size="11" fill="#111">{label}</text>')
        # 数值标注
        P.append(f'<text x="{X(pess)-4:.1f}" y="{y+rh*0.38:.1f}" text-anchor="end" font-size="9.5" fill="#C0392B">{pess:,.0f}</text>')
        P.append(f'<text x="{X(opt)+4:.1f}" y="{y+rh*0.38:.1f}" font-size="9.5" fill="#007C7C">{opt:,.0f}</text>')
        # 摆幅
        P.append(f'<text x="{w-8}" y="{y+rh*0.38:.1f}" text-anchor="end" font-size="11" fill="#EC008C" font-weight="bold">±20% → {swing:.0f}%</text>')
    # 轴
    P.append(f'<line x1="{x0}" y1="{h-28}" x2="{x1_}" y2="{h-28}" stroke="#111" stroke-width="1.2"/>')
    for v in range(int(lo_min//2000*2000), int(hi_max//2000*2000)+1, 4000):
        P.append(f'<line x1="{X(v):.1f}" y1="{h-28}" x2="{X(v):.1f}" y2="{h-23}" stroke="#111"/>')
        P.append(f'<text x="{X(v):.0f}" y="{h-12}" text-anchor="middle" font-size="9.5" fill="#6B6B6B">{v/10000:.1f}万</text>')
    # 图例
    P.append(f'<rect x="{x1_-150}" y="8" width="14" height="9" fill="#C0392B" fill-opacity="0.75"/>')
    P.append(f'<text x="{x1_-132}" y="16" font-size="9.5" fill="#333">悲观</text>')
    P.append(f'<rect x="{x1_-95}" y="8" width="14" height="9" fill="#00A5A5" fill-opacity="0.72"/>')
    P.append(f'<text x="{x1_-77}" y="16" font-size="9.5" fill="#333">乐观</text>')
    P.append('</svg>')
    return "".join(P)

SVG_1Y = tornado_svg(rows, base1, w=780)
SVG_3Y = tornado_svg([(r[0], r[4], r[5], r[6]) for r in rows], base3, w=780)

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>AiKen 模型 · 敏感性检验（龙卷风图）</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html,body {{ background:#3a3a3a; }}
  body {{ margin:0; }}
  #slide {{ width:1280px; max-width:96vw; margin:24px auto; background:#FFF; font-family:"Microsoft YaHei",sans-serif;
           color:#111; box-shadow:0 8px 40px rgba(0,0,0,.45); }}
  .pad {{ padding:24px 34px 18px; display:flex; flex-direction:column; }}
  .hd {{ display:flex; align-items:flex-end; justify-content:space-between; border-bottom:2.5px solid #111; padding-bottom:8px; }}
  .hd h1 {{ font-size:24px; }}
  .hd h1 em {{ color:#EC008C; font-style:normal; }}
  .hd .tag {{ font-size:11px; color:#fff; background:#111; padding:4px 10px; border-radius:3px; letter-spacing:1px; }}
  .note {{ margin-top:10px; font-size:11.5px; color:#444; background:#F7F7F7; border-radius:6px; padding:8px 14px; line-height:1.6; }}
  .note b {{ color:#111; }}
  .note .mk {{ color:#EC008C; font-weight:bold; }}
  .chartbox {{ margin-top:14px; border:1.5px solid #E6E6E6; border-radius:8px; padding:10px 14px; }}
  .chartbox h3 {{ font-size:15px; margin-bottom:4px; }}
  .chartbox svg {{ width:100%; }}
  .concl {{ margin-top:14px; border:2px solid #111; border-radius:8px; padding:12px 18px; background:#FDF3F8; }}
  .concl h3 {{ font-size:15px; color:#EC008C; margin-bottom:6px; }}
  .concl li {{ font-size:12px; color:#111; line-height:1.75; margin-left:18px; }}
  .concl li b {{ color:#EC008C; }}
  .ft {{ margin-top:12px; border-top:1.5px solid #111; padding-top:8px; font-size:10px; color:#9a9a9a; display:flex; justify-content:space-between; }}
</style>
</head>
<body>
<div id="slide"><div class="pad">

  <div class="hd">
    <h1>AiKen 销量模型 <em>· 敏感性检验（龙卷风图）</em></h1>
    <div class="tag">v0.5 · ¥699 口径</div>
  </div>

  <div class="note">
    方法：<b>每个参数单独 ±20%</b>（其余不动），重跑 8,000 次蒙特卡洛，看首年/三年 P50 的摆动幅度。<b>条越长 = 结论越依赖这个假设 = 越该被挑战或验证</b>。
    漏斗三参数（CVR/预算/CTR）摆幅相同是结构性的——它们以乘积进入销量，弹性等价。
  </div>

  <div class="chartbox">
    <h3>首年销量 P50 的敏感性排序</h3>
    {SVG_1Y}
  </div>

  <div class="chartbox">
    <h3>三年累计 P50 的敏感性排序</h3>
    {SVG_3Y}
  </div>

  <div class="concl">
    <h3>结论 · 模型的最大软肋与防御</h3>
    <li><b>① 首年看漏斗，三年看天花板</b>：首年 P50 对 CVR/预算/CTR 最敏感（各 ±35%）——冷启动期的一切由投放效率决定；三年 P50 对 m 市场潜力最敏感（±19%）——长期由品类空间决定。首年和三年是两套敏感逻辑。</li>
    <li><b>② 最值钱的假设是 CVR</b>：CVR 拨 ±20%，首年 P50 在 1.79万–2.56万 之间摆。而它目前的依据是 S1 实测 0.98%+回测余量——<b>上市前最值得花钱搞清楚的一件事就是 AiKen 自己的落地页转化率</b>（概念测试页 A/B 版就是干这个的）。</li>
    <li><b>③ q 口碑系数意外地不敏感</b>（首年 ±3%）：因为口碑起飞主要发生在 6 个月之后，首年基本是漏斗的形状。q 的价值在三年口径（±9%）——种草动作是长线投资，不背首年 KPI。</li>
    <li><b>④ 渗透上限约束从未触发</b>（0% 摆幅）：m×55% 的物理约束在当前参数域内不咬合，可以放心保留（防极端情况）。</li>
    <li><b>⑤ 整体判断</b>：没有任何一个参数 ±20% 能让首年 P50 翻倍或腰斩（最大摆幅 35%）——<b>结论对单参数扰动稳健</b>；分歧主要靠 Checkpoint 贝叶斯更新消化（上市 30 天即收窄 ~47%）。</li>
  </div>

  <div class="ft">
    <span>每个情景 = 独立重跑 8,000 次蒙特卡洛（种子 20261022）· 基线 = v0.5（核心对标带校准）</span>
    <span>防御逻辑：敏感参数标注 + Checkpoint 贝叶斯更新 + 上市前定向验证（CVR/PSM）</span>
  </div>

</div></div>
</body>
</html>
"""

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v0.5\AiKen敏感性检验_龙卷风图.html"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)
print("written:", OUT)
