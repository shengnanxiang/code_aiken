// compile.js — 编译品牌战略对齐页为 PPTX
const pptxgen = require('pptxgenjs');
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';

const theme = { primary: "111111", secondary: "444444", accent: "EC008C", light: "FDF3F8", bg: "FFFFFF" };

const slideModule = require('./slide-01.js');
slideModule.createSlide(pres, theme);

pres.writeFile({ fileName: './output/AiKen品牌战略对齐页.pptx' }).then(() => {
  console.log('OK: AiKen品牌战略对齐页.pptx');
});
