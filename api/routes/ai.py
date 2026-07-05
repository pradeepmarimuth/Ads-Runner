"""
AI Workspace API routes
Handles Ollama AI integration, caption generation, hashtag generation, and chat
"""
import os
import re
import json
import random
import datetime
from flask import Blueprint, jsonify, request, session, current_app
from api.middleware.auth import login_required
from database.models import db, User, Campaign, CampaignLog

ai_bp = Blueprint('ai', __name__, url_prefix='/api')


def get_ollama_service():
    """Get or create Ollama service instance"""
    if hasattr(current_app, 'ollama_service'):
        return current_app.ollama_service
    
    from api.services.ollama_service import OllamaService
    from backend.config import get_config
    service = OllamaService(get_config())
    current_app.ollama_service = service
    return service


# Mock helper functions
def mock_captions(name):
    """Generate mock captions for fallback"""
    n = re.sub(r'[^a-zA-Z0-9 ]', '', name or 'Product').strip().capitalize()
    templates = [
        [f"Defy gravity with {n} — The future is weightless.", 
         f"{n}: Because the ground is just a suggestion.", 
         f"Rise above everything. Rise with {n}."],
        [f"Experience the weightless revolution of {n}.", 
         f"Elevating your perspective — only with {n}.", 
         f"No gravity? No problem. {n} is here."],
        [f"Redefining physics: {n} brings anti-gravity to life.", 
         f"Float higher, dream bigger: Discover {n}.", 
         f"Break the chains of gravity with {n}."],
        [f"Step into the future of motion with {n}.", 
         f"{n} — where gravity becomes optional.", 
         f"Elevate your daily orbit with {n}."]
    ]
    idx = sum(ord(c) for c in n) % len(templates)
    return templates[idx]


def mock_hashtags(kw):
    """Generate mock hashtags for fallback"""
    c = re.sub(r'[^a-zA-Z0-9]', '', kw or 'hover').capitalize()
    tag_options = [
        [f"#{c}Ads", f"#Future{c}", f"#AntiGravity{c}"],
        [f"#{c}Innovation", f"#NextGen{c}", f"#Levitate{c}"],
        [f"#Discover{c}", f"#ZeroGravity{c}", f"#{c}Universe"],
        [f"#{c}Marketing", f"#Smart{c}Campaign", f"#Float{c}"]
    ]
    idx = sum(ord(char) for char in c) % len(tag_options)
    return tag_options[idx]


def extract_keywords_from_url(url):
    """Extract meaningful keywords from URL"""
    if not url:
        return []
    
    clean_url = re.sub(r'https?://(?:www\.)?', '', url.lower())
    words = re.findall(r'[a-z]{3,}', clean_url)
    
    ignore = {
        'com', 'org', 'net', 'www', 'http', 'https', 'html', 'php', 'watch', 'watchv',
        'utm', 'source', 'medium', 'campaign', 'link', 'ads', 'adlink', 'instagram',
        'youtube', 'facebook', 'tiktok', 'google', 'twitter', 'linkedin', 'pinterest'
    }
    filtered = [w for w in words if w not in ignore]
    
    seen = set()
    return [w for w in filtered if not (w in seen or seen.add(w))]


