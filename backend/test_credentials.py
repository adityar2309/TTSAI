from google.cloud import texttospeech
from google.cloud import speech
import google.generativeai as genai
import os
from dotenv import load_dotenv

def test_credentials():
    # Load environment variables
    load_dotenv()
    
    print("Testing Google Cloud credentials...")
    
    try:
        # Test Text-to-Speech
        tts_client = texttospeech.TextToSpeechClient()
        print("✓ Text-to-Speech client initialized successfully")
        
        # Test Speech-to-Text
        speech_client = speech.SpeechClient()
        print("✓ Speech-to-Text client initialized successfully")
        
        # Test Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        print(f"API Key found: {api_key[:4]}...{api_key[-4:]}")
        
        genai.configure(api_key=api_key)
        
        # List available models first
        print("\nAvailable models:")
        for m in genai.list_models():
            print(f"- {m.name}")
        
        # Try to get the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Test with a simple prompt
        response = model.generate_content("Say hello!")
        print(f"\nTest response: {response.text}")
        
        print("✓ Gemini API initialized successfully")
        print("\nAll credentials are working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing credentials: {str(e)}")
        if 'api_key' in locals():
            print(f"\nDebug info:")
            print(f"- API key length: {len(api_key)}")
            print(f"- API key format: {api_key[:4]}...{api_key[-4:]}")
        return False

if __name__ == "__main__":
    test_credentials() 