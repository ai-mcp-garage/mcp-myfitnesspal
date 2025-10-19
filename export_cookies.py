#!/usr/bin/env python3
"""
Cookie Export Utility for MyFitnessPal MCP Server

Extracts MyFitnessPal cookies from your browser and saves them to .env file
for deployment scenarios where browser access isn't available (servers, containers, etc.)
"""

import browser_cookie3
import json
from pathlib import Path


def export_cookies_to_env():
    """Extract cookies from browser and save to .env file"""
    print("🍪 Extracting MyFitnessPal cookies from browser...")
    
    # Get cookies from browser
    cookies = browser_cookie3.load(domain_name='myfitnesspal.com')
    
    # Convert to dict
    cookie_dict = {}
    for cookie in cookies:
        cookie_dict[cookie.name] = {
            'value': cookie.value,
            'domain': cookie.domain,
            'path': cookie.path,
            'secure': cookie.secure,
        }
    
    if not cookie_dict:
        print("❌ No cookies found! Make sure you're logged into MyFitnessPal in your browser.")
        return False
    
    print(f"✓ Found {len(cookie_dict)} cookies")
    
    # Save to .env file
    env_path = Path(__file__).parent / '.env'
    
    # Convert to JSON string for single env var
    cookies_json = json.dumps(cookie_dict, indent=None)
    
    with open(env_path, 'w') as f:
        f.write("# MyFitnessPal Cookies (extracted from browser)\n")
        f.write("# Use this for deployment without browser access\n\n")
        f.write(f'MFP_COOKIES={cookies_json}\n')
    
    print(f"✓ Saved cookies to {env_path}")
    print("\n📝 Key cookies found:")
    important_cookies = ['_mfp_session', '__Secure-next-auth.session-token', 'known_user', 'remember_me']
    for key in important_cookies:
        if key in cookie_dict:
            value = cookie_dict[key]['value']
            print(f"  - {key}: {value[:20]}...")
    
    print("\n⚠️  Security Notes:")
    print("  - These cookies grant access to your MyFitnessPal account")
    print("  - Keep .env file secure and never commit to git")
    print("  - Cookies expire after ~30 days, re-run this script when needed")
    
    return True


def export_cookies_to_json():
    """Extract cookies and save as JSON file (alternative format)"""
    print("🍪 Extracting MyFitnessPal cookies from browser...")
    
    cookies = browser_cookie3.load(domain_name='myfitnesspal.com')
    
    cookie_list = []
    for cookie in cookies:
        cookie_list.append({
            'name': cookie.name,
            'value': cookie.value,
            'domain': cookie.domain,
            'path': cookie.path,
            'secure': cookie.secure,
            'httpOnly': cookie.has_nonstandard_attr('HttpOnly'),
        })
    
    if not cookie_list:
        print("❌ No cookies found! Make sure you're logged into MyFitnessPal in your browser.")
        return False
    
    print(f"✓ Found {len(cookie_list)} cookies")
    
    json_path = Path(__file__).parent / 'mfp_cookies.json'
    
    with open(json_path, 'w') as f:
        json.dump(cookie_list, f, indent=2)
    
    print(f"✓ Saved cookies to {json_path}")
    print("\n⚠️  Keep this file secure - it grants access to your account!")
    
    return True


if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("MyFitnessPal Cookie Export Utility")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        success = export_cookies_to_json()
    else:
        success = export_cookies_to_env()
    
    if success:
        print("\n✅ Cookie export complete!")
        print("\nNext steps:")
        print("  1. Deploy your server with the .env file")
        print("  2. The server will use cookies from .env instead of browser")
        print("  3. Re-run this script when cookies expire (~30 days)")
    else:
        print("\n❌ Cookie export failed")
        sys.exit(1)

