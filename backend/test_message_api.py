#!/usr/bin/env python3

import json

import requests


def test_message_endpoint():
    """Test the POST /api/v1/messages/ endpoint"""

    # Get auth token first
    login_url = "http://localhost:8000/api/v1/login/access-token"
    login_data = {"username": "alice@example.com", "password": "password123"}

    try:
        response = requests.post(login_url, data=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return

        token = response.json()["access_token"]
        print(f"✅ Got auth token: {token[:20]}...")

        # Get conversations to get a valid conversation_id
        conv_response = requests.get(
            "http://localhost:8000/api/v1/conversations/",
            headers={"Authorization": f"Bearer {token}"},
        )

        if conv_response.status_code != 200:
            print(f"❌ Failed to get conversations: {conv_response.status_code}")
            return

        conversations = conv_response.json()
        if not conversations.get("data"):
            print("❌ No conversations found")
            return

        conversation_id = conversations["data"][0]["id"]
        print(f"✅ Using conversation_id: {conversation_id}")

        # Test the POST /api/v1/messages/ endpoint
        message_url = "http://localhost:8000/api/v1/messages/"

        # Test different payload formats
        test_payloads = [
            # Current format (query params + body)
            {
                "url": f"{message_url}?conversation_id={conversation_id}&message_type=text",
                "data": {
                    "ciphertext": "Hello, this is a test message!",
                    "recipient_keys": [],
                },
                "description": "Query params + JSON body",
            },
            # Alternative format (all in body)
            {
                "url": message_url,
                "data": {
                    "conversation_id": conversation_id,
                    "ciphertext": "Hello, this is a test message!",
                    "message_type": "text",
                    "recipient_keys": [],
                },
                "description": "All in JSON body",
            },
        ]

        for test in test_payloads:
            print(f"\n🧪 Testing: {test['description']}")
            print(f"URL: {test['url']}")
            print(f"Data: {json.dumps(test['data'], indent=2)}")

            response = requests.post(
                test["url"],
                json=test["data"],
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            )

            print(f"Status: {response.status_code}")
            if response.status_code == 422:
                print(f"❌ Validation Error: {response.text}")
            elif response.status_code == 200:
                print(f"✅ Success: {response.json()}")
            else:
                print(f"❓ Other response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_message_endpoint()
