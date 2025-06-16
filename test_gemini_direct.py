#!/usr/bin/env python3
"""
Direct test of Gemini API to diagnose the 503 translation errors
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test if Gemini API is working with the current key"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test with a simple model
        print("🔄 Testing Gemini model initialization...")
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        print("🔄 Testing content generation...")
        response = model.generate_content("Hello, world!")
        
        print(f"✅ Gemini API working! Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        
        # Check if it's an API key issue
        if "API_KEY_INVALID" in str(e) or "invalid API key" in str(e).lower():
            print("💡 Solution: Your API key appears to be invalid")
            print("   1. Check your Google AI Studio console: https://aistudio.google.com/app/apikey")
            print("   2. Generate a new API key if needed")
            print("   3. Update your .env file with the new key")
        
        # Check if it's a quota issue
        elif "quota" in str(e).lower() or "rate limit" in str(e).lower():
            print("💡 Solution: API quota/rate limit exceeded")
            print("   1. Check your Google AI Studio quota")
            print("   2. Wait a few minutes and try again")
            print("   3. Consider upgrading your plan if needed")
        
        # Check if it's a model issue
        elif "model" in str(e).lower():
            print("💡 Solution: Model access issue")
            print("   1. Try with a different model like 'gemini-pro'")
            print("   2. Check if you have access to gemini-2.0-flash-exp")
        
        return False

def test_alternative_model():
    """Test with an alternative Gemini model"""
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        return False
    
    try:
        genai.configure(api_key=api_key)
        
        print("🔄 Testing alternative model 'gemini-pro'...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Test")
        
        print(f"✅ Alternative model working! Response: {response.text}")
        print("💡 Consider updating config.py to use 'gemini-pro' instead")
        return True
        
    except Exception as e:
        print(f"❌ Alternative model also failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("GEMINI API DIAGNOSTIC TEST")
    print("=" * 50)
    
    success = test_gemini_api()
    
    if not success:
        print("\n" + "=" * 50)
        print("TRYING ALTERNATIVE MODEL")
        print("=" * 50)
        test_alternative_model()
    
    print("\n" + "=" * 50)
    print("NEXT STEPS")
    print("=" * 50)
    
    if success:
        print("✅ Gemini is working. The 503 error might be temporary.")
        print("💡 Try redeploying your backend to Google Cloud Run:")
        print("   cd backend && gcloud run deploy")
    else:
        print("❌ Gemini API is not working.")
        print("💡 Possible solutions:")
        print("   1. Fix your API key (see error messages above)")
        print("   2. Use a fallback provider temporarily")
        print("   3. Check Google AI Studio status") 