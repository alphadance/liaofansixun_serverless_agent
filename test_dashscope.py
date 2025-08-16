#!/usr/bin/env python3
"""Test script for DashScope API integration."""

import asyncio
import json
import sys

import httpx


async def test_dashscope_server(base_url: str = "http://localhost:8000") -> None:
    """Test the DashScope proxy server."""
    async with httpx.AsyncClient() as client:
        # Test health check
        print("Testing health check...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"Health check: {response.json()}\n")
        except Exception as e:
            print(f"Error: {e}\n")
        
        # Test initial question
        print("Testing initial question...")
        try:
            response = await client.post(
                f"{base_url}/process",
                json={"user_input": "你好，请介绍一下《了凡四训》"},
                headers={"X-Request-ID": "test-1"}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {data['text'][:100]}...")
                print(f"Session ID: {data['session_id']}")
                session_id = data['session_id']
            else:
                print(f"Error: {response.text}")
                return
        except Exception as e:
            print(f"Error: {e}")
            return
        
        # Test follow-up question with session
        print("\nTesting follow-up question with session...")
        try:
            response = await client.post(
                f"{base_url}/process",
                json={
                    "user_input": "第一部分'立命之学'的核心观点是什么？",
                    "session_id": session_id
                },
                headers={"X-Request-ID": "test-2"}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {data['text'][:100]}...")
                print(f"Session maintained: {data['session_id'] == session_id}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    asyncio.run(test_dashscope_server(base_url))