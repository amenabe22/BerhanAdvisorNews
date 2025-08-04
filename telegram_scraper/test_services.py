#!/usr/bin/env python3

from src.api.services import ChannelService, PostService, StatisticsService

def test_services():
    try:
        # Test ChannelService
        print("Testing ChannelService.get_all_channels()...")
        channels = ChannelService.get_all_channels()
        print(f"Found {len(channels)} channels")
        
        # Test PostService
        print("\nTesting PostService.get_posts()...")
        posts_result = PostService.get_posts()
        print(f"Found {posts_result['total']} posts")
        print(f"Items: {len(posts_result['items'])}")
        
        # Test StatisticsService
        print("\nTesting StatisticsService.get_statistics()...")
        stats = StatisticsService.get_statistics()
        print(f"Statistics: {stats}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_services() 