# -*- coding: utf-8 -*-
"""方向B修正 v2：用 glob 定位文件（规避 PowerShell 传中文路径的编码问题）"""
import io
import glob
import os

BASE = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\潮玩相机品类"

def find(pattern):
    hits = glob.glob(os.path.join(BASE, pattern))
    return hits[0] if hits else None

PC = find("*电脑版.html")
M1 = find("AiKen品类组合演化逻辑*.html")
M2 = find("AiKen从品牌投资到品类回报_手机版.html") or find("*手机版.html")
# M2 可能匹配到演化逻辑页，分开处理
all_mobile = glob.glob(os.path.join(BASE, "*手机版.html"))

def fix_pc(path):
    t = io.open(path, encoding="utf-8").read()
    n = 0
    t = t.replace(
        "<h4>Gen 1.5 换壳款</h4>",
        "<h4>Gen 1.5 换色款</h4>")
    t = t.replace(
        '<div class="tm">现金流工具 · 相同设计</div>',
        '<div class="tm">市场测试 + 现金流 · 非联名</div>')
    t = t.replace(
        '<div class="kpi" style="color:#2E7D32">&lt;1 万台<small> 盈亏平衡</small></div>',
        '<div class="kpi" style="color:#2E7D32">NRE≈0–15 万<small> 色母/打样级</small></div>')
    t = t.replace(
        "<p>NRE ≈50 万（模具全复用）</p>",
        "<p>模具不变，只换配色（MOQ 2,000 小批快跑）</p>")
    t = t.replace(
        "<p><b>现金流为正</b>：收割剩余需求 + 维持热度</p>",
        "<p><b>现金流为正</b> + 测试哪个颜色卖得动</p>")
    t = t.replace(
        '<div class="drv">为 Gen2 攒数据和时间；潮玩品类标准打法</div>',
        '<div class="drv">换色销量数据直接喂给 Gen2 的 CMF 方向选择</div>')
    t = t.replace(
        "<h4>Gen 2 CMF 迭代 ¥599</h4>",
        "<h4>Gen 2 CMF 系统迭代 ¥599</h4>")
    t = t.replace(
        '<div class="tm">主力收割 · 软件模具全复用</div>',
        '<div class="tm">主力收割 · 换壳+表面工艺系统升级</div>')
    t = t.replace(
        "NRE 100 万 ｜ 首年 P50",
        "NRE 100 万（ID+CMF）｜ 首年 P50")
    if "Gen 1.5 换色款" in t: n += 1
    if "CMF 系统迭代" in t: n += 1
    io.open(path, "w", encoding="utf-8").write(t)
    return n

def fix_m_evo(path):
    t = io.open(path, encoding="utf-8").read()
    n = 0
    t = t.replace("<h5>Gen 1.5 换壳/配色款</h5>", "<h5>Gen 1.5 换色款</h5>")
    t = t.replace(
        '<div class="be">&lt;1 万<small>NRE ≈ 50 万以内</small></div>',
        '<div class="be">NRE≈0–15万<small>色母/打样级</small></div>')
    t = t.replace(
        '<div class="p">相同设计=模具全复用<br><b style="color:#2E7D32">现金流为正，资金效率最高</b></div>',
        '<div class="p">模具不变 MOQ 2,000<br><b style="color:#2E7D32">现金流为正+测颜色</b></div>')
    t = t.replace("<h5>走量迭代 ¥599</h5>", "<h5>CMF 系统迭代 ¥599</h5>")
    if "Gen 1.5 换色款" in t: n += 1
    io.open(path, "w", encoding="utf-8").write(t)
    return n

def fix_m_ret(path):
    t = io.open(path, encoding="utf-8").read()
    n = 0
    t = t.replace("<h5>Gen 1.5 换壳款<span>", "<h5>Gen 1.5 换色款<span>")
    t = t.replace("+6-12 月 · 现金流工具</span>", "+6-12 月 · 市场测试+现金流</span>")
    t = t.replace(
        "NRE ≈50 万（模具全复用，相同设计）｜ 盈亏平衡 <b>&lt;1 万台</b><br><b class=\"pos\">现金流为正</b>：收割 Gen1 剩余需求 + 维持品类热度，为 Gen2 攒数据和时间",
        "NRE≈0–15 万（色母/打样级，模具不变）｜ MOQ 2,000 小批快跑<br><b class=\"pos\">现金流为正</b> + 测试哪个颜色卖得动——换色销量直接喂给 Gen2 的 CMF 方向")
    t = t.replace("<h5>Gen 2 CMF 迭代 ¥599<span>", "<h5>Gen 2 CMF 系统迭代 ¥599<span>")
    t = t.replace("NRE 100 万（软件/模具全复用）｜ 首年 P50", "NRE 100 万（ID+CMF）｜ 首年 P50")
    if "Gen 1.5 换色款" in t: n += 1
    io.open(path, "w", encoding="utf-8").write(t)
    return n

results = []
if PC: results.append(("PC", PC, fix_pc(PC)))
for m in all_mobile:
    if "品类组合" in m:
        results.append(("Evo", m, fix_m_evo(m)))
    elif "品类回报" in m:
        results.append(("Ret", m, fix_m_ret(m)))

for tag, p, n in results:
    print(f"[{tag}] {os.path.basename(p)} -> {n} blocks")
print("done")
