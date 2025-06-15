#!/usr/bin/env python3
"""
Setup script for AI Avatar Conversation System
Initializes the system and runs basic validation
"""

import os
import sys
import subprocess
import requests
import time
import json

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask-cors',
        'google-generativeai',
        'python-dotenv',
        'sqlalchemy',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n🔧 Checking environment variables...")
    
    required_vars = [
        'GEMINI_API_KEY',
        'GOOGLE_APPLICATION_CREDENTIALS'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}")
        else:
            missing_vars.append(var)
            print(f"❌ {var}")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables:")
        for var in missing_vars:
            if var == 'GEMINI_API_KEY':
                print(f"  {var}: Get your API key from https://makersuite.google.com/app/apikey")
            elif var == 'GOOGLE_APPLICATION_CREDENTIALS':
                print(f"  {var}: Path to your Google Cloud credentials JSON file")
        return False
    
    return True

def start_backend_server():
    """Start the backend server"""
    print("\n🚀 Starting backend server...")
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found")
        return None
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start the server
        process = subprocess.Popen([
            sys.executable, 'app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(5)
        
        # Check if server is running
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully")
                return process
            else:
                print("❌ Backend server not responding correctly")
                return None
        except requests.exceptions.RequestException:
            print("❌ Backend server not reachable")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        return None

def test_avatar_endpoints():
    """Test the avatar system endpoints"""
    print("\n🧪 Testing avatar endpoints...")
    
    base_url = "http://localhost:5000/api"
    
    # Test avatar fetching
    try:
        response = requests.get(f"{base_url}/avatars?language=en", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Avatar fetching: Found {data['total']} English avatars")
        else:
            print(f"❌ Avatar fetching failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Avatar fetching error: {e}")
        return False
    
    # Test specific avatar details
    try:
        response = requests.get(f"{base_url}/avatar/emma_teacher?language=en", timeout=10)
        if response.status_code == 200:
            avatar = response.json()
            print(f"✅ Avatar details: {avatar['name']} - {avatar['role']}")
        else:
            print(f"❌ Avatar details failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Avatar details error: {e}")
        return False
    
    # Test conversation session start
    try:
        payload = {
            'userId': 'test_user',
            'language': 'en',
            'avatarId': 'emma_teacher'
        }
        response = requests.post(f"{base_url}/conversation/start-session", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Session start: {data['session_id'][:8]}...")
            session_id = data['session_id']
        else:
            print(f"❌ Session start failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Session start error: {e}")
        return False
    
    # Test avatar conversation
    try:
        payload = {
            'text': 'Hello Emma!',
            'language': 'en',
            'userId': 'test_user',
            'avatarId': 'emma_teacher',
            'context': 'general',
            'proficiency': 'beginner',
            'conversationHistory': []
        }
        response = requests.post(f"{base_url}/conversation/avatar", json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Avatar conversation: {data['avatar']['name']} responded")
            print(f"   Response: {data['response'][:50]}...")
        else:
            print(f"❌ Avatar conversation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Avatar conversation error: {e}")
        return False
    
    return True

def display_avatar_showcase():
    """Display available avatars"""
    print("\n🤖 Avatar Showcase:")
    print("=" * 60)
    
    languages = ['en', 'es', 'fr', 'de', 'ja', 'zh']
    
    for lang in languages:
        try:
            response = requests.get(f"http://localhost:5000/api/avatars?language={lang}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"\n{lang.upper()} - {len(data['avatars'])} avatars:")
                for avatar in data['avatars']:
                    print(f"  {avatar['avatar_image']} {avatar['name']} - {avatar['role']}")
                    print(f"     {avatar['personality']}")
        except:
            print(f"\n{lang.upper()} - Unable to fetch avatars")
    
    print("\n" + "=" * 60)

def run_interactive_demo():
    """Run an interactive demo of the avatar system"""
    print("\n🎮 Interactive Avatar Demo")
    print("Type 'quit' to exit")
    
    # Select language and avatar
    print("\nAvailable languages: en, es, fr, de, ja, zh")
    language = input("Select language (default: en): ").strip() or 'en'
    
    # Get avatars for language
    try:
        response = requests.get(f"http://localhost:5000/api/avatars?language={language}")
        if response.status_code != 200:
            print("❌ Failed to get avatars")
            return
        
        avatars = response.json()['avatars']
        print(f"\nAvailable avatars for {language}:")
        for i, avatar in enumerate(avatars):
            print(f"{i+1}. {avatar['avatar_image']} {avatar['name']} - {avatar['role']}")
        
        choice = input(f"Select avatar (1-{len(avatars)}): ").strip()
        try:
            avatar_index = int(choice) - 1
            selected_avatar = avatars[avatar_index]
        except (ValueError, IndexError):
            selected_avatar = avatars[0]
        
        print(f"\n🤖 Starting conversation with {selected_avatar['name']}")
        print(f"Background: {selected_avatar['background']}")
        print("-" * 50)
        
        # Start conversation session
        session_response = requests.post('http://localhost:5000/api/conversation/start-session', json={
            'userId': 'demo_user',
            'language': language,
            'avatarId': selected_avatar['id']
        })
        
        if session_response.status_code != 200:
            print("❌ Failed to start conversation session")
            return
        
        session_data = session_response.json()
        print(f"🤖 {selected_avatar['name']}: {session_data['initial_message']['response']}")
        
        conversation_history = [session_data['initial_message']]
        
        # Interactive conversation loop
        while True:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Send message to avatar
            try:
                response = requests.post('http://localhost:5000/api/conversation/avatar', json={
                    'text': user_input,
                    'language': language,
                    'userId': 'demo_user',
                    'avatarId': selected_avatar['id'],
                    'context': 'general',
                    'proficiency': 'intermediate',
                    'conversationHistory': conversation_history
                })
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"\n🤖 {selected_avatar['name']}: {data['response']}")
                    
                    if data.get('translation') and data['translation'] != data['response']:
                        print(f"💬 Translation: {data['translation']}")
                    
                    if data.get('vocabulary'):
                        print(f"📚 Vocabulary: {', '.join(data['vocabulary'])}")
                    
                    if data.get('grammar_notes'):
                        print(f"📝 Grammar: {data['grammar_notes']}")
                    
                    if data.get('cultural_note'):
                        print(f"🌍 Culture: {data['cultural_note']}")
                    
                    if data.get('teaching_tip'):
                        print(f"💡 Tip: {data['teaching_tip']}")
                    
                    # Update conversation history
                    conversation_history.append({
                        'type': 'user',
                        'text': user_input,
                        'timestamp': '2024-01-01T00:00:00Z'
                    })
                    conversation_history.append({
                        'type': 'avatar',
                        'response': data['response'],
                        'timestamp': '2024-01-01T00:00:00Z'
                    })
                    
                    # Keep only last 5 exchanges
                    if len(conversation_history) > 10:
                        conversation_history = conversation_history[-10:]
                        
                else:
                    print(f"❌ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")

def main():
    """Main setup function"""
    print("🚀 AI Avatar Conversation System Setup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    # Check environment variables
    if not check_environment_variables():
        print("\n❌ Please set required environment variables")
        return
    
    # Start backend server
    server_process = start_backend_server()
    if not server_process:
        print("\n❌ Failed to start backend server")
        return
    
    try:
        # Test endpoints
        if test_avatar_endpoints():
            print("\n✅ All avatar endpoints working correctly!")
            
            # Display avatar showcase
            display_avatar_showcase()
            
            # Ask if user wants to run interactive demo
            demo = input("\n🎮 Run interactive demo? (y/n): ").strip().lower()
            if demo in ['y', 'yes']:
                run_interactive_demo()
            
            print("\n🎉 Avatar system setup complete!")
            print("\nNext steps:")
            print("1. Start your frontend: cd frontend && npm start")
            print("2. Test the avatar conversation feature")
            print("3. Run full test suite: python test_avatar_system.py")
            
        else:
            print("\n❌ Some avatar endpoints are not working correctly")
            
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
    
    finally:
        # Clean up
        if server_process:
            print("\n🧹 Stopping backend server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main() 