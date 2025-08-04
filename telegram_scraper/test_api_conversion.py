#!/usr/bin/env python3

from src.core.database import db_manager
from src.models.database import TelegramPost, TelegramChannel
from src.api.routes import convert_post_to_response, convert_channel_to_response

def test_api_conversion():
    session = db_manager.get_session_direct()
    
    try:
        # Test channel conversion
        channels = session.query(TelegramChannel).all()
        if channels:
            channel = channels[0]
            print(f"Testing channel conversion for: {channel.name}")
            channel_response = convert_channel_to_response(channel)
            print(f"Channel response: {channel_response}")
        
        # Test post conversion
        posts = session.query(TelegramPost).all()
        if posts:
            post = posts[0]
            print(f"\nTesting post conversion for: {post.title[:50] if post.title else 'No title'}")
            print(f"Post channel: {post.channel.name if post.channel else 'No channel'}")
            
            try:
                post_response = convert_post_to_response(post)
                print(f"Post response created successfully")
                print(f"Post title: {post_response.title}")
                print(f"Post channel: {post_response.channel.name}")
            except Exception as e:
                print(f"Error converting post: {e}")
                import traceback
                traceback.print_exc()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    test_api_conversion() 