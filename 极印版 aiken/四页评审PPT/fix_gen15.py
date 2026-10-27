# -*- coding: utf-8 -*-
"""方向B修正：Gen1.5 = Gen1 周期内的换色动作（非联名），Gen2 = CMF 系统迭代"""
import io

def fix(path):
    t = io.open(path, encoding="utf-8").read()
    n = 0

    t = t.replace(
        """<span class="st">第 2 步 · +6–12 月</span>
      <h4>Gen 1.5 换壳款</h4>
      <div class="tm">现金流工具 · 相同设计</div>
      <div class="kpi" style="color:#2E7D32">&lt;1 万台<small> 盈亏平衡</small></div>
      <p>NRE ≈50 万（模具全复用）</p>
      <p><b>现金流为正</b>：收割剩余需求 + 维持热度</p>
      <div class="drv">为 Gen2 攒数据和时间；潮玩品类标准打法</div>""",
        """<span class="st">第 2 步 · +6–12 月</span>
      <h4>Gen 1.5 换色款</h4>
      <div class="tm">市场测试 + 现金流 · 非联名</div>
      <div class="kpi" style="color:#2E7D32">NRE≈0–15 万<small> 色母/打样级</small></div>
      <p>模具不变，只换配色（MOQ 2,000 小批快跑）</p>
      <p><b>现金流为正</b> + 测试哪个颜色卖得动</p>
      <div class="drv">换色销量数据直接喂给 Gen2 的 CMF 方向选择</div>""")
    if "Gen 1.5 换色款" in t: n += 1

    t = t.replace(
        "<h4>Gen 2 CMF 迭代 ¥599</h4>",
        "<h4>Gen 2 CMF 系统迭代 ¥599</h4>")
    t = t.replace(
        '<div class="tm">主力收割 · 软件模具全复用</div>',
        '<div class="tm">主力收割 · 换壳+表面工艺系统升级</div>')
    t = t.replace(
        "NRE 100 万 ｜ 首年 P50 = <b>33,291 台</b>（Gen1 ×1.5）",
        "NRE 100 万（ID+CMF）｜ 首年 P50 = <b>33,291 台</b>（Gen1 ×1.5）")
    if "CMF 系统迭代" in t: n += 1

    io.open(path, "w", encoding="utf-8").write(t)
    return n

n1 = fix(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\四页评审PPT\AiKen从品牌投资到品类回报_电脑版.html")
print(f"PC blocks: {n1}")

def fix_m(path):
    t = io.open(path, encoding="utf-8").read()
    n = 0
    t = t.replace(
        """<h5>Gen 1.5 换壳/配色款</h5>
          <div class="be">&lt;1 万<small>NRE ≈ 50 万以内</small></div>
          <div class="p">相同设计=模具全复用<br><b style="color:#2E7D32">现金流为正，资金效率最高</b></div>""",
        """<h5>Gen 1.5 换色款</h5>
          <div class="be">NRE≈0–15万<small>色母/打样级</small></div>
          <div class="p">模具不变 MOQ 2,000<br><b style="color:#2E7D32">现金流为正+测颜色</b></div>""")
    if "Gen 1.5 换色款" in t: n += 1
    t = t.replace(
        "<h5>走量迭代 ¥599</h5>\n          <div class=\"be\">≈5 万<small>投入 310–330 万</small></div>",
        "<h5>CMF 系统迭代 ¥599</h5>\n          <div class=\"be\">≈5 万<small>投入 310–330 万</small></div>")
    if "CMF 系统迭代" in t: n += 1
    io.open(path, "w", encoding="utf-8").write(t)
    return n

n2 = fix_m(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\四页评审PPT\AiKen品类组合演化逻辑_手机版.html")
print(f"Mobile blocks: {n2}")

# 第二个手机版（从品牌投资到品类回报）
def fix_m2(path):
    t = io.open(path, encoding="utf-8").read()
    n = 0
    t = t.replace(
        """<h5>Gen 1.5 换壳款<span>+6-12 月 · 现金流工具</span></h5>
            <p>NRE ≈50 万（模具全复用，相同设计）｜ 盈亏平衡 <b>&lt;1 万台</b><br><b class="pos">现金流为正</b>：收割 Gen1 剩余需求 + 维持品类热度，为 Gen2 攒数据和时间</p>""",
        """<h5>Gen 1.5 换色款<span>+6-12 月 · 市场测试+现金流</span></h5>
            <p>NRE≈0–15 万（色母/打样级，模具不变）｜ MOQ 2,000 小批快跑<br><b class="pos">现金流为正</b> + 测试哪个颜色卖得动——换色销量直接喂给 Gen2 的 CMF 方向</p>""")
    if "Gen 1.5 换色款" in t: n += 1
    t = t.replace(
        "<h5>Gen 2 CMF 迭代 ¥599<span>+6-12 月 · 主力收割</span></h5>",
        "<h5>Gen 2 CMF 系统迭代 ¥599<span>+12 月 · 主力收割</span></h5>")
    t = t.replace(
        "NRE 100 万（软件/模具全复用）｜ 首年 P50 = <b>33,291 台</b>（Gen1 的 1.5 倍）",
        "NRE 100 万（ID+CMF）｜ 首年 P50 = <b>33,291 台</b>（Gen1 的 1.5 倍）")
    if "CMF 系统迭代" in t: n += 1
    io.open(path, "w", encoding="utf-8").write(t)
    return n

n3 = fix_m2(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\四页评审PPT\AiKen从品牌投资到品类回报_手机版.html")
print(f"Mobile2 blocks: {n3}")
