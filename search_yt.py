from googleapiclient.discovery import build
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

API_KEY = "APIKEY_HERE"
VIDEO_ID = "Goy1SeSQyuo"
OUTPUT_DIR = Path("data/input")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

youtube = build("youtube", "v3", developerKey=API_KEY)

comments = []

request = youtube.commentThreads().list(
    part="snippet,replies",
    videoId=VIDEO_ID,
    maxResults=100,
    order="relevance",
    textFormat="plainText"
)

response = request.execute()

for item in response.get("items", []):
    comment = item["snippet"]["topLevelComment"]["snippet"]
    comments.append({
        "comment_id": item["id"],
        "author": comment.get("authorDisplayName"),
        "text": comment.get("textDisplay"),
        "like_count": comment.get("likeCount"),
        "published_at": comment.get("publishedAt"),
        "total_reply_count": item["snippet"].get("totalReplyCount", 0),
        "is_reply": False
    })
    if "replies" in item:
        for reply in item["replies"]["comments"]:
            reply_snippet = reply["snippet"]
            comments.append({
                "comment_id": reply["id"],
                "author": reply_snippet.get("authorDisplayName"),
                "text": reply_snippet.get("textDisplay"),
                "like_count": reply_snippet.get("likeCount"),
                "published_at": reply_snippet.get("publishedAt"),
                "total_reply_count": 0,
                "is_reply": True
            })

now_str = datetime.now().strftime("%Y%m%d%H%M%S")
json_path = OUTPUT_DIR / f"yt_comments_{now_str}.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(comments, f, ensure_ascii=False, indent=2)

df = pd.DataFrame(comments)
csv_path = OUTPUT_DIR / f"yt_comments_{now_str}.csv"
df.to_csv(csv_path, index=False, encoding="utf-8")
