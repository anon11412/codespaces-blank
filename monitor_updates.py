"""
Monitor how often ScoresAndOdds actually updates their data
This will tell you if going to their source would be faster
"""

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json
import hashlib

def get_consensus_snapshot():
    """Get current consensus data as a hash to detect changes"""
    url = "https://www.scoresandodds.com/mlb/consensus-picks"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract all consensus data
        data = {}
        trend_cards = soup.find_all('div', class_='trend-card')
        
        for card in trend_cards:
            if 'consensus-table-moneyline' not in ' '.join(card.get('class', [])):
                continue
            
            # Get team names
            teams = card.find_all('span', class_='team-name')
            if len(teams) < 2:
                continue
            
            game_key = f"{teams[0].get_text(strip=True)}@{teams[1].get_text(strip=True)}"
            
            # Get percentages
            trend_graphs = card.find('ul', class_='trend-graphs')
            if trend_graphs:
                percentages = trend_graphs.find_all('span', class_='trend-graph-percentage')
                if len(percentages) >= 2:
                    # Bet percentages
                    bet_spans = percentages[0].find_all('span')
                    # Money percentages
                    money_spans = percentages[1].find_all('span')
                    
                    if len(bet_spans) >= 2 and len(money_spans) >= 2:
                        data[game_key] = {
                            'bet': f"{bet_spans[0].get_text(strip=True)}/{bet_spans[1].get_text(strip=True)}",
                            'money': f"{money_spans[0].get_text(strip=True)}/{money_spans[1].get_text(strip=True)}"
                        }
        
        # Create hash of the data to detect any changes
        data_str = json.dumps(data, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        
        return {
            'data': data,
            'hash': data_hash,
            'timestamp': datetime.now()
        }
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now()
        }

def monitor_update_frequency(duration_minutes=30, check_interval_seconds=30):
    """Monitor how often the data actually changes"""
    
    print("🔍 MONITORING SCORESANDODDS.COM UPDATE FREQUENCY")
    print("="*70)
    print(f"⏱️  Duration: {duration_minutes} minutes")
    print(f"🔄 Check interval: {check_interval_seconds} seconds")
    print("="*70 + "\n")
    
    previous_snapshot = None
    updates = []
    check_count = 0
    error_count = 0
    
    end_time = time.time() + (duration_minutes * 60)
    start_time = time.time()
    
    while time.time() < end_time:
        check_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        snapshot = get_consensus_snapshot()
        
        if 'error' in snapshot:
            error_count += 1
            print(f"[{timestamp}] ❌ Error: {snapshot['error']}")
        elif previous_snapshot is None:
            print(f"[{timestamp}] 📊 Initial snapshot captured")
            print(f"  Games found: {len(snapshot['data'])}")
            for game, pcts in snapshot['data'].items():
                print(f"    {game}")
                print(f"      Bets:  {pcts['bet']}")
                print(f"      Money: {pcts['money']}")
            print(f"  Data hash: {snapshot['hash'][:12]}...")
            previous_snapshot = snapshot
        elif snapshot['hash'] != previous_snapshot['hash']:
            # DATA CHANGED!
            time_since_last = (snapshot['timestamp'] - previous_snapshot['timestamp']).total_seconds()
            updates.append({
                'time': snapshot['timestamp'],
                'seconds_since_last': time_since_last
            })
            
            print(f"\n[{timestamp}] 🔄 DATA UPDATED! (Update #{len(updates)})")
            print(f"  Time since last update: {time_since_last/60:.1f} minutes")
            
            # Show what changed
            old_data = previous_snapshot['data']
            new_data = snapshot['data']
            
            for game in set(list(old_data.keys()) + list(new_data.keys())):
                old_val = old_data.get(game, {})
                new_val = new_data.get(game, {})
                
                if old_val != new_val:
                    print(f"\n  📈 {game}")
                    if old_val:
                        print(f"     OLD - Bets: {old_val.get('bet', 'N/A')}, Money: {old_val.get('money', 'N/A')}")
                    if new_val:
                        print(f"     NEW - Bets: {new_val.get('bet', 'N/A')}, Money: {new_val.get('money', 'N/A')}")
            
            print(f"  New hash: {snapshot['hash'][:12]}...")
            previous_snapshot = snapshot
        else:
            # No change
            elapsed = (datetime.now() - previous_snapshot['timestamp']).total_seconds()
            print(f"[{timestamp}] ✅ No changes (check #{check_count}, {elapsed/60:.1f}min since last update)")
        
        time.sleep(check_interval_seconds)
    
    # Final report
    total_duration = (time.time() - start_time) / 60
    
    print("\n" + "="*70)
    print("📊 FINAL REPORT")
    print("="*70 + "\n")
    
    print(f"⏱️  Total monitoring time: {total_duration:.1f} minutes")
    print(f"🔍 Total checks performed: {check_count}")
    print(f"❌ Errors encountered: {error_count}")
    print(f"🔄 Data updates detected: {len(updates)}\n")
    
    if len(updates) > 0:
        print("📈 UPDATE DETAILS:")
        for i, update in enumerate(updates, 1):
            time_str = update['time'].strftime("%H:%M:%S")
            print(f"  Update {i}: {time_str} ({update['seconds_since_last']/60:.1f} min since previous)")
        
        avg_interval = sum(u['seconds_since_last'] for u in updates[1:]) / max(len(updates)-1, 1)
        print(f"\n⏰ Average time between updates: {avg_interval/60:.1f} minutes")
    else:
        print("❌ NO UPDATES DETECTED during monitoring period")
        print("   This means the data is either:")
        print("   - Updated less frequently than your monitoring window")
        print("   - Static/cached for this time period")
        print("   - Only updated during active betting hours")
    
    print("\n💡 CONCLUSION:")
    if len(updates) == 0:
        print("  ⚠️  ScoresAndOdds updates VERY INFREQUENTLY (>30 min)")
        print("  ⚠️  Your scraper won't get faster data by polling more often")
        print("  ✅ You NEED to find their upstream data source for real-time updates")
    elif len(updates) > 0:
        avg_interval = sum(u['seconds_since_last'] for u in updates[1:]) / max(len(updates)-1, 1)
        if avg_interval < 120:  # Less than 2 minutes
            print(f"  ✅ ScoresAndOdds updates fairly frequently (~{avg_interval/60:.0f} min)")
            print("  ⚠️  But they're still aggregating from somewhere...")
        else:
            print(f"  ⚠️  ScoresAndOdds updates every ~{avg_interval/60:.0f} minutes")
            print("  ✅ Finding their source could give you faster data")
    
    print("\n🎯 NEXT STEPS:")
    print("  1. Run 'python investigate_sources.py' to find their API")
    print("  2. Use Chrome DevTools to capture actual network requests")
    print("  3. Look for WebSocket connections (real-time data)")
    print("  4. Consider paid APIs (Action Network, OddsJam) for true real-time")

if __name__ == "__main__":
    # Monitor for 30 minutes, checking every 30 seconds
    # You can adjust these values
    monitor_update_frequency(duration_minutes=30, check_interval_seconds=30)
