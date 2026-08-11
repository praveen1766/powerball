import re

with open('index.html.tmp', 'r') as f:
    html = f.read()

# buildGrid function
html = html.replace('function buildGrid(containerId, maxNum) {', 'function buildGrid(containerId, minNum, maxNum) {')
html = html.replace('for (let i = 1; i <= maxNum; i++) {', 'for (let i = minNum; i <= maxNum; i++) {')

# Calls to buildGrid
html = html.replace("buildGrid('wb-grid', 69);", "buildGrid('wb-grid', activeGame.wbMin, activeGame.wbMax);")
html = html.replace("buildGrid('pb-grid', 26);", "buildGrid('pb-grid', activeGame.pbMin, activeGame.pbMax);")

# Update render() grid headers
grid_header_replacement = """
  document.querySelector('#wb-grid').previousElementSibling.previousElementSibling.textContent = activeGame.gridHeaders ? activeGame.gridHeaders[0] : `White Balls (${activeGame.wbMin} – ${activeGame.wbMax})`;
  const pbHeader = document.querySelector('#pb-grid').previousElementSibling;
  if(activeGame.hasPb) {
      pbHeader.parentElement.style.display = 'block';
      pbHeader.textContent = activeGame.gridHeaders ? activeGame.gridHeaders[1] : `Powerball (${activeGame.pbMin} – ${activeGame.pbMax})`;
  } else {
      pbHeader.parentElement.style.display = 'none';
  }
"""
html = html.replace("const d = allDraws[currentIndex];", grid_header_replacement + "\n  const d = allDraws[currentIndex];")

# Replace maxWb usages and hardcoded 69 loops
html = html.replace('for (let i = 1; i <= 69; i++)', 'for (let i = activeGame.wbMin; i <= activeGame.wbMax; i++)')
html = html.replace('for (let i=1;i<=69;i++)', 'for (let i = activeGame.wbMin; i <= activeGame.wbMax; i++)')
html = html.replace('for (let n = 1; n <= 69; n++)', 'for (let n = activeGame.wbMin; n <= activeGame.wbMax; n++)')

# Replace maxPb usages and hardcoded 26 loops
html = html.replace('for (let i = 1; i <= 26; i++)', 'for (let i = activeGame.pbMin; i <= activeGame.pbMax; i++)')
html = html.replace('for (let i=1;i<=26;i++)', 'for (let i = activeGame.pbMin; i <= activeGame.pbMax; i++)')
html = html.replace('for (let p = 1; p <= 26; p++)', 'for (let p = activeGame.pbMin; p <= activeGame.pbMax; p++)')

# Replace boundary checks 1..69 and 1..26
html = html.replace('n >= 1 && n <= 69', 'n >= activeGame.wbMin && n <= activeGame.wbMax')
html = html.replace('d.pb >= 1 && d.pb <= 26', 'd.pb >= activeGame.pbMin && d.pb <= activeGame.pbMax')
html = html.replace('chosen = Math.max(1, Math.min(69, chosen));', 'chosen = Math.max(activeGame.wbMin, Math.min(activeGame.wbMax, chosen));')
html = html.replace('chosenPb = Math.max(1, Math.min(26, chosenPb));', 'chosenPb = Math.max(activeGame.pbMin, Math.min(activeGame.pbMax, chosenPb));')

# Replace hardcoded counts
html = html.replace('const max = trendType === \'wb\' ? 69 : 26;', 'const max = trendType === \'wb\' ? activeGame.wbMax : activeGame.pbMax;\n  const min = trendType === \'wb\' ? activeGame.wbMin : activeGame.pbMin;')
html = html.replace('let n = parseInt(trendDisplay.textContent);', 'let n = parseInt(trendDisplay.textContent);\n  if(isNaN(n)) n = min;')
html = html.replace('if (n > max) n = 1;', 'if (n > max) n = min;')
html = html.replace('if (n < 1) n = max;', 'if (n < min) n = max;')

# Remove Power Play tab entirely when not Powerball
tab_logic = """
  document.querySelector('[data-tab="powerplay"]').style.display = activeGame.hasPb ? 'block' : 'none';
  document.querySelector('[data-tab="gap"]').style.display = activeGame.hasPb ? 'block' : 'none'; // Simplify for Pick3/4
  
  if (!activeGame.hasPb && (activeTab === 'powerplay' || activeTab === 'gap')) {
    activeTab = 'freq';
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelector('[data-tab="freq"]').classList.add('active');
  }
"""
html = html.replace('function renderTab() {', 'function renderTab() {' + tab_logic)

with open('index.html.tmp2', 'w') as f:
    f.write(html)
print("Refactoring phase 2 done")
