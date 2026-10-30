# -*- coding: utf-8 -*-
"""修补 make_review_slide_699.py：锚改为 P20/P50/P90"""
import io

p = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\make_review_slide_699.py"
src = io.open(p, encoding="utf-8").read()

# 1. 首年图：P10 竖线改为 P20（Worst 锚）
src = src.replace(
    '''    marks=[(pct(y1,10), "P10", "#C0392B", "4 3"),
           (pct(y1,50), "P50", "#111", "4 3"),
           (pct(y1,90), "P90", "#7A4FA0", "4 3")],
    shade=(pct(y1,90), f"P(≥P90) = 10%"),''',
    '''    marks=[(pct(y1,20), "P20·Worst", "#C0392B", "4 3"),
           (pct(y1,50), "P50·Normal", "#111", "4 3"),
           (pct(y1,90), "P90·Best", "#7A4FA0", "4 3")],
    shade=(pct(y1,90), f"P(≥P90) = 10%"),''')

# 2. KPI 卡：Worst 锚改用 P20
src = src.replace(
    '''    <div class="kpi"><div class="k">Worst 锚（P10）</div><div class="v">__Y1_P10__<em> 台</em></div><div class="s">首年平均月销 ~__M_WORST__ ｜ 备选 P20=__Y1_P20__（月均 ~__M_P20__）</div></div>''',
    '''    <div class="kpi"><div class="k">Worst 锚（P20）</div><div class="v">__Y1_P20__<em> 台</em></div><div class="s">首年平均月销 ~__M_P20__ ｜ 跌破概率 20%（80% 置信守线）</div></div>''')

# 3. 杠杆卡对照锚
src = src.replace(
    '''<div class="s">P(≥P90) 10%→__BOOST_P90__ ｜ P(≥3.0万 Best锚) 16%→__BOOST_BEST__ ｜ 花钱买概率增量</div>''',
    '''<div class="s">P(≥P90 Best) 10%→__BOOST_P90__ ｜ P(≥Worst P20) 80%→__BOOST_W20__ ｜ 花钱买概率增量</div>''')

# 4. 替换段加 BOOST_W20
src = src.replace(
    '''    .replace("__BOOST_P90__", f"{prob(y1_b, pct(y1,90))*100:.0f}%")''',
    '''    .replace("__BOOST_P90__", f"{prob(y1_b, pct(y1,90))*100:.0f}%")
    .replace("__BOOST_W20__", f"{prob(y1_b, pct(y1,20))*100:.0f}%")''')

# 5. 副注
src = src.replace("三档锚 = P10 / P50 / P90", "三档锚 = P20（Worst）/ P50（Normal）/ P90（Best）")

# 6. 首年 nums 行
src = src.replace(
    '''      <div class="nums">P10 <b>__Y1_P10__</b> ｜ P50 <b>__Y1_P50__</b> ｜ P90 <b>__Y1_P90__</b></div>''',
    '''      <div class="nums">P20·Worst <b>__Y1_P20__</b> ｜ P50·Normal <b>__Y1_P50__</b> ｜ P90·Best <b>__Y1_P90__</b></div>''')

io.open(p, "w", encoding="utf-8").write(src)
print("patched OK")
