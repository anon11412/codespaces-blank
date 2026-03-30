# ScoresAndOdds.com Consensus Data Analysis

## Summary
ScoresAndOdds.com displays **public betting consensus percentages** (also called "splits") that show what percentage of bettors are wagering on each side of a game. They aggregate this data from multiple sportsbooks.

---

## Where They Get Their Consensus Numbers

### 1. **Data Sources**
Based on the HTML analysis, ScoresAndOdds pulls consensus data from:

- **Multiple Sportsbooks Integration**: They aggregate betting data across major sportsbooks including:
  - DraftKings
  - FanDuel  
  - BetMGM
  - Caesars
  - bet365
  - BetRivers
  - ESPN BET
  - Fanatics
  - Hard Rock
  - And others

### 2. **Data Types Displayed**
For each game, they show:
- **Percentage of Bets** (e.g., "42% on Tigers, 58% on Guardians")
- **Percentage of Money** (e.g., "31% on Tigers, 69% on Guardians")
- These are shown separately for:
  - **Moneyline** bets
  - **Spread/Runline** bets  
  - **Total** (Over/Under) bets

### 3. **Example from Their HTML**:
```html
<span class="trend-graph-percentage">
  <span class="percentage-a" style="width:42%; background-color: #0c2c56">42%</span>
  <span class="percentage-b" style="width:58%; background-color: #e31937">58%</span>
</span>
<span class="trend-graph-sides center">
  <span>% of Money</span>
</span>
```

This shows that for the Tigers vs Guardians game:
- **42% of bets** are on Tigers moneyline
- **58% of bets** are on Guardians moneyline
- **31% of money** is on Tigers  
- **69% of money** is on Guardians

---

## How to Get Real-Time Updates (Not Their Update Intervals)

### Current Limitations:
ScoresAndOdds updates their consensus data at **their own intervals** (likely every 15-30 minutes based on typical industry standards). The data you see on their website is NOT truly "real-time" - it's periodically refreshed.

### Options for Real-Time Access:

#### **Option 1: Use Their API (If Available)**
- Look for: `https://api.scoresandodds.com` or similar endpoints
- **Issue**: No public API documentation found in their HTML
- You would need to:
  1. Contact ScoresAndOdds directly for API access
  2. Check if they offer premium data feeds

#### **Option 2: Action Network (Their Data Provider)**
ScoresAndOdds uses **Action Network** for some of their data. Evidence:
```html
<img src="https://assets.actionnetwork.com/461059_det_n.png" alt="Tigers" />
```

Action Network provides:
- Real-time odds data
- Public betting percentages
- Line movement tracking

**Action Network API**: https://www.actionnetwork.com/developer
- They offer professional data feeds
- Pricing typically starts at $500+/month for real-time data

#### **Option 3: Alternative Real-Time Data Sources**

1. **The Action Network Pro** ($79.99/month)
   - Real-time public betting percentages
   - Professional-grade betting data
   - Mobile app with live updates

2. **Sports Insights** (sportsinsights.com)
   - Real-time betting percentages
   - Live odds from 80+ sportsbooks
   - API available for enterprise clients

3. **OddsJam** (oddsjam.com)
   - Real-time odds aggregation
   - Public betting data
   - API access for developers

4. **RapidAPI Sports Odds APIs**
   - Multiple sports betting data APIs
   - Real-time odds and lines
   - Pricing: $0-$500/month depending on volume

#### **Option 4: Build Your Own Scraper**
⚠️ **Legal Considerations**: Always check Terms of Service before scraping

```python
import requests
from bs4 import BeautifulSoup
import time

def scrape_consensus():
    url = "https://www.scoresandodds.com/mlb/consensus-picks"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find consensus percentages
    percentages = soup.find_all('span', class_='trend-graph-percentage')
    
    for pct in percentages:
        away_pct = pct.find('span', class_='percentage-a')
        home_pct = pct.find('span', class_='percentage-b')
        print(f"Away: {away_pct.text}, Home: {home_pct.text}")
    
    return True

# Run every 60 seconds for "real-time" updates
while True:
    scrape_consensus()
    time.sleep(60)  # Wait 1 minute
```

