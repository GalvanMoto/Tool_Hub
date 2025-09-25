#!/usr/bin/env python3

import requests
import json

def test_seo_audit_api():
    """Test the SEO audit API endpoint directly."""
    try:
        url = "http://127.0.0.1:5000/tools/seo-audit"
        data = {
            'website_url': 'https://example.com',
            'audit_depth': 'standard',
            'include_mobile': 'on'
        }
        
        print("Testing SEO Audit API...")
        print(f"Posting to: {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(f"JSON Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Response Text: {response.text[:500]}...")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error testing API: {e}")
        return False

if __name__ == "__main__":
    success = test_seo_audit_api()
    print(f"\nAPI Test {'PASSED' if success else 'FAILED'}")