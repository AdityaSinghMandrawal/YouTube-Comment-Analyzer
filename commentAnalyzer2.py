import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from googleapiclient.discovery import build
from collections import Counter
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime

# Your YouTube API key
DEVELOPER_KEY = "AIzaSyC8cgT4pOnPv0pb9z0EC7DfCS_qwQGd0Kg"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# ID of the video you want to analyze
videoID = "0PW3aBqjCgQ"

# Initialize YouTube API client
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

def get_comments(videoID):
    """Fetches comments from a given YouTube video."""
    comments = []
    try:
        # Request comments
        response = youtube.commentThreads().list(
            part="snippet", videoId=videoID, textFormat="plainText", maxResults=100
        ).execute()

        while response:
            # Extract comment text
            for item in response["items"]:
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment)
            
            # Check for more comments (pagination)
            if 'nextPageToken' in response:
                response = youtube.commentThreads().list(
                    part="snippet", videoId=videoID, textFormat="plainText", maxResults=100,
                    pageToken=response['nextPageToken']
                ).execute()
            else:
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    
    return comments

def get_video_details(videoID):
    """Fetches the title and publish date of a YouTube video."""
    try:
        response = youtube.videos().list(part="snippet", id=videoID).execute()
        video_details = response['items'][0]['snippet']
        title = video_details['title']
        published_at = video_details['publishedAt']
        published_date = datetime.strptime(published_at,
                                           '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
        return title, published_date
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def read_stopwords(file_path):
    """Reads stopwords from a file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

# Paths to stopwords files
hinglish_stopwords_file = 'stop_hinglish.txt'
hindi_stopwords_file = 'hindiStopWords.txt'

# Load stopwords
hinglish_stopwords = read_stopwords(hinglish_stopwords_file)
hindi_stopwords = read_stopwords(hindi_stopwords_file)
english_stopwords = set(stopwords.words('english'))

# Combine all stopwords
all_stopwords = english_stopwords.union(hinglish_stopwords).union(hindi_stopwords)

# Fetch comments and video details
video_comments = get_comments(videoID)
video_title, video_date = get_video_details(videoID)

if isinstance(video_comments, list):
    print(f"Fetched {len(video_comments)} comments from video ID: {videoID}")

    # Process comments
    all_comments = ' '.join(video_comments)
    words = nltk.word_tokenize(all_comments.lower())
    words = [word for word in words if word.isalpha() and word not in all_stopwords]
    word_freq = Counter(words)
    most_common_words = word_freq.most_common(20)

    def create_window():
        """Creates a GUI window to display the most common words."""
        window = tk.Tk()
        window.title("Most Common Words")
        window.geometry("800x600")

        frame = ttk.Frame(window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text=f"Video Title: {video_title}",
                  font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(frame, text=f"Published Date: {video_date}",
                  font=("Helvetica", 12)).grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Label(frame, text=f"Fetched Comments: {len(video_comments)}",
                  font=("Helvetica", 12)).grid(row=2, column=0, columnspan=2, pady=5)

        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=22,
                                              font=("Helvetica", 12))
        text_area.grid(row=3, column=0, columnspan=2, pady=10)
        text_area.insert(tk.END, "Top 20 Most Common Words:\n\n")
        
        for i, (word, freq) in enumerate(most_common_words, start=1):
            text_area.insert(tk.END, f"{i}.\t{word}\t:\t{freq}\n")

        text_area.configure(state='disabled')
        window.mainloop()

    if most_common_words:
        create_window()
    else:
        print("No comments or valid words found.")

else:
    print("Failed to fetch comments.")
