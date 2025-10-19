"""
MyFitnessPal API Client

Wrapper around the python-myfitnesspal library (local copy from GitHub).
Supports both browser cookie authentication and environment-based cookies.
"""

import sys
import os
import json
from pathlib import Path
from datetime import date, timedelta
from typing import Optional
from http.cookiejar import Cookie, CookieJar

# Add myfitnesspal library to path
myfitnesspal_path = Path(__file__).parent / "myfitnesspal"
sys.path.insert(0, str(myfitnesspal_path))

import myfitnesspal


class MyFitnessPalClient:
    """Simplified client wrapping python-myfitnesspal library"""
    
    def __init__(self):
        """
        Initialize client using cookies from browser or environment.
        
        Priority:
        1. MFP_COOKIES environment variable (for deployment)
        2. Browser cookies (for local development)
        """
        cookiejar = self._load_cookies_from_env()
        
        if cookiejar:
            # Use cookies from environment
            self.client = myfitnesspal.Client(cookiejar=cookiejar)
        else:
            # Fall back to browser cookies
            self.client = myfitnesspal.Client()
    
    def _load_cookies_from_env(self) -> Optional[CookieJar]:
        """Load cookies from MFP_COOKIES environment variable if present"""
        cookies_json = os.getenv('MFP_COOKIES')
        
        if not cookies_json:
            return None
        
        try:
            cookie_dict = json.loads(cookies_json)
            jar = CookieJar()
            
            for name, data in cookie_dict.items():
                cookie = Cookie(
                    version=0,
                    name=name,
                    value=data['value'],
                    port=None,
                    port_specified=False,
                    domain=data.get('domain', '.myfitnesspal.com'),
                    domain_specified=True,
                    domain_initial_dot=data.get('domain', '').startswith('.'),
                    path=data.get('path', '/'),
                    path_specified=True,
                    secure=data.get('secure', False),
                    expires=None,
                    discard=True,
                    comment=None,
                    comment_url=None,
                    rest={},
                    rfc2109=False
                )
                jar.set_cookie(cookie)
            
            return jar
            
        except Exception as e:
            print(f"Warning: Failed to load cookies from environment: {e}")
            return None
    
    def get_day(self, target_date: date):
        """
        Get complete day data including meals, exercise, water, and notes.
        
        Returns a Day object with:
        - meals: List of Meal objects with entries
        - totals: Dict of total nutrition (calories, carbs, fat, protein, etc.)
        - goals: Dict of daily goals
        - water: Float (water intake)
        - exercises: List of Exercise objects
        - notes: String (food notes)
        - complete: Boolean (whether day is marked complete)
        """
        return self.client.get_date(target_date)
    
    def get_date_range(self, start_date: date, end_date: date):
        """
        Get data for multiple days.
        
        Yields Day objects for each date in the range.
        """
        current = start_date
        while current <= end_date:
            try:
                yield self.get_day(current)
            except Exception:
                # Skip days with errors
                pass
            current = current + timedelta(days=1)
