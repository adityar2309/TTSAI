from google.cloud import texttospeech
from google.cloud import speech
import requests
import os
from dotenv import load_dotenv
from config import get_llm_config, get_model_name, OPENROUTER_API_KEY, OPENROUTER_BASE_URL

def test_credentials():
    # Load environment variables
    load_dotenv()
    
    print("Testing Google Cloud and OpenRouter credentials...")
    
    try:
        # Test Text-to-Speech
        tts_client = texttospeech.TextToSpeechClient()
        print("✓ Text-to-Speech client initialized successfully")
        
        # Test Speech-to-Text
        speech_client = speech.SpeechClient()
        print("✓ Speech-to-Text client initialized successfully")
        
        # Test OpenRouter with configured model
        api_key = OPENROUTER_API_KEY
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        print(f"OpenRouter API Key found: {api_key[:8]}...{api_key[-4:]}")
        
        # Get LLM configuration from centralized config
        llm_config = get_llm_config()
        model_name = get_model_name()
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": "Say hello and confirm you are Gemini 2.0 Flash!"}],
            "max_tokens": llm_config["max_tokens"]
        }
        
        print(f"\nTesting OpenRouter API with {model_name}...")
        response = requests.post(
            OPENROUTER_BASE_URL,
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            test_response = result['choices'][0]['message']['content']
            print(f"✓ OpenRouter API test successful!")
            print(f"Model response: {test_response}")
            print(f"Model used: {model_name}")
        else:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
        
        print("\n✅ All credentials are working correctly!")
        print(f"✅ {model_name} model is accessible via OpenRouter")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing credentials: {str(e)}")
        if 'api_key' in locals():
            print(f"\nDebug info:")
            print(f"- OpenRouter API key length: {len(api_key)}")
            print(f"- OpenRouter API key format: {api_key[:8]}...{api_key[-4:]}")
        return False

if __name__ == "__main__":
    test_credentials() 