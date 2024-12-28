import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

# Define headers for API authentication
HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}


def get_user_id(username):
    """Get user ID by username."""
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json()["data"]["id"]
    else:
        print(f"Error: {response.status_code}, {response.json()}")
        return None


def get_user_tweets(user_id, max_results=10, pagination_token=None):
    """Fetch tweets from a user's timeline."""
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    params = {
        "max_results": max_results,  # Up to 10 per request under free plan
        "tweet.fields": "public_metrics,created_at",
    }
    if pagination_token:
        params["pagination_token"] = pagination_token

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.json()}")
        return None


def fetch_top_tweets(username, top_n=5):
    """Fetch top N tweets sorted by likes."""
    user_id = get_user_id(username)
    if not user_id:
        return []

    tweets = []
    next_token = None

    while len(tweets) < top_n:
        data = get_user_tweets(user_id, max_results=10, pagination_token=next_token)
        if not data or "data" not in data:
            break

        tweets.extend(data["data"])
        next_token = data.get("meta", {}).get("next_token")
        if not next_token:  # No more pages
            break

    # Sort tweets by like count and return top N
    sorted_tweets = sorted(
        tweets,
        key=lambda x: x["public_metrics"]["like_count"],
        reverse=True
    )
    return sorted_tweets[:top_n]


def main():
    username = "stijnnoorman"
    top_tweets = fetch_top_tweets(username, top_n=5)

    print(f"Top {len(top_tweets)} Tweets for @{username}:")
    for idx, tweet in enumerate(top_tweets, start=1):
        metrics = tweet["public_metrics"]
        print(f"{idx}. {tweet['text']}")
        print(f"   Likes: {metrics['like_count']}, Retweets: {metrics['retweet_count']}, Replies: {metrics['reply_count']}")
        print(f"   Created at: {tweet['created_at']}\n")


if __name__ == "__main__":
    main()