@ai_bp.route('/generate-caption', methods=['POST'])
@login_required
def generate_caption():
    """Generate marketing captions using AI"""
    ollama_service = get_ollama_service()
    
    data = request.get_json() or {}
    name = data.get('productName', '').strip()
    
    if not name:
        return jsonify({'message': 'productName required'}), 400
    
    # Try Ollama first
    prompt = (
        f"Generate 3 anti-gravity marketing slogans for the product: {name}. "
        f"Return a JSON object with a single key 'captions' containing a list of 3 strings. "
        f"Example: {{\"captions\": [\"Slogan 1\", \"Slogan 2\", \"Slogan 3\"]}}"
    )
    
    ollama_resp = ollama_service.generate_text(prompt, json_mode=True)
    if ollama_resp:
        cleaned_json = ollama_service.clean_json_response(ollama_resp)
        if cleaned_json and 'captions' in cleaned_json and isinstance(cleaned_json['captions'], list):
            caps = []
            for item in cleaned_json['captions']:
                if isinstance(item, dict):
                    val = (item.get('content') or item.get('value') or 
                           item.get('slogan') or item.get('text') or str(item))
                    caps.append(val)
                elif isinstance(item, str):
                    caps.append(item)
            if caps:
                return jsonify({
                    'captions': caps[:3],
                    'isMock': False,
                    'ai_source': 'Ollama'
                }), 200
    
    # OpenAI fallback
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if api_key and api_key != 'your_openai_api_key_here':
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': 'Generate 3 anti-gravity marketing slogans. Return JSON {captions:[...]}'},
                    {'role': 'user', 'content': f'Product: {name}'}
                ],
                response_format={'type': 'json_object'}
            )
            result = json.loads(resp.choices[0].message.content)
            return jsonify({
                'captions': result.get('captions', [])[:3],
                'isMock': False,
                'ai_source': 'OpenAI'
            }), 200
        except Exception:
            pass
    
    # Mock fallback
    return jsonify({
        'captions': mock_captions(name),
        'isMock': True
    }), 200


@ai_bp.route('/generate-hashtags', methods=['POST'])
@login_required
def generate_hashtags():
    """Generate hashtags using AI"""
    ollama_service = get_ollama_service()
    
    data = request.get_json() or {}
    kw = data.get('keyword', '').strip()
    
    if not kw:
        return jsonify({'message': 'keyword required'}), 400
    
    # Try Ollama first
    prompt = (
        f"Generate 3 trending social media hashtags for the keyword: {kw}. "
        f"Return a JSON object with a single key 'hashtags' containing a list of 3 strings (each starting with '#'). "
        f"Example: {{\"hashtags\": [\"#Tag1\", \"#Tag2\", \"#Tag3\"]}}"
    )
    
    ollama_resp = ollama_service.generate_text(prompt, json_mode=True)
    if ollama_resp:
        cleaned_json = ollama_service.clean_json_response(ollama_resp)
        if cleaned_json and 'hashtags' in cleaned_json and isinstance(cleaned_json['hashtags'], list):
            tags = []
            for item in cleaned_json['hashtags']:
                if isinstance(item, dict):
                    val = (item.get('tag') or item.get('name') or 
                           item.get('value') or item.get('text') or str(item))
                    tags.append(val)
                elif isinstance(item, str):
                    tags.append(item)
            cleaned_tags = [t if t.startswith('#') else f'#{t}' for t in tags]
            if cleaned_tags:
                return jsonify({
                    'hashtags': cleaned_tags[:3],
                    'isMock': False,
                    'ai_source': 'Ollama'
                }), 200
    
    # OpenAI fallback
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if api_key and api_key != 'your_openai_api_key_here':
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': 'Generate 3 trending hashtags. Return JSON {hashtags:[...]}'},
                    {'role': 'user', 'content': f'Keyword: {kw}'}
                ],
                response_format={'type': 'json_object'}
            )
            result = json.loads(resp.choices[0].message.content)
            return jsonify({
                'hashtags': result.get('hashtags', [])[:3],
                'isMock': False,
                'ai_source': 'OpenAI'
            }), 200
        except Exception:
            pass
    
    # Mock fallback
    return jsonify({
        'hashtags': mock_hashtags(kw),
        'isMock': True
    }), 200


