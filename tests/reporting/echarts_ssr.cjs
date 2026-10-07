// Read-only SVG rendering QA with the packaged upstream ECharts runtime.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const echarts = require('../../src/trust_receipt/reporting/assets/echarts/echarts-6.0.0.min.js');

const directory = process.argv[2];
assert(directory, 'Provide a directory containing *.option.json');
let count = 0;
for (const name of fs.readdirSync(directory).filter(name => name.endsWith('.option.json'))) {
  const option = JSON.parse(fs.readFileSync(path.join(directory, name), 'utf8'));
  for (const width of [390, 1440]) {
    const chart = echarts.init(null, null, { renderer: 'svg', ssr: true, width, height: 480 });
    try {
      chart.setOption(option);
      const svg = chart.renderToSVGString();
      assert(svg.includes('<svg'), 'No SVG produced');
      assert(!svg.includes('<script'), 'Unexpected script in static graph');
      assert(!svg.includes('NaN'), 'Invalid visual coordinates');
      fs.writeFileSync(path.join(directory, `${name}.${width}.svg`), svg);
      console.log(name, width, svg.length, 'SVG rendered');
      count++;
    } finally {
      chart.dispose();
    }
  }
}
assert(count > 0, 'No input graph options');