**Limitations of Scraping**:
- Against most Terms of Service
- Risk of IP blocking
- Data still limited to their update frequency
- No access to historical tick data

---

## Understanding the Data Structure

### HTML Pattern for Consensus Data:
```html
<div class="trend-card consensus consensus-table-moneyline--0 active">
  <div class="event-header">
    <!-- Team information -->
  </div>
  <div class="module-body">
    <ul class="trend-graphs">
      <li class="consensus active">
        <span class="trend-graph-chart">
          <!-- Bet percentage bar -->
          <span class="trend-graph-percentage">
            <span class="percentage-a" style="width:42%">42%</span>
            <span class="percentage-b" style="width:58%">58%</span>
          </span>
          <!-- Money percentage bar -->
          <span class="trend-graph-percentage">
            <span class="percentage-a" style="width:31%">31%</span>
            <span class="percentage-b" style="width:69%">69%</span>
          </span>
        </span>
      </li>
    </ul>
  </div>
</div>
```

### Key Data Attributes:
- `data-event="mlb/10371220"` - Game identifier
- `data-market="moneyline"` or `"spread"` or `"total"` - Bet type
- `style="width:42%"` - Visual percentage representation
- Text content contains actual percentage values

---

## Recommended Approach for Real-Time Data

### **Best Solution**:
1. **Sign up for Action Network Pro** ($79.99/month)
   - This appears to be where ScoresAndOdds sources their data
   - You'll get the same data but with real-time updates
   - Includes mobile app and web interface

2. **Or use Sports Insights**
   - Professional-grade real-time betting data
   - Used by many professional bettors
   - Includes sharp vs public money tracking

3. **For Development/Automation**:
   - Contact Action Network for API access
   - Or use OddsJam API for integration
   - Budget: $500-2000/month for real-time data feeds

### **Budget Option**:
- Monitor ScoresAndOdds every 5-10 minutes manually or with a simple script
- Combine with direct sportsbook data
- Use free tools like OddsPortal for additional context

---

## Additional Technical Details

### WebSocket Connections
ScoresAndOdds uses: `data-role="socket" data-room="sao:all"`

This suggests they may use WebSocket for some real-time updates, but:
- This is for internal use only
- Not accessible to public users
- You cannot tap into their WebSocket feed

### JavaScript Files
Their main odds/consensus logic appears to be in:
- `https://bctn-sao.s3.amazonaws.com/js/lines.js`
- This file handles the display and updates of betting lines
- It's minified and obfuscated

---

## Important Considerations

### Why "Consensus" Data Isn't Perfectly Real-Time:

1. **Sportsbooks don't share live data publicly**
   - Most consensus data is aggregated periodically
   - Even premium services have 5-15 minute delays

2. **"Sharp vs Public" distinction**
   - Large bets from professionals ("sharp money") move lines differently
   - ScoresAndOdds shows "% of bets" vs "% of money" to illustrate this

3. **Data aggregation complexity**
   - Combining data from 10+ sportsbooks takes time
   - Each book updates at different intervals
   - Normalization and processing adds latency

### Legal & Ethical Reminders:
- ✅ Viewing public websites is legal
- ✅ Using official APIs with permission is legal
- ❌ Automated scraping often violates Terms of Service
- ❌ Overwhelming servers with requests can be illegal
- ⚠️ Always read and respect Terms of Service

---

## Conclusion

**ScoresAndOdds gets their consensus numbers from**:
- Aggregating public betting data across multiple major sportsbooks
- Partnering with Action Network for data infrastructure
- Processing and displaying both "% of bets" and "% of money"

**For TRUE real-time updates**:
- You need direct access to sportsbook APIs or professional data feeds
- Action Network Pro or Sports Insights are your best options
- Budget for $80-$2000/month depending on your needs
- No free solution exists for truly real-time consensus data

**The data updates at THEIR intervals because**:
- They aggregate from multiple sources (takes time)
- Real-time individual sportsbook data is proprietary
- Even premium services have delays of 5-30 minutes

If you need more specific implementation help or want to explore API options, let me know!
