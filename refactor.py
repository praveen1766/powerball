import re

with open('index.html', 'r') as f:
    html = f.read()

# Add game state and configuration
game_config = """
// ── Game Configuration ──────────────────────────────────────────────────────────
const GAMES = {
  powerball: {
    id: 'powerball',
    name: 'Powerball',
    wbMin: 1, wbMax: 69, pbMin: 1, pbMax: 26,
    wbCount: 5, hasPb: true,
    title: 'Powerball Analytics', subtitle: 'Interactive visualizer with historical pattern analysis',
    formatDesc: 'Current format · 5 of 69 + PB 1–26'
  },
  pick3: {
    id: 'pick3',
    name: 'Pick 3',
    wbMin: 0, wbMax: 9, pbMin: 0, pbMax: 0,
    wbCount: 3, hasPb: false,
    title: 'NJ Pick 3 Analytics', subtitle: 'Historical numbers analysis',
    formatDesc: 'Pick 3 · 3 Digits (0–9)'
  },
  pick4: {
    id: 'pick4',
    name: 'Pick 4',
    wbMin: 0, wbMax: 9, pbMin: 0, pbMax: 0,
    wbCount: 4, hasPb: false,
    title: 'NJ Pick 4 Analytics', subtitle: 'Historical numbers analysis',
    formatDesc: 'Pick 4 · 4 Digits (0–9)'
  }
};
let activeGame = GAMES.powerball;
"""

# Insert Game Config at the start of the JS
html = html.replace('// ── Global State ─────────────────────────────────────────────────────────', game_config + '\n// ── Global State ─────────────────────────────────────────────────────────')

# Inject Game Selector in HTML
game_selector_html = """
<div class="game-selector">
  <button class="game-btn active" data-game="powerball">Powerball</button>
  <button class="game-btn" data-game="pick3">Play 3</button>
  <button class="game-btn" data-game="pick4">Play 4</button>
</div>
"""
html = html.replace('<h1>Powerball Analytics</h1>', f'<h1 id="main-title">Powerball Analytics</h1>{game_selector_html}')
html = html.replace('<p class="subtitle">Interactive visualizer with historical pattern analysis</p>', '<p id="main-subtitle" class="subtitle">Interactive visualizer with historical pattern analysis</p>')
html = html.replace('<span>Current format · 5 of 69 + PB 1–26</span>', '<span id="format-desc">Current format · 5 of 69 + PB 1–26</span>')

# Inject Game Selector CSS
css = """
  .game-selector {
    display: flex; gap: 10px; justify-content: center; margin: 15px 0 25px;
  }
  .game-btn {
    padding: 8px 20px; border: 2px solid #e52b36; border-radius: 999px;
    background: transparent; color: #e52b36; font-weight: 700; font-family: inherit;
    cursor: pointer; transition: all 0.2s;
  }
  .game-btn:hover { background: #fef2f2; }
  .game-btn.active { background: #e52b36; color: white; }
"""
html = html.replace('</style>', css + '\n</style>')

# Write back for now
with open('index.html.tmp', 'w') as f:
    f.write(html)
print("Refactoring phase 1 done")
