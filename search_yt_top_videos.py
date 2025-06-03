import requests
import pandas as pd
import json
from pathlib import Path
from config import YOUTUBE_API_KEY

output_dir = Path("data/input")
output_dir.mkdir(parents=True, exist_ok=True)

search_url = "https://www.googleapis.com/youtube/v3/search"
search_params = {
    "part": "snippet",
    "q": "trans",
    "type": "video",
    "maxResults": 50,
    "key": YOUTUBE_API_KEY
}

search_response = requests.get(search_url, params=search_params)
search_data = search_response.json()

video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]

details_url = "https://www.googleapis.com/youtube/v3/videos"
details_params = {
    "part": "snippet,statistics",
    "id": ",".join(video_ids),
    "key": YOUTUBE_API_KEY
}

details_response = requests.get(details_url, params=details_params)
videos = details_response.json().get("items", [])

processed_videos = []
for video in videos:
    snippet = video["snippet"]
    stats = video.get("statistics", {})
    processed_videos.append({
        "video_id": video["id"],
        "title": snippet["title"],
        "channel": snippet["channelTitle"],
        "published_at": snippet["publishedAt"],
        "view_count": int(stats.get("viewCount", 0)),
        "like_count": int(stats.get("likeCount", 0)) if "likeCount" in stats else None,
        "comment_count": int(stats.get("commentCount", 0)) if "commentCount" in stats else None,
        "description": snippet.get("description", "")
    })

top_videos = sorted(processed_videos, key=lambda x: x["view_count"], reverse=True)[:10]

df = pd.DataFrame(top_videos)
csv_path = output_dir / "top_trans_videos.csv"
json_path = output_dir / "top_trans_videos.json"
df.to_csv(csv_path, index=False)
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(top_videos, f, ensure_ascii=False, indent=2)

print(f"Salvo: {csv_path}")
