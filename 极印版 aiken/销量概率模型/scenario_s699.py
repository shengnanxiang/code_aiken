# -*- coding: utf-8 -*-
"""
AiKen 699 元定价情景初算（task-s699-scenario）
================================================
定位：模型内假设推演（非外部数据验证）。在 pricing-analyst 报告
（deliverables/04-pricing-model-assessment.md，含附 2 对齐纪要）推荐的四层框架
内的层 1+层 2 执行：量价贡献模型情景矩阵 + 盈亏平衡弹性容忍度。

复用与不改动的既有资产（全部只读）：
  - v04_results.npz：v0.4 销量分布（8000 次蒙特卡洛，种子 20261027）
  - finance_update.py 的财务口径：投资 4,773,550 元（261027 Budget）
  - AiKen JY Finance_261027.xlsx BOM&ASP sheet 的渠道结构

口径（与 v0.4 / 261027 新口径一致）：
  - 599 基准：混合 ASP 487.29 含税 / 431.23 不含税；BOM 250；销售费用率 30%
    → 单台净贡献 51.9 元
  - 699 情景：混合折扣 0.8135 不变 → 混合 ASP 568.64 含税 / 503.22 不含税
    → 单台净贡献 102.3 元（+97.2%）
  - 简化口径：三年净利 = y3 × 单台净贡献 − 投资（忽略模具摊销分年/资金成本，
    读数系统性偏乐观，已在结论文档标注）

主传导（报告附 2 确认）：恒弹性 × 预算效率双参数。
  恒弹性作用于全分布（8000 条轨迹逐条缩放）：
    q699 = q599 × (699/599)^ε  （逐轨迹乘同一缩放因子）
  弹性七档：-0.5 / -1.0 / -1.5 / -2.0 / -2.5 / -2.95（容忍度点弹性）/ -4.24（弧弹性保守参照）
  预算效率三档：0.9 / 1.0 / 1.1（699 人群池缩小可能使同预算买到的曝光/点击劣化
    → <1；人群更聚焦投放效率可能改善 → >1；作用于弹性后销量之上再乘）

交叉验证侧矩阵（不做主传导）：CVR 衰减情景——按价位上探后 CVR 折减系数
  f_cvr ∈ {0.8, 0.9, 1.0} 直接缩放 s6 后重解 Bass（用 v0.4 相同机制），
  仅用于展示「漏斗路径」与「恒弹性路径」的量级对照。

输出（全部新文件，含 _s699 后缀，不覆盖任何既有文件）：
  - scenario_s699_输出.txt   控制台读数存档
  - scenario_s699_results.npz 全部分布数组
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

# ============ [0] 基础口径（与 v0.4 / 261027 一致） ============
BASE = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型"

D = np.load(BASE + r"\v04_results.npz")
y1, y3 = D["y1"], D["y3"]          # 599 基准首年 / 三年销量分布（8000 条）
m_prior, q_prior = D["m_prior"], D["q_prior"]

P_BASE, P_NEW = 599.0, 699.0
MIX = 0.65 * 0.85 + 0.30 * 0.75 + 0.05 * 0.72   # 0.8135（BOM&ASP 反推）
VAT = 1.13
BOM = 250.0
SALES_RATE = 0.30
INVEST = 4_773_550                                 # 261027 Budget 新投资口径

asp_base_notax = P_BASE * MIX / VAT                # 431.23
asp_699_notax = P_NEW * MIX / VAT                  # 503.22
cm_base = asp_base_notax * (1 - SALES_RATE) - BOM  # 51.86
cm_699 = asp_699_notax * (1 - SALES_RATE) - BOM    # 102.25

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

# ============ [1] 静态财务对照（层 2：盈亏平衡弹性容忍度） ============
q_hold = cm_base / cm_699                                    # 0.5073
elas_point = (q_hold - 1) / ((P_NEW - P_BASE) / P_BASE)      # -2.95
elas_arc = ((q_hold - 1) / ((1 + q_hold) / 2)) / ((P_NEW - P_BASE) / ((P_NEW + P_BASE) / 2))  # -4.24
be_base = INVEST / cm_base       # 599 覆盖全部投资所需三年销量
be_699 = INVEST / cm_699         # 699 同口径

print("=" * 70)
print("AiKen 699 元定价情景矩阵 · 模型内假设推演（task-s699-scenario）")
print("=" * 70)
print(f"\n【口径】投资 {INVEST:,.0f} 元 · 销售费用率 {SALES_RATE:.0%} · BOM {BOM:.0f} · 简化口径（偏乐观）")
print(f"  599: 混合ASP含税 {P_BASE*MIX:.2f} / 不含税 {asp_base_notax:.2f} → 净贡献 {cm_base:.2f} 元/台")
print(f"  699: 混合ASP含税 {P_NEW*MIX:.2f} / 不含税 {asp_699_notax:.2f} → 净贡献 {cm_699:.2f} 元/台（{(cm_699/cm_base-1)*100:+.1f}%）")
print(f"\n【层 2 · 弹性容忍度（零数据依赖的底线刻度）】")
print(f"  总净贡献持平的销量容忍度 = {q_hold*100:.1f}%（可跌去 {(1-q_hold)*100:.1f}%）")
print(f"  对应点弹性 {elas_point:.2f} / 弧弹性（中点法）{elas_arc:.2f}")
print(f"  覆盖全部投资所需三年销量: 599 需 {be_base:,.0f} 台 vs 699 需 {be_699:,.0f} 台")
print(f"  v0.4 三年分布参照: P10={pct(y3,10):,.0f} P50={pct(y3,50):,.0f} P90={pct(y3,90):,.0f}")

# ============ [2] 599 基准复现（口径核对锚） ============
pnl3_base = y3 * cm_base - INVEST
print(f"\n【599 基准复现（简化口径）】")
print(f"  P(三年转正) = {prob(pnl3_base, 0)*100:.1f}%   （v0.4 摘要 28.3% 同口径，作复现锚）")
print(f"  P(三年净亏>200万) = {float((pnl3_base < -2e6).mean())*100:.1f}%")
print(f"  三年净利: P10 {pct(pnl3_base,10)/1e4:+.0f}万 | P50 {pct(pnl3_base,50)/1e4:+.0f}万 | P90 {pct(pnl3_base,90)/1e4:+.0f}万")

# ============ [3] 主矩阵：恒弹性 × 预算效率（层 1） ============
ELAS = [-0.5, -1.0, -1.5, -2.0, -2.5, -2.95, -4.24]   # 七档（附 2 确认）
EFF = [0.9, 1.0, 1.1]                                   # 预算效率三档

scale = (P_NEW / P_BASE) ** np.array(ELAS)              # 每档弹性的销量缩放因子
print(f"\n【主矩阵 · 699 恒弹性情景（预算效率=1.0）】")
print(f"  {'弹性':>6} | {'销量因子':>7} | {'y3-P50':>8} | {'P(转正)':>7} | {'P(亏>200万)':>9} | {'净利P50':>8} | {'净利P10':>8}")
rows_main = []
for e, s_ in zip(ELAS, scale):
    y3s = y3 * s_
    pnl = y3s * cm_699 - INVEST
    r = (e, s_, pct(y3s, 50), prob(pnl, 0), float((pnl < -2e6).mean()),
         pct(pnl, 50) / 1e4, pct(pnl, 10) / 1e4)
    rows_main.append((e, s_, y3s, pnl))
    print(f"  {e:>6.2f} | {s_:>7.3f} | {r[2]:>8,.0f} | {r[3]*100:>6.1f}% | {r[4]*100:>8.1f}% | {r[5]:>+7.0f}万 | {r[6]:>+7.0f}万")

print(f"\n【主矩阵 · 预算效率敏感性（弹性=-1.0 中性档下，效率 0.9/1.0/1.1）】")
e_mid = ELAS.index(-1.0)
for f_eff in EFF:
    y3s = y3 * scale[e_mid] * f_eff
    pnl = y3s * cm_699 - INVEST
    print(f"  效率 {f_eff:.1f}: P(转正) {prob(pnl,0)*100:.1f}% | P(亏>200万) {float((pnl<-2e6).mean())*100:.1f}% | 净利P50 {pct(pnl,50)/1e4:+.0f}万")

# ============ [4] 临界弹性精确解（indifference 点细化） ============
# 找到使 P(三年转正) 恰好等于 599 基准值的连续弹性解（分布级 indifference）
# 弹性越负 → 销量缩得越多 → 转正概率越低。p_ 仍高于基准时向更负侧收。
lo, hi = -12.0, -0.05
target = prob(pnl3_base, 0)
for _ in range(60):
    mid = 0.5 * (lo + hi)
    s_ = (P_NEW / P_BASE) ** mid
    p_ = prob(y3 * s_ * cm_699 - INVEST, 0)
    if p_ > target:
        hi = mid      # 转正概率仍高于基准 → 答案在更负侧
    else:
        lo = mid
e_star = 0.5 * (lo + hi)
print(f"\n【分布级 indifference 弹性】")
print(f"  使 P(三年转正) 恰回落到 599 基准（{target*100:.1f}%）的弹性 ε* ≈ {e_star:.2f}")
print(f"  （总净贡献持平的确定性口径为 {elas_point:.2f}；两者差异来自分布非线性）")

# ============ [5] 交叉验证侧矩阵：CVR 衰减（漏斗路径量级对照，非主传导） ============
# 用 v0.4 相同机制：s6 缩放 → 重解 Bass p → 重建 y1/y3
def bass_cum_year(m, p, q, t_year):
    t = np.asarray(t_year, dtype=float)
    denom = 1 + (q / p) * np.exp(-(p + q) * t)
    return m * (1 - np.exp(-(p + q) * t)) / denom

def solve_p(m, q, s6_target):
    lo_ = np.full_like(m, 1e-5); hi_ = np.full_like(m, 1.2)
    for _ in range(40):
        mid = (lo_ + hi_) / 2
        too_small = bass_cum_year(m, mid, q, 0.5) < s6_target
        lo_ = np.where(too_small, mid, lo_); hi_ = np.where(too_small, hi_, mid)
    return 0.5 * (lo_ + hi_)

t_year = np.arange(1, 37) / 12.0
print(f"\n【交叉验证 · CVR 衰减路径（漏斗机制，非主传导）】")
print(f"  {'CVR折减':>7} | {'隐含弹性':>8} | {'y3-P50':>8} | {'P(转正)':>7}")
cvr_rows = []
for f_cvr in [1.0, 0.9, 0.8]:
    s6_cv = D["s6"] * f_cvr
    p_cv = solve_p(m_prior, q_prior, s6_cv)
    paths_cv = bass_cum_year(m_prior[:, None], p_cv[:, None], q_prior[:, None], t_year[None, :])
    y3_cv = paths_cv[:, 35]
    pnl_cv = y3_cv * cm_699 - INVEST
    # 隐含弹性：y3 中位数相对基准的变化折算
    imp = np.log(pct(y3_cv, 50) / pct(y3, 50)) / np.log(P_NEW / P_BASE)
    cvr_rows.append((f_cvr, y3_cv, pnl_cv))
    print(f"  {f_cvr:>7.1f} | {imp:>8.2f} | {pct(y3_cv,50):>8,.0f} | {prob(pnl_cv,0)*100:>6.1f}%")
print("  注：CVR 折减作用于前 6 个月，经 Bass 扩散放大后对 y3 的影响小于对前 6 月的直接影响；")
print("      站内价位-CVR 散点非单调（N2 ¥799 CVR 3.27% 最高），此路径仅作量级对照（报告附 2）。")

# ============ [6] 三档锚位移表（战略侧量化注脚） ============
print(f"\n【三档锚位移（首年 P10/P50/P90，供 SI pptx P9 用户池论证引用）】")
print(f"  {'弹性':>6} | {'P10':>7} | {'P50':>7} | {'P90':>7} | {'P50用户池':>8}")
for e, s_, _, _ in rows_main:
    y1s = y1 * s_
    print(f"  {e:>6.2f} | {pct(y1s,10):>7,.0f} | {pct(y1s,50):>7,.0f} | {pct(y1s,90):>7,.0f} | {pct(y1s,50)/1e4:>7.2f}万人")

# ============ [7] 保存 ============
out = {
    "cm_base": cm_base, "cm_699": cm_699, "q_hold": q_hold,
    "elas_point": elas_point, "elas_arc": elas_arc,
    "be_base": be_base, "be_699": be_699, "e_star_prob": e_star,
    "pnl3_base": pnl3_base, "p_trans_base": prob(pnl3_base, 0),
}
for (e, s_, y3s, pnl) in rows_main:
    tag = f"e{abs(e):.2f}".replace(".", "p")
    out[f"y3_{tag}"] = y3s
    out[f"pnl3_{tag}"] = pnl
    out[f"y1_{tag}"] = y1 * s_
for f_eff in EFF:
    tag = f"eff{f_eff:.1f}".replace(".", "p")
    y3s = y3 * scale[e_mid] * f_eff
    out[f"y3_{tag}"] = y3s
    out[f"pnl3_{tag}"] = y3s * cm_699 - INVEST
for (f_cvr, y3_cv, pnl_cv) in cvr_rows:
    tag = f"cvr{f_cvr:.1f}".replace(".", "p")
    out[f"y3_{tag}"] = y3_cv
    out[f"pnl3_{tag}"] = pnl_cv
np.savez(BASE + r"\scenario_s699_results.npz", **out)
print(f"\n[Saved] scenario_s699_results.npz（{len(out)} 个数组）")
