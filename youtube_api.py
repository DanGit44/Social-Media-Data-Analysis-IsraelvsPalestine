import pandas as pd
import csv
import time
from googleapiclient.discovery import   build
from datetime import date

API_KEY = ""
MAX_VIDEOS_PER_HASHTAG = 200
MAX_RESULTS = 1000  # Max comments per video
HASHTAGS = ["#israel", "#palestine", "#idf1", "#gaza"]


def search_videos_by_hashtag(hashtag, max_results):
    """Search for videos by hashtag/keyword and return a list of video IDs."""
    youtube = build("youtube", "v3", developerKey=API_KEY)
    video_ids = []
    next_page_token = None

    seen_df = pd.read_csv('seen_videos_ids.csv')
    seen_videos_ids = set(seen_df['video_id'].astype(str))

    while len(video_ids) < max_results:
        request = youtube.search().list(
            q=hashtag,
            part="id",
            type="video",
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response["items"]:
            if item["id"]["kind"] == "youtube#video" and item["id"]["videoId"] not in seen_videos_ids:
                video_ids.append(item["id"]["videoId"])
                if len(video_ids) >= max_results:
                    break

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    print(f"🔍 Found {len(video_ids)} videos for hashtag {hashtag}")
    return video_ids


def get_video_info(video_id):
    """Fetch video-level info: title, description, publish date, views, likes."""
    youtube = build("youtube", "v3", developerKey=API_KEY)
    response = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    ).execute()

    if not response.get("items"):
        return None

    item = response["items"][0]
    snippet = item["snippet"]
    stats = item.get("statistics", {})

    return {
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "video_publish_date": snippet.get("publishedAt", ""),
        "views": stats.get("viewCount", 0),
        "video_likes": stats.get("likeCount", 0)
    }


def get_all_comments(video_id, api_key, tag):
    """Fetch all comments for a video and combine with video info."""
    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    next_page_token = None

    # Fetch video info first
    video_info = get_video_info(video_id)
    if not video_info:
        print(f"⚠️ Could not get info for {video_id}")
        return comments

    while True:
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token,
                textFormat="plainText"
            )
            response = request.execute()
        except Exception as e:
            if "commentsDisabled" in str(e):
                print(f"🚫 Comments disabled on video {video_id}. Skipping.")
            else:
                print(f"⚠️ Error on video {video_id}: {e}")
            return []

        for item in response["items"]:
            c_snip = item["snippet"]["topLevelComment"]["snippet"]
            channel_id_snippet = c_snip["authorChannelId"]
            comment_text = c_snip.get("textDisplay", "")
            comment_likes = c_snip.get("likeCount", 0)
            comment_date = c_snip.get("publishedAt", "")
            author_name = c_snip.get("authorDisplayName", "")
            author_id = channel_id_snippet.get("value", "")

            comments.append({
                "video_id": video_id,
                "title": video_info["title"],
                "description": video_info["description"],
                "video_publish_date": video_info["video_publish_date"],
                "views": video_info["views"],
                "video_likes": video_info["video_likes"],
                "comment": comment_text,
                "comment_likes": comment_likes,
                "comment_date": comment_date,
                "author_name": author_name,
                "author_id": author_id,
                "tag": tag
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
        if len(comments) >= MAX_RESULTS:
            break

    print(f"✅ Collected {len(comments)} comments from video {video_id}")
    return comments


def save_to_csv(data, filename):
    """Save all comment+video data to CSV."""
    with open(filename, "w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "video_id", "title", "description", "video_publish_date",
            "views", "video_likes", "comment", "comment_likes",
            "comment_date", "author_name", "author_id", "tag"
        ])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"💾 Saved to {filename}")


def main():
    all_comments = []
    for tag in HASHTAGS:
        video_ids = search_videos_by_hashtag(tag, MAX_VIDEOS_PER_HASHTAG)

        #This if for adding the scanned videos into the file for not scanning again later
        seen_df = pd.read_csv('seen_videos_ids.csv')
        seen_videos_ids = set(seen_df['video_id'].astype(str))
        seen_videos_ids.update(video_ids)
        pd.DataFrame(list(seen_videos_ids), columns=['video_id']).to_csv('seen_videos_ids.csv', index=False)
        
        for vid in video_ids:
            comments = get_all_comments(vid, API_KEY, tag)
            all_comments.extend(comments)
            
    today = date.today()
    save_to_csv(all_comments, f"comments_youtube_{today}.csv")


if __name__ == "__main__":
    main()
