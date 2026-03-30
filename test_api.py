#!/usr/bin/env python3
"""Quick test script to verify the API endpoints work"""

import requests
import json

def test_leagues_endpoint():
    """Test the /api/leagues endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/leagues', timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print("✅ /api/leagues endpoint works!")
        print(f"Found {len(data['leagues'])} leagues:")
        for league in data['leagues'][:10]:  # Show first 10
            print(f"  - {league['name']}")
        if len(data['leagues']) > 10:
            print(f"  ... and {len(data['leagues']) - 10} more")
        return True
    except Exception as e:
        print(f"❌ Error testing /api/leagues: {e}")
        return False

def test_consensus_endpoint():
    """Test the /api/consensus endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/consensus', timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n✅ /api/consensus endpoint works!")
        print(f"Found {data.get('count', 0)} games")
        if 'leagues_with_data' in data:
            print(f"Leagues with active games: {', '.join(data['leagues_with_data'])}")
        return True
    except Exception as e:
        print(f"❌ Error testing /api/consensus: {e}")
        return False

if __name__ == '__main__':
    print("Testing API endpoints...\n")
    test_leagues_endpoint()
    test_consensus_endpoint()