@ai_bp.route('/analyze-link', methods=['POST'])
@login_required
def analyze_link():
    """Analyze ad link and generate campaign insights"""
    ollama_service = get_ollama_service()
    
    data = request.get_json() or {}
    ad_link = data.get('adLink', '').strip()
    
    if not ad_link:
        return jsonify({'message': 'adLink required'}), 400
    
    uid = session['user_id']
    
    # Generate defaults
    ctr = round(random.uniform(2.1, 7.8), 2)
    clicks = random.randint(800, 2500)
    convs = int(clicks * random.uniform(0.02, 0.07))
    spend = round(random.uniform(300, 950), 2)
    revenue = round(spend * random.uniform(1.8, 4.5), 2)
    eng = round(random.uniform(5.5, 18.2), 2)
    
    # Parse platform and keywords
    platform = 'Instagram' if 'instagram' in ad_link.lower() else (
        'YouTube' if 'youtube' in ad_link.lower() else 'Google Ads'
    )
    if 'facebook' in ad_link.lower():
        platform = 'Facebook'
    elif 'tiktok' in ad_link.lower():
        platform = 'TikTok'
    
    keywords = extract_keywords_from_url(ad_link)
    keywords_str = ", ".join(keywords) if keywords else "general marketing"
    
    # Default tags and verdict
    if keywords:
        hashtags = [f"#{k.capitalize()}" for k in keywords[:2]]
        hashtags.append(f"#{platform.replace(' ', '')}Campaign")
        product_title = " ".join([k.capitalize() for k in keywords])
        verdict = (
            f"Targeted {platform} campaign focusing on '{product_title}'. "
            f"Landing page optimized to convert search intent with relevant copy."
        )
    else:
        hashtags = mock_hashtags(platform)
        verdict = (
            f"High-velocity {platform} campaign detected. "
            f"Clean landing page layout and clear call to action."
        )
    
    ai_source = 'Mock'
    
    # Try Ollama
    prompt = (
        f"Analyze this marketing ad URL: '{ad_link}'.\n"
        f"Context keywords extracted from URL: {keywords_str}.\n"
        f"Identify the platform (Instagram, Google Ads, YouTube, TikTok, Facebook) and write a detailed marketing analysis verdict "
        f"about the target product/keywords ({keywords_str}) and campaign strategy (max 2 sentences).\n"
        f"Return a JSON object with the keys 'platform' (string), 'hashtags' (list of 3 strings), and 'verdict' (string). "
        f"Example: {{\"platform\": \"YouTube\", \"hashtags\": [\"#Review\", \"#Tech\", \"#Viral\"], "
        f"\"verdict\": \"YouTube campaign driving traffic for the target product using video engagement.\"}}"
    )
    
    ollama_resp = ollama_service.generate_text(prompt, json_mode=True)
    if ollama_resp:
        cleaned_json = ollama_service.clean_json_response(ollama_resp)
        if cleaned_json:
            if 'platform' in cleaned_json:
                platform = cleaned_json['platform']
            if 'hashtags' in cleaned_json and isinstance(cleaned_json['hashtags'], list):
                tags = []
                for item in cleaned_json['hashtags']:
                    if isinstance(item, dict):
                        val = (item.get('tag') or item.get('name') or 
                               item.get('value') or item.get('text') or str(item))
                        tags.append(val)
                    elif isinstance(item, str):
                        tags.append(item)
                hashtags = [t if t.startswith('#') else f'#{t}' for t in tags]
            if 'verdict' in cleaned_json:
                verdict = cleaned_json['verdict']
            ai_source = 'Ollama'
    
    insights = {
        'predicted_ctr': f'{ctr}%',
        'estimated_engagement': f'{eng}%',
        'hashtags': hashtags[:3],
        'verdict': verdict,
        'ai_source': ai_source
    }
    
    log = CampaignLog(
        user_id=uid,
        ad_link=ad_link,
        analysis_result=json.dumps(insights)
    )
    db.session.add(log)
    
    match = re.search(r'https?://(?:www\.)?([^/.]+)', ad_link)
    cname = f"Audit: {match.group(1).capitalize()}" if match else f"{platform} Ad Audit"
    
    camp = Campaign(
        user_id=uid,
        name=cname,
        platform=platform[:50],
        clicks=clicks,
        conversions=convs,
        spend=spend,
        revenue=revenue,
        date=datetime.date.today()
    )
    db.session.add(camp)
    db.session.commit()
    
    return jsonify({
        'log': log.to_dict(),
        'campaign': camp.to_dict()
    }), 201


