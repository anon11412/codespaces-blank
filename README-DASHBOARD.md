# Real-Time Betting Consensus Dashboard

A beautiful, real-time web dashboard that displays live betting consensus data from multiple sportsbooks.

## Features

- 🎯 **Real-time Updates** - Auto-refreshes every 30 seconds
- 📊 **Consensus Data** - Shows both bet percentages and money percentages
- 💰 **Best Odds** - Displays the best available odds from multiple sportsbooks
- 🎨 **Modern UI** - Clean, responsive design that works on all devices
- ⚡ **Live Status** - Real-time status indicator showing connection health
- 🔄 **Manual Refresh** - One-click refresh button for instant updates
- 🎮 **Toggle Controls** - Enable/disable auto-refresh as needed

## What It Displays

For each game, you'll see:
- **Teams & Game Time** - Matchup and scheduled start time
- **Market Type** - Moneyline, Spread, or Total
- **Bet Distribution** - Percentage of bets on each side
- **Money Distribution** - Percentage of money on each side (shows where the big money is)
- **Best Odds** - Current best available odds from top sportsbooks

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

### 3. Open in Browser

Navigate to: `http://localhost:5000`

The dashboard will automatically start fetching and displaying data!

## How It Works

### Backend (Flask)
- Scrapes consensus data from ScoresAndOdds.com
- Parses HTML to extract betting percentages and odds
- Provides clean JSON API at `/api/consensus`
- Updates available every 30 seconds (respects rate limiting)

### Frontend (JavaScript)
- Fetches data from the API every 30 seconds
- Displays beautiful percentage bars showing consensus
- Color-coded: Purple for bets, Green for money
- Responsive grid layout adapts to screen size

## API Endpoints

### `GET /api/consensus`
Returns current consensus data for all games.

**Response:**
```json
{
  "success": true,
  "games": [
    {
      "away_team": "Tigers",
      "home_team": "Guardians",
      "game_time": "2025-10-01T17:08:00Z",
      "market_type": "moneyline",
      "bet_percentages": {
        "away": 42,
        "home": 58
      },
      "money_percentages": {
        "away": 31,
        "home": 69
      },
      "best_odds": {
        "away": "+118",
        "home": "-125"
      }
    }
  ],
  "last_updated": "2025-10-01T14:30:00",
  "total_games": 4
}
```

### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-01T14:30:00"
}
```

## Understanding the Data

### Bet Percentages vs Money Percentages

**Bet %** = What percentage of individual bets are on each side
- Shows where the public/recreational bettors are placing their money
- Each bet counts equally (whether $10 or $10,000)

**Money %** = What percentage of total money wagered is on each side
- Shows where the "smart money" or large bettors are
- $10,000 bet has more weight than $10 bet

### Key Insight
When bet % and money % differ significantly, it indicates "sharp" (professional) bettors are on the opposite side of the public.

**Example:**
- 70% of bets on Team A
- 30% of money on Team A
- **Interpretation:** Public loves Team A, but sharp bettors are hammering Team B with large bets

## Customization

### Change Refresh Interval

Edit `templates/index.html`, line with `setInterval`:

```javascript
autoRefreshInterval = setInterval(fetchData, 30000); // Change 30000 to desired milliseconds
```

### Change Color Scheme

Edit CSS in `templates/index.html`:

```css
background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); /* Bet bars */
background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%); /* Money bars */
```

### Add More Sports

The scraper currently targets MLB. To add other sports, modify the URL in `app.py`:

```python
url = "https://www.scoresandodds.com/nfl/consensus-picks"  # For NFL
url = "https://www.scoresandodds.com/nba/consensus-picks"  # For NBA
```

## Troubleshooting

### No Data Showing
- Check that ScoresAndOdds.com is accessible
- Verify there are games scheduled for today
- Check browser console for JavaScript errors

### Connection Errors
- Ensure you have internet connection
- ScoresAndOdds may be blocking requests (try different User-Agent)
- Add delay between requests if rate limited

### Slow Loading
- Increase timeout in `app.py` (default is 10 seconds)
- Check your internet connection speed
- Consider caching data for faster subsequent loads

## Important Notes

### Legal & Ethical
- ⚠️ **Respect Terms of Service** - Web scraping may violate site TOS
- ⚠️ **Rate Limiting** - Don't overwhelm the source website
- ⚠️ **Personal Use** - This tool is for personal use only
- ✅ **Consider Premium APIs** - For commercial use, subscribe to official data feeds

### Data Accuracy
- Data is only as current as ScoresAndOdds.com updates
- Typical delay: 5-30 minutes behind real-time
- For true real-time data, use professional APIs (Action Network, Sports Insights)

### Performance
- Scraping adds ~2-5 seconds load time per refresh
- Dashboard caches in browser for smooth experience
- Consider running on a server for 24/7 monitoring

## Future Enhancements

Potential improvements:
- [ ] Historical data tracking and charts
- [ ] Email/SMS alerts for significant line movements
- [ ] Multiple sports on one dashboard
- [ ] Database storage for trend analysis
- [ ] Dark mode toggle
- [ ] Filter by sport/team
- [ ] Export data to CSV

## Support

For issues or questions:
1. Check the browser console for errors
2. Verify API endpoint returns data: `http://localhost:5000/api/consensus`
3. Review the logs in the terminal running Flask
4. Check requirements are installed correctly

## License

This tool is for educational purposes. Always respect website Terms of Service and consider using official APIs for production use.

---

**Enjoy your real-time betting consensus dashboard! 🎯📊**
