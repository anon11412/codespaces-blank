from flask import Flask, render_template, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Global variables to track data changes
_cached_data = None
_last_update_time = None

def scrape_consensus_data():
    urls = {'NFL': 'https://api.actionnetwork.com/web/v1/scoreboard/nfl',
            'NCAAF': 'https://api.actionnetwork.com/web/v1/scoreboard/ncaaf',
            'MLB': 'https://api.actionnetwork.com/web/v1/scoreboard/mlb'}
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
        all_games = []
        
        for league, url in urls.items():
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for event in data.get('games', []):
                # Include more game statuses to keep live games visible
                game_status = event.get('status')
                
                # Exclude only clearly finished games
                if game_status in ['final', 'completed', 'canceled', 'cancelled', 'postponed']:
                    continue
                    
                teams = event.get('teams', [])
                if len(teams) < 2:
                    continue
                
                away_team = None
                home_team = None
                for team in teams:
                    if team.get('id') == event.get('away_team_id'):
                        away_team = team
                    elif team.get('id') == event.get('home_team_id'):
                        home_team = team
                
                if not away_team or not home_team:
                    continue
                
                odds_list = event.get('odds', [])
                consensus_data = None
                
                for odds in odds_list:
                    if odds.get('type') == 'game' and odds.get('ml_home_public') is not None:
                        consensus_data = odds
                        break
                
                if not consensus_data:
                    continue
                
                bet_away = consensus_data.get('ml_away_public', 0)
                bet_home = consensus_data.get('ml_home_public', 0)
                money_away = consensus_data.get('ml_away_money', 0)
                money_home = consensus_data.get('ml_home_money', 0)
                ml_away = consensus_data.get('ml_away', 'N/A')
                ml_home = consensus_data.get('ml_home', 'N/A')
                spread_away = consensus_data.get('spread_away', 'N/A')
                spread_home = consensus_data.get('spread_home', 'N/A')
                spread_away_public = consensus_data.get('spread_away_public', 0)
                spread_home_public = consensus_data.get('spread_home_public', 0)
                spread_away_money = consensus_data.get('spread_away_money', 0)
                spread_home_money = consensus_data.get('spread_home_money', 0)
                total_over = consensus_data.get('total_over', 'N/A')
                total_under = consensus_data.get('total_under', 'N/A')
                total_over_public = consensus_data.get('total_over_public', 0)
                total_under_public = consensus_data.get('total_under_public', 0)
                total_over_money = consensus_data.get('total_over_money', 0)
                total_under_money = consensus_data.get('total_under_money', 0)
                
                game_data = {
                    'league': league,
                    'away_team': away_team.get('display_name', 'Unknown'),
                    'home_team': home_team.get('display_name', 'Unknown'),
                    'bet_percentages': {'away': f'{bet_away}%', 'home': f'{bet_home}%'},
                    'money_percentages': {'away': f'{money_away}%', 'home': f'{money_home}%'},
                    'spread_percentages': {'away': f'{spread_away_public}%', 'home': f'{spread_home_public}%'},
                    'spread_money_percentages': {'away': f'{spread_away_money}%', 'home': f'{spread_home_money}%'},
                    'total_percentages': {'over': f'{total_over_public}%', 'under': f'{total_under_public}%'},
                    'total_money_percentages': {'over': f'{total_over_money}%', 'under': f'{total_under_money}%'},
                    'best_odds': {
                        'away': f'{ml_away:+d}' if isinstance(ml_away, int) else str(ml_away),
                        'home': f'{ml_home:+d}' if isinstance(ml_home, int) else str(ml_home)
                    },
                    'spread': {
                        'away': f'{spread_away:+.1f}' if isinstance(spread_away, (int, float)) else str(spread_away),
                        'home': f'{spread_home:+.1f}' if isinstance(spread_home, (int, float)) else str(spread_home)
                    },
                    'totals': {
                        'over': f'{total_over:+.1f}' if isinstance(total_over, (int, float)) else str(total_over),
                        'under': f'{total_under:+.1f}' if isinstance(total_under, (int, float)) else str(total_under)
                    },
                    'num_bets': consensus_data.get('num_bets', 0),
                    'event_id': event.get('id'),
                    'start_time': event.get('start_time'),
                    'status': game_status,
                    'is_live': game_status in ['in_progress', 'live', 'active', 'halftime', 'break']
                }
                all_games.append(game_data)
        
        # Sort games: Live games first, then by start time
        all_games.sort(key=lambda x: (
            0 if x.get('is_live') else 1,  # Live games first
            x.get('start_time', '') or ''  # Then by start time
        ))
        return {'games': all_games, 'source': 'Action Network (NFL + NCAAF + MLB)', 'count': len(all_games)}
        
    except Exception as e:
        print(f"Error: {e}")
        return {'games': [], 'error': str(e)}

def data_has_changed(new_data, old_data):
    """Compare two data sets to see if they're different"""
    if old_data is None:
        return True
    
    # Convert to JSON strings for comparison (excluding timestamp fields)
    def clean_data_for_comparison(data):
        if not data or 'games' not in data:
            return ""
        # Create a clean copy without timestamp-sensitive fields
        clean_games = []
        for game in data['games']:
            clean_game = {k: v for k, v in game.items() if k != 'start_time'}
            clean_games.append(clean_game)
        return json.dumps(clean_games, sort_keys=True)
    
    return clean_data_for_comparison(new_data) != clean_data_for_comparison(old_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/consensus')
def get_consensus():
    global _cached_data, _last_update_time
    
    # Get fresh data
    new_data = scrape_consensus_data()
    
    # Check if data has actually changed
    if data_has_changed(new_data, _cached_data):
        _cached_data = new_data.copy()
        _last_update_time = datetime.now().isoformat()
        print(f"Data changed - updating timestamp: {_last_update_time}")
    else:
        print("No data changes detected - keeping previous timestamp")
    
    # Add the last update time to the response
    if _last_update_time:
        new_data['last_updated'] = _last_update_time
    
    return jsonify(new_data)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'leagues': ['NFL', 'NCAAF', 'MLB']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
