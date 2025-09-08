#!/usr/bin/env python3

import asyncio
import json

import requests
import websockets


# First, let's get a valid JWT token
def get_auth_token():
    """Get authentication token for testing"""
    login_url = "http://localhost:8000/api/v1/login/access-token"

    # Try to login with existing user - you'll need to use actual credentials
    # For now, let's just create a token manually or use existing one

    # If you have users in your database, try this:
    login_data = {
        "username": "alice@example.com",  # Replace with actual user email
        "password": "password123",  # Replace with actual password
    }

    try:
        response = requests.post(login_url, data=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None


async def test_websocket():
    """Test WebSocket connection"""

    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Could not get auth token")
        return

    print(f"✅ Got auth token: {token[:20]}...")

    # Test the correct WebSocket endpoint
    url = f"ws://localhost:8000/api/v1/chat/ws/default?token={token}"
    
    print(f"\n🔗 Testing WebSocket connection: {url}")
    try:
        async with websockets.connect(url) as websocket:
            print(f"✅ Connected successfully!")

            # Send a ping message
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            print("� Sent ping message")

            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 Received: {response}")
            
            # Test sending a chat message
            print("\n💬 Testing chat message...")
            chat_message = {
                "type": "send_message",
                "conversation_id": "10063778-57a1-4486-b5de-0a7ad79811a6",  # Use a valid conversation ID
                "content": "Hello from WebSocket test!",
                "message_type": "text"
            }
            await websocket.send(json.dumps(chat_message))
            print("📤 Sent chat message")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 Received: {response}")

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ Connection closed: {e}")
    except asyncio.TimeoutError:
        print("❌ Timeout waiting for response")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())
