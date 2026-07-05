"""
Ollama AI Service
Handles all interactions with the local Ollama API
"""
import requests
import json
import re


class OllamaService:
    """Service class for Ollama AI integration"""
    
    def __init__(self, config):
        self.url = config.OLLAMA_URL
        self.model = config.OLLAMA_MODEL
        self.timeout = config.OLLAMA_TIMEOUT
        self.max_tokens = config.OLLAMA_MAX_TOKENS
        self.chat_histories = {}  # Store chat histories per user
    
    def get_available_models(self):
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.url}/tags", timeout=2)
            if response.status_code == 200:
                return [m['name'] for m in response.json().get('models', [])]
        except Exception as e:
            print(f"Failed to get models: {e}")
        return []
    
    def select_model(self):
        """Select the best available model"""
        models = self.get_available_models()
        if not models:
            return self.model
        
        preferred = ['qwen2.5:0.5b', 'tinyllama', 'llama3.2:1b', 'llama3.2:3b']
        for p in preferred:
            if any(p in m for m in models):
                return next(m for m in models if p in m)
        
        return models[0]  # Fallback to first available
    
    def generate_text(self, prompt, json_mode=False):
        """
        Generate text using Ollama
        
        Args:
            prompt: The input prompt
            json_mode: Whether to return JSON format
            
        Returns:
            Generated text or None if failed
        """
        try:
            model = self.select_model()
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": self.max_tokens
                }
            }
            
            if json_mode:
                payload["format"] = "json"
            
            response = requests.post(
                f"{self.url}/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
        except Exception as e:
            print(f"Ollama generate failed: {e}")
        
        return None
    
    def chat(self, messages):
        """
        Chat with Ollama using conversation history
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Generated response or None if failed
        """
        try:
            model = self.select_model()
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": self.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.url}/chat",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get('message', {}).get('content', '')
        except Exception as e:
            print(f"Ollama chat failed: {e}")
        
        return None
    
    def get_chat_history(self, user_id):
        """Get chat history for a user"""
        return self.chat_histories.get(user_id, [])
    
    def add_to_history(self, user_id, role, content):
        """Add a message to chat history"""
        if user_id not in self.chat_histories:
            self.chat_histories[user_id] = []
        
        self.chat_histories[user_id].append({
            "role": role,
            "content": content
        })
        
        # Keep only last 10 messages
        self.chat_histories[user_id] = self.chat_histories[user_id][-10:]
    
    def clear_history(self, user_id):
        """Clear chat history for a user"""
        if user_id in self.chat_histories:
            self.chat_histories[user_id] = []
    
    @staticmethod
    def clean_json_response(text):
        """Clean Ollama JSON output"""
        if not text:
            return None
        
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
        
        try:
            return json.loads(text)
        except Exception:
            try:
                cleaned = re.sub(r',\s*([\]}])', r'\1', text)
                cleaned = cleaned.replace("'", '"')
                return json.loads(cleaned)
            except Exception:
                return None


# Global service instance (will be initialized in app)
ollama_service = None
