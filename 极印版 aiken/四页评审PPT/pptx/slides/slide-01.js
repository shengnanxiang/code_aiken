// slide-01.js — AiKen × 极印品牌战略对齐（单页，对应 HTML 版全部内容）
const pptxgen = require("pptxgenjs");

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: "FFFFFF" };
  const F = "Microsoft YaHei";

  // ===== 顶部标题 =====
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.4, y: 0.32, w: 0.09, h: 0.52, fill: { color: "EC008C" } });
  slide.addText([
    { text: "AiKen × 极印品牌战略对齐 ", options: { fontSize: 22, bold: true, color: "111111" } },
    { text: "· 潮玩相机线，第一款", options: { fontSize: 22, bold: true, color: "EC008C" } },
  ], { x: 0.62, y: 0.26, w: 8.2, h: 0.6, fontFace: F, align: "left", valign: "middle" });
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.7, y: 0.3, w: 1.0, h: 0.34, fill: { color: "111111" }, rectRadius: 0.05 });
  slide.addText("评审 · 第1页", { x: 8.7, y: 0.3, w: 1.0, h: 0.34, fontSize: 9, fontFace: F, color: "FFFFFF", align: "center", valign: "middle" });
  slide.addShape(pres.shapes.LINE, { x: 0.4, y: 0.95, w: 9.3, h: 0, line: { color: "111111", width: 2 } });

  // ===== 三栏 =====
  const colY = 1.1, colH = 3.62;
  const colW = 3.0, gap = 0.15;

  // ---- A 栏 ----
  const ax = 0.4;
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: ax, y: colY, w: colW, h: colH, fill: { color: "FFFFFF" }, line: { color: "E6E6E6", width: 1 }, rectRadius: 0.06 });
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: ax + 0.12, y: colY + 0.1, w: 1.05, h: 0.26, fill: { color: "111111" }, rectRadius: 0.03 });
  slide.addText("A · 品牌战略骨架", { x: ax + 0.12, y: colY + 0.1, w: 1.05, h: 0.26, fontSize: 8.5, fontFace: F, color: "FFFFFF", align: "center", valign: "middle" });
  slide.addText("极印要成为什么", { x: ax + 0.12, y: colY + 0.42, w: 2.7, h: 0.3, fontSize: 13, bold: true, fontFace: F, color: "111111" });

  const kv = (y, k, v, vs) => {
    slide.addShape(pres.shapes.LINE, { x: ax + 0.16, y: y + 0.05, w: 0, h: 0.52, line: { color: "E6E6E6", width: 1.5 } });
    slide.addText(k, { x: ax + 0.26, y: y, w: 2.6, h: 0.18, fontSize: 7.5, fontFace: F, color: "6B6B6B" });
    slide.addText(v, { x: ax + 0.26, y: y + 0.16, w: 2.6, h: 0.24, fontSize: 9.5, bold: true, fontFace: F, color: "111111" });
    slide.addText(vs, { x: ax + 0.26, y: y + 0.38, w: 2.6, h: 0.2, fontSize: 7.5, fontFace: F, color: "6B6B6B" });
  };
  kv(colY + 0.78, "BRAND PURPOSE 品牌使命", "让值得留下来的，真正留下来", "洞察：记录越来越容易，真正留下越来越难");
  kv(colY + 1.42, "品牌原型 ARCHETYPE", "Creator 创造者（主）× Jester 玩趣派（辅）", "Creator 敢信敢下单 · Jester 敢玩玩上瘾");
  kv(colY + 2.06, "战略跃迁 STRATEGIC SHIFT", "工具型 → 情绪型 → 创作型生活方式", "打印机线立足工具型；AiKen 锚定情绪型");

  // 跃迁小图（三个台阶块）
  const ty = colY + 2.78;
  slide.addShape(pres.shapes.RECTANGLE, { x: ax + 0.22, y: ty + 0.32, w: 0.72, h: 0.26, fill: { color: "E6E6E6" } });
  slide.addShape(pres.shapes.RECTANGLE, { x: ax + 1.0, y: ty + 0.16, w: 0.72, h: 0.42, fill: { color: "111111" } });
  slide.addShape(pres.shapes.RECTANGLE, { x: ax + 1.78, y: ty, w: 0.72, h: 0.58, fill: { color: "00C2C2" }, fillOpacity: 0.3 });
  slide.addText("工具型", { x: ax + 0.22, y: ty + 0.32, w: 0.72, h: 0.26, fontSize: 7.5, fontFace: F, color: "6B6B6B", align: "center", valign: "middle" });
  slide.addText("情绪型", { x: ax + 1.0, y: ty + 0.16, w: 0.72, h: 0.42, fontSize: 7.5, fontFace: F, color: "FFFFFF", align: "center", valign: "middle", bold: true });
  slide.addText("创作型", { x: ax + 1.78, y: ty, w: 0.72, h: 0.58, fontSize: 7.5, fontFace: F, color: "007C7C", align: "center", valign: "middle", bold: true });
  slide.addText("▲ AiKen 跃迁先锋", { x: ax + 0.22, y: ty + 0.62, w: 2.4, h: 0.2, fontSize: 7.5, fontFace: F, color: "EC008C", bold: true });
  slide.addText("来源：《极印品牌战略与增长蓝图 v4》2026-08", { x: ax + 0.12, y: colY + colH - 0.24, w: 2.8, h: 0.18, fontSize: 6.5, fontFace: F, color: "9A9A9A" });

  // ---- B 栏 ----
  const bx = ax + colW + gap;
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx, y: colY, w: colW, h: colH, fill: { color: "FFFFFF" }, line: { color: "EC008C", width: 1.5 }, rectRadius: 0.06 });
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx + 0.12, y: colY + 0.1, w: 1.05, h: 0.26, fill: { color: "EC008C" }, rectRadius: 0.03 });
  slide.addText("B · AiKen 的位置", { x: bx + 0.12, y: colY + 0.1, w: 1.05, h: 0.26, fontSize: 8.5, fontFace: F, color: "FFFFFF", align: "center", valign: "middle" });
  slide.addText("品牌架构：三大品类", { x: bx + 0.12, y: colY + 0.42, w: 2.7, h: 0.3, fontSize: 13, bold: true, fontFace: F, color: "111111" });

  // 三个品类框
  const catY = colY + 0.82, catW = 0.87, catH = 0.78;
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx + 0.12, y: catY, w: catW, h: catH, fill: { color: "FDF3F8" }, line: { color: "EC008C", width: 1.75 }, rectRadius: 0.05 });
  slide.addText("潮玩相机", { x: bx + 0.12, y: catY + 0.08, w: catW, h: 0.22, fontSize: 9.5, bold: true, fontFace: F, color: "EC008C", align: "center" });
  slide.addText("AiKen ¥599\n首款", { x: bx + 0.12, y: catY + 0.3, w: catW, h: 0.42, fontSize: 7.5, fontFace: F, color: "6B6B6B", align: "center" });
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx + 1.06, y: catY, w: catW, h: catH, fill: { color: "FFFFFF" }, line: { color: "E6E6E6", width: 1 }, rectRadius: 0.05 });
  slide.addText("照片打印机", { x: bx + 1.06, y: catY + 0.08, w: catW, h: 0.22, fontSize: 9, bold: true, fontFace: F, color: "111111", align: "center" });
  slide.addText("N1 ¥459\nN3 ¥649  N2 ¥799", { x: bx + 1.06, y: catY + 0.3, w: catW, h: 0.42, fontSize: 7.5, fontFace: F, color: "6B6B6B", align: "center" });
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx + 2.0, y: catY, w: catW, h: catH, fill: { color: "FFFFFF" }, line: { color: "E6E6E6", width: 1 }, rectRadius: 0.05 });
  slide.addText("打印切割一体机", { x: bx + 2.0, y: catY + 0.08, w: catW, h: 0.22, fontSize: 8, bold: true, fontFace: F, color: "111111", align: "center" });
  slide.addText("S1 ¥1799\n创意旗舰", { x: bx + 2.0, y: catY + 0.3, w: catW, h: 0.42, fontSize: 7.5, fontFace: F, color: "6B6B6B", align: "center" });

  // 人群漏斗条
  const flY = catY + 0.95;
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx + 0.12, y: flY, w: 1.28, h: 0.66, fill: { color: "F7F7F7" }, rectRadius: 0.04 });
  slide.addText("AiKen 入口\n18–30 潮流青年\n认真拍下今天", { x: bx + 0.14, y: flY + 0.03, w: 1.24, h: 0.6, fontSize: 7.5, fontFace: F, color: "111111", align: "center", valign: "middle" });
  slide.addText("→", { x: bx + 1.42, y: flY + 0.12, w: 0.24, h: 0.4, fontSize: 14, fontFace: F, color: "EC008C", bold: true, align: "center", valign: "middle" });
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx + 1.68, y: flY, w: 1.28, h: 0.66, fill: { color: "F7F7F7" }, rectRadius: 0.04 });
  slide.addText("极印生态承接\n20–39 悦己氛围青年\n值得的，做成作品", { x: bx + 1.7, y: flY + 0.03, w: 1.24, h: 0.6, fontSize: 7.5, fontFace: F, color: "111111", align: "center", valign: "middle" });

  // 两条防线
  slide.addText([
    { text: "价位无冲突：", options: { bold: true } },
    { text: "AiKen ¥599 与 N3 ¥649 分属不同品类——卖「拍的仪式」vs 卖「印的便携」，货架陈列错位即可。\n", options: {} },
    { text: "人群无内耗：", options: { bold: true } },
    { text: "不碰「摄影摄像爱好者」（避开参数比较框架），该人群留给 N2/S1 承接。", options: {} },
  ], { x: bx + 0.12, y: flY + 0.78, w: 2.8, h: 0.95, fontSize: 8, fontFace: F, color: "444444", valign: "top", lineSpacingMultiple: 1.15 });

  // ---- C 栏 ----
  const cx = bx + colW + gap;
  const cW = 9.7 - (cx - 0.4) + 0.4; // 到右边界
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: colY, w: cW, h: colH, fill: { color: "FFFFFF" }, line: { color: "E6E6E6", width: 1 }, rectRadius: 0.06 });
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx + 0.12, y: colY + 0.1, w: 1.25, h: 0.26, fill: { color: "111111" }, rectRadius: 0.03 });
  slide.addText("C · AiKen 如何加分", { x: cx + 0.12, y: colY + 0.1, w: 1.25, h: 0.26, fontSize: 8.5, fontFace: F, color: "FFFFFF", align: "center", valign: "middle" });
  slide.addText("五个对齐点：战略要求 ↔ AiKen 供给", { x: cx + 0.12, y: colY + 0.42, w: cW - 0.24, h: 0.3, fontSize: 13, bold: true, fontFace: F, color: "111111" });

  const rows = [
    ["1", "品牌原型的极致载体", "36 张限额·封卷 = Creator 认真创作；盲拍惊喜·开盲盒 = Jester 玩趣彩蛋。打印机线 Jester 偏弱，AiKen 是首个双核打满的产品"],
    ["2", "情绪型跃迁的活证据", "从第一天就是纯情绪产品（设备仪式感 × 内容情感密度），是极印「非工具叙事」的第一件作品"],
    ["3", "核心人群的年轻入口", "覆盖 18–30 更年轻入口段，先进圈 → 导入打印机生态，拉低品牌人群年龄中位数"],
    ["4", "创作闭环补全上游", "品牌闭环默认素材来自手机；AiKen 把「素材输入」仪式化——盲拍是高光的发现机制，与下游作品化无缝衔接"],
    ["5", "团队能力的试验田", "练出的种草、内容与用户运营能力，全品牌长期复用（SI 第三点：锻炼 C 端潮玩打法）"],
  ];
  let ry = colY + 0.8;
  for (const [no, t, d] of rows) {
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx + 0.12, y: ry, w: cW - 0.24, h: 0.5, fill: { color: "FFFFFF" }, line: { color: "E6E6E6", width: 0.75 }, rectRadius: 0.04 });
    slide.addShape(pres.shapes.OVAL, { x: cx + 0.2, y: ry + 0.15, w: 0.21, h: 0.21, fill: { color: "111111" } });
    slide.addText(no, { x: cx + 0.2, y: ry + 0.15, w: 0.21, h: 0.21, fontSize: 8.5, fontFace: F, color: "FFFFFF", align: "center", valign: "middle", bold: true });
    slide.addText([
      { text: t + "　", options: { bold: true, fontSize: 8.5, color: "111111" } },
      { text: d, options: { fontSize: 7.5, color: "444444" } },
    ], { x: cx + 0.5, y: ry + 0.03, w: cW - 0.68, h: 0.44, fontFace: F, valign: "middle", lineSpacingMultiple: 1.05 });
    ry += 0.56;
  }

  // ===== 底部叙事链 =====
  const by = colY + colH + 0.12;
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.4, y: by, w: 9.3, h: 0.78, fill: { color: "FFFFFF" }, line: { color: "111111", width: 1.5 }, rectRadius: 0.06 });

  const chain = [
    ["AiKen 主张", "「因为不知道，所以认真」", "F7F7F7", "111111"],
    ["AiKen 行为", "认真拍下今天（发现高光）", "FDF3F8", "EC008C"],
    ["品牌 CCI", "「让今天值得留下来」", "111111", "FFFFFF"],
    ["生态承接（不入 AiKen 话术）", "值得的，做成作品", "F7F7F7", "111111"],
  ];
  let chx = 0.55;
  const chW = 2.06, chGap = 0.18;
  chain.forEach(([t, s, bg, fg], i) => {
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: chx, y: by + 0.09, w: chW, h: 0.44, fill: { color: bg }, rectRadius: 0.05 });
    slide.addText(t, { x: chx, y: by + 0.1, w: chW, h: 0.16, fontSize: 6.5, fontFace: F, color: bg === "111111" ? "BBBBBB" : "6B6B6B", align: "center" });
    slide.addText(s, { x: chx, y: by + 0.26, w: chW, h: 0.24, fontSize: 9, bold: true, fontFace: F, color: fg, align: "center" });
    if (i < 3) slide.addText("→", { x: chx + chW, y: by + 0.16, w: chGap, h: 0.3, fontSize: 11, fontFace: F, color: "EC008C", bold: true, align: "center", valign: "middle" });
    chx += chW + chGap;
  });
  slide.addText([
    { text: "CCI 纪律：", options: { bold: true, color: "EC008C" } },
    { text: "AiKen 语境沿用「让今天值得留下来」，不使用「把高光极印成我」——规避「印 / 打印」联想，用词与 MessageHouse 联动微调。", options: { color: "444444" } },
  ], { x: 0.55, y: by + 0.56, w: 9.0, h: 0.2, fontSize: 7.5, fontFace: F, valign: "middle" });

  return slide;
}

module.exports = { createSlide };
