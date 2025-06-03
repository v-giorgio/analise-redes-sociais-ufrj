import requests
import pandas as pd
import json
from pathlib import Path
from config import YOUTUBE_API_KEY

input_videos = Path("data/input/top_trans_videos.csv")
output_dir = Path("data/input/yt_comments")
output_dir.mkdir(parents=True, exist_ok=True)

videos_df = pd.read_csv(input_videos)

API_KEY = YOUTUBE_API_KEY
COMMENTS_PER_VIDEO = 500
COMMENTS_PER_PAGE = 100

def fetch_comments(video_id):
    comments = []
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet,replies",
        "videoId": video_id,
        "maxResults": COMMENTS_PER_PAGE,
        "textFormat": "plainText",
        "key": API_KEY
    }

    total_fetched = 0
    next_page_token = None

    while total_fetched < COMMENTS_PER_VIDEO:
        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Erro ao buscar comentários do vídeo {video_id}: {response.text}")
            break

        data = response.json()
        for item in data.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "video_id": video_id,
                "comment_id": item["id"],
                "author": top.get("authorDisplayName"),
                "text": top.get("textDisplay"),
                "like_count": top.get("likeCount"),
                "published_at": top.get("publishedAt"),
                "is_reply": False,
                "total_reply_count": item["snippet"].get("totalReplyCount", 0),
                "reply_to": None
            })

            replies = item.get("replies", {}).get("comments", [])
            for reply in replies:
                rep = reply["snippet"]
                comments.append({
                    "video_id": video_id,
                    "comment_id": reply["id"],
                    "author": rep.get("authorDisplayName"),
                    "text": rep.get("textDisplay"),
                    "like_count": rep.get("likeCount"),
                    "published_at": rep.get("publishedAt"),
                    "is_reply": True,
                    "total_reply_count": 0,
                    "reply_to": item["id"]
                })

        total_fetched += len(data.get("items", []))
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return comments

for _, row in videos_df.iterrows():
    video_id = row["video_id"]
    print(f"Buscando comentários para vídeo {video_id}...")
    comments = fetch_comments(video_id)

    if not comments:
        print(f"Nenhum comentário encontrado para vídeo {video_id}")
        continue

    df = pd.DataFrame(comments)
    
    csv_path = output_dir / f"yt_comments_{video_id}.csv"
    json_path = output_dir / f"yt_comments_{video_id}.json"

    df.to_csv(csv_path, index=False, encoding="utf-8")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

    print(f"Salvo: {csv_path} e {json_path}")
