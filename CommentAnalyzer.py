import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from googleapiclient.discovery import build
from collections import Counter

# Download NLTK resources (if not already downloaded)
# nltk.download('punkt')
# nltk.download('stopwords')

# Replace with your actual API key
DEVELOPER_KEY = "Paste your api key"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Replace with the video ID you want to fetch comments from
videoID = "m-zbIfF-RYA"  # Example video ID

# Build the YouTube service
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

# Function to fetch comments
def get_comments(videoID):
    try:
        comments = []
        # Execute API request
        response = youtube.commentThreads().list(part="snippet", videoId=videoID, textFormat="plainText", maxResults=100).execute()
        # Extract comments text from API response
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]
            comment_text = comment["snippet"]["textDisplay"]
            comments.append(comment_text)
        
        # Get next page of comments if available
        try:
            nextToken = response["nextPageToken"]
        except KeyError:
            nextToken = None
        
        while nextToken is not None:
            response = youtube.commentThreads().list(part="snippet", videoId=videoID, textFormat="plainText", pageToken=nextToken, maxResults=100).execute()
            for item in response["items"]:
                comment = item["snippet"]["topLevelComment"]
                comment_text = comment["snippet"]["textDisplay"]
                comments.append(comment_text)
            
            try:
                nextToken = response["nextPageToken"]
            except KeyError:
                nextToken = None
        
        return comments
    
    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Function to read stopwords from file
def read_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        stopwords_list = [line.strip() for line in file]
    return stopwords_list

# Path to your Hinglish and Hindi stopwords files
hinglish_stopwords_file = 'stop_hinglish.txt'
hindi_stopwords_file = 'hindiStopWords.txt'

# Read Hinglish and Hindi stopwords from files
hinglish_stopwords = read_stopwords(hinglish_stopwords_file)
hindi_stopwords = read_stopwords(hindi_stopwords_file)

# English stopwords from NLTK
english_stopwords = set(stopwords.words('english'))

# Merge English, Hinglish, and Hindi stopwords
all_stopwords = english_stopwords.union(hinglish_stopwords).union(hindi_stopwords)

# Call the function to fetch comments
video_comments = get_comments(videoID)

# Display fetched comments
if isinstance(video_comments, list):
    print(f"Fetched {len(video_comments)} comments from video ID: {videoID}")

    # Combine all comments into a single string
    all_comments = ' '.join(video_comments)

    # Tokenize and process the comments
    words = nltk.word_tokenize(all_comments.lower())

    # Remove stopwords and non-alphabetic words
    words = [word for word in words if word.isalpha() and word not in all_stopwords]

    # Calculate word frequencies
    word_freq = Counter(words)

    # Get the top 20 most common words
    most_common_words = word_freq.most_common(20)

    # Print the top 20 most common words and their frequencies
    if most_common_words:
        print("Top 20 Most Common Words:")
        for word, freq in most_common_words:
            print(f"{word}: {freq}")
    else:
        print("No comments or valid words found.")

else:
    print("Failed to fetch comments.")
