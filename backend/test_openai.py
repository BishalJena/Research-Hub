#!/usr/bin/env python3
"""
Quick test to check OpenAI/OpenRouter API connectivity
"""
import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openai_connection():
    """Test OpenAI/OpenRouter API connection"""
    try:
        print("Testing OpenAI/OpenRouter API connection...")
        
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
        
        print(f"API Base: {api_base}")
        print(f"API Key: {api_key[:20]}..." if api_key else "No API key")
        
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        response = await client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "user", "content": "Hello, this is a test. Please respond with 'API working'."}
            ],
            max_tokens=10,
            temperature=0.1,
            extra_headers={
                "HTTP-Referer": "https://research-hub.apcce.gov.in",
                "X-Title": "Smart Research Hub"
            }
        )
        
        print("✅ API Response:", response.choices[0].message.content)
        return True
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_openai_connection())
    print(f"Test result: {'PASS' if result else 'FAIL'}")