@ai_bp.route('/campaign-logs')
@login_required
def campaign_logs():
    """Get user campaign logs"""
    logs = CampaignLog.query.filter_by(
        user_id=session['user_id']
    ).order_by(CampaignLog.timestamp.desc()).all()
    
    return jsonify([l.to_dict() for l in logs]), 200


@ai_bp.route('/ai-chat', methods=['POST'])
@login_required
def ai_chat():
    """AI chat endpoint with context-aware responses"""
    ollama_service = get_ollama_service()
    
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'message': 'message required'}), 400
    
    uid = session['user_id']
    user = User.query.get(uid)
    campaigns = Campaign.query.filter_by(user_id=uid).all()
    logs = CampaignLog.query.filter_by(user_id=uid).all()
    
    # Add user message to history
    ollama_service.add_to_history(uid, "user", message)
    
    # Check if query is about campaigns/database
    query_lower = message.lower()
    campaign_keywords = {
        "campaign", "my ad", "performance", "roi", "clicks", "conversion", "spend",
        "revenue", "metrics", "history", "log", "analytics", "stats", "telemetry",
        "audit", "scraped", "database", "record"
    }
    campaign_names = [c.name.lower() for c in campaigns]
    has_campaign_name_match = any(name in query_lower for name in campaign_names)
    is_asking_about_db = any(kw in query_lower for kw in campaign_keywords) or has_campaign_name_match
    
    # Build context if needed
    context_parts = []
    if is_asking_about_db:
        if user:
            context_parts.append(
                f"User Profile: Name: {user.name}, Email: {user.email}, "
                f"Role: {user.role}, Tagline: {user.tagline or 'N/A'}"
            )
        
        if campaigns:
            context_parts.append("Active Campaigns:")
            for c in campaigns:
                roi = ((c.revenue - c.spend) / c.spend * 100) if c.spend > 0 else 0
                context_parts.append(
                    f"- Campaign Name: '{c.name}' on Platform: {c.platform} | "
                    f"Clicks: {c.clicks}, Conversions: {c.conversions}, "
                    f"Spend: ${c.spend:.2f}, Revenue: ${c.revenue:.2f}, ROI: {roi:.1f}%"
                )
        
        if logs:
            context_parts.append("Recent URL Audit Logs:")
            for l in logs:
                try:
                    insights = json.loads(l.analysis_result)
                except:
                    insights = {}
                verdict = insights.get('verdict', 'N/A')
                context_parts.append(f"- Audited adLink: '{l.ad_link}' | Verdict: {verdict}")
    
    context_str = "\n".join(context_parts) if context_parts else ""
    
    # Build system message
    if context_str:
        system_content = (
            f"You are an expert AI marketing assistant with comprehensive knowledge in digital marketing, advertising, and campaign optimization.\n\n"
            f"USER DATABASE CONTEXT:\n"
            f"=========================================\n"
            f"{context_str}\n"
            f"=========================================\n\n"
            f"RESPONSE GUIDELINES:\n"
            f"1. Provide COMPREHENSIVE and DETAILED answers (minimum 4-6 paragraphs for general queries)\n"
            f"2. Structure your response with clear sections and formatting:\n"
            f"   - Use **bold** for important terms, headers, and key points\n"
            f"   - Use bullet points (•) for lists and features\n"
            f"   - Use numbered lists (1., 2., 3.) for steps or sequences\n"
            f"   - Add line breaks between sections for better readability\n"
            f"3. When answering queries about products, services, businesses, or locations:\n"
            f"   - Provide specific, actionable information\n"
            f"   - Include relevant details like contact info, addresses, hours if applicable to the topic\n"
            f"   - Organize information in clearly labeled sections\n"
            f"   - Use emojis strategically (📍 locations, 📞 contact, ⏰ hours, 🌐 websites, 📊 stats)\n"
            f"4. Reference the user's campaign data and metrics when relevant\n"
            f"5. Provide actionable insights, specific recommendations, and detailed explanations\n"
            f"6. If you don't have specific factual information, provide comprehensive general guidance and best practices\n\n"
            f"Answer the user's query with rich detail and structure:"
        )
    else:
        system_content = (
            f"You are an expert AI marketing assistant with comprehensive knowledge across all aspects of digital marketing.\n\n"
            f"RESPONSE GUIDELINES:\n"
            f"1. Provide COMPREHENSIVE and DETAILED answers (minimum 4-6 paragraphs)\n"
            f"2. Structure responses clearly:\n"
            f"   - Use **bold** for important terms and section headers\n"
            f"   - Use bullet points (•) for lists\n"
            f"   - Use numbered lists for steps/sequences\n"
            f"   - Add line breaks between sections\n"
            f"3. When asked about specific topics (products, companies, marketing strategies):\n"
            f"   - Provide in-depth explanations\n"
            f"   - Include multiple aspects and perspectives\n"
            f"   - Give practical, actionable advice\n"
            f"   - Use examples where helpful\n"
            f"4. Format responses for easy reading with clear visual structure\n"
            f"5. Use emojis strategically for visual markers\n\n"
            f"User Query: {message}\n\n"
            f"Provide a comprehensive, well-structured response:"
        )
    
    messages_payload = [{"role": "system", "content": system_content}]
    messages_payload.extend(ollama_service.get_chat_history(uid))
    
    # Try Ollama chat
    ollama_resp = ollama_service.chat(messages_payload)
    if ollama_resp:
        response_text = ollama_resp.strip()
        ollama_service.add_to_history(uid, "assistant", response_text)
        return jsonify({
            'response': response_text,
            'isMock': False,
            'ai_source': 'Ollama'
        }), 200
    
    # OpenAI fallback
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if api_key and api_key != 'your_openai_api_key_here':
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=messages_payload
            )
            response_text = resp.choices[0].message.content.strip()
            ollama_service.add_to_history(uid, "assistant", response_text)
            return jsonify({
                'response': response_text,
                'isMock': False,
                'ai_source': 'OpenAI'
            }), 200
        except Exception:
            pass
    
    # Mock fallback
    if is_asking_about_db and campaigns:
        c = campaigns[-1]
        roi = ((c.revenue - c.spend) / c.spend * 100) if c.spend > 0 else 0
        response_text = (
            f"Based on your database record, your campaign '{c.name}' on {c.platform} "
            f"is currently running with {c.clicks} clicks, {c.conversions} conversions, "
            f"and a spend of ${c.spend:.2f}. The ROI is currently {roi:.1f}%."
        )
        ollama_service.add_to_history(uid, "assistant", response_text)
        return jsonify({
            'response': response_text,
            'isMock': True,
            'ai_source': 'Mock'
        }), 200
    
    mock_responses = [
        "To optimize your marketing strategy, consider conducting A/B testing on your headlines and targeting high-intent long-tail keywords.",
        "A great Instagram strategy involves engaging visuals, storytelling in captions, and 3-5 hyper-relevant hashtags to build organic reach.",
        "To boost conversion rates, simplify your landing page checkout funnel, add clear trust badges, and present a compelling call-to-action.",
        f"Focusing on the customer's primary pain point in your copy is usually the fastest way to drive engagement for your brand."
    ]
    idx = sum(ord(c) for c in message) % len(mock_responses)
    response_text = mock_responses[idx]
    ollama_service.add_to_history(uid, "assistant", response_text)
    
    return jsonify({
        'response': response_text,
        'isMock': True
    }), 200


@ai_bp.route('/ai-chat/clear', methods=['POST'])
@login_required
def ai_chat_clear():
    """Clear chat history"""
    ollama_service = get_ollama_service()
    
    uid = session['user_id']
    ollama_service.clear_history(uid)
    
    return jsonify({'message': 'Chat history cleared successfully'}), 200
