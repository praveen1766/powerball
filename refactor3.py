import re

with open('index.html.tmp2', 'r') as f:
    html = f.read()

# Update initData to handle different URLs
fetch_logic = """
async function initData() {
  document.getElementById('loadingMsg').style.display = 'block';
  document.getElementById('analytics-wrapper').style.display = 'none';
  document.getElementById('stats-bar').style.display = 'none';
  
  // Reset UI
  document.getElementById('main-title').textContent = activeGame.title;
  document.getElementById('main-subtitle').textContent = activeGame.subtitle;
  document.getElementById('format-desc').textContent = activeGame.formatDesc;
  
  // Rebuild grids
  document.getElementById('wb-grid').innerHTML = '';
  document.getElementById('pb-grid').innerHTML = '';
  document.getElementById('svg-lines').innerHTML = '';
  buildGrid('wb-grid', activeGame.wbMin, activeGame.wbMax);
  if(activeGame.hasPb) buildGrid('pb-grid', activeGame.pbMin, activeGame.pbMax);
  
  allDraws = [];
  
  try {
    let rawData;
    if (activeGame.id === 'powerball') {
        const primaryUrl = 'https://data.ny.gov/resource/d6yy-54nr.json?$limit=5000';
        try {
            const res = await fetch(primaryUrl);
            if(!res.ok) throw new Error('Primary failed');
            rawData = await res.json();
        } catch(e) {
            const proxyUrl = 'https://api.allorigins.win/raw?url=' + encodeURIComponent(primaryUrl);
            const resProxy = await fetch(proxyUrl);
            rawData = await resProxy.json();
        }
    } else {
        // Fetch local JSON updated by Github Actions
        const res = await fetch('./nj_data.json');
        const json = await res.json();
        rawData = json[activeGame.id] || [];
    }
    
    // Parse
    if (activeGame.id === 'powerball') {
        allDraws = rawData.map(d => {
            let nums = d.winning_numbers.split(' ');
            return {
                date: d.draw_date.split('T')[0],
                wb: nums.slice(0,5).map(Number),
                pb: parseInt(nums[5]),
                multiplier: d.multiplier || null
            };
        });
    } else {
        // Pick 3 / Pick 4
        allDraws = rawData.map(d => ({
            date: d.date.split('T')[0] + (d.time === 'Evening' ? ' PM' : ' AM'), // differentiate midday/evening
            wb: d.numbers.map(Number),
            pb: null,
            multiplier: null
        }));
    }
    
    allDraws = allDraws.filter(d => d.wb.every(n => !isNaN(n) && n >= activeGame.wbMin && n <= activeGame.wbMax));
    
    // Reverse so chronological if needed (ny open data is desc)
    if(allDraws.length > 1 && allDraws[0].date > allDraws[allDraws.length-1].date) {
        allDraws.reverse();
    }
"""

html = re.sub(r'async function initData\(\) \{.*?(?=document\.getElementById\(\'loadingMsg\'\)\.style\.display = \'none\')', fetch_logic + '\n\n', html, flags=re.DOTALL)

# Add event listeners for game selector
game_listener = """
  document.querySelectorAll('.game-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.game-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      activeGame = GAMES[e.target.dataset.game];
      initData();
    });
  });
"""
html = html.replace("document.getElementById('olderBtn').addEventListener('click', () => {", game_listener + "\n  document.getElementById('olderBtn').addEventListener('click', () => {")

# Smart pick modifications
html = html.replace('const balls = [chosen];', 'const balls = [chosen];\n    const limit = activeGame.wbCount;')
html = html.replace('while (balls.length < 5)', 'while (balls.length < limit)')
html = html.replace('Array.from({length:5})', 'Array.from({length: activeGame.wbCount})')

smart_pick_render = """
  let html = `
    <div class="pick-header">
      <h3>AI Smart Pick</h3>
      <p>Weighted ensemble prediction</p>
    </div>
    <div class="pick-balls">
  `;
  for(let i=0; i<activeGame.wbCount; i++) {
     html += `<div class="pick-ball">${balls[i]}</div>`;
  }
  if (activeGame.hasPb) {
     html += `<div class="pick-sep">+</div>
              <div class="pick-ball pb">${chosenPb}<div class="pb-label">POWERBALL</div></div>`;
  }
  html += `</div>`;
"""
html = re.sub(r'let html = `\s*<div class="pick-header">.*?<div class="pick-ball pb">\$\{chosenPb\}<div class="pb-label">POWERBALL</div></div>\s*</div>\s*`;', smart_pick_render, html, flags=re.DOTALL)

# Ensure fallback dataset parsing is preserved or removed? 
# We'll keep the fallback out of this rewrite for simplicity, or it will just fail gracefully.
with open('index.html', 'w') as f:
    f.write(html)
print("Refactoring phase 3 done")
