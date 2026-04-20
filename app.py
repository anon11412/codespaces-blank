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

# Leagues supported by ScoresAndOdds for scraping
SCRAPE_LEAGUES = {
    'NFL': 'nfl',
    'NCAAF': 'ncaaf',
    'NBA': 'nba',
    'NCAAB': 'ncaab',
    'MLB': 'mlb',
    'NHL': 'nhl'
}

def scrape_consensus_data():
    all_games = []
    failed_leagues = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for league_display, league_slug in SCRAPE_LEAGUES.items():
        url = f"https://www.scoresandodds.com/{league_slug}/consensus-picks"
        try:
            print(f"Scraping {league_display} from {url}...")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all trend cards (consensus data containers)
            trend_cards = soup.find_all('div', class_='trend-card')
            
            # Map to keep track of games to avoid duplicates 
            games_by_teams = {}
            
            for card in trend_cards:
                # Extract market type
                market = 'unknown'
                classes = card.get('class', [])
                for cls in classes:
                    if 'moneyline' in cls: market = 'moneyline'
                    elif 'spread' in cls: market = 'spread'
                    elif 'total' in cls: market = 'total'
                
                # Get teams
                team_names = card.find_all('span', class_='team-name')
                if len(team_names) < 2:
                    continue
                
                away_team = team_names[0].get_text(strip=True)
                home_team = team_names[1].get_text(strip=True)
                game_id = f"{league_display}_{away_team}_{home_team}".replace(" ", "_")
                
                if game_id not in games_by_teams:
                    games_by_teams[game_id] = {
                        'league': league_display,
                        'away_team': away_team,
                        'home_team': home_team,
                        'bet_percentages': {'away': '0%', 'home': '0%'},
                        'money_percentages': {'away': '0%', 'home': '0%'},
                        'spread_percentages': {'away': '0%', 'home': '0%'},
                        'spread_money_percentages': {'away': '0%', 'home': '0%'},
                        'total_percentages': {'over': '0%', 'under': '0%'},
                        'total_money_percentages': {'over': '0%', 'under': '0%'},
                        'best_odds': {'away': 'N/A', 'home': 'N/A'},
                        'spread': {'away': '', 'home': ''},
                        'totals': {'over': '', 'under': ''},
                        'num_bets': 0,
                        'event_id': game_id,
                        'start_time': datetime.now().isoformat(),
                        'status': 'scheduled',
                        'is_live': False
                    }
                
                game_data = games_by_teams[game_id]
                
                # Extract percentages
                graphs = card.find_all('span', class_='trend-graph-percentage')
                
                def extract_pct(graph):
                    if not graph: return '0%', '0%'
                    p_a = graph.find('span', class_='percentage-a')
                    p_b = graph.find('span', class_='percentage-b')
                    val_a = p_a.get_text(strip=True) if p_a else '0%'
                    val_b = p_b.get_text(strip=True) if p_b else '0%'
                    if not val_a or val_a == '\u00a0': val_a = '0%'
                    if not val_b or val_b == '\u00a0': val_b = '0%'
                    return val_a, val_b

                if market == 'moneyline':
                    if len(graphs) >= 1:
                        a, h = extract_pct(graphs[0])
                        game_data['bet_percentages'] = {'away': a, 'home': h}
                    if len(graphs) >= 2:
                        a, h = extract_pct(graphs[1])
                        game_data['money_percentages'] = {'away': a, 'home': h}
                
                elif market == 'spread':
                    if len(graphs) >= 1:
                        a, h = extract_pct(graphs[0])
                        game_data['spread_percentages'] = {'away': a, 'home': h}
                    if len(graphs) >= 2:
                        a, h = extract_pct(graphs[1])
                        game_data['spread_money_percentages'] = {'away': a, 'home': h}
                
                elif market == 'total':
                    if len(graphs) >= 1:
                        o, u = extract_pct(graphs[0])
                        game_data['total_percentages'] = {'over': o, 'under': u}
                    if len(graphs) >= 2:
                        o, u = extract_pct(graphs[1])
                        game_data['total_money_percentages'] = {'over': o, 'under': u}

            for g in games_by_teams.values():
                all_games.append(g)
                
        except Exception as e:
            failed_leagues.append(league_display)
            print(f"Error scraping {league_display}: {e}")
            continue

    return {
        'games': all_games,
        'source': 'ScoresAndOdds Scraper',
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
            return jsonify(_cached_data)

    new_data = scrape_consensus_data()
    _cached_data = new_data
    _last_update_time = now.isoformat()
    new_data['last_updated'] = _last_update_time
    
    # Apply filters
    league_filter = request.args.get('league')
    if league_filter and league_filter != 'all':
        filtered_games = [g for g in new_data['games'] if g['league'] == league_filter]
        filtered_data = new_data.copy()
        filtered_data['games'] = filtered_games
        filtered_data['count'] = len(filtered_games)
        return jsonify(filtered_data)
        
    return jsonify(new_data)

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
# Final ScoresAndOdds Scraper v2 - 2026-04-20
