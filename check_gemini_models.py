"""Check Available Gemini Models"""
import sys

print("=" * 60)
print("Checking Available Gemini Models")
print("=" * 60)

try:
    from agents.config import Config
    import google.generativeai as genai
    
    print(f"\n[1] API Key: {Config.GOOGLE_API_KEY[:20]}...")
    genai.configure(api_key=Config.GOOGLE_API_KEY)
    
    print("\n[2] Available Models:")
    available = []
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"    - {model.name}")
            available.append(model.name)
    
    if not available:
        print("    No models found!")
        sys.exit(1)
    
    # Test first available model
    print(f"\n[3] Testing: {available[0]}")
    model = genai.GenerativeModel(available[0].replace('models/', ''))
    response = model.generate_content("Say 'OK' in one word")
    print(f"    Response: {response.text}")
    print(f"\n[SUCCESS] Working model: {available[0]}")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
