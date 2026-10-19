# -*- coding: utf-8 -*-
"""AiKen 定价与销量情景测算 — 精确复刻用户模型口径（不含税净利）
模型口径验证点：
- Normal Y1 净利/台 = -1220.10（模型 -1220.09 ✓）
- Normal Y2 净利/台 = 188.82（模型 188.82 ✓）
- Best 3年累计 = 397.7万（模型 N13 ✓）
"""
MOLD_JIG = 1_315_000
OTHER_RD = 4_443_050
TOTAL_INV = MOLD_JIG + OTHER_RD  # 5,758,050

VAT = 1.13
MPC_Y = [250.6, 250.6 * 0.98, 250.6 * 0.98 ** 2]   # 出厂价含税，年降2%
LOGI = 0.58 / 1.09                                  # 物流不含税(9%)
REPAIR = 250.6 * 0.017 / VAT                        # 返修不含税(恒定)
SELL_RATE = 0.02                                    # 销售费率恒定2%(模型实际口径)

# 压力口径增量
PLATFORM_RATE = 0.8 * 0.045                         # 线上占比80% x 综合佣金4.5%
MKT_RATE_STRESS = [0.08, 0.06, 0.05]                # 新品类营销费率


def asp_list(price):
    y1 = price * 0.84
    return [y1, (y1 - 3) * 0.98, (y1 - 3) * 0.98 * 0.98]


def scenario(price, vols, stress=False):
    asps = asp_list(price)
    rows = []
    for i, vol in enumerate(vols):
        mpc = MPC_Y[i]
        moh = mpc * 0.05                             # MOH=5%×MPC含税(模型未做不含税处理)
        capital = mpc * 0.005                        # 资金成本=0.5%×MPC含税
        sell = asps[i] * SELL_RATE
        amort = (TOTAL_INV / vol / VAT) if i == 0 else 0.0
        asp_n = asps[i] / VAT
        mpc_n = mpc / VAT
        npu = asp_n - mpc_n - LOGI - moh - REPAIR - capital - sell - amort
        extras = []
        if stress:
            platform = asps[i] * PLATFORM_RATE
            mkt_add = asps[i] * (MKT_RATE_STRESS[i] - SELL_RATE)
            npu -= platform + mkt_add
            extras = [platform, mkt_add]
        rows.append(dict(year=i+1, vol=vol, asp=asps[i], npu=npu,
                         net=npu*vol, rev=asps[i]*vol,
                         amort=amort, extras=extras))
    total_net = sum(r['net'] for r in rows)
    return dict(rows=rows, total_vol=sum(vols),
                total_rev=sum(r['rev'] for r in rows),
                total_net=total_net, roi=total_net/TOTAL_INV)


print('=== 单台稳态净利（Y2口径，摊销后） ===')
for p in (499, 599):
    r = scenario(p, [1000, 1000, 1000])
    print(f'{p}: Y1 {r["rows"][0]["npu"]+TOTAL_INV/1000/VAT:.1f} / Y2 {r["rows"][1]["npu"]:.1f} / Y3 {r["rows"][2]["npu"]:.1f} 元/台')
    rs = scenario(p, [1000, 1000, 1000], stress=True)
    print(f'{p} 压力: Y2 {rs["rows"][1]["npu"]:.1f} / Y3 {rs["rows"][2]["npu"]:.1f} 元/台')

print()
print('=== 回本销量门槛 ===')
for p in (499, 599):
    for stress in (False, True):
        tag = '压力' if stress else '模型'
        lo, hi = 3000, 80000
        for _ in range(40):
            mid = (lo+hi)//2
            v = [mid, mid, mid]
            if scenario(p, v, stress)['total_net'] < 0:
                lo = mid
            else:
                hi = mid
        print(f'{p} {tag}口径: 均匀月销 {hi/12:,.0f} 台/月 x 3年 (年销 {hi:,}) 回本')

SCEN = {
    'Worst 保底': [2400, 2400, 1800],
    'Normal 基准': [4800, 8400, 7200],
    'Best 乐观': [12000, 21600, 18000],
}
for p in (499, 599):
    print(f'\n=== 情景测算 @{p} ===')
    for name, vols in SCEN.items():
        for stress in (False, True):
            tag = '压力' if stress else '模型'
            r = scenario(p, vols, stress)
            y1, y2, y3 = [x['net'] for x in r['rows']]
            print(f'{name}({tag}): 3年{r["total_vol"]:,}台 收入{r["total_rev"]/10000:,.0f}万 '
                  f'Y1 {y1/10000:,.0f}万 Y2 {y2/10000:,.0f}万 Y3 {y3/10000:,.0f}万 '
                  f'累计{r["total_net"]/10000:,.0f}万 ROI {r["roi"]*100:,.0f}%')
