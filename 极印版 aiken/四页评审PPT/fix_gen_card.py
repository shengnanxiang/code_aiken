# -*- coding: utf-8 -*-
"""修正手机页的 Gen 代际卡片（真实复用结构版）"""
import io

P = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\四页评审PPT\AiKen品类组合演化逻辑_手机版.html"
t = io.open(P, encoding="utf-8").read()

OLD_TITLE = "<h3>每一代的盈亏平衡销量在收敛</h3>"
NEW_TITLE = "<h3>每一代的盈亏平衡销量在收敛（按真实复用结构修正）</h3>\n      <p style=\"margin-bottom:4px\"><b>Gen2 复用的真实结构</b>：软件+测试人力 <b>≈194 万可复用</b>（50 人月经验迁移）；硬件结构/模具治具 110 万<b>需重做</b>；CMF/ID <b>追加 30–50 万</b> → Gen2 总投入 ≈ <b>310–330 万</b>。</p>"

OLD_G2 = """<div class="g">
          <span class="t">Gen 2</span>
          <h5>走量迭代 ¥599</h5>
          <div class="be">≈3.7 万<small>NRE 复用 50%</small></div>
          <div class="p">P50 预计 &gt; Gen1<br><b style="color:#2E7D32">→ 大概率盈利</b></div>
        </div>"""
NEW_G2 = """<div class="g">
          <span class="t">Gen 1.5</span>
          <h5>换壳/配色款</h5>
          <div class="be">&lt;1 万<small>NRE ≈ 50 万以内</small></div>
          <div class="p">相同设计=模具全复用<br><b style="color:#2E7D32">现金流为正，资金效率最高</b></div>
        </div>
        <div class="g">
          <span class="t">Gen 2</span>
          <h5>走量迭代 ¥599</h5>
          <div class="be">≈5 万<small>投入 310–330 万</small></div>
          <div class="p">P50 若 6.3 万→+80 万；若 5 万→贴线<br><b style="color:#B8860B">谨慎乐观：重看 Gen1 资产兑现</b></div>
        </div>"""

OLD_G3 = """<div class="be">≈1.5 万<small>净贡献 ~100 元/台</small></div>
          <div class="p">只需走量款 1/3 销量<br><b style="color:#2E7D32">→ 利润层</b></div>"""
NEW_G3 = """<div class="be">≈2.5–3 万<small>净贡献 ~100 元/台</small></div>
          <div class="p">利润层，须过两道检查<br>（净贡献 &amp; NRE 复用）</div>"""

OLD_FOOT = "收敛动力全部来自上一代资产：NRE 复用 + 市场已被教育 + 用户池免费触达。这就是「第二款开始盈利」的数学本质。"
NEW_FOOT = "收敛仍成立（9.2万 → 5万 → 2.5万）但幅度按真实复用率下修：软件是最大复用块，硬件每代重付。Gen2 从「大概率盈利」修正为「谨慎乐观」——立项门更依赖 Gen1 资产兑现（自然流量占比、用户池转化）。"

n = 0
if OLD_TITLE in t: t = t.replace(OLD_TITLE, NEW_TITLE); n += 1
if OLD_G2 in t: t = t.replace(OLD_G2, NEW_G2); n += 1
if OLD_G3 in t: t = t.replace(OLD_G3, NEW_G3); n += 1
if OLD_FOOT in t: t = t.replace(OLD_FOOT, NEW_FOOT); n += 1

# 一句话卡同步修正
t = t.replace(
    "第二款盈利 = 资产让盈亏平衡销量降到预期之下。",
    "第二款盈利 = 资产让盈亏平衡销量降到预期之下（软件复用是最大杠杆）。",
)
t = t.replace(
    "Gen2/Gen3 数字为示意推演，立项前须用 Gen1 实测参数重跑概率模型。",
    "Gen2/Gen3 数字按真实复用结构推演（软件 194 万复用 / 硬件重做 / CMF 追加），立项前须用 Gen1 实测参数重跑概率模型。",
)

io.open(P, "w", encoding="utf-8").write(t)
print(f"replaced {n}/4 blocks; file saved")
