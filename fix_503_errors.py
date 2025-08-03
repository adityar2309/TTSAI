#!/usr/bin/env python3
"""
Fix 503 Service Unavailable errors in TTSAI backend
"""

import os
import sys
import subprocess
import time

def set_environment_variable():
    """Set the Gemini API key in the current environment"""
    api_key = "AIzaSyCZzto0BK9sPgX8_QEidRP4mM8-90tf-OM"
    
    print("🔧 Setting GEMINI_API_KEY environment variable...")
    os.environ['GEMINI_API_KEY'] = api_key
    
    # Verify it's set
    if os.getenv('GEMINI_API_KEY'):
        print(f"✅ API Key set: {api_key[:10]}...")
        return True
    else:
        print("❌ Failed to set API key")
        return False

def test_gemini_connection():
    """Test if Gemini API is working"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        print("🔄 Testing Gemini connection...")
        genai.configure(api_key=api_key)
        
        # Try with gemini-pro first (more stable)
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Hello")
            print(f"✅ Gemini API working with gemini-pro!")
            return True
        except Exception as e:
            print(f"❌ gemini-pro failed: {e}")
            
            # Try with the configured model
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = model.generate_content("Hello")
                print(f"✅ Gemini API working with gemini-2.0-flash-exp!")
                return True
            except Exception as e2:
                print(f"❌ gemini-2.0-flash-exp failed: {e2}")
                return False
                
    except ImportError:
        print("❌ google-generativeai package not installed")
        return False
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

def test_backend():
    """Test the backend endpoints"""
    print("🔄 Testing backend...")
    
    try:
        # Change to backend directory
        os.chdir('backend')
        
        # Run the backend test
        result = subprocess.run([sys.executable, 'test_backend.py'], 
                              capture_output=True, text=True, timeout=30)
        
        print("Backend Test Results:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Backend test timed out")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False
    finally:
        # Change back to original directory
        os.chdir('..')

def suggest_fixes():
    """Suggest additional fixes"""
    print("\n" + "="*50)
    print("🛠️  ADDITIONAL SOLUTIONS")
    print("="*50)
    
    print("\n1. **Manual Environment Setup:**")
    print("   Add this to your backend/.env file:")
    print("   GEMINI_API_KEY=AIzaSyCZd37vcyOUdxhQ5XWJrDCOkbRRDadf-OM")
    
    print("\n2. **PowerShell Setup:**")
    print("   $env:GEMINI_API_KEY = 'AIzaSyCZd37vcyOUdxhQ5XWJrDCOkbRRDadf-OM'")
    
    print("\n3. **Redeploy Backend:**")
    print("   cd backend")
    print("   gcloud run deploy ttsai-backend --source . --region us-central1")
    
    print("\n4. **Check Google AI Studio:**")
    print("   - Visit: https://aistudio.google.com/app/apikey")
    print("   - Verify your API key is active")
    print("   - Check quota and usage limits")
    
    print("\n5. **Alternative Model:**")
    print("   - Edit backend/config.py")
    print("   - Change LLM_MODEL to 'gemini-pro' (more stable)")

def main():
    """Main diagnostic and fix function"""
    print("🚨 FIXING 503 SERVICE UNAVAILABLE ERRORS")
    print("="*50)
    
    # Step 1: Set environment variable
    if not set_environment_variable():
        print("❌ Failed to set environment variable")
        suggest_fixes()
        return
    
    # Step 2: Test Gemini connection
    if not test_gemini_connection():
        print("❌ Gemini API connection failed")
        suggest_fixes()
        return
    
    # Step 3: Test backend
    if not test_backend():
        print("❌ Backend tests still failing")
        suggest_fixes()
        return
    
    print("\n🎉 SUCCESS! The 503 errors should now be fixed!")
    print("\n📝 Next Steps:")
    print("1. Your frontend should now work with translations")
    print("2. If issues persist, redeploy your backend to Cloud Run")
    print("3. Check the browser console for any remaining errors")

if __name__ == "__main__":
    main() 