# Powerball & NJ Lottery Analytics

An interactive, client-side data visualization and analytics dashboard for **Powerball**, **NJ Pick 3**, and **NJ Pick 4**. This application uses historical lottery data to generate statistical insights, spot trends, and provide an AI-weighted "Smart Pick" ensemble generator.

## Features

- **Multi-Game Support**: Seamlessly toggle between Powerball, NJ Pick 3, and NJ Pick 4.
- **Interactive Visualizations**: View comprehensive data charts with tooltips and dynamic highlights.
- **Statistical Analytics Engine**:
  - **Frequency Chart**: See the total number of appearances for each digit/ball.
  - **Hot & Cold Analysis**: Track the most frequently and least frequently drawn numbers with variable lookback windows (e.g., last 20, 50, or 100 draws).
  - **Gap Analysis**: Identifies overdue numbers based on draws since their last appearance.
  - **Pair Correlation** *(Powerball Only)*: Shows which numbers frequently appear together in the same draw.
  - **Day Patterns**: See which days are most popular for certain numbers.
  - **Trend Lines**: View cumulative appearance trajectories and rolling 30-draw windows for specific numbers.
- **AI Smart Pick**: Generates a smart lottery pick based on a weighted ensemble of historical data (frequency, overdue status, pair correlations).

## Automated Live Data Feed

This repository includes a fully automated data pipeline:
- **`scraper.py`**: A Python script utilizing `cloudscraper` and `BeautifulSoup4` to parse the latest daily and evening draws from LotteryPost.
- **GitHub Actions (`.github/workflows/scrape.yml`)**: A cron job that runs the Python scraper every day at 11:30 PM EST. New draws are automatically appended to `nj_data.json` and committed directly to the repository. No paid APIs required!
- **Powerball Data**: Powered dynamically by the official NY Open Data API.

## Project Structure

- `index.html`: The core single-page application. Contains all styles, layout, and JavaScript logic (no external frameworks used; 100% vanilla JS and SVG).
- `scraper.py`: The data extraction script for NJ Pick 3 and Pick 4.
- `nj_data.json`: The local JSON database storing all parsed historical draws.
- `.github/workflows/scrape.yml`: CI/CD configuration for automated daily data scraping.

## Running Locally

Because the application is a single static HTML file, running it is incredibly simple:

1. Clone the repository.
2. Serve the directory using any local web server (e.g., Python's `http.server`, Node's `serve`, or VS Code Live Server).
   ```bash
   npx serve .
   # OR
   python3 -m http.server 3000
   ```
3. Open `http://localhost:3000` in your web browser.

## Tech Stack
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6), raw SVG DOM manipulation.
- **Backend (Data Pipeline)**: Python 3, `cloudscraper`, `beautifulsoup4`, GitHub Actions.
