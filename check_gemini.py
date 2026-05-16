#!/usr/bin/env python3
"""
Gemini Model Checker - Diagnose which models are available and working
Run this script to test Gemini API connectivity and available models.
"""

import os
import sys
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def check_gemini_availability():
    """Check which Gemini models are available."""
    api_key = os.getenv("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("   Set it in .env file: GEMINI_API_KEY=your_key_here")
        return False
    
    print(f"✅ API Key found (length: {len(api_key)} chars)\n")
    
    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("   Install with: pip install google-generativeai")
        return False
    
    print("✅ google-generativeai package available\n")
    
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured successfully\n")
    except Exception as e:
        print(f"❌ Failed to configure Gemini API: {e}\n")
        return False
    
    # List available models
    print("📋 Checking available models...\n")
    try:
        models = genai.list_models()
        available_models = []
        for model in models:
            if "generateContent" in [method.name for method in model.supported_generation_methods]:
                available_models.append(model.name)
                print(f"✅ {model.name}")
        
        if not available_models:
            print("⚠️  No models found that support generateContent")
            return False
        
        print(f"\n✅ Found {len(available_models)} available models\n")
        
        # Try free-tier models with smart fallback
        print("🧪 Testing FREE-TIER models (best to worst)...\n")
        test_models = [
            "gemini-pro",           # Most stable, widely available
            "gemini-2.0-flash",     # Newest, free tier
            "gemini-1.5-flash",     # Fast, free tier
        ]
        
        for model_name in test_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say 'Hello'", stream=False)
                if response.text:
                    print(f"✅ {model_name}: WORKING (SDK)")
                else:
                    print(f"⚠️  {model_name}: No response text")
            except Exception as e:
                error_msg = str(e)
                if "not found" in error_msg.lower():
                    print(f"❌ {model_name}: Not available (SDK)")
                else:
                    print(f"⚠️  {model_name}: {error_msg[:50]}...")
        
        # Also test REST API for each model
        print("\n🧪 Testing REST API endpoints...\n")
        for model_name in test_models:
            try:
                rest_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
                response = requests.post(rest_url, json=payload, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ {model_name}: WORKING (REST API)")
                elif response.status_code == 404:
                    print(f"❌ {model_name}: Not found (REST API)")
                else:
                    print(f"⚠️  {model_name}: {response.status_code} (REST API)")
            except Exception as e:
                print(f"❌ {model_name}: Connection error")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing models: {e}\n")
        return False


def recommend_fix():
    """Provide recommendations for fixing the issue."""
    print("\n" + "="*60)
    print("RECOMMENDED FIXES - FREE TIER ONLY")
    print("="*60 + "\n")
    
    print("1. Verify API Key (Free Tier):")
    print("   - Go to: https://aistudio.google.com/app/apikey")
    print("   - Create a FREE API key (no credit card needed)")
    print("   - Add to .env: GEMINI_API_KEY=your_key\n")
    
    print("2. Free Tier Limits:")
    print("   - Up to 15 requests per minute")
    print("   - Up to 1,500 requests per day")
    print("   - Works great for this app!\n")
    
    print("3. Available Free Models (in order of preference):")
    print("   ✅ gemini-pro (most stable - recommended)")
    print("   ✅ gemini-2.0-flash (newest - good option)")
    print("   ✅ gemini-1.5-flash (fast - good backup)\n")
    
    print("4. Update google-generativeai package:")
    print("   python -m pip install --upgrade google-generativeai\n")
    
    print("5. For NYC Trail Planner:")
    print("   - App tries gemini-pro → gemini-2.0-flash → gemini-1.5-flash")
    print("   - All are FREE tier, no payment needed")
    print("   - Falls back to local generation if API is down\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("GEMINI MODEL AVAILABILITY CHECKER")
    print("="*60 + "\n")
    
    success = check_gemini_availability()
    
    if success:
        print("\n✅ Gemini API is ready to use!")
    else:
        print("\n❌ Gemini API has issues - see recommendations below")
        recommend_fix()
    
    sys.exit(0 if success else 1)
