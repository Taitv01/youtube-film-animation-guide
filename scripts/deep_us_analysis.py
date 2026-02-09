import requests
import json
import sys
from collections import Counter
from datetime import datetime

# Force UTF-8 encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "AIzaSyAWephvX37EU4Jk2C1_UH9NXQuNIWaanpU"
BASE_URL = "https://www.googleapis.com/youtube/v3"

CATEGORY_MAP = {
    '1': 'Film & Animation',
    '2': 'Autos & Vehicles',
    '10': 'Music',
    '15': 'Pets & Animals',
    '17': 'Sports',
    '19': 'Travel & Events',
    '20': 'Gaming',
    '22': 'People & Blogs',
    '23': 'Comedy',
    '24': 'Entertainment',
    '25': 'News & Politics',
    '26': 'Howto & Style',
    '27': 'Education',
    '28': 'Science & Technology',
    '29': 'Nonprofits & Activism',
}

def get_trending_by_category(category_id, region_code="US", max_results=25):
    """Fetch trending videos for a specific category"""
    url = f"{BASE_URL}/videos"
    params = {
        'part': 'snippet,statistics,contentDetails',
        'chart': 'mostPopular',
        'regionCode': region_code,
        'videoCategoryId': category_id,
        'maxResults': max_results,
        'key': API_KEY
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    return response.json().get('items', [])

def get_channel_info(channel_id):
    """Get channel subscriber count"""
    url = f"{BASE_URL}/channels"
    params = {
        'part': 'statistics',
        'id': channel_id,
        'key': API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    items = response.json().get('items', [])
    if items:
        return items[0]['statistics']
    return None

def format_number(num_str):
    """Format large numbers for readability"""
    try:
        num = int(num_str)
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        return str(num)
    except:
        return num_str

def analyze_category_deep(category_id, category_name):
    """Deep analysis of a specific category"""
    print(f"\n{'='*60}")
    print(f"📊 DEEP ANALYSIS: {category_name.upper()}")
    print(f"{'='*60}")
    
    videos = get_trending_by_category(category_id)
    if not videos:
        print("No videos found for this category.")
        return None
    
    all_tags = []
    all_titles = []
    channel_sizes = []
    view_counts = []
    like_ratios = []
    
    print(f"\n🔥 Top {len(videos)} Trending Videos:\n")
    
    for i, video in enumerate(videos[:10], 1):
        snippet = video['snippet']
        stats = video['statistics']
        
        title = snippet['title']
        channel = snippet['channelTitle']
        channel_id = snippet['channelId']
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        tags = snippet.get('tags', [])
        
        view_counts.append(views)
        all_tags.extend(tags)
        all_titles.append(title.lower())
        
        if views > 0 and likes > 0:
            like_ratio = (likes / views) * 100
            like_ratios.append(like_ratio)
        
        # Get channel size
        ch_stats = get_channel_info(channel_id)
        if ch_stats:
            subs = int(ch_stats.get('subscriberCount', 0))
            channel_sizes.append(subs)
            subs_str = format_number(str(subs))
        else:
            subs_str = "N/A"
        
        print(f"{i}. {title[:60]}...")
        print(f"   📺 {channel} ({subs_str} subs)")
        print(f"   👁 {format_number(str(views))} views | 👍 {format_number(str(likes))} likes | 💬 {format_number(str(comments))} comments")
        print()
    
    # Analysis Summary
    print(f"\n{'─'*60}")
    print("📈 INSIGHTS & METRICS")
    print(f"{'─'*60}")
    
    if view_counts:
        avg_views = sum(view_counts) / len(view_counts)
        print(f"• Average Views: {format_number(str(int(avg_views)))}")
    
    if like_ratios:
        avg_like_ratio = sum(like_ratios) / len(like_ratios)
        print(f"• Average Like Ratio: {avg_like_ratio:.2f}%")
    
    if channel_sizes:
        small_channels = len([s for s in channel_sizes if s < 100_000])
        medium_channels = len([s for s in channel_sizes if 100_000 <= s < 1_000_000])
        large_channels = len([s for s in channel_sizes if s >= 1_000_000])
        print(f"• Channel Size Distribution:")
        print(f"  - Small (<100K subs): {small_channels}")
        print(f"  - Medium (100K-1M subs): {medium_channels}")
        print(f"  - Large (>1M subs): {large_channels}")
    
    # Tag Analysis
    print(f"\n{'─'*60}")
    print("🏷️ TOP TRENDING TAGS")
    print(f"{'─'*60}")
    tag_counts = Counter([t.lower() for t in all_tags])
    for tag, count in tag_counts.most_common(15):
        print(f"  • {tag}: {count}")
    
    # Title Word Analysis
    print(f"\n{'─'*60}")
    print("📝 COMMON TITLE KEYWORDS")
    print(f"{'─'*60}")
    title_words = []
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'it', 'this', 'that', '|', '-', '–', '—'}
    for title in all_titles:
        words = title.replace('|', ' ').replace('-', ' ').split()
        title_words.extend([w for w in words if len(w) > 2 and w not in stop_words])
    
    word_counts = Counter(title_words)
    for word, count in word_counts.most_common(15):
        if count > 1:
            print(f"  • {word}: {count}")
    
    return {
        'category': category_name,
        'avg_views': avg_views if view_counts else 0,
        'top_tags': tag_counts.most_common(10),
        'small_channel_opportunity': small_channels if channel_sizes else 0
    }

def main():
    print("="*60)
    print("🇺🇸 YOUTUBE US MARKET - DEEP NICHE ANALYSIS")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    # Categories to analyze deeply
    categories_to_analyze = [
        ('20', 'Gaming'),
        ('24', 'Entertainment'),
        ('28', 'Science & Technology'),
        ('26', 'Howto & Style'),
        ('27', 'Education'),
        ('1', 'Film & Animation'),
    ]
    
    results = []
    for cat_id, cat_name in categories_to_analyze:
        result = analyze_category_deep(cat_id, cat_name)
        if result:
            results.append(result)
    
    # Final Summary
    print("\n" + "="*60)
    print("🎯 FINAL RECOMMENDATIONS")
    print("="*60)
    
    print("\n📌 BEST NICHES FOR NEW CREATORS (based on small channel presence):")
    sorted_results = sorted(results, key=lambda x: x['small_channel_opportunity'], reverse=True)
    for r in sorted_results[:3]:
        print(f"  • {r['category']}: {r['small_channel_opportunity']} small channels in trending")
    
    print("\n📌 HIGHEST VIEW POTENTIAL:")
    sorted_by_views = sorted(results, key=lambda x: x['avg_views'], reverse=True)
    for r in sorted_by_views[:3]:
        print(f"  • {r['category']}: {format_number(str(int(r['avg_views'])))} avg views")

if __name__ == "__main__":
    main()
