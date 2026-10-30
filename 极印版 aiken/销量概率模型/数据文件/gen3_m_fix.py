# -*- coding: utf-8 -*-
"""
Gen3 Pro · m 先验修正版
========================
用户修正（17:32）：Pro 的 m 不应只看 X half 平替，
而是整个「¥1,000+ 价位的复古/质感相机品类盘」：
  · 富士 instax 线 ¥1,000+ 覆盖：mini Evo（国行 ¥1,499）、mini 99（~¥1,299）、Wide Evo（更高）
  · Flashback One75（$179 ≈ ¥1,300，海外）
  · Rewindpix（$119 ≈ ¥860，Kickstarter 2026-06 发货，新兴）
  · Kodak Mini Shot 3 Retro（¥1,059-1,269）

参照类销量锚（调研 2026-10-27）：
  · mini Evo：日本发售即超计划 2 倍，助推富士登顶 BCN 不可换镜头相机榜——
    单款日本年销估计 15-25 万台，中国国行 ¥1,499 首年估计 3-6 万台
  · instax 全线 ¥1,000+（Evo + mini 99 + Wide Evo）中国市场年销估计 8-15 万台
  · Flashback One75/Rewindpix：海外众筹级（万级），国内未售
  · Kodak Mini Shot：国内年销 1-2 万台

修正后的 m 口径：¥1,000-1,500 复古质感相机中国市场
  P50 = 3.5 万（三年累计，取 instax ¥1,000+ 中国盘的下沿 + AiKen 品牌自身认知不及富士的折扣）
  sigma = 0.85（保留右尾：品类若被 X half/CCD 潮进一步放大，8 万+）
  Pro 可获取份额：AiKen 是这个价位带的新进入者（品牌力 < 富士），渗透率假设 30-60%
  → Pro 的有效 m = 品类盘 × 份额
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20261027)
N_SIM = 8000
t_year = np.arange(1, 37) / 12.0

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
print("Gen3 Pro · m 先验修正（整个 ¥1,000+ 复古质感相机品类盘 × AiKen 份额）")
print("=" * 70)

# ---- 品类盘：¥1,000-1,500 复古/质感相机中国市场（三年累计） ----
# 参照：instax ¥1,000+ 线中国年销 8-15 万台 → 三年盘 15-30 万，但含更低价段渗透
# 保守取 P50 = 20 万（三年品类盘），lognormal sigma 0.7（右尾到 50 万+，X half 效应）
cat_pool = rng.lognormal(mean=np.log(200_000), sigma=0.70, size=N_SIM)
print(f"\n品类盘（¥1,000-1,500 复古质感相机 · 中国 · 三年累计）")
print(f"  P10={pct(cat_pool,10)/1e4:.1f}万 P50={pct(cat_pool,50)/1e4:.1f}万 P90={pct(cat_pool,90)/1e4:.1f}万")
print(f"  参照锚：instax ¥1,000+ 中国年销 8-15 万（mini Evo 国行¥1,499 日本超计划2倍）")
print(f"          + Flashback One75($179)/Rewindpix($119) 海外众筹热 + Kodak Mini Shot ¥1,059")

# ---- AiKen Pro 份额 ----
# 新进入者 vs 富士品牌力；但 AiKen 有 Gen1/Gen2 用户池 + 平替价格（999 vs 1499）+ 生态联动
share = rng.triangular(0.15, 0.28, 0.50, size=N_SIM)
print(f"\nAiKen Pro 份额假设（品类盘中 Pro 能拿到的比例）")
print(f"  P10={pct(share,10)*100:.0f}% P50={pct(share,50)*100:.0f}% P90={pct(share,90)*100:.0f}%")
print(f"  逻辑：品牌力弱于富士（-），价格 999 vs mini Evo 1499（+），Gen1/2 用户池导流（+），打印生态（+）")

# ---- Pro 有效 m ----
m3 = cat_pool * share
print(f"\nPro 有效 m = 品类盘 × 份额")
print(f"  P10={pct(m3,10)/1e4:.2f}万 P50={pct(m3,50)/1e4:.2f}万 P90={pct(m3,90)/1e4:.2f}万")

# ---- 重跑 Pro（其余参数同前） ----
q3 = np.clip(rng.normal(0.45, 0.12, size=N_SIM), 0.20, 0.70)
B3 = rng.triangular(500_000, 850_000, 1_400_000, size=N_SIM)
CPM3 = rng.triangular(45, 58, 80, size=N_SIM)
CTR3 = rng.triangular(0.025, 0.030, 0.035, size=N_SIM)
CVR3 = rng.triangular(0.006, 0.010, 0.016, size=N_SIM)
nat3_ratio = rng.triangular(0.30, 0.40, 0.50, size=N_SIM)

expo3 = B3 / CPM3 * 1000
paid3 = expo3 * CTR3 * CVR3
natural3 = nat3_ratio * paid3 / (1 - nat3_ratio)
s6_3 = np.minimum(paid3 + natural3, m3 * 0.60)

p3 = solve_p(m3, q3, s6_3)
paths3 = bass_cum_year(m3[:, None], p3[:, None], q3[:, None], t_year[None, :])
y1_g3 = paths3[:, 11]; y3_g3 = paths3[:, 35]

CM3 = 151.9
NRE3 = 3_000_000
pnl_g3 = y3_g3 * CM3 - NRE3

print(f"\n【Gen3 Pro 修正后（品类盘口径 m）】")
print(f"  首年销量: P10={pct(y1_g3,10):,.0f} P50={pct(y1_g3,50):,.0f} P90={pct(y1_g3,90):,.0f}")
print(f"  三年累计: P10={pct(y3_g3,10):,.0f} P50={pct(y3_g3,50):,.0f} P90={pct(y3_g3,90):,.0f}")
print(f"  三年净利: P10={pct(pnl_g3,10)/1e4:+.0f}万 P50={pct(pnl_g3,50)/1e4:+.0f}万 P90={pct(pnl_g3,90)/1e4:+.0f}万")
print(f"  P(三年转正) = {prob(pnl_g3,0)*100:.0f}%")

# 对比旧口径
print(f"\n【对比：m 口径变化的影响】")
print(f"  旧（X half 平替窄口径）: m P50=1.8万  → P50 净利 -38万  P(转正)=42%")
print(f"  新（品类盘×份额口径）:   m P50={pct(m3,50)/1e4:.1f}万  → P50 净利 {pct(pnl_g3,50)/1e4:+.0f}万  P(转正)={prob(pnl_g3,0)*100:.0f}%")

# 份额敏感性（新口径下的关键杠杆）
print(f"\n【新口径下的关键杠杆：AiKen 份额】")
for sh_lo, sh_md, sh_hi, label in [(0.10, 0.18, 0.35, "悲观份额 18%"),
                                     (0.15, 0.28, 0.50, "基准份额 28%"),
                                     (0.25, 0.40, 0.60, "乐观份额 40%")]:
    sh = rng.triangular(sh_lo, sh_md, sh_hi, size=N_SIM)
    m3t = cat_pool * sh
    s6t = np.minimum(paid3 + natural3, m3t * 0.60)
    p3t = solve_p(m3t, q3, s6t)
    pt = bass_cum_year(m3t[:, None], p3t[:, None], q3[:, None], t_year[None, :])[:, 35]
    pnl_t = pt * CM3 - NRE3
    print(f"  {label}: m P50={pct(m3t,50)/1e4:.1f}万  P50三年={pct(pt,50):,.0f}  P(转正)={prob(pnl_t,0)*100:.0f}%")

# 组合更新
D = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\gen23_results.npz")
pnl_g2 = D["pnl_g2"]
pnl_combo_new = pnl_g2 + pnl_g3 - 1_500_000
print(f"\n【组合更新（新 m 口径）】")
print(f"  Gen1+Gen2+Gen3 三年累计: P10={pct(pnl_combo_new,10)/1e4:+.0f}万 P50={pct(pnl_combo_new,50)/1e4:+.0f}万 P90={pct(pnl_combo_new,90)/1e4:+.0f}万")
print(f"  P(组合三年整体转正) = {prob(pnl_combo_new,0)*100:.0f}%")

np.savez(
    r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\gen23_results_v2.npz",
    y1_g3=y1_g3, y3_g3=y3_g3, pnl_g3=pnl_g3, m3=m3,
    cat_pool=cat_pool, share=share, pnl_combo=pnl_combo_new,
)
print("\n[Saved] gen23_results_v2.npz")
