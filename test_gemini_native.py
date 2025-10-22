"""Test Gemini with native Google API"""
import sys

print("Testing Gemini Native API")
print("=" * 60)

try:
    from agents.config import Config
    import google.generativeai as genai
    
    print(f"[1] API Key: {Config.GOOGLE_API_KEY[:20]}...")
    
    genai.configure(api_key=Config.GOOGLE_API_KEY)
    
    # List available models
    print("\n[2] Available models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"    - {model.name}")
    
    # Test with gemini-pro
    print("\n[3] Testing gemini-pro:")
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'test successful' in 3 words")
    print(f"    Response: {response.text}")
    print("\n[SUCCESS] Native Gemini API works!")
    
except Exception as e:
    print(f"\n[FAIL] {e}")
    import traceback
    traceback.print_exc()
