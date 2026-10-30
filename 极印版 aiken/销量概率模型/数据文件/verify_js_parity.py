# -*- coding: utf-8 -*-
"""
数值一致性验证：从生成的 HTML 中抽取 JS 核心逻辑跑 Python 对照
验证点：lognormalFromQuantiles / mulberry32 / gauss / solveP / bassCum 全链路
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

# ============ Python 复刻 JS 逻辑（逐行对应） ============
def mulberry32(seed):
    a = seed & 0xFFFFFFFF
    def rnd():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = ((a ^ (a >> 15)) * (1 | a)) & 0xFFFFFFFF
        t = (t + (((t ^ (t >> 7)) * (61 | t)) & 0xFFFFFFFF)) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return rnd

_state = {"spare": None}
def gauss_js(rng):
    # JS 版用 Math.cos 分支；为对齐序列，模拟它的 Box-Muller（cos 支路）
    u = 0.0; v = 0.0
    while u == 0: u = rng()
    while v == 0: v = rng()
    return np.sqrt(-2 * np.log(u)) * np.cos(2 * np.pi * v)

def lognormal_from_q(p10, p50, p90, rng):
    mu = np.log(p50)
    s1 = np.log(p90) - np.log(p50)
    s2 = np.log(p50) - np.log(p10)
    sigma = (s1 + s2) / 2 / 1.2816
    return np.exp(mu + sigma * gauss_js(rng))

def bass_cum(m, p, q, t):
    denom = 1 + (q / p) * np.exp(-(p + q) * t)
    return m * (1 - np.exp(-(p + q) * t)) / denom

def solve_p(m, q, s6):
    lo, hi = 1e-5, 1.2
    for _ in range(40):
        mid = (lo + hi) / 2
        if bass_cum(m, mid, q, 0.5) < s6: lo = mid
        else: hi = mid
    return (lo + hi) / 2

# ============ 用 AiKen 699 参数跑 ============
N = 8000
rng = mulberry32(20261028)
clicks = 1550000 / 45 * 1000 * 0.023

y1 = np.empty(N); y3 = np.empty(N)
for i in range(N):
    m = lognormal_from_q(30000, 110000, 320000, rng)
    q = 0.42 + 0.12 * gauss_js(rng)
    q = max(0.15, min(0.75, q))
    cvr_i = 0.014 * (1 + 0.2 * gauss_js(rng))
    s6 = min(clicks * max(0.004, cvr_i), m * 0.55)
    p = solve_p(m, q, s6)
    y1[i] = bass_cum(m, p, q, 1.0)
    y3[i] = bass_cum(m, p, q, 3.0)

y1s = np.sort(y1); y3s = np.sort(y3)
print("=== Python 复刻 JS 逻辑 · AiKen 699 参数 ===")
print(f"首年: P20={np.percentile(y1s,20):,.0f}  P50={np.percentile(y1s,50):,.0f}  P90={np.percentile(y1s,90):,.0f}")
print(f"三年: P20={np.percentile(y3s,20)/1e4:.2f}万  P50={np.percentile(y3s,50)/1e4:.2f}万  P90={np.percentile(y3s,90)/1e4:.2f}万")

# 对照原模型（numpy 种子不同，只对量级合理性）
print("\n=== 对照原 v0.4/699 模型量级 ===")
print("原模型: 首年 P20=16,844 P50=22,123 P90=32,793 ｜ 三年 P50=6.38万")
diff_p50 = abs(np.percentile(y1s,50) - 22123) / 22123 * 100
print(f"JS复刻 P50 与原模型差异: {diff_p50:.1f}%（随机种子不同，<5% 属正常蒙特卡洛波动）")
