# -*- coding: utf-8 -*-
"""
Gen2（CMF 迭代款）与 Gen3（Pro 款）销量概率分布模拟
=====================================================
用户输入（2026-10-27 17:24）：
  [时间] Gen2 = Gen1+6~12 月；Gen3 = Gen1+18 月
  [关系] Gen2 替代 Gen1；Gen3 与 Gen2 并行（人群重叠、价格敏感度分层）
  [Gen2] CMF 迭代：NRE 复用 80% → 按 100 万整算（ID+CMF only，软件/模具全复用）；价格维持 599
        CVR 提升至三角(1.5%,2.2%,3.0%)（用户认可）；m 与 Gen1 相同（不复购换壳）；
        资产推演前提 = Gen1 达 P50
  [Gen3] Pro：BOM 250→350，定价 999；NRE 300 万（软件复用，其余重做）
        定位 = 富士 X half（现价 ¥2,800-3,000）的 1/3 价格平替
        参照带：Kodak Mini Shot 3 Retro（¥1,059 促销）+ instax mini Evo（¥1,200-1,450，日本热销至计划 2 倍）
        CVR 三角(0.6%,1.0%,1.6%)；CTR 上修 2.5-3.5%（质感素材）；净贡献 ~152 元/台（渠道混合 ASP 717×70%-350）
        销售费用：与 Gen2 分摊（同人群池），投 Content 为主而非效果广告

建模口径：
  · Gen2 m：与 Gen1 相同先验（P50=11万），但增加约束——Gen2 独立销售窗口为 Gen1+6月 至 Gen3上市（约12个月主力期）
  · Gen2 漏斗：继承 Gen1 资产（App 用户池 = Gen1 销量×1.5；自然流量占比 30-40%）
  · Gen3 m：独立 ¥999 价位带（参照 Kodak/mini Evo 国内年销 1-3 万台量级 → P50≈1.8万）
  · 预算：Gen2 与 Gen3 并行期分摊（各 50%），Gen2 独占期全量
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20261027)
N_SIM = 8000

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

def bass_cum_year(m, p, q, t_year):
    t = np.asarray(t_year, dtype=float)
    denom = 1 + (q / p) * np.exp(-(p + q) * t)
    return m * (1 - np.exp(-(p + q) * t)) / denom

def solve_p(m, q, s6_target):
    lo = np.full_like(m, 1e-5); hi = np.full_like(m, 1.2)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        too_small = bass_cum_year(m, mid, q, 0.5) < s6_target
        lo = np.where(too_small, mid, lo); hi = np.where(too_small, hi, mid)
    return 0.5 * (lo + hi)

print("=" * 70)
print("Gen2 / Gen3 销量概率分布模拟（基于 Gen1 方法论 + Gen1@P50 资产推演）")
print("=" * 70)

# ================= Gen1 基准（P50 资产前提） =================
# Gen1 首年 P50 = 22,009；App 注册 = 销量 × 1.5 ≈ 33,000
GEN1_P50 = 22_009
APP_POOL = GEN1_P50 * 1.5

# ================= Gen2：CMF 迭代款（¥599） =================
# m：与 Gen1 相同（用户裁决：不至于一年再买换壳）
m2 = rng.lognormal(mean=np.log(110_000), sigma=0.85, size=N_SIM)
# q：市场已被 Gen1 教育一年 → 口碑系数上修
q2 = np.clip(rng.normal(0.48, 0.10, size=N_SIM), 0.22, 0.72)
# 漏斗：CVR 提升带（1.5/2.2/3.0），CTR 同 Gen1，CPM 略优（素材成熟+店铺权重）
# 预算：6个月 100-240 万（Gen1 同量级；若与 Gen3 并行期则减半，用混合）
B2 = rng.triangular(1_000_000, 1_500_000, 2_400_000, size=N_SIM)
CPM2 = rng.triangular(36, 42, 58, size=N_SIM)
CTR2 = rng.triangular(0.020, 0.026, 0.034, size=N_SIM)   # 素材迭代 + 认知提升
CVR2 = rng.triangular(0.015, 0.022, 0.030, size=N_SIM)   # 用户认可的带

exposure2 = B2 / CPM2 * 1000
paid2 = exposure2 * CTR2 * CVR2
# 自然流量：Gen1 资产（App 池 3.3万 + 品牌搜索），自然销量占比 25-40%
natural2 = rng.triangular(0.25, 0.32, 0.40, size=N_SIM) * paid2 / (1 - rng.triangular(0.25, 0.32, 0.40, size=N_SIM))
s6_2 = np.minimum(paid2 + natural2, m2 * 0.55)

p2 = solve_p(m2, q2, s6_2)
t_year = np.arange(1, 37) / 12.0
paths2 = bass_cum_year(m2[:, None], p2[:, None], q2[:, None], t_year[None, :])
# Gen2 主力销售窗：上市后 12 个月（之后被 Gen3 分流 + Gen1 完全退出）
y1_g2 = paths2[:, 11]
# 但 Gen2 是「替代盘」：三年累计不能超 m（与 Gen1 共享同一个 m 池——Gen1 已消耗的部分要扣）
# 简化处理：Gen2 的独立销量 = Bass 曲线，但 m 池按 Gen1 达 P50 后剩余潜力算
# Gen1 三年 P50 = 63,130（占 m P50=11万的 57%）→ 剩余 43% + 增量教育带来的 m 上浮
# 用户说 m 与 Gen1 相同 → Gen2 的可用 m = m - Gen1已消耗（用 P50 口径 63,130 做中心，带不确定性）
gen1_consumed = rng.normal(63_130, 12_000, size=N_SIM).clip(20_000)
m2_avail = np.maximum(m2 - gen1_consumed, 8_000)   # 剩余池下限 8 千
# 重跑 Gen2 曲线（用可用池）
p2b = solve_p(m2_avail, q2, s6_2)
paths2b = bass_cum_year(m2_avail[:, None], p2b[:, None], q2[:, None], t_year[None, :])
y1_g2 = paths2b[:, 11]
y2_g2 = paths2b[:, 23]
y3_g2 = paths2b[:, 35]

# Gen2 财务（NRE 100 万，净贡献 51.9 同 Gen1 + BOM 微降 2%）
CM2 = 52.9   # BOM 245 口径
NRE2 = 1_000_000
pnl_g2 = y3_g2 * CM2 - NRE2

print("\n【Gen2 · CMF 迭代款 ¥599（NRE 100 万 · 软件模具全复用）】")
print(f"  剩余 m 池: P10={pct(m2_avail,10)/1e4:.1f}万 P50={pct(m2_avail,50)/1e4:.1f}万 P90={pct(m2_avail,90)/1e4:.1f}万（Gen1@P50 消耗后）")
print(f"  首年销量: P10={pct(y1_g2,10):,.0f} P50={pct(y1_g2,50):,.0f} P90={pct(y1_g2,90):,.0f}")
print(f"  三年累计: P10={pct(y3_g2,10):,.0f} P50={pct(y3_g2,50):,.0f} P90={pct(y3_g2,90):,.0f}")
print(f"  三年净利: P10={pct(pnl_g2,10)/1e4:+.0f}万 P50={pct(pnl_g2,50)/1e4:+.0f}万 P90={pct(pnl_g2,90)/1e4:+.0f}万")
print(f"  P(三年转正) = {prob(pnl_g2,0)*100:.0f}%   P(首年≥1.5万) = {prob(y1_g2,15_000)*100:.0f}%")

# ================= Gen3：Pro 款（¥999） =================
# m：独立 ¥999 价位带。参照：Kodak Mini Shot（国内年销约1-2万）+ instax mini Evo（日本发售即计划2倍，全球热销）
# 国内 ¥1,000 价位「质感相机」盘子：P50 = 1.8 万（36个月累计），右尾到 5 万
m3 = rng.lognormal(mean=np.log(18_000), sigma=0.75, size=N_SIM)
q3 = np.clip(rng.normal(0.45, 0.12, size=N_SIM), 0.20, 0.70)
# 预算：与 Gen2 并行期分摊 → Pro 独立预算约 Gen1 的 40-60%（Content 为主，CPM 更贵但 CTR 更高）
B3 = rng.triangular(500_000, 850_000, 1_400_000, size=N_SIM)
CPM3 = rng.triangular(45, 58, 80, size=N_SIM)         # Content 投放更贵
CTR3 = rng.triangular(0.025, 0.030, 0.035, size=N_SIM) # 质感素材（金属蒙皮/氙灯）
CVR3 = rng.triangular(0.006, 0.010, 0.016, size=N_SIM) # ¥999 门槛
# 自然流量：Gen1+Gen2 双代资产 + X half 平替话题性
nat3_ratio = rng.triangular(0.30, 0.40, 0.50, size=N_SIM)

expo3 = B3 / CPM3 * 1000
paid3 = expo3 * CTR3 * CVR3
natural3 = nat3_ratio * paid3 / (1 - nat3_ratio)
s6_3 = np.minimum(paid3 + natural3, m3 * 0.60)

p3 = solve_p(m3, q3, s6_3)
paths3 = bass_cum_year(m3[:, None], p3[:, None], q3[:, None], t_year[None, :])
y1_g3 = paths3[:, 11]; y3_g3 = paths3[:, 35]

# Pro 财务：BOM 350 · 定价 999 · ASP 不含税 ≈ 717 · 净贡献 717×0.7−350 = 151.9
CM3 = 151.9
NRE3 = 3_000_000
pnl_g3 = y3_g3 * CM3 - NRE3

print("\n【Gen3 · Pro 款 ¥999（NRE 300 万 · BOM 350 · 净贡献 151.9 元/台）】")
print(f"  m 先验: P10={pct(m3,10)/1e4:.1f}万 P50={pct(m3,50)/1e4:.1f}万 P90={pct(m3,90)/1e4:.1f}万（参照 Kodak/mini Evo 价位带）")
print(f"  首年销量: P10={pct(y1_g3,10):,.0f} P50={pct(y1_g3,50):,.0f} P90={pct(y1_g3,90):,.0f}")
print(f"  三年累计: P10={pct(y3_g3,10):,.0f} P50={pct(y3_g3,50):,.0f} P90={pct(y3_g3,90):,.0f}")
print(f"  三年净利: P10={pct(pnl_g3,10)/1e4:+.0f}万 P50={pct(pnl_g3,50)/1e4:+.0f}万 P90={pct(pnl_g3,90)/1e4:+.0f}万")
print(f"  P(三年转正) = {prob(pnl_g3,0)*100:.0f}%   P(首年≥8,000) = {prob(y1_g3,8_000)*100:.0f}%")

# ================= 组合视角 =================
print("\n【组合视角（Gen1@P50 前提下）】")
# 品类组合三年累计净利（Gen1 亏 -150 已定 + Gen2 + Gen3 的分布）
pnl_combo = pnl_g2 + pnl_g3 - 1_500_000  # Gen1 Normal 口径 -150 万（三年）
print(f"  Gen1+Gen2+Gen3 三年累计净利: P10={pct(pnl_combo,10)/1e4:+.0f}万 P50={pct(pnl_combo,50)/1e4:+.0f}万 P90={pct(pnl_combo,90)/1e4:+.0f}万")
print(f"  P(组合三年整体转正) = {prob(pnl_combo,0)*100:.0f}%")

# 敏感性：Pro 的关键前提
print("\n【敏感性：Pro 净贡献与 m 的关键假设】")
for cm_test, label in [(151.9, "基准 151.9"), (120, "悲观 120（费用率上浮）"), (180, "乐观 180（BOM 良率改善）")]:
    pnl_t = y3_g3 * cm_test - NRE3
    print(f"  净贡献 {label}: P(三年转正)={prob(pnl_t,0)*100:.0f}%  P50 净利 {pct(pnl_t,50)/1e4:+.0f}万")
for m50, label in [(12_000, "m P50=1.2万（小众盘）"), (18_000, "基准 1.8万"), (28_000, "m P50=2.8万（X half 热度外溢）")]:
    m3t = rng.lognormal(mean=np.log(m50), sigma=0.75, size=N_SIM)
    s6t = np.minimum(paid3 + natural3, m3t * 0.60)
    p3t = solve_p(m3t, q3, s6t)
    pt = bass_cum_year(m3t[:, None], p3t[:, None], q3[:, None], t_year[None, :])[:, 35]
    pnl_t = pt * CM3 - NRE3
    print(f"  {label}: P50 三年销量 {pct(pt,50):,.0f}  P(转正)={prob(pnl_t,0)*100:.0f}%")

np.savez(
    r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\gen23_results.npz",
    y1_g2=y1_g2, y3_g2=y3_g2, pnl_g2=pnl_g2, m2_avail=m2_avail,
    y1_g3=y1_g3, y3_g3=y3_g3, pnl_g3=pnl_g3, m3=m3,
    pnl_combo=pnl_combo,
)
print("\n[Saved] gen23_results.npz")
