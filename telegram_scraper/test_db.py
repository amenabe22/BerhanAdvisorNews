#!/usr/bin/env python3

from src.core.database import db_manager
from src.models.database import TelegramPost, TelegramChannel

def test_database():
    session = db_manager.get_session_direct()
    
    try:
        # Test channels
        channels = session.query(TelegramChannel).all()
        print(f"Found {len(channels)} channels")
        
        # Test posts
        posts = session.query(TelegramPost).all()
        print(f"Found {len(posts)} posts")
        
        # Test posts with channel relationship
        posts_with_channel = session.query(TelegramPost).join(TelegramChannel).all()
        print(f"Found {len(posts_with_channel)} posts with channel relationship")
        
        # Test a specific post
        if posts:
            post = posts[0]
            print(f"Post {post.id}: {post.title[:50] if post.title else 'No title'}")
            print(f"Channel: {post.channel.name if post.channel else 'No channel'}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    test_database() 