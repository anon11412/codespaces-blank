"""
Investigate ScoresAndOdds.com to find their actual API endpoints and data sources
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time

def analyze_page_sources():
    """Analyze the page to find API endpoints and data sources"""
    
    url = "https://www.scoresandodds.com/mlb/consensus-picks"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.scoresandodds.com/'
    }
    
    print("🔍 INVESTIGATING SCORESANDODDS.COM")
    print("="*70 + "\n")
    
    # Step 1: Get the main page
    print("📄 Step 1: Fetching main page...")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    print(f"✅ Status: {response.status_code}\n")
    
    # Step 2: Find all JavaScript files
    print("📁 Step 2: Analyzing JavaScript files...")
    scripts = soup.find_all('script', src=True)
    js_files = []
    
    for script in scripts:
        src = script.get('src')
        if src:
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = 'https://www.scoresandodds.com' + src
            js_files.append(src)
            print(f"  📜 {src}")
    
    print(f"\n  Found {len(js_files)} JavaScript files\n")
    
    # Step 3: Look for API endpoints in JS files
    print("🎯 Step 3: Searching for API endpoints in JavaScript...")
    api_endpoints = set()
    
    for js_url in js_files[:10]:  # Check first 10 JS files
        try:
            print(f"  Checking: {js_url.split('/')[-1]}...")
            js_response = requests.get(js_url, headers=headers, timeout=5)
            js_content = js_response.text
            
            # Search for API-like patterns
            patterns = [
                r'https?://[a-zA-Z0-9.-]+\.(?:com|net|io)/[^\s\'"<>]*(?:api|data|feed|consensus|odds)[^\s\'"<>]*',
                r'["\'](?:api|/api)[/\w-]*(?:consensus|odds|betting|data)[/\w-]*["\']',
                r'endpoint\s*[:=]\s*["\']([^"\']+)["\']',
                r'apiUrl\s*[:=]\s*["\']([^"\']+)["\']',
                r'baseUrl\s*[:=]\s*["\']([^"\']+)["\']',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, js_content, re.IGNORECASE)
                for match in matches:
                    cleaned = match.strip('"\' ')
                    if cleaned and len(cleaned) > 5:
                        api_endpoints.add(cleaned)
        except Exception as e:
            print(f"    ⚠️  Error: {str(e)[:50]}")
    
    if api_endpoints:
        print(f"\n  ✅ Found {len(api_endpoints)} potential endpoints:")
        for endpoint in list(api_endpoints)[:15]:
            print(f"    - {endpoint}")
    else:
        print("  ❌ No obvious API endpoints found in JS files")
    
    print()
    
    # Step 4: Check for WebSocket connections
    print("🔌 Step 4: Looking for WebSocket connections...")
    ws_elements = soup.find_all(attrs={'data-role': 'socket'})
    if ws_elements:
        for elem in ws_elements:
            print(f"  ✅ Found WebSocket element:")
            print(f"    - data-role: {elem.get('data-role')}")
            print(f"    - data-room: {elem.get('data-room')}")
            print(f"    - Other attrs: {elem.attrs}")
    else:
        print("  ❌ No WebSocket elements found")
    
    print()
    
    # Step 5: Look for embedded JSON data
    print("📊 Step 5: Searching for embedded JSON data...")
    inline_scripts = soup.find_all('script', src=False)
    json_found = False
    
    for script in inline_scripts:
        if script.string:
            content = script.string
            # Look for large JSON objects
            if 'consensus' in content.lower() or 'betting' in content.lower():
                # Try to extract JSON
                json_patterns = [
                    r'var\s+\w+\s*=\s*(\{[^;]+\});',
                    r'const\s+\w+\s*=\s*(\{[^;]+\});',
                    r'data\s*[:=]\s*(\{[^}]+\})',
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        json_found = True
                        print(f"  ✅ Found embedded data in inline script")
                        print(f"    - Pattern matched: {pattern[:40]}...")
                        # Try to parse first match
                        try:
                            data = json.loads(matches[0])
                            print(f"    - Keys: {list(data.keys())[:5]}")
                        except:
                            pass
                        break
    
    if not json_found:
        print("  ❌ No embedded JSON data found")
    
    print()
    
    # Step 6: Test common API endpoint patterns
    print("🧪 Step 6: Testing common API endpoint patterns...")
    base_domains = [
        "https://www.scoresandodds.com",
        "https://api.scoresandodds.com",
        "https://data.scoresandodds.com",
    ]
    
    endpoints = [
        "/api/consensus",
        "/api/mlb/consensus",
        "/api/consensus/mlb",
        "/api/v1/consensus",
        "/api/betting/consensus",
        "/data/consensus",
        "/feeds/mlb/consensus.json",
    ]
    
    working_endpoints = []
    
    for base in base_domains:
        for endpoint in endpoints:
            test_url = base + endpoint
            try:
                test_response = requests.get(test_url, headers=headers, timeout=3)
                if test_response.status_code == 200:
                    print(f"  ✅ FOUND: {test_url}")
                    print(f"    - Status: {test_response.status_code}")
                    print(f"    - Size: {len(test_response.content)} bytes")
                    
                    # Try to parse as JSON
                    try:
                        data = test_response.json()
                        print(f"    - Type: JSON")
                        print(f"    - Keys: {list(data.keys())[:5]}")
                        working_endpoints.append((test_url, data))
                    except:
                        print(f"    - Type: HTML/Text")
                    print()
                elif test_response.status_code not in [404, 403]:
                    print(f"  ⚠️  {test_url} - Status {test_response.status_code}")
            except requests.exceptions.ConnectionError:
                # Domain doesn't exist
                pass
            except Exception as e:
                pass
    
    if not working_endpoints:
        print("  ❌ No working API endpoints found")
    
    print()
    
    # Step 7: Analyze AWS S3 bucket
    print("☁️  Step 7: Checking AWS S3 bucket references...")
    s3_pattern = r'https?://[a-zA-Z0-9-]+\.s3\.amazonaws\.com/[^\s\'"<>]+'
    s3_urls = re.findall(s3_pattern, str(soup))
    
    if s3_urls:
        unique_s3 = list(set(s3_urls))[:5]
        print(f"  ✅ Found {len(unique_s3)} S3 URLs:")
        for s3_url in unique_s3:
            print(f"    - {s3_url}")
            # Check if it's a data file
            if any(ext in s3_url for ext in ['.json', '.xml', '.csv']):
                print(f"      🎯 DATA FILE - Testing...")
                try:
                    s3_response = requests.get(s3_url, timeout=5)
                    if s3_response.status_code == 200:
                        print(f"      ✅ Accessible! Size: {len(s3_response.content)} bytes")
                except:
                    pass
    else:
        print("  ❌ No S3 URLs found")
    
    print("\n" + "="*70)
    print("📋 SUMMARY")
    print("="*70 + "\n")
    
    if working_endpoints:
        print("✅ WORKING API ENDPOINTS FOUND:")
        for url, data in working_endpoints:
            print(f"  🎯 {url}")
            if isinstance(data, dict):
                print(f"     Sample keys: {list(data.keys())[:5]}")
        print()
    
    if api_endpoints:
        print(f"🔍 POTENTIAL ENDPOINTS TO INVESTIGATE:")
        for endpoint in list(api_endpoints)[:10]:
            print(f"  - {endpoint}")
        print()
    
    print("💡 RECOMMENDATIONS:")
    print("  1. Use Chrome DevTools Network tab (Ctrl+Shift+I)")
    print("  2. Visit: https://www.scoresandodds.com/mlb/consensus-picks")
    print("  3. Filter by 'Fetch/XHR' to see AJAX requests")
    print("  4. Look for requests that return JSON with consensus data")
    print("  5. Check the 'Preview' tab to see the data structure")
    print("  6. Note the URL and request headers needed")
    
    return working_endpoints, api_endpoints

if __name__ == "__main__":
    working, potential = analyze_page_sources()
