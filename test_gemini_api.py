"""Test Gemini API - Check if gemini-1.5-flash works"""
import sys

print("=" * 60)
print("Testing Gemini API Models")
print("=" * 60)

# Test 1: Load config
try:
    from agents.config import Config
    print(f"\n[1] Config loaded")
    print(f"    API Key: {Config.GOOGLE_API_KEY[:20]}..." if Config.GOOGLE_API_KEY else "    No API key")
except Exception as e:
    print(f"\n[1] Config failed: {e}")
    sys.exit(1)

# Test 2: Try different Gemini models
models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
]

for model_name in models_to_test:
    print(f"\n[TEST] Model: {model_name}")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.3
        )
        print(f"    [OK] Initialized")
        
        # Try simple query
        message = HumanMessage(content="Say 'test successful' in 3 words")
        response = llm.invoke([message])
        print(f"    [OK] Response: {response.content[:50]}")
        print(f"    [SUCCESS] {model_name} WORKS!")
        break
        
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print(f"    [FAIL] 404 - Model not found")
        elif "429" in error_msg:
            print(f"    [FAIL] 429 - Rate limit/quota exceeded")
        elif "403" in error_msg:
            print(f"    [FAIL] 403 - Invalid API key")
        else:
            print(f"    [FAIL] {error_msg[:100]}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
