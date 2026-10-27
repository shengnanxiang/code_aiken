# -*- coding: utf-8 -*-
"""
v0.4 财务层更新版 —— 新投资口径 477.355 万（261027 Budget）
其余口径不变：ASP不含税 431.2 / 销售费用 30% / BOM 250 → 单台净贡献 51.9 元
输出：三档覆盖 / 全分布财务读数 / 转正概率 / 对比旧口径(413.8万)
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

D = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v04_results.npz")
y1, y3 = D["y1"], D["y3"]

INVEST_NEW = 4_773_550   # 新：继续投入（Budget H9, 261027）
INVEST_OLD = 4_138_050   # 旧口径对照
cm_unit = 51.9069        # 431.2269...×0.7-250（不变）

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

print("=" * 64)
print("AiKen 财务层 · 新投资口径 477.36 万（v0.4 分布 × 新 Budget）")
print("=" * 64)
print(f"\n【口径】单台净贡献 {cm_unit:.1f} 元（不变）｜ 投资 4,773,550 元（旧 4,138,050）")

for label, INV in [("新口径 477.4万", INVEST_NEW), ("旧口径 413.8万(对照)", INVEST_OLD)]:
    cov1 = y1 * cm_unit / INV
    pnl3 = y3 * cm_unit - INV
    print(f"\n--- {label} ---")
    print(f"  三档首年投入覆盖: Worst(P10) {pct(cov1,10)*100:.0f}% | Normal(P50) {pct(cov1,50)*100:.0f}% | Best(P90) {pct(cov1,90)*100:.0f}%")
    print(f"  P(首年覆盖≥100%) = {prob(cov1,1.0)*100:.1f}%")
    print(f"  三档三年累计净利: Worst {pct(pnl3,10)/1e4:+.0f}万 | Normal {pct(pnl3,50)/1e4:+.0f}万 | Best {pct(pnl3,90)/1e4:+.0f}万")
    print(f"  P(三年转正) = {prob(pnl3,0)*100:.1f}%")
    print(f"  P(三年净利≥+100万) = {prob(pnl3,1e6)*100:.1f}%")
    print(f"  P(三年净亏>200万) = {float((pnl3<-2e6).mean())*100:.1f}%")

# 与财务表 Excel 三档对照（Excel 用的是取整锚 14,400/21,600/32,400）
print("\n【与财务表 Excel 对照】（Excel 取整锚 14,400/21,600/32,400 · 摊销含首年）")
cm = cm_unit
for name, v in [("Worst 14,400", 14_400), ("Normal 21,600", 21_600), ("Best 32,400", 32_400)]:
    # Excel 口径：三年净利 = 3年×年销×单台毛利(209.99含税... 实际用不含税201.3?) - 投入
    # Excel 算出 Normal -140万 / Best +1.6万 / Worst -234万（含模具摊销等细节）
    # 我们的简化口径（单台净贡献×3年销量-投资）：
    pnl_simple = v * 3 * cm - INVEST_NEW
    print(f"  {name}: 简化口径三年净利 {pnl_simple/1e4:+.0f}万")

# 保存新财务数组
cov1 = y1 * cm_unit / INVEST_NEW
pnl3 = y3 * cm_unit - INVEST_NEW
np.savez(
    r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v04_finance_new.npz",
    cov1=cov1, pnl3=pnl3, inv=INVEST_NEW, cm_unit=cm_unit,
)
print("\n[Saved] v04_finance_new.npz")

# ===== 生成新财务读数表（Excel） =====
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = openpyxl.Workbook()
wb.remove(wb.active)
HDR = PatternFill("solid", fgColor="111111")
HF = Font(color="FFFFFF", bold=True, size=10, name="Microsoft YaHei")
TF = Font(bold=True, size=13, name="Microsoft YaHei")
BF = Font(size=10.5, name="Microsoft YaHei")
KF = Font(size=10.5, bold=True, color="EC008C", name="Microsoft YaHei")
NF = Font(size=9.5, color="6B6B6B", name="Microsoft YaHei")
thin = Side(style="thin", color="CCCCCC")
BD = Border(left=thin, right=thin, top=thin, bottom=thin)

ws = wb.create_sheet("财务读数·新投资口径")
ws.cell(1,1,"AiKen 财务读数 · 新投资口径（477.36 万 · Budget 261027）").font = TF
ws.cell(2,1,"单台净贡献 51.9 元（ASP不含税431.2×70%−BOM250）· 分布 = v0.4 · 与读数表/评审页同源").font = NF

rows_hdr = ["指标", "Worst (P10)", "Normal (P50)", "Best (P90)"]
data = [
    ("首年销量（台）", f"{pct(y1,10):,.0f}", f"{pct(y1,50):,.0f}", f"{pct(y1,90):,.0f}"),
    ("首年净贡献（万元）", f"{pct(y1,10)*cm/1e4:.0f}", f"{pct(y1,50)*cm/1e4:.0f}", f"{pct(y1,90)*cm/1e4:.0f}"),
    ("首年投入覆盖", f"{pct(cov1,10)*100:.0f}%", f"{pct(cov1,50)*100:.0f}%", f"{pct(cov1,90)*100:.0f}%"),
    ("三年累计（台）", f"{pct(y3,10):,.0f}", f"{pct(y3,50):,.0f}", f"{pct(y3,90):,.0f}"),
    ("三年累计净利（万元）", f"{pct(pnl3,10)/1e4:+.0f}", f"{pct(pnl3,50)/1e4:+.0f}", f"{pct(pnl3,90)/1e4:+.0f}"),
]
for c, h in enumerate(rows_hdr, 1):
    cell = ws.cell(4, c, h); cell.fill = HDR; cell.font = HF; cell.border = BD; cell.alignment = Alignment(horizontal="center")
for r, row in enumerate(data, 5):
    for c, v in enumerate(row, 1):
        cell = ws.cell(r, c, v); cell.font = BF; cell.border = BD

ws.cell(11,1,"全分布读数").font = TF
kpis = [
    ("P(首年投入覆盖 ≥100%)", f"{prob(cov1,1.0)*100:.1f}%"),
    ("P(三年累计转正)", f"{prob(pnl3,0)*100:.1f}%"),
    ("P(三年净利 ≥ +100万)", f"{prob(pnl3,1e6)*100:.1f}%"),
    ("P(三年净亏 > 200万)", f"{float((pnl3<-2e6).mean())*100:.1f}%"),
    ("P(三年累计 ≥10万台)", f"{prob(y3,100_000)*100:.0f}%"),
]
for r, (k, v) in enumerate(kpis, 12):
    ws.cell(r,1,k).font = BF; ws.cell(r,1).border = BD
    ws.cell(r,2,v).font = KF; ws.cell(r,2).border = BD

ws.cell(18,1,"注：本表为「简化口径」（单台净贡献×销量−投资），不含模具摊销分年/资金成本/MOH等细节；").font = NF
ws.cell(19,1,"    精确口径以财务表 Excel Scenario sheets 为准（Normal −140万/Best +1.6万/Worst −234万）。").font = NF
for col, w in zip("ABCD", [26, 14, 14, 14]):
    ws.column_dimensions[col].width = w

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen财务读数_新投资口径.xlsx"
wb.save(OUT)
print("[Saved] AiKen财务读数_新投资口径.xlsx")
