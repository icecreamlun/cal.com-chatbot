"""
Check if all required environment variables are set.
"""

import os
from dotenv import load_dotenv

load_dotenv()

required_vars = {
    "OPENAI_API_KEY": "OpenAI API key for LLM calls",
    "CALCOM_API_KEY": "Cal.com API key (optional for testing classifier)",
    "CALCOM_USER_EMAIL": "Cal.com user email (optional for testing classifier)",
    "CALCOM_EVENT_TYPE_ID": "Cal.com event type ID (optional for testing classifier)"
}

print("=" * 60)
print("Environment Variables Check")
print("=" * 60)

all_set = True
for var, description in required_vars.items():
    value = os.getenv(var)
    if value:
        # Mask the value for security
        if "KEY" in var or "API" in var:
            masked = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"
            print(f"✅ {var}: {masked}")
        else:
            print(f"✅ {var}: {value}")
    else:
        print(f"❌ {var}: NOT SET")
        print(f"   Description: {description}")
        if var == "OPENAI_API_KEY":
            all_set = False

print("=" * 60)

if all_set:
    print("✅ Minimum required variables are set (OPENAI_API_KEY)")
    print("\n📝 Note: Cal.com variables are optional for testing the classifier")
    print("   You can test general questions without Cal.com API")
else:
    print("❌ OPENAI_API_KEY is required!")
    print("\n🔧 Fix:")
    print("   1. Copy env.example to .env:")
    print("      cp env.example .env")
    print("   2. Edit .env and add your OPENAI_API_KEY")
    print("   3. Restart the server")

print("\n💡 Testing imports...")
try:
    from calcom_chatbot.graph import compiled_graph
    print("✅ Graph imported successfully")
except Exception as e:
    print(f"❌ Failed to import graph: {e}")

try:
    from calcom_chatbot.utils.config import get_openai_api_key
    key = get_openai_api_key()
    print(f"✅ OpenAI API key loaded: {key[:10]}...{key[-4:]}")
except Exception as e:
    print(f"❌ Failed to load OpenAI API key: {e}")

print("=" * 60)

