from flask import Flask, render_template, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

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
                if event.get('status') not in ['scheduled', 'in_progress']:
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
                
                game_data = {
                    'league': league,
                    'away_team': away_team.get('display_name', 'Unknown'),
                    'home_team': home_team.get('display_name', 'Unknown'),
                    'bet_percentages': {'away': f'{bet_away}%', 'home': f'{bet_home}%'},
                    'money_percentages': {'away': f'{money_away}%', 'home': f'{money_home}%'},
                    'spread_percentages': {'away': f'{spread_away_public}%', 'home': f'{spread_home_public}%'},
                    'best_odds': {
                        'away': f'{ml_away:+d}' if isinstance(ml_away, int) else str(ml_away),
                        'home': f'{ml_home:+d}' if isinstance(ml_home, int) else str(ml_home)
                    },
                    'spread': {
                        'away': f'{spread_away:+.1f}' if isinstance(spread_away, (int, float)) else str(spread_away),
                        'home': f'{spread_home:+.1f}' if isinstance(spread_home, (int, float)) else str(spread_home)
                    },
                    'num_bets': consensus_data.get('num_bets', 0),
                    'event_id': event.get('id'),
                    'start_time': event.get('start_time')
                }
                all_games.append(game_data)
        
        all_games.sort(key=lambda x: x.get('start_time', ''))
        return {'games': all_games, 'source': 'Action Network (NFL + NCAAF)', 'count': len(all_games)}
        
    except Exception as e:
        print(f"Error: {e}")
        return {'games': [], 'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/consensus')
def get_consensus():
    return jsonify(scrape_consensus_data())

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'leagues': ['NFL', 'NCAAF', 'MLB']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
