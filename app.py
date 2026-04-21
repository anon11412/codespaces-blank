from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import re

app = Flask(__name__)
CORS(app)

# Global variables to track data changes
_cached_data = None
_last_update_time = None

# Leagues supported by Action Network
SCRAPE_LEAGUES = {
    'NFL': 'nfl',
    'NCAAF': 'ncaaf',
    'NBA': 'nba',
    'NCAAB': 'ncaab',
    'MLB': 'mlb',
    'NHL': 'nhl'
}

def get_action_network_data(league_slug):
    url = f"https://www.actionnetwork.com/{league_slug}/public-betting"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        
        if script:
            return json.loads(script.string)
        else:
            match = re.search(r'{"props":.*}', response.text)
            if match:
                return json.loads(match.group(0))
    except Exception as e:
        print(f"Error fetching {league_slug} from Action Network: {e}")
    return None

def scrape_consensus_data():
    all_games = []
    
    for league_display, league_slug in SCRAPE_LEAGUES.items():
        print(f"Processing {league_display}...")
        data = get_action_network_data(league_slug)
        
        if not data:
            continue
            
        try:
            page_props = data.get('props', {}).get('pageProps', {})
            scoreboard = page_props.get('scoreboardResponse', {})
            games = scoreboard.get('games', [])
            
            for g in games:
                # Basic game info - Using FULL NAME
                away_team = "N/A"
                home_team = "N/A"
                for t in g.get('teams', []):
                    if t['id'] == g['away_team_id']: away_team = t.get('full_name', t.get('display_name', 'N/A'))
                    if t['id'] == g['home_team_id']: home_team = t.get('full_name', t.get('display_name', 'N/A'))
                
                game_id = str(g.get('id', ''))
                
                game_data = {
                    'league': league_display,
                    'away_team': away_team,
                    'home_team': home_team,
                    'bet_percentages': {'away': '0%', 'home': '0%'},
                    'money_percentages': {'away': '0%', 'home': '0%'},
                    'spread_percentages': {'away': '0%', 'home': '0%'},
                    'spread_money_percentages': {'away': '0%', 'home': '0%'},
                    'total_percentages': {'over': '0%', 'under': '0%'},
                    'total_money_percentages': {'over': '0%', 'under': '0%'},
                    'best_odds': {'away': '', 'home': ''},
                    'spread': {'away': '', 'home': ''},
                    'totals': {'over': '', 'under': ''},
                    'num_bets': g.get('num_bets', 0),
                    'event_id': game_id,
                    'start_time': g.get('start_time'),
                    'status': g.get('status_display', 'scheduled'),
                    'is_live': g.get('status') == 'live'
                }
                
                markets_container = g.get('markets', {})
                if not markets_container:
                    continue

                # PRIORITY 1: Pinnacle (Book 15) for consensus percentages
                # PRIORITY 2: Any other book for percentages
                
                # First, find best odds and market values (spread/total) from ANY book if 15 is missing
                all_book_ids = list(markets_container.keys())
                
                # Helper to extract data from a specific book's market
                def extract_from_book(book_id, target_data):
                    book_event = markets_container.get(book_id, {}).get('event', {})
                    
                    # Moneyline
                    for o in book_event.get('moneyline', []):
                        side = 'away' if o.get('team_id') == g['away_team_id'] else 'home'
                        if not target_data['best_odds'][side]:
                            target_data['best_odds'][side] = str(o.get('odds', ''))
                        
                        # Only take percentages if they are non-zero or if we don't have them yet
                        tickets = o.get('bet_info', {}).get('tickets', {}).get('percent', 0)
                        money = o.get('bet_info', {}).get('money', {}).get('percent', 0)
                        if tickets > 0 or target_data['bet_percentages'][side] == '0%':
                            target_data['bet_percentages'][side] = f"{tickets}%"
                        if money > 0 or target_data['money_percentages'][side] == '0%':
                            target_data['money_percentages'][side] = f"{money}%"

                    # Spread
                    for o in book_event.get('spread', []):
                        side = 'away' if o.get('team_id') == g['away_team_id'] else 'home'
                        if not target_data['spread'][side]:
                            val = o.get('value')
                            if val is not None:
                                target_data['spread'][side] = f"{'+' if val > 0 else ''}{val}"
                        
                        tickets = o.get('bet_info', {}).get('tickets', {}).get('percent', 0)
                        money = o.get('bet_info', {}).get('money', {}).get('percent', 0)
                        if tickets > 0 or target_data['spread_percentages'][side] == '0%':
                            target_data['spread_percentages'][side] = f"{tickets}%"
                        if money > 0 or target_data['spread_money_percentages'][side] == '0%':
                            target_data['spread_money_percentages'][side] = f"{money}%"

                    # Total
                    for o in book_event.get('total', []):
                        side = o.get('side')
                        if side in ['over', 'under']:
                            if not target_data['totals'][side]:
                                val = o.get('value')
                                if val is not None:
                                    target_data['totals'][side] = str(val)
                            
                            tickets = o.get('bet_info', {}).get('tickets', {}).get('percent', 0)
                            money = o.get('bet_info', {}).get('money', {}).get('percent', 0)
                            if tickets > 0 or target_data['total_percentages'][side] == '0%':
                                target_data['total_percentages'][side] = f"{tickets}%"
                            if money > 0 or target_data['total_money_percentages'][side] == '0%':
                                target_data['total_money_percentages'][side] = f"{money}%"

                # 1. Try Pinnacle first for everything
                if '15' in markets_container:
                    extract_from_book('15', game_data)
                
                # 2. For anything still 0 or empty, try other books
                for bid in all_book_ids:
                    if bid == '15': continue
                    extract_from_book(bid, game_data)

                all_games.append(game_data)
                
        except Exception as e:
            print(f"Error parsing {league_display} data: {e}")
            continue

    return {
        'games': all_games,
        'source': 'Action Network Scraper',
        'count': len(all_games),
        'leagues_with_data': list(set(g['league'] for g in all_games))
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/consensus')
def get_consensus():
    global _cached_data, _last_update_time
    
    # Check if we should use cache (simple 30s cache)
    now = datetime.now()
    if _cached_data and _last_update_time:
        last_time = datetime.fromisoformat(_last_update_time)
        if (now - last_time).total_seconds() < 30:
            data_to_return = _cached_data
        else:
            new_data = scrape_consensus_data()
            _cached_data = new_data
            _last_update_time = now.isoformat()
            new_data['last_updated'] = _last_update_time
            data_to_return = new_data
    else:
        new_data = scrape_consensus_data()
        _cached_data = new_data
        _last_update_time = now.isoformat()
        new_data['last_updated'] = _last_update_time
        data_to_return = new_data
    
    # Apply league filter
    league_filter = request.args.get('league')
    if league_filter and league_filter != 'all':
        filtered_games = [g for g in data_to_return['games'] if g['league'] == league_filter]
        filtered_data = data_to_return.copy()
        filtered_data['games'] = filtered_games
        filtered_data['count'] = len(filtered_games)
        return jsonify(filtered_data)
        
    return jsonify(data_to_return)

@app.route('/api/leagues')
def get_leagues():
    leagues = [{'id': name, 'name': name, 'display_name': name} for name in SCRAPE_LEAGUES.keys()]
    return jsonify({'leagues': leagues})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'leagues': list(SCRAPE_LEAGUES.keys())})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
