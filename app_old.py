"""
Real-Time Sports Betting Consensus Dashboard
Fetches and displays betting consensus data with automatic updates
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)

def scrape_consensus_data():
    """Scrape consensus betting data from ScoresAndOdds"""
    try:
        url = "https://www.scoresandodds.com/mlb/consensus-picks"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        games = []
        
        # Find all trend cards (consensus data containers)
        trend_cards = soup.find_all('div', class_='trend-card')
        
        # Group cards by game (each game has multiple market types)
        seen_games = set()
        
        for card in trend_cards:
            # Only process consensus cards with active class (moneyline by default)
            card_classes = card.get('class', [])
            if 'consensus' not in card_classes:
                continue
            
            # Skip non-moneyline cards to avoid duplicates (we'll show moneyline data)
            if 'consensus-table-moneyline' not in ' '.join(card_classes):
                continue
                
            # Extract game info
            event_header = card.find('div', class_='event-header')
            if not event_header:
                continue
            
            # Get teams
            team_pennants = event_header.find_all('div', class_='team-pennant')
            if len(team_pennants) < 2:
                continue
                
            away_team = team_pennants[0].find('span', class_='team-name')
            home_team = team_pennants[1].find('span', class_='team-name')
            
            if not away_team or not home_team:
                continue
                
            away_team_name = away_team.get_text(strip=True)
            home_team_name = home_team.get_text(strip=True)
            
            # Skip if we've already processed this game
            game_key = f"{away_team_name}@{home_team_name}"
            if game_key in seen_games:
                continue
            seen_games.add(game_key)
            
            # Get game time
            game_time_elem = event_header.find('span', attrs={'data-role': 'localtime'})
            game_time = game_time_elem.get('data-value', 'TBD') if game_time_elem else 'TBD'
            
            # Market type is moneyline (since we filtered for it above)
            market_type = 'moneyline'
            
            # Get consensus percentages
            trend_graphs = card.find('ul', class_='trend-graphs')
            if not trend_graphs:
                continue
                
            percentages = trend_graphs.find_all('span', class_='trend-graph-percentage')
            
            bet_percentages = {'away': 0, 'home': 0}
            money_percentages = {'away': 0, 'home': 0}
            
            if len(percentages) >= 2:
                # First bar is bet percentages
                bet_spans = percentages[0].find_all('span', class_=['percentage-a', 'percentage-b'])
                if len(bet_spans) >= 2:
                    away_bet = bet_spans[0].get_text(strip=True).replace('%', '')
                    home_bet = bet_spans[1].get_text(strip=True).replace('%', '')
                    bet_percentages['away'] = int(away_bet) if away_bet.isdigit() else 0
                    bet_percentages['home'] = int(home_bet) if home_bet.isdigit() else 0
                
                # Second bar is money percentages
                money_spans = percentages[1].find_all('span', class_=['percentage-a', 'percentage-b'])
                if len(money_spans) >= 2:
                    away_money = money_spans[0].get_text(strip=True).replace('%', '').replace('&nbsp;', '0')
                    home_money = money_spans[1].get_text(strip=True).replace('%', '').replace('&nbsp;', '0')
                    money_percentages['away'] = int(away_money) if away_money.isdigit() else 0
                    money_percentages['home'] = int(home_money) if home_money.isdigit() else 0
            
            # Get best odds
            best_odds = {'away': None, 'home': None}
            best_odds_containers = card.find_all('div', class_='best-odds-container')
            
            for container in best_odds_containers:
                label = container.find('span')
                if not label:
                    continue
                    
                label_text = label.get_text(strip=True).lower()
                odds_link = container.find('a')
                
                if odds_link:
                    moneyline_span = odds_link.find('span', class_='data-moneyline')
                    odds_span = odds_link.find('small', class_='data-odds')
                    
                    if moneyline_span:
                        odds_value = moneyline_span.get_text(strip=True)
                        if odds_span:
                            odds_value += ' ' + odds_span.get_text(strip=True)
                        
                        if 'away' in label_text or 'over' in label_text:
                            best_odds['away'] = odds_value
                        elif 'home' in label_text or 'under' in label_text:
                            best_odds['home'] = odds_value
            
            game_data = {
                'away_team': away_team_name,
                'home_team': home_team_name,
                'game_time': game_time,
                'market_type': market_type,
                'bet_percentages': bet_percentages,
                'money_percentages': money_percentages,
                'best_odds': best_odds
            }
            
            games.append(game_data)
        
        return {
            'success': True,
            'games': games,
            'last_updated': datetime.now().isoformat(),
            'total_games': len(games)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'games': [],
            'last_updated': datetime.now().isoformat(),
            'total_games': 0
        }

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api/consensus')
def get_consensus():
    """API endpoint to get consensus data"""
    data = scrape_consensus_data()
    return jsonify(data)

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
