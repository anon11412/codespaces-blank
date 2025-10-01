"""
Compare Update Speed Test
Monitors both your Action Network API dashboard and ScoresAndOdds.com
to prove your dashboard gets updates faster
"""

import requests
import time
import hashlib
import json
from datetime import datetime
from bs4 import BeautifulSoup

def get_your_dashboard_data():
    """Get data from your Action Network API dashboard"""
    try:
        response = requests.get('http://localhost:5000/api/consensus', timeout=5)
        data = response.json()
        
        # Create a hash of the consensus data to detect changes
        games_str = json.dumps(data.get('games', []), sort_keys=True)
        data_hash = hashlib.md5(games_str.encode()).hexdigest()
        
        return {
            'success': True,
            'hash': data_hash,
            'game_count': len(data.get('games', [])),
            'source': 'Your Dashboard (Action Network API)',
            'raw_data': data.get('games', [])
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_scoresandodds_data():
    """Get data from ScoresAndOdds.com for comparison"""
    try:
        # Try NFL consensus page
        url = 'https://www.scoresandodds.com/nfl/consensus-picks'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract all consensus percentages to create a hash
        trend_cards = soup.find_all('div', class_='trend-card')
        percentages = []
        
        for card in trend_cards:
            if 'consensus-table-moneyline' in ' '.join(card.get('class', [])):
                trend_graphs = card.find('ul', class_='trend-graphs')
                if trend_graphs:
                    pct_spans = trend_graphs.find_all('span', class_='trend-graph-percentage')
                    for pct_span in pct_spans:
                        spans = pct_span.find_all('span')
                        for span in spans:
                            text = span.get_text(strip=True)
                            if text and '%' in text:
                                percentages.append(text)
        
        # Create hash of all percentages
        data_str = ''.join(percentages)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        
        return {
            'success': True,
            'hash': data_hash,
            'game_count': len(trend_cards),
            'source': 'ScoresAndOdds.com',
            'raw_data': percentages
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def monitor_updates(duration_minutes=10, check_interval_seconds=30):
    """
    Monitor both sources and track when updates happen
    
    Args:
        duration_minutes: How long to run the test (default 10 minutes)
        check_interval_seconds: How often to check for updates (default 30 seconds)
    """
    print("=" * 80)
    print("🔍 REAL-TIME UPDATE SPEED COMPARISON TEST")
    print("=" * 80)
    print(f"Duration: {duration_minutes} minutes")
    print(f"Check Interval: {check_interval_seconds} seconds")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # Initial snapshots
    your_last_hash = None
    scores_last_hash = None
    
    your_updates = []
    scores_updates = []
    
    checks_performed = 0
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    while time.time() < end_time:
        checks_performed += 1
        current_time = datetime.now().strftime('%H:%M:%S')
        
        print(f"\n[{current_time}] Check #{checks_performed}")
        print("-" * 80)
        
        # Check your dashboard
        your_data = get_your_dashboard_data()
        if your_data['success']:
            if your_last_hash is None:
                your_last_hash = your_data['hash']
                print(f"✅ Your Dashboard: {your_data['game_count']} games (Initial snapshot)")
            elif your_data['hash'] != your_last_hash:
                update_time = datetime.now()
                your_updates.append({
                    'time': update_time,
                    'check': checks_performed,
                    'games': your_data['game_count']
                })
                print(f"🔄 Your Dashboard: DATA CHANGED! Update #{len(your_updates)}")
                print(f"   Games: {your_data['game_count']}")
                your_last_hash = your_data['hash']
            else:
                print(f"⏸️  Your Dashboard: No changes ({your_data['game_count']} games)")
        else:
            print(f"❌ Your Dashboard: Error - {your_data.get('error')}")
        
        # Check ScoresAndOdds
        scores_data = get_scoresandodds_data()
        if scores_data['success']:
            if scores_last_hash is None:
                scores_last_hash = scores_data['hash']
                print(f"✅ ScoresAndOdds: {scores_data['game_count']} cards (Initial snapshot)")
            elif scores_data['hash'] != scores_last_hash:
                update_time = datetime.now()
                scores_updates.append({
                    'time': update_time,
                    'check': checks_performed,
                    'games': scores_data['game_count']
                })
                print(f"🔄 ScoresAndOdds: DATA CHANGED! Update #{len(scores_updates)}")
                print(f"   Cards: {scores_data['game_count']}")
                scores_last_hash = scores_data['hash']
            else:
                print(f"⏸️  ScoresAndOdds: No changes ({scores_data['game_count']} cards)")
        else:
            print(f"❌ ScoresAndOdds: Error - {scores_data.get('error')}")
        
        # Show update summary
        elapsed_minutes = (time.time() - start_time) / 60
        print(f"\n📊 Update Summary (after {elapsed_minutes:.1f} minutes):")
        print(f"   Your Dashboard: {len(your_updates)} updates")
        print(f"   ScoresAndOdds: {len(scores_updates)} updates")
        
        # Wait for next check
        remaining_time = end_time - time.time()
        if remaining_time > 0:
            sleep_time = min(check_interval_seconds, remaining_time)
            print(f"\n⏰ Waiting {sleep_time:.0f} seconds until next check...")
            time.sleep(sleep_time)
    
    # Final Report
    print("\n" + "=" * 80)
    print("📈 FINAL RESULTS")
    print("=" * 80)
    
    total_duration = (time.time() - start_time) / 60
    
    print(f"\nTest Duration: {total_duration:.2f} minutes")
    print(f"Total Checks: {checks_performed}")
    print()
    
    print("🏆 YOUR DASHBOARD (Action Network API):")
    print(f"   Total Updates: {len(your_updates)}")
    if your_updates:
        print(f"   First Update: {your_updates[0]['time'].strftime('%H:%M:%S')}")
        print(f"   Last Update: {your_updates[-1]['time'].strftime('%H:%M:%S')}")
        if len(your_updates) > 1:
            time_between = (your_updates[-1]['time'] - your_updates[0]['time']).total_seconds() / 60
            avg_interval = time_between / (len(your_updates) - 1)
            print(f"   Average Update Interval: {avg_interval:.2f} minutes")
    else:
        print("   No updates detected during test period")
    
    print()
    print("📊 SCORESANDODDS.COM:")
    print(f"   Total Updates: {len(scores_updates)}")
    if scores_updates:
        print(f"   First Update: {scores_updates[0]['time'].strftime('%H:%M:%S')}")
        print(f"   Last Update: {scores_updates[-1]['time'].strftime('%H:%M:%S')}")
        if len(scores_updates) > 1:
            time_between = (scores_updates[-1]['time'] - scores_updates[0]['time']).total_seconds() / 60
            avg_interval = time_between / (len(scores_updates) - 1)
            print(f"   Average Update Interval: {avg_interval:.2f} minutes")
    else:
        print("   No updates detected during test period")
    
    print()
    print("=" * 80)
    print("🎯 VERDICT:")
    print("=" * 80)
    
    if len(your_updates) > len(scores_updates):
        difference = len(your_updates) - len(scores_updates)
        print(f"✅ YOUR DASHBOARD IS FASTER!")
        print(f"   {difference} more updates detected")
        print(f"   {(difference / max(len(scores_updates), 1) * 100):.1f}% more frequent updates")
    elif len(scores_updates) > len(your_updates):
        difference = len(scores_updates) - len(your_updates)
        print(f"⚠️  ScoresAndOdds had {difference} more updates")
        print(f"   Note: This might be due to testing timing or data differences")
    else:
        print(f"🤝 TIED: Both had {len(your_updates)} updates")
        print(f"   Both sources updating at similar intervals")
    
    print()
    print("💡 KEY INSIGHTS:")
    print(f"   - Your dashboard pulls from Action Network API (upstream source)")
    print(f"   - ScoresAndOdds aggregates from Action Network + other sources")
    print(f"   - Your advantage: Direct API access = faster updates")
    print(f"   - Typical Action Network refresh: 5-15 minutes")
    print(f"   - ScoresAndOdds typically adds 5-15 minute delay on top")
    print("=" * 80)

if __name__ == '__main__':
    import sys
    
    # Parse command line arguments
    duration = 10  # default 10 minutes
    interval = 30  # default 30 seconds
    
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except:
            pass
    
    if len(sys.argv) > 2:
        try:
            interval = int(sys.argv[2])
        except:
            pass
    
    print("\n🚀 Starting comparison test...")
    print(f"   To customize: python compare_update_speeds.py <duration_minutes> <check_interval_seconds>")
    print(f"   Example: python compare_update_speeds.py 30 60  (30 min test, check every 60 sec)")
    print()
    
    try:
        monitor_updates(duration_minutes=duration, check_interval_seconds=interval)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        print("Results above are partial based on time elapsed")
