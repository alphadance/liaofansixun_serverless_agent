#!/usr/bin/env python3
"""Simple test script for the proxy server."""

import asyncio
import json
import sys

import httpx


async def test_server(base_url: str = "http://localhost:8000") -> None:
    """Test the proxy server endpoints."""
    async with httpx.AsyncClient() as client:
        # Test valid request
        print("Testing valid request...")
        try:
            response = await client.post(
                f"{base_url}/process",
                json={"user_input": "Hello, how are you?"},
                headers={"X-Request-ID": "test-123"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test invalid request (empty input)
        print("\nTesting invalid request (empty input)...")
        try:
            response = await client.post(
                f"{base_url}/process",
                json={"user_input": ""}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test invalid request (missing field)
        print("\nTesting invalid request (missing field)...")
        try:
            response = await client.post(
                f"{base_url}/process",
                json={}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    asyncio.run(test_server(base_url))