#!/usr/bin/env python3
"""
Test script for detailed AI responses
Tests the enhanced chatbot's ability to provide comprehensive answers
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_header(title):
    print("\n" + "="*80)
    print(f"{CYAN}{title}{RESET}")
    print("="*80)

def print_response(response_text, ai_source):
    print(f"\n{GREEN}AI Response ({ai_source}):{RESET}")
    print("-" * 80)
    print(response_text)
    print("-" * 80)
    print(f"Length: {len(response_text)} characters")
    print(f"Word count: {len(response_text.split())} words")

def login():
    """Login to get session cookie"""
    session = requests.Session()
    
    # Login with customer account
    response = session.post(
        f"{BASE_URL}/login",
        data={
            'email': 'customer@antigravity.io',
            'password': 'pass123'
        },
        allow_redirects=True
    )
    
    if response.status_code == 200:
        print(f"{GREEN}✓{RESET} Logged in successfully")
        return session
    else:
        print(f"{YELLOW}✗{RESET} Login failed")
        return None

def test_chat_query(session, query, test_name):
    """Send a chat query and display the response"""
    print_header(f"TEST: {test_name}")
    print(f"Query: {CYAN}{query}{RESET}")
    
    start_time = time.time()
    
    try:
        response = session.post(
            f"{BASE_URL}/api/ai-chat",
            json={"message": query},
            timeout=90
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            ai_source = data.get('ai_source', 'Unknown')
            is_mock = data.get('isMock', False)
            
            print(f"\n{GREEN}✓{RESET} Response received in {elapsed:.2f} seconds")
            print(f"Source: {ai_source} {'(Mock Fallback)' if is_mock else ''}")
            print_response(response_text, ai_source)
            
            # Check response quality
            word_count = len(response_text.split())
            has_formatting = any(marker in response_text for marker in ['**', '•', '1.', '2.', '##'])
            
            print(f"\n{CYAN}Quality Metrics:{RESET}")
            print(f"  • Comprehensive: {'✓' if word_count > 100 else '✗'} ({word_count} words)")
            print(f"  • Formatted: {'✓' if has_formatting else '✗'}")
            print(f"  • Response time: {elapsed:.2f}s")
            
            return True
        else:
            print(f"{YELLOW}✗{RESET} Request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"{YELLOW}✗{RESET} Error: {e}")
        return False

def main():
    print(f"\n{CYAN}{'='*80}{RESET}")
    print(f"{CYAN}DETAILED RESPONSE TEST SUITE{RESET}")
    print(f"{CYAN}{'='*80}{RESET}")
    
    # Login first
    session = login()
    if not session:
        print("Failed to login. Please check if Flask app is running.")
        return
    
    # Test queries designed to elicit detailed responses
    test_queries = [
        (
            "Provide a comprehensive marketing strategy for launching Hover Shoes including target audience, platforms, budget allocation, and content strategy",
            "Comprehensive Marketing Strategy"
        ),
        (
            "Explain everything about improving Instagram ad performance - including visuals, copy, targeting, timing, and A/B testing strategies",
            "Instagram Ad Optimization Guide"
        ),
        (
            "Give me a detailed breakdown of how to improve click-through rates with specific tactics for creative optimization, audience targeting, and performance tracking",
            "CTR Improvement Blueprint"
        ),
        (
            "Analyze my campaign performance and provide detailed recommendations",
            "Campaign Analysis (with database context)"
        ),
        (
            "What are the best practices for social media marketing in 2026? Provide a complete guide",
            "Social Media Best Practices"
        )
    ]
    
    results = []
    
    for query, test_name in test_queries:
        success = test_chat_query(session, query, test_name)
        results.append((test_name, success))
        time.sleep(2)  # Brief pause between requests
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = f"{GREEN}✓ PASS{RESET}" if success else f"{YELLOW}✗ FAIL{RESET}"
        print(f"{status} - {test_name}")
    
    print(f"\n{CYAN}Total: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}✨ All tests passed! Your chatbot provides detailed, comprehensive responses.{RESET}")
    else:
        print(f"\n{YELLOW}⚠️  Some tests failed. Check the output above for details.{RESET}")

if __name__ == '__main__':
    main()
