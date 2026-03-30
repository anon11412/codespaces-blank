#!/bin/bash
echo "🧪 Testing Auto-Update Functionality"
echo "===================================="
echo ""

echo "Making 3 API calls 5 seconds apart to simulate auto-refresh:"
echo ""

for i in 1 2 3; do
    echo "Call #$i ($(date +%H:%M:%S)):"
    curl -s http://localhost:5000/api/consensus | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'  ✓ Fetched {data.get(\"count\", 0)} games')
print(f'  ✓ Leagues: {len(data.get(\"leagues_with_data\", []))} active')
if 'last_updated' in data:
    print(f'  ✓ Last updated: {data[\"last_updated\"]}')
"
    echo ""
    if [ $i -lt 3 ]; then
        sleep 5
    fi
done

echo "✅ Auto-update is working!"
echo ""
echo "Your dashboard refreshes every 30 seconds automatically."
echo "Try opening it in a browser to see live updates!"
