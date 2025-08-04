#!/usr/bin/env python3
"""
Test script for the Telegram Scraper API
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_statistics():
    """Test statistics endpoint"""
    print("📊 Testing statistics endpoint...")
    response = requests.get(f"{BASE_URL}/statistics")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Total Channels: {stats['total_channels']}")
        print(f"Total Posts: {stats['total_posts']}")
        print(f"Total Logs: {stats['total_logs']}")
        print(f"Posts by Category: {stats['posts_by_category']}")
        print(f"Posts by Language: {stats['posts_by_language']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_channels():
    """Test channels endpoint"""
    print("📺 Testing channels endpoint...")
    response = requests.get(f"{BASE_URL}/channels")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        channels = response.json()
        print(f"Found {len(channels)} channels:")
        for channel in channels:
            print(f"  - {channel['name']} (@{channel['username']})")
    else:
        print(f"Error: {response.text}")
    print()

def test_posts():
    """Test posts endpoint"""
    print("📰 Testing posts endpoint...")
    response = requests.get(f"{BASE_URL}/posts?size=5")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Posts: {data['total']}")
        print(f"Page: {data['page']} of {data['pages']}")
        print(f"Posts in this page: {len(data['items'])}")
        
        for post in data['items']:
            title = post['title'] or post['content'][:50] + "..." if post['content'] else "No title"
            print(f"  - {title}")
    else:
        print(f"Error: {response.text}")
    print()

def test_recent_posts():
    """Test recent posts endpoint"""
    print("🕒 Testing recent posts endpoint...")
    response = requests.get(f"{BASE_URL}/posts/recent/3")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        posts = response.json()
        print(f"Found {len(posts)} recent posts:")
        for post in posts:
            title = post['title'] or post['content'][:50] + "..." if post['content'] else "No title"
            print(f"  - {title}")
    else:
        print(f"Error: {response.text}")
    print()

def test_logs():
    """Test logs endpoint"""
    print("📋 Testing logs endpoint...")
    response = requests.get(f"{BASE_URL}/logs?size=5")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Logs: {data['total']}")
        print(f"Recent logs:")
        for log in data['items']:
            print(f"  - {log['channel']['name']}: {log['posts_new']} new posts, {log['status']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_scraping():
    """Test scraping endpoint"""
    print("🔄 Testing scraping endpoint...")
    payload = {
        "channels": ["shegamediaet"],
        "posts_per_channel": 2,
        "force": False
    }
    response = requests.post(f"{BASE_URL}/scrape", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print("Scraping results:")
        for result in results:
            print(f"  - {result['channel_name']}: {result['posts_new']} new, {result['posts_duplicate']} duplicates")
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all API tests"""
    print("🧪 Testing Telegram Scraper API")
    print("=" * 50)
    
    try:
        test_health()
        test_statistics()
        test_channels()
        test_posts()
        test_recent_posts()
        test_logs()
        test_scraping()
        
        print("✅ All API tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running:")
        print("   python3 api.py")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    main() 