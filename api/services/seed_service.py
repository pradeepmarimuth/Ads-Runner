"""
Database seeding service
Handles initial data population
"""
import datetime
from database.models import db, User, Campaign, Post, Message, Connection


def seed_campaigns(uid):
    """Seed sample campaigns for a user"""
    samples = [
        Campaign(
            user_id=uid,
            name='Levitation Boots Launch',
            platform='Instagram',
            clicks=1250,
            conversions=85,
            spend=750,
            revenue=4250,
            date=datetime.date(2026, 6, 10)
        ),
        Campaign(
            user_id=uid,
            name='Zero-G Board Display',
            platform='Google Ads',
            clicks=3100,
            conversions=210,
            spend=2150,
            revenue=10500,
            date=datetime.date(2026, 6, 15)
        ),
        Campaign(
            user_id=uid,
            name='Hover Scooter Vlog',
            platform='YouTube',
            clicks=4500,
            conversions=180,
            spend=3000,
            revenue=15000,
            date=datetime.date(2026, 6, 20)
        ),
        Campaign(
            user_id=uid,
            name='Anti-Grav Cushion Promos',
            platform='Instagram',
            clicks=1900,
            conversions=140,
            spend=1100,
            revenue=7000,
            date=datetime.date(2026, 6, 25)
        ),
        Campaign(
            user_id=uid,
            name='Hoverboard Search Leads',
            platform='Google Ads',
            clicks=2800,
            conversions=190,
            spend=1800,
            revenue=9500,
            date=datetime.date(2026, 7, 1)
        ),
        Campaign(
            user_id=uid,
            name='Space Boots Assembly',
            platform='YouTube',
            clicks=5200,
            conversions=230,
            spend=3500,
            revenue=19500,
            date=datetime.date(2026, 7, 3)
        ),
    ]
    db.session.bulk_save_objects(samples)
    db.session.commit()


def seed_system():
    """Seed the system with default accounts and data"""
    if User.query.count() > 0:
        return
    
    print("Seeding system with default accounts...")
    
    accounts = [
        ('Commander Admin', 'admin@antigravity.io', 'adminpassword', 'Admin', 'System Administrator'),
        ('Alex Drift', 'influencer@antigravity.io', 'pass123', 'Influencer', 'Anti-Gravity Content Creator & Hover Tech Reviewer'),
        ('Nova Ads Corp', 'adpub@antigravity.io', 'pass123', 'AdPublisher', 'Premium Ad Slots for Hover & Zero-G Products'),
        ('Jordan Customer', 'customer@antigravity.io', 'pass123', 'Customer', 'Zero-G Enthusiast & Early Adopter'),
    ]
    
    avatars = [
        'https://i.pravatar.cc/150?img=5',
        'https://i.pravatar.cc/150?img=12',
        'https://i.pravatar.cc/150?img=25',
        'https://i.pravatar.cc/150?img=47',
    ]
    
    bios = [
        'Overseeing all marketing operations in the Anti-Gravity universe.',
        'Creating viral content for hover shoes, levitation boards, and zero-g experiences. DMs open for brand collabs!',
        'We help brands reach the anti-gravity audience. Competitive rates, premium slots across Instagram, Google & YouTube.',
        'Early adopter of all things anti-gravity. Always looking for the next big launch to invest in.',
    ]
    
    created = []
    for (name, email, pwd, role, tagline), avatar, bio in zip(accounts, avatars, bios):
        u = User(
            name=name,
            email=email,
            role=role,
            tagline=tagline,
            avatar_url=avatar,
            bio=bio,
            location='New Orbit City'
        )
        u.set_password(pwd)
        db.session.add(u)
        db.session.flush()
        created.append(u)
    
    db.session.commit()
    
    # Seed campaigns for Customer
    customer = next(u for u in created if u.role == 'Customer')
    seed_campaigns(customer.id)
    
    # Seed some posts
    influencer = next(u for u in created if u.role == 'Influencer')
    adpub = next(u for u in created if u.role == 'AdPublisher')
    
    post_data = [
        (influencer.id, "🚀 Just tested the new Hover Boots X9 — absolutely mind-blowing! Zero-G activation in 3 seconds flat. #HoverTech #AntiGravity"),
        (influencer.id, "✨ My latest Zero-G Board review is live! Reach out if your brand wants a feature. DMs open for brand partnerships!"),
        (adpub.id, "📢 New ad slots available for Q3 2026! Premium placements on Instagram Reels and YouTube Shorts for hover-tech brands. Inquire now."),
        (adpub.id, "💡 Did you know? Anti-Gravity product ads get 3.2× higher CTR than traditional gadget ads. Get featured in our network!"),
        (customer.id, "🛒 Just placed an order for the Levitation Boots. Fingers crossed they ship before the weekend! #AntiGravity"),
    ]
    
    for uid, content in post_data:
        db.session.add(Post(user_id=uid, content=content))
    
    # Seed a sample message conversation
    db.session.add(Message(
        sender_id=customer.id,
        receiver_id=influencer.id,
        content="Hi Alex! Huge fan of your hover content. Would love to collab on a Zero-G Board review. Interested?"
    ))
    db.session.add(Message(
        sender_id=influencer.id,
        receiver_id=customer.id,
        content="Hey! Thanks so much 🙌 Absolutely open to it. Send me the product details and we can discuss rates!"
    ))
    
    # Seed a connection
    db.session.add(Connection(
        requester_id=customer.id,
        receiver_id=influencer.id,
        status='accepted'
    ))
    
    db.session.commit()
    print("Seeding complete.")
