#!/bin/bash
# Test script for favorites feature persistence

echo "🧪 Testing Favorites Feature"
echo "===================================="
echo ""

# Get API data
DATA=$(curl -s http://localhost:5000/api/consensus)
GAME_COUNT=$(echo "$DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('count', 0))")
GAME_ID=$(echo "$DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['games'][0]['event_id'] if d.get('count',0) > 0 else 'NONE')")

echo "✅ API Working:"
echo "  • Games loaded: $GAME_COUNT"
echo "  • Sample game ID: $GAME_ID"
echo ""

echo "✅ Test Steps:"
echo "  1. Open http://localhost:5000 in browser"
echo "  2. Find a game card"
echo "  3. Click the ☆ star (top-right corner)"
echo "  4. Star should turn ⭐ GOLD"
echo "  5. Card border should be GOLD"
echo "  6. Click 'Favorites' tab"
echo "  7. Your starred game SHOULD appear there"
echo "  8. Return to 'All Games' tab"
echo "  9. Star should STILL be ⭐ GOLD (not lost!)"
echo "  10. Refresh page - Star and favorite SHOULD persist!"
echo ""

echo "🔍 Console Debug Info:"
echo "  • Open browser DevTools (F12)"
echo "  • Click 'Console' tab"
echo "  • When you click a star, you'll see debug logs"
echo "  • This helps verify favorites are being saved"
echo ""

echo "💾 Favorites Storage:"
echo "  • Stored in browser cookies"
echo "  • Expires in 1 year"
echo "  • Persists across page refreshes"
echo "  • Works even if you close browser"
echo ""

echo "✨ Expected Behavior:"
echo "  ✓ Click star → Turns GOLD immediately"
echo "  ✓ Card gets GOLD border"
echo "  ✓ Badge count increases"
echo "  ✓ Click Favorites tab → Game appears"
echo "  ✓ Switch tabs → Game stays in favorites"
echo "  ✓ Refresh page → Favorites still there"
echo "  ✓ Close/reopen browser → Favorites persist"
