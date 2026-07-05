#!/usr/bin/env python3
"""
Ollama Integration Test Script
Tests the Ollama service and API connectivity
"""

import requests
import json
import sys

OLLAMA_URL = "http://localhost:11434/api"
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_status(message, status='info'):
    """Print colored status messages"""
    if status == 'success':
        print(f"{GREEN}✓{RESET} {message}")
    elif status == 'error':
        print(f"{RED}✗{RESET} {message}")
    elif status == 'warning':
        print(f"{YELLOW}⚠{RESET} {message}")
    else:
        print(f"  {message}")

def test_ollama_service():
    """Test if Ollama service is running"""
    print("\n" + "="*60)
    print("OLLAMA SERVICE TEST")
    print("="*60)
    
    try:
        response = requests.get(f"{OLLAMA_URL}/tags", timeout=5)
        if response.status_code == 200:
            print_status("Ollama service is running", 'success')
            return True
        else:
            print_status(f"Ollama service returned status code: {response.status_code}", 'error')
            return False
    except requests.exceptions.ConnectionError:
        print_status("Ollama service is not running", 'error')
        print_status("Start Ollama with: ollama serve", 'info')
        return False
    except Exception as e:
        print_status(f"Error connecting to Ollama: {e}", 'error')
        return False

def test_available_models():
    """List available Ollama models"""
    print("\n" + "="*60)
    print("AVAILABLE MODELS")
    print("="*60)
    
    try:
        response = requests.get(f"{OLLAMA_URL}/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print_status(f"Found {len(models)} model(s):", 'success')
                for model in models:
                    name = model.get('name', 'Unknown')
                    size = model.get('size', 0) / (1024**3)  # Convert to GB
                    print(f"  • {name} ({size:.2f} GB)")
                return True
            else:
                print_status("No models installed", 'warning')
                print_status("Install a model with: ollama pull qwen2.5:0.5b", 'info')
                return False
        else:
            print_status("Failed to list models", 'error')
            return False
    except Exception as e:
        print_status(f"Error listing models: {e}", 'error')
        return False

def test_ollama_generation():
    """Test Ollama text generation"""
    print("\n" + "="*60)
    print("TEXT GENERATION TEST")
    print("="*60)
    
    try:
        response = requests.get(f"{OLLAMA_URL}/tags", timeout=5)
        models = response.json().get('models', [])
        
        if not models:
            print_status("No models available for testing", 'warning')
            return False
            
        # Use the first available model
        model_name = models[0].get('name')
        print_status(f"Testing with model: {model_name}", 'info')
        
        payload = {
            "model": model_name,
            "prompt": "Generate 3 marketing hashtags for anti-gravity shoes. Return only hashtags.",
            "stream": False
        }
        
        print_status("Sending test prompt...", 'info')
        response = requests.post(f"{OLLAMA_URL}/generate", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            generated_text = data.get('response', '')
            
            if generated_text:
                print_status("Generation successful!", 'success')
                print("\nGenerated Response:")
                print("-" * 60)
                print(generated_text[:200])  # Show first 200 chars
                if len(generated_text) > 200:
                    print("... (truncated)")
                print("-" * 60)
                return True
            else:
                print_status("Empty response from Ollama", 'error')
                return False
        else:
            print_status(f"Generation failed with status: {response.status_code}", 'error')
            return False
            
    except requests.exceptions.Timeout:
        print_status("Request timed out (this is normal for first run)", 'warning')
        return False
    except Exception as e:
        print_status(f"Error during generation: {e}", 'error')
        return False

def test_ollama_chat():
    """Test Ollama chat API"""
    print("\n" + "="*60)
    print("CHAT API TEST")
    print("="*60)
    
    try:
        response = requests.get(f"{OLLAMA_URL}/tags", timeout=5)
        models = response.json().get('models', [])
        
        if not models:
            print_status("No models available for testing", 'warning')
            return False
            
        model_name = models[0].get('name')
        print_status(f"Testing chat with model: {model_name}", 'info')
        
        messages = [
            {"role": "system", "content": "You are a helpful marketing assistant."},
            {"role": "user", "content": "Give me one tip to improve Instagram ad CTR."}
        ]
        
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False
        }
        
        print_status("Sending chat message...", 'info')
        response = requests.post(f"{OLLAMA_URL}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            chat_response = data.get('message', {}).get('content', '')
            
            if chat_response:
                print_status("Chat successful!", 'success')
                print("\nChat Response:")
                print("-" * 60)
                print(chat_response[:200])
                if len(chat_response) > 200:
                    print("... (truncated)")
                print("-" * 60)
                return True
            else:
                print_status("Empty chat response", 'error')
                return False
        else:
            print_status(f"Chat failed with status: {response.status_code}", 'error')
            return False
            
    except requests.exceptions.Timeout:
        print_status("Request timed out", 'warning')
        return False
    except Exception as e:
        print_status(f"Error during chat: {e}", 'error')
        return False

def test_flask_app():
    """Test if Flask app is running"""
    print("\n" + "="*60)
    print("FLASK APPLICATION TEST")
    print("="*60)
    
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=5, allow_redirects=False)
        if response.status_code in [200, 302]:
            print_status("Flask app is running on port 5000", 'success')
            return True
        else:
            print_status(f"Flask app returned status: {response.status_code}", 'warning')
            return False
    except requests.exceptions.ConnectionError:
        print_status("Flask app is not running", 'warning')
        print_status("Start Flask with: python app.py", 'info')
        return False
    except Exception as e:
        print_status(f"Error checking Flask: {e}", 'error')
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("OLLAMA INTEGRATION TEST SUITE")
    print("="*60)
    
    results = {
        'service': test_ollama_service(),
        'models': test_available_models(),
        'generation': test_ollama_generation(),
        'chat': test_ollama_chat(),
        'flask': test_flask_app()
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = 'success' if result else 'error'
        print_status(f"{test_name.upper()}: {'PASS' if result else 'FAIL'}", status)
    
    print("\n" + "-"*60)
    print(f"Total: {passed}/{total} tests passed")
    print("-"*60)
    
    if passed == total:
        print_status("\n✨ All systems operational! Your Ollama chatbot is ready!", 'success')
        return 0
    else:
        print_status("\n⚠️  Some tests failed. Check the output above for details.", 'warning')
        return 1

if __name__ == '__main__':
    sys.exit(main())
