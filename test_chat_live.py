#!/usr/bin/env python3
"""Test the chat API endpoint."""
import requests
import json

def test_chat():
    url = "http://localhost:8000/api/v1/messages/send?user_id=user123"
    messages = [
        "Hello Jimmy!",
        "Who are you?",
        "Can you help me?",
        "What can you do?",
    ]
    
    print("=" * 60)
    print("🤖 JIMMY BOT CHAT TEST")
    print("=" * 60)
    
    for msg in messages:
        try:
            resp = requests.post(url, json={"content": msg}, timeout=10)
            data = resp.json()
            
            print(f"\n👤 YOU:   {msg}")
            print(f"🤖 JIMMY: {data['response']}")
            print(f"   [ID: {data['id'][:8]}...]")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ CHAT TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_chat()
