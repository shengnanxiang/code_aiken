# -*- coding: utf-8 -*-
"""生成《AiKen销量模型_参数审计表》：全部输入参数的来源、数值、证据等级"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# ===== 重算（种子一致）=====
rng = np.random.default_rng(20261022)
N_SIM = 8000
m = rng.lognormal(mean=np.log(110_000), sigma=0.85, size=N_SIM)
q = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)
B = rng.triangular(800_000, 1_550_000, 2_400_000, size=N_SIM)
CPM = rng.triangular(38, 45, 65, size=N_SIM)
CTR = rng.triangular(0.018, 0.023, 0.030, size=N_SIM)
CVR = rng.triangular(0.009, 0.014, 0.022, size=N_SIM)
exposure = B / CPM * 1000
clicks = exposure * CTR
s6_raw = clicks * CVR
s6 = np.minimum(s6_raw, m * 0.55)

def bass(m_, p_, q_, t):
    t = np.asarray(t, dtype=float)
    return m_*(1-np.exp(-(p_+q_)*t))/(1+(q_/p_)*np.exp(-(p_+q_)*t))
def solve_p(m_, q_, s6t):
    lo = np.full_like(m_, 1e-5); hi = np.full_like(m_, 1.2)
    for _ in range(40):
        mid = 0.5*(lo+hi)
        small = bass(m_, mid, q_, 0.5) < s6t
        lo = np.where(small, mid, lo); hi = np.where(small, hi, mid)
    return 0.5*(lo+hi)
p = solve_p(m, q, s6)
pct = lambda a, x: float(np.percentile(a, x))

wb = Workbook()
HDR_FILL = PatternFill("solid", fgColor="111111")
EVID_A = PatternFill("solid", fgColor="E8F5E9")   # 实测/公开数据
EVID_B = PatternFill("solid", fgColor="FFF8E1")   # 实测外推/回测校准
EVID_C = PatternFill("solid", fgColor="FDF3F8")   # 推断校准
HDR_FONT = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
B_FONT = Font(name="微软雅黑", size=10, bold=True)
N_FONT = Font(name="微软雅黑", size=10)
S_FONT = Font(name="微软雅黑", size=9, color="6B6B6B")
THIN = Border(*[Side(style="thin", color="D9D9D9")] * 4)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center")

# ===== Sheet 1: 参数总表 =====
ws = wb.active
ws.title = "参数总表"
ws["A1"] = "AiKen 销量概率模型 · 参数审计表（v0.4 · ¥699 口径）"
ws["A1"].font = Font(name="微软雅黑", size=14, bold=True)
ws["A2"] = ("用途：模型全部输入参数的来源与数值一览。每行一个参数：是什么→设成多少→依据是什么→证据等级。"
            "种子 20261022 · 8000 次蒙特卡洛。")
ws["A2"].font = S_FONT
ws["A3"] = "证据等级：■ 绿 = 实测/公开数据 ｜ ■ 黄 = 实测外推/回测校准 ｜ ■ 粉 = 推断校准（最需要挑战的）"
ws["A3"].font = Font(name="微软雅黑", size=9, color="444444")

headers = ["参数", "角色", "分布设定", "实际抽样 P10 / P50 / P90", "依据", "证据等级"]
r = 5
for j, h in enumerate(headers, 1):
    ws.cell(row=r, column=j, value=h)
    ws.cell(row=r, column=j).fill = HDR_FILL
    ws.cell(row=r, column=j).font = HDR_FONT
    ws.cell(row=r, column=j).border = THIN
r += 1

rows = [
    ("m 市场潜力", "3年累计销量上限（Bass 天花板）",
     "对数正态 P50=11万, σ=0.85",
     f"{pct(m,10):,.0f} / {pct(m,50):,.0f} / {pct(m,90):,.0f}",
     "区间证据：instax mini 中国盘年销百万级（天花板参照）↔ Flashback One35 众筹 $80万≈6-7千台+三年用户5-10万（存活基线）↔ Kodak Mini Shot 年销1-3万（中游带）；P50=11万取证据带中位偏下；σ=0.85 保留右尾（P≥100万=0.6%，P95=42.8万）",
     "C"),
    ("q 口碑系数", "模仿/传染强度（Bass 起飞斜率，年口径）",
     "正态 μ=0.42, σ=0.10，截断[0.18, 0.68]",
     f"{pct(q,10):.3f} / {pct(q,50):.3f} / {pct(q,90):.3f}",
     "品类典型带 0.28-0.55（营销科学文献耐用品常规区间）；CCD 潮（小红书笔记165万+条、抖音复古器材年销7500万+170%YoY）与撕拉片（单张¥400+）证明该品类口碑传染强 → 取中高位 0.42；下限0.18=口碑几乎失效，上限0.68=instax/CCD级强传染",
     "C"),
    ("p 创新系数", "外部刺激驱动的首发购买（Bass 冷启动）",
     "不设先验——由漏斗反解输出",
     f"{pct(p,10):.3f} / {pct(p,50):.3f} / {pct(p,90):.3f}",
     "每次模拟：预算→曝光→点击→转化 定出前6个月销量 S6，再反解 Bass 的 p 使曲线在 S6 衔接。p 分布宽（P5=0.042~P95=0.99）是正常的——它继承漏斗参数的不确定性",
     "B"),
    ("媒介预算（6个月）", "漏斗入口（决定曝光量）",
     "三角 (80万, 155万, 240万)",
     f"{pct(B,10)/1e4:.0f}万 / {pct(B,50)/1e4:.0f}万 / {pct(B,90)/1e4:.0f}万",
     "市场部（Maggie）2026-10-26 提供的意向区间",
     "A"),
    ("CPM 千次曝光成本", "曝光→预算换算",
     "三角 (38, 45, 65) 元",
     f"{pct(CPM,10):.0f} / {pct(CPM,50):.0f} / {pct(CPM,90):.0f}",
     "极印投放数据 2026 YTD（站外 2026-10-26 表）：S1 站内实测 45.2 加权，低效源余量下探 38，上界 65",
     "A"),
    ("CTR 点击率", "曝光→点击",
     "三角 (1.8%, 2.3%, 3.0%)",
     f"{pct(CTR,10)*100:.1f}% / {pct(CTR,50)*100:.1f}% / {pct(CTR,90)*100:.1f}%",
     "S1 站内实测 2.14% 为中心，上下余量",
     "A"),
    ("CVR 落地页转化率", "点击→订单",
     "三角 (0.9%, 1.4%, 2.2%)",
     f"{pct(CVR,10)*100:.1f}% / {pct(CVR,50)*100:.1f}% / {pct(CVR,90)*100:.1f}%",
     "S1 站内实测 0.98% 为下界参照 + S1 回测教训（N 系参数对 S1 高估 2 倍）转化的保守余量；P50=1.4% 约为实测的 1.4 倍",
     "B"),
    ("渗透上限", "S6 的物理约束",
     "S6 ≤ m × 55%",
     f"钳制触发率 {float((s6_raw > m*0.55).mean())*100:.1f}%",
     "前 6 个月最多吃掉市场潜力的 55%（认知渗透的经验约束，防止漏斗在低 m 样本上跑出不可能销量）",
     "C"),
]
for name, role, dist, vals, evid, grade in rows:
    ws.cell(row=r, column=1, value=name).font = B_FONT
    ws.cell(row=r, column=2, value=role)
    ws.cell(row=r, column=3, value=dist)
    ws.cell(row=r, column=4, value=vals)
    ws.cell(row=r, column=5, value=evid)
    ws.cell(row=r, column=6, value=grade)
    for j in range(1, 7):
        ws.cell(row=r, column=j).border = THIN
        if j in (2, 3, 5): ws.cell(row=r, column=j).alignment = WRAP
        if j == 4: ws.cell(row=r, column=j).alignment = CENTER
        if j == 6: ws.cell(row=r, column=j).alignment = CENTER
    fill = {"A": EVID_A, "B": EVID_B, "C": EVID_C}[grade]
    ws.cell(row=r, column=6).fill = fill
    r += 1

r += 1
ws.cell(row=r, column=1, value="输出锚（供核对面值）").font = B_FONT
r += 1
outs = [
    ("首年销量", "P20=16,844 / P50=22,123 / P90=32,793（Worst 锚取 P20）"),
    ("三年累计", "P50=63,831 / P90=106,182"),
    ("漏斗中间量（P50）", f"曝光 {pct(exposure,50)/1e6:.0f}M → 点击 {pct(clicks,50)/1e4:.0f}万 → S6 {pct(s6,50):,.0f} 台"),
]
for label, v in outs:
    ws.cell(row=r, column=1, value=label).font = B_FONT
    ws.cell(row=r, column=2, value=v)
    r += 1

for col, w_ in zip("ABCDEF", [16, 26, 24, 26, 66, 10]):
    ws.column_dimensions[col].width = w_

# ===== Sheet 2: RCF 参照产品证据表 =====
ws2 = wb.create_sheet("RCF参照产品")
ws2["A1"] = "RCF 参照类 · 产品证据表"
ws2["A1"].font = Font(name="微软雅黑", size=14, bold=True)
ws2["A2"] = ("参照产品不是逐个拟合参数，而是用真实数据『圈定』m 和 q 的先验区间。下表 = 每个参照提供了什么证据、锚定了哪个参数的哪一端。")
ws2["A2"].font = S_FONT

r = 4
for j, h in enumerate(["参照产品", "价格带", "关键数据", "锚定的参数与方向", "数据来源", "证据等级"], 1):
    ws2.cell(row=r, column=j, value=h)
    ws2.cell(row=r, column=j).fill = HDR_FILL
    ws2.cell(row=r, column=j).font = HDR_FONT
    ws2.cell(row=r, column=j).border = THIN
r += 1
refs = [
    ("富士 instax mini 系列", "¥599 同价位", "全球年销 2004 年 10 万台 → 2019 年 1,000 万台；mini 款主力价位与 AiKen 相同", "m 天花板：instax 若在中国盘做『平替』，百万台级是可达上限 → 支撑 m 右尾延伸到 P(≥100万)≈0.6%", "富士财报/公开报道（smejapan 等）", "A"),
    ("Flashback One35 / V2", "¥749 直接对标", "Kickstarter 众筹 $80 万（约 6-7 千台首单）；三年全球拍摄 1,000 万张照片（估算用户 5-10 万）；V2 京东价 ¥749", "m 存活基线：最接近 AiKen 的形态对标（复古胶卷风数码机）证明小众也能活 → 锚定 m 下界证据；定价 749 直接对标", "Kickstarter/DCfever/ZOL（2026-10 调研）", "A"),
    ("Kodak Mini Shot 3 Retro", "¥1,269", "国内电商年销约 1-3 万台", "m 中游带：授权品牌+照片打印组合品类的中国实际水位 → 锚定 m 的 P25-P50 区域", "电商页面估算（精度有限，作参照带）", "C"),
    ("Paper Shoot 纸可拍", "¥400-700", "无屏幕极简相机，小众圈层存活多年", "q 佐证：小众圈层产品的口碑传染存活模式", "公开资料", "C"),
    ("CCD 复古潮（品类信号）", "二手 ¥300-3000", "小红书相关笔记 165 万+条；抖音复古摄影器材年销 7,500 万元（+170% YoY）；二手价翻 10 倍", "q 上界证据：该品类的社交传染强度 → 支撑 q 取中高位 0.42、上限 0.68", "搜狐/电商报道（2026-10 调研）", "A"),
    ("撕拉片现象（需求信号）", "单张 ¥400+", "停产相纸被炒至 3,000-4,500 元/盒；明星效应带火", "支付意愿证据：目标人群为『情绪价值+社交货币』付费的能力 → 支撑 m 中位以上的可信度", "新京报/极客网等（2025-2026）", "A"),
    ("薇娅直播脉冲（内部）", "—", "2020 年薇娅直播 5 分钟售罄 6,600 台口袋打印机", "q 脉冲上界：口碑/流量脉冲在中国市场的单次爆发力", "内部历史数据", "A"),
    ("S1 贴纸一体机（内部）", "¥1,799", "站内实测 CTR 2.14% / CVR 0.98% / CPM 45.2；回测：内部点预测 25,000 实际宽口径 ~7,285（N 系参数高估 2 倍）", "漏斗参数全部 + CVR 保守余量；『锚 S1 而非 N 系』的方法论依据", "极印投放数据 2026-10-26 + 回测", "A"),
    ("DJI Pocket 3（方法验证）", "¥3,499", "内部预期 30-40万 → 2024 实售 ~500 万（P96.7）；累计破 1,000 万（P99.3）", "不进参数；用于验证『分布保留右尾』的方法论必要性", "雷峰网/IT之家 2025-09（供应链消息）", "A"),
]
for name, price, data, anchor, src, grade in refs:
    ws2.cell(row=r, column=1, value=name).font = B_FONT
    ws2.cell(row=r, column=2, value=price)
    ws2.cell(row=r, column=3, value=data)
    ws2.cell(row=r, column=4, value=anchor)
    ws2.cell(row=r, column=5, value=src)
    ws2.cell(row=r, column=6, value=grade)
    for j in range(1, 7):
        ws2.cell(row=r, column=j).border = THIN
        ws2.cell(row=r, column=j).alignment = WRAP
    ws2.cell(row=r, column=6).fill = {"A": EVID_A, "B": EVID_B, "C": EVID_C}[grade]
    r += 1

for col, w_ in zip("ABCDEF", [20, 12, 42, 44, 26, 10]):
    ws2.column_dimensions[col].width = w_

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen销量模型_参数审计表.xlsx"
wb.save(OUT)
print("saved:", OUT)
