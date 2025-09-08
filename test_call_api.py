#!/usr/bin/env python3

import json

import requests


def test_call_initiate():
    """Test the call initiate endpoint"""

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

        # Test call initiation
        call_url = "http://localhost:8000/api/v1/calls/initiate"

        # Test different payload formats
        test_payloads = [
            # Correct format - JSON body
            {
                "description": "JSON body with participants list",
                "data": {
                    "participants": [
                        "1971222b-8798-4d2b-a4b0-fff035ac844b"
                    ],  # Some user ID
                    "call_type": "audio",
                },
                "content_type": "application/json",
            },
            # Alternative format - query params
            {
                "description": "Query parameters",
                "data": None,
                "content_type": "application/json",
                "params": {
                    "participants": ["1971222b-8798-4d2b-a4b0-fff035ac844b"],
                    "call_type": "audio",
                },
            },
        ]

        for test in test_payloads:
            print(f"\n🧪 Testing: {test['description']}")

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": test["content_type"],
            }

            if test["data"]:
                print(f"Data: {json.dumps(test['data'], indent=2)}")
                response = requests.post(call_url, json=test["data"], headers=headers)
            else:
                print(f"Params: {test.get('params', {})}")
                response = requests.post(
                    call_url, params=test.get("params", {}), headers=headers
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
    test_call_initiate()
