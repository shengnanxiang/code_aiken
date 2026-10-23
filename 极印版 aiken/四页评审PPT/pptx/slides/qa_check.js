// qa_check.js — QA：复制为 zip 解压并验证内容
const fs = require('fs');
const { execSync } = require('child_process');

fs.copyFileSync('output/AiKen品牌战略对齐页.pptx', '_qa_copy.zip');
execSync('powershell -Command "Expand-Archive -Path _qa_copy.zip -DestinationPath _qa -Force"');

const s1 = fs.readFileSync('_qa/ppt/slides/slide1.xml', 'utf8');
const checks = [
  '潮玩相机', '照片打印机', '打印切割一体机', '让今天值得留下来',
  '因为不知道，所以认真', '五个对齐点', 'Creator', 'Jester',
  '生态承接', '认真拍下今天', 'AiKen ¥599', '工具型', '情绪型', '创作型',
  'CCI 纪律', '把高光极印成我', '年轻入口', '试验田', '双核', '盲拍'
];
let p = 0, f = 0;
checks.forEach(c => {
  const ok = s1.includes(c);
  ok ? p++ : f++;
  console.log((ok ? 'PASS' : 'FAIL') + ': ' + c);
});
console.log(p + '/' + checks.length + ' passed');
process.exit(f > 0 ? 1 : 0);
