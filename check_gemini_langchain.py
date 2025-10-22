"""Check Gemini Models via LangChain"""
from agents.config import Config

print("=" * 60)
print("Testing Gemini Models with LangChain")
print("=" * 60)

models = [
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro-latest", 
    "gemini-1.5-pro",
    "gemini-pro",
    "gemini-1.0-pro",
]

print(f"\nAPI Key: {Config.GOOGLE_API_KEY[:20]}...\n")

for model_name in models:
    print(f"Testing: {model_name}")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.3,
            max_retries=1
        )
        
        msg = HumanMessage(content="Say OK")
        response = llm.invoke([msg])
        print(f"  [SUCCESS] {model_name} - Response: {response.content[:30]}\n")
        break
        
    except Exception as e:
        error = str(e)
        if "404" in error:
            print(f"  [FAIL] Not found\n")
        elif "429" in error:
            print(f"  [FAIL] Rate limit\n")
        elif "403" in error:
            print(f"  [FAIL] Invalid API key\n")
        else:
            print(f"  [FAIL] {error[:80]}\n")

print("=" * 60)
