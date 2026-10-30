# -*- coding: utf-8 -*-
"""
米家口袋照片打印机 Pro（Ricotta）回测检验
==========================================
严格 ex-ante 设计（站位 2024-12，Ricotta Finance 表定稿时点）：

事前信息（当时可得）：
  · 内部三档预测（Ricotta Finance_241206）：
      Worst 首年 12 万 / Normal 40.8 万（国内 28.8 + 海外 12）/ Best 60 万
  · 参照 1：米家口袋照片打印机 1S（ZINK，¥399，小米生态链同品牌同渠道）
      —— 上市数年，京东单品 20 万+ 评价（生命周期累计约 50 万+ 台）
      —— 品牌力/传播/渠道与 Pro 完全匹配，但价位低 200 元、ZINK 画质弱
  · 参照 2：汉印 CP2100（热升华竞品，¥699 京东价）
      —— 京东约 2 万评价（生命周期约 5 万台），品牌弱于小米
  · Ricotta 定价 ¥599（1S 之上 200 元，CP2100 之下 100 元）
  · 小米品牌背书 + 米家 App 生态 + 京东小米自营渠道（1S 验证过的放量通道）

先验设定（站在 2024-12，全部用当时可得证据）：
  · m：1S 生命周期 ~50 万台是同品牌同品类天花板；Pro 价位更高 →
      取 1S 的 0.3~1.2 倍带：lognormal 中心 18 万、σ=0.85
      （P10≈6.2万 / P50≈18万 / P90≈52万，三年累计口径）
  · q：照片打印为已教育品类（1S/instax 已把市场带熟）→ q 中心 0.45，
      小米生态链自带流量转化 → 略高；σ=0.10
  · 漏斗：1S 是小米自营爆款，站内 CPM 低（~40）；CTR/CVR 用当时
      米家品类均值（CTR 2.5% / CVR 2.0%，小米自营店铺转化好于行业）
  · 预算：小米生态链产品的标准首发支持，6 个月 200-600 万
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20241206)  # 站位 2024-12-06（Finance 表定稿日）

N_SIM = 8000
T_MONTHS = 36

# ============ 事前先验 ============
m_prior = rng.lognormal(mean=np.log(180_000), sigma=0.85, size=N_SIM)
q_prior = np.clip(rng.normal(0.45, 0.10, size=N_SIM), 0.20, 0.70)

B_budget = rng.triangular(2_000_000, 4_000_000, 6_000_000, size=N_SIM)  # 6个月
CPM = rng.triangular(35, 42, 55, size=N_SIM)       # 小米自营站内
CTR = rng.triangular(0.020, 0.025, 0.032, size=N_SIM)
CVR = rng.triangular(0.015, 0.020, 0.028, size=N_SIM)

exposure = B_budget / CPM * 1000
clicks = exposure * CTR
s6_raw = clicks * CVR
s6 = np.minimum(s6_raw, m_prior * 0.55)

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

p_solved = solve_p(m_prior, q_prior, s6)
t_year = np.arange(1, T_MONTHS + 1) / 12.0
paths = bass_cum_year(m_prior[:, None], p_solved[:, None], q_prior[:, None], t_year[None, :])
y1 = paths[:, 11]   # 首年（含国内+海外，模型是总盘）
y3 = paths[:, 35]

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

# ============ 内部三档预测（Ricotta Finance 表） ============
INTERNAL = {"Worst": 120_000, "Normal": 408_000, "Best": 600_000}

print("=" * 70)
print("米家口袋照片打印机 Pro（Ricotta）回测 · 事前分布（2024-12 视角）")
print("=" * 70)
print(f"\n先验检查：m P10={pct(m_prior,10)/1e4:.1f}万 P50={pct(m_prior,50)/1e4:.1f}万 P90={pct(m_prior,90)/1e4:.1f}万（3年累计）")
print(f"漏斗中位：预算{pct(B_budget,50)/1e4:.0f}万 → 曝光{pct(exposure,50)/1e6:.0f}M → 点击{pct(clicks,50)/1e4:.0f}万 → 前6月{pct(s6,50)/1e4:.1f}万台")

print(f"\n【事前分布 · 首年（总盘=国内+海外）】")
print(f"  P5 ={pct(y1,5)/1e4:.1f}万   P10={pct(y1,10)/1e4:.1f}万   P20={pct(y1,20)/1e4:.1f}万   P50={pct(y1,50)/1e4:.1f}万   P80={pct(y1,80)/1e4:.1f}万   P90={pct(y1,90)/1e4:.1f}万   P95={pct(y1,95)/1e4:.1f}万")

print(f"\n【三年累计】")
print(f"  P10={pct(y3,10)/1e4:.1f}万   P50={pct(y3,50)/1e4:.1f}万   P90={pct(y3,90)/1e4:.1f}万")

# ============ 内部三档在事前分布中的位置 ============
print(f"\n【内部三档预测的位置检验】")
for name, v in INTERNAL.items():
    pos = float((y1 <= v).mean()) * 100
    print(f"  {name} {v/1e4:.0f}万台 → 事前分布 P{pos:.0f} 分位")

print(f"\n【关键概率（事前视角）】")
for th, label in [(120_000, "Worst 12万"), (408_000, "Normal 40.8万"), (600_000, "Best 60万")]:
    print(f"  P(首年 ≥ {label}) = {prob(y1, th)*100:.1f}%")

# 敏感性：漏斗参数对结果的影响（如果当时漏斗估计错了会怎样）
print(f"\n【敏感性 · 首年 P50】")
for cvr_lo, cvr_m, cvr_hi, tag in [
    (0.010, 0.014, 0.020, "CVR 悲观（1.4%中位）"),
    (0.015, 0.020, 0.028, "CVR 基准（2.0%中位）"),
    (0.022, 0.030, 0.040, "CVR 乐观（3.0%中位，1S爆款水平）"),
]:
    rng2 = np.random.default_rng(20241206)
    m2 = rng2.lognormal(mean=np.log(180_000), sigma=0.85, size=N_SIM)
    q2 = np.clip(rng2.normal(0.45, 0.10, size=N_SIM), 0.20, 0.70)
    B2 = rng2.triangular(2_000_000, 4_000_000, 6_000_000, size=N_SIM)
    C2 = rng2.triangular(35, 42, 55, size=N_SIM)
    T2 = rng2.triangular(0.020, 0.025, 0.032, size=N_SIM)
    V2 = rng2.triangular(cvr_lo, cvr_m, cvr_hi, size=N_SIM)
    s62 = np.minimum((B2/C2*1000)*T2*V2, m2*0.55)
    p2 = solve_p(m2, q2, s62)
    y1b = bass_cum_year(m2[:, None], p2[:, None], q2[:, None], t_year[None, :])[:, 11]
    print(f"  {tag}: P50={pct(y1b,50)/1e4:.1f}万  P(Normal 40.8万 达成)={prob(y1b, 408_000)*100:.0f}%")

np.savez(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\ricotta_backtest.npz",
         y1=y1, y3=y3, m_prior=m_prior, q_prior=q_prior, p_solved=p_solved, s6=s6)
print("\n[saved ricotta_backtest.npz]")
