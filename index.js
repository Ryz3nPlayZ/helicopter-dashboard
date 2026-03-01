#!/usr/bin/env node

const blessed = require('blessed');

// Create screen with auto-resize
const screen = blessed.screen({
  smartCSR: true,
  title: '🚁 Helicopter Terminal',
  fullUnicode: true,
  autoRefresh: true,
});

// Make it resizeable
screen.on('resize', () => {
  render();
});

// Colors
const colors = {
  green: '#00ff00',
  red: '#ff0000',
  cyan: '#00ffff',
  yellow: '#ffff00',
  magenta: '#ff00ff',
  white: '#ffffff',
  bg: '#0a0a0f',
};

// Sample data (would come from APIs)
const data = {
  watchlist: [
    { symbol: 'BTC', price: '67,234', change: '+2.34%', up: true },
    { symbol: 'ETH', price: '3,456', change: '+1.12%', up: true },
    { symbol: 'SOL', price: '142.33', change: '-0.89%', up: false },
    { symbol: 'NVDA', price: '892.45', change: '+4.56%', up: true },
    { symbol: 'AAPL', price: '178.32', change: '+0.23%', up: true },
  ],
};

// Pad helper
const pad = (s, n) => String(s) + ' '.repeat(Math.max(0, n - String(s).length));

// Render function that adapts to screen size
function render() {
  // Clear existing boxes
  while (screen.children.length > 0) {
    screen.remove(screen.children[0]);
  }
  
  const w = screen.width;
  const h = screen.height;
  
  // Minimum sizes
  if (w < 80 || h < 20) {
    return; // Too small
  }
  
  const colW = Math.floor(w / 3);
  const mainH = Math.floor(h * 0.55);
  const botH = h - mainH - 5;
  
  // Header
  screen.append(blessed.box({
    top: 0, left: 0, width: w, height: 3,
    style: { bg: '#1a1a2e', fg: '#ffffff' },
    content: ` {bold}🚁 HELICOPTER TERMINAL v1.0{/bold}`,
  }));
  
  // 3 columns
  const left = blessed.box({
    top: 3, left: 0, width: colW, height: mainH,
    border: { type: 'line', fg: 'cyan' }, style: { bg: colors.bg, border: { fg: 'cyan' } },
    label: ' 📋 WATCHLIST ',
  });
  
  const mid = blessed.box({
    top: 3, left: colW, width: colW, height: mainH,
    border: { type: 'line', fg: 'yellow' }, style: { bg: colors.bg, border: { fg: 'yellow' } },
    label: ' 📊 CHART ',
  });
  
  const right = blessed.box({
    top: 3, left: colW * 2, width: w - colW * 2, height: mainH,
    border: { type: 'line', fg: 'magenta' }, style: { bg: colors.bg, border: { fg: 'magenta' } },
    label: ' 📋 ORDER BOOK ',
  });
  
  screen.append(left);
  screen.append(mid);
  screen.append(right);
  
  // Bottom 3 columns
  const botLeft = blessed.box({
    top: 3 + mainH, left: 0, width: colW, height: botH - 1,
    border: { type: 'line', fg: 'green' }, style: { bg: colors.bg, border: { fg: 'green' } },
    label: ' 💼 PORTFOLIO ',
  });
  
  const botMid = blessed.box({
    top: 3 + mainH, left: colW, width: colW, height: botH - 1,
    border: { type: 'line', fg: 'yellow' }, style: { bg: colors.bg, border: { fg: 'yellow' } },
    label: ' 📰 NEWS ',
  });
  
  const botRight = blessed.box({
    top: 3 + mainH, left: colW * 2, width: w - colW * 2, height: botH - 1,
    border: { type: 'line', fg: 'cyan' }, style: { bg: colors.bg, border: { fg: 'cyan' } },
    label: ' ⚡ SYSTEM ',
  });
  
  screen.append(botLeft);
  screen.append(botMid);
  screen.append(botRight);
  
  // Footer
  screen.append(blessed.box({
    top: h - 2, left: 0, width: w, height: 2,
    style: { bg: '#1a1a2e', fg: '#888888' },
    content: ' Arrow Keys: Navigate | Space: Refresh | q: Quit | Tab: Switch Panel ',
  }));
  
  // Populate
  let wl = '\n';
  data.watchlist.forEach(item => {
    const arrow = item.up ? '▲' : '▼';
    const col = item.up ? '{green}' : '{red}';
    wl += `{cyan}${item.symbol}{/cyan}   ${col}${item.price}{/}  ${col}${arrow}${item.change}{/}\n`;
  });
  left.setContent(wl);
  
  // Simple chart
  let chart = '\n';
  const prices = [67, 68, 66, 69, 70, 68, 71, 69, 72, 70, 73, 71, 74, 72, 75];
  for (let row = 0; row < 10; row++) {
    chart += ' ' + String(75 - row * 2).padStart(5) + ' │';
    for (let i = 0; i < prices.length; i++) {
      const p = prices[i];
      const inBand = p >= (73 - row * 2) && p <= (77 - row * 2);
      chart += inBand ? (p >= prices[i-1] || i === 0 ? '{green}█{/}' : '{red}█{/}') : ' ';
    }
    chart += '\n';
  }
  chart += '       └' + '─'.repeat(prices.length + 1) + '\n';
  chart += '       09  10  11  12  13  14  15  16  17  18  19';
  mid.setContent(chart);
  
  // Order book
  let ob = '\n';
  for (let i = 0; i < 8; i++) {
    const bid = (67000 + i).toString();
    const ask = (67001 + i).toString();
    const bv = (Math.random() * 5).toFixed(1);
    const av = (Math.random() * 5).toFixed(1);
    ob += `{green}${bid.padEnd(8)}{/} ${bid.padEnd(5)}  │  {red}${ask.padEnd(8)}{/} ${av}\n`;
  }
  right.setContent(ob);
  
  // Portfolio
  let pf = '\n{cyan}Asset    Amount    Value        %{/}\n';
  pf += '{cyan}───────  ──────  ──────────  ───{/}\n';
  pf += 'BTC      1.25     $120,917     45%\n';
  pf += 'ETH      8.5      $29,376      11%\n';
  pf += 'SOL      150      $21,349      8%\n';
  pf += 'USDC     $58,000  $58,000      21%\n';
  pf += '\n{green}{bold}TOTAL: $269,785{/}\n';
  botLeft.setContent(pf);
  
  // News
  let news = '\n{yellow}●{/} Fed signals rate cut\n{yellow}●{/} BTC ETF inflows: $420M\n{yellow}●{/} SEC approves ETH ETF\n{yellow}●{/} MicroStrategy buys 1K';
  botMid.setContent(news);
  
  // System
  let sys = '\n{cyan}APIs:{/}\n';
  sys += '  ✓ Polygon   Connected\n';
  sys += '  ✓ Binance    Connected\n';
  sys += '\n{cyan}Memory:{/}\n';
  sys += '  RAM: 2.4GB / 8GB\n';
  sys += '\n{cyan}Status:{/} {green}ACTIVE{/}\n';
  sys += 'Uptime: 4h 23m';
  botRight.setContent(sys);
  
  screen.render();
}

// Initial render
render();

// Auto-refresh every 3 seconds
const interval = setInterval(() => {
  data.watchlist.forEach(item => {
    const change = (Math.random() * 4 - 2).toFixed(2);
    item.change = (change >= 0 ? '+' : '') + change + '%';
    item.up = parseFloat(change) >= 0;
  });
  render();
}, 3000);

// Quit
screen.key(['q', 'C-c'], () => {
  clearInterval(interval);
  process.exit(0);
});


