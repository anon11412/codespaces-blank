# 🛠 Technical Specification: Action Network Data Integration

## 🛰 Overview
This project utilizes a custom-engineered data extraction layer to pull professional-grade betting consensus data directly from **Action Network**. This replaces the legacy ScoresAndOdds scraping method, providing higher accuracy, lower latency, and more detailed "Money %" metrics.

---

## 🏗 The "Next.js State Extraction" Strategy
Action Network is built on the Next.js framework. To optimize for speed and Search Engine Optimization (SEO), the site uses **Server-Side Rendering (SSR)**.

### How it Works:
1.  **The Payload:** When Action Network's server prepares a page, it bundles all the raw data (odds, bet counts, percentages) into a structured JSON object.
2.  **The Injection:** This object is injected into the HTML source code within a `<script id="__NEXT_DATA__">` tag.
3.  **The Extraction:** Our backend (`app.py`) fetches the public URL, identifies this specific script tag, and parses the JSON.
4.  **The Advantage:** This method is significantly more robust than traditional HTML scraping. We are not looking for CSS classes like `.team-name` (which change frequently); we are pulling from the **raw data state** that powers their own frontend.

---

## 📈 Data Source: Pinnacle (Book ID 15)
The consensus data displayed on the dashboard primarily targets **Pinnacle Sportsbook** (internal ID `15` in the Action Network system).

*   **Why Pinnacle?** Known as the "sharpest" bookmaker in the world, Pinnacle's betting patterns are the industry standard for identifying where professional money is moving.
*   **Fallback Logic:** If Pinnacle data is unavailable for a specific game or market, our scraper automatically falls back to an aggregate of other major books (DraftKings, FanDuel, BetMGM) to ensure the dashboard remains populated.

---

## 🔄 Autonomous Update Lifecycle
The system is designed to be "zero-maintenance" once deployed to Render.

1.  **On-Demand Fetching:** When a user opens the dashboard, the frontend makes a request to `/api/consensus`.
2.  **Server-Side Scrape:** The Flask server checks its 30-second cache. If expired, it performs a fresh scrape of Action Network's 6 supported leagues (NFL, NCAAF, NBA, NCAAB, MLB, NHL).
3.  **Frontend Auto-Refresh:** The dashboard utilizes a `setInterval` loop to refresh every 15-30 seconds, ensuring that even if the tab is left open all day, the data remains current without manual intervention.

---

## ⚖️ The "API Loophole" Explained
This method provides the same data as Action Network's **$79.99/month Pro Subscription** but via a different delivery mechanism.

| Feature | Action Network Pro API | Our Custom Scraper |
| :--- | :--- | :--- |
| **Delivery** | Private JSON Endpoint (REST) | Public HTML State Extraction |
| **Authentication** | API Key Required | Standard Browser Headers |
| **Cost** | $960 / Year | **$0 / Free** |
| **Reliability** | Extremely High | High (Depends on URL structure) |
| **Legal Status** | Licensed for Commercial Use | Optimized for Private/Internal Use |

### Why this is possible:
Action Network *must* send this data to the browser for their website to function. We have essentially built a "bridge" that intercepts this data package before it gets rendered into a visual webpage, allowing us to use the raw numbers directly.

---

## 🛠 Technical Implementation Details

### Backend (Python/Flask)
*   **Library:** `requests` + `BeautifulSoup4` for the initial fetch and tag location.
*   **Parsing:** Native `json` library to decode the state object.
*   **Resilience:** Multi-book aggregation logic in `app.py` ensures that "0%" values are avoided whenever alternative data exists in the payload.

### Frontend (JavaScript/CSS)
*   **Dynamic Rendering:** Always displays Spread and Totals rows if values exist, maintaining a consistent UI even during low-volume betting periods (e.g., early season NCAAF).
*   **State Management:** Uses a local `Set` and browser cookies to persist "Favorite" games across sessions.

---

## 📝 Compliance & Best Practices
*   **User-Agent Rotation:** The scraper identifies as a standard modern browser to avoid triggering basic anti-bot defenses.
*   **Rate Limiting:** The 30-second server-side cache ensures we do not "spam" Action Network's servers, maintaining a polite and sustainable crawling frequency.
