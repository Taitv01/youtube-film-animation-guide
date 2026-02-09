import requests
import json
import sys
from collections import Counter

# Force UTF-8 encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "AIzaSyAWephvX37EU4Jk2C1_UH9NXQuNIWaanpU"
BASE_URL = "https://www.googleapis.com/youtube/v3"

# Category ID map for readable output
CATEGORY_MAP = {
    '1': 'Film & Animation',
    '2': 'Autos & Vehicles',
    '10': 'Music',
    '15': 'Pets & Animals',
    '17': 'Sports',
    '18': 'Short Movies',
    '19': 'Travel & Events',
    '20': 'Gaming',
    '21': 'Videoblogging',
    '22': 'People & Blogs',
    '23': 'Comedy',
    '24': 'Entertainment',
    '25': 'News & Politics',
    '26': 'Howto & Style',
    '27': 'Education',
    '28': 'Science & Technology',
    '29': 'Nonprofits & Activism',
    '30': 'Movies',
    '31': 'Anime/Animation',
    '32': 'Action/Adventure',
    '33': 'Classics',
    '34': 'Comedy',
    '35': 'Documentary',
    '36': 'Drama',
    '37': 'Family',
    '38': 'Foreign',
    '39': 'Horror',
    '40': 'Sci-Fi/Fantasy',
    '41': 'Thriller',
    '42': 'Shorts',
    '43': 'Shows',
    '44': 'Trailers'
}

def get_trending_videos(region_code="VN", max_results=50):
    url = f"{BASE_URL}/videos"
    params = {
        'part': 'snippet,statistics',
        'chart': 'mostPopular',
        'regionCode': region_code,
        'maxResults': max_results,
        'key': API_KEY
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []
    
    return response.json().get('items', [])

def analyze_videos(videos):
    categories = []
    tags = []
    
    print(f"Analyzing {len(videos)} trending videos...\n")
    
    for video in videos:
        snippet = video['snippet']
        stats = video['statistics']
        
        title = snippet['title']
        channel = snippet['channelTitle']
        views = stats.get('viewCount', 'N/A')
        cat_id = snippet.get('categoryId')
        video_tags = snippet.get('tags', [])
        
        cat_name = CATEGORY_MAP.get(cat_id, f"ID {cat_id}")
        categories.append(cat_name)
        tags.extend(video_tags)
        
        # print(f"- [{cat_name}] {title} ({channel}) - {views} views")

    print("\n--- Top Categories ---")
    cat_counts = Counter(categories)
    for cat, count in cat_counts.most_common():
        print(f"{cat}: {count}")

    print("\n--- Common Tags ---")
    tag_counts = Counter([t.lower() for t in tags])
    for tag, count in tag_counts.most_common(20):
        print(f"{tag}: {count}")

if __name__ == "__main__":
    print("Fetching Trending Data for Vietnam (VN)...")
    vn_videos = get_trending_videos("VN")
    analyze_videos(vn_videos)

    print("\n" + "="*50 + "\n")

    print("Fetching Trending Data for Global/US (US)...")
    us_videos = get_trending_videos("US")
    analyze_videos(us_videos)
