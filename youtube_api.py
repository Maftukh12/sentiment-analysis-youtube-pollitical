"""
YouTube API Integration Module
Handles video search and comment collection from YouTube Data API v3
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv

load_dotenv()

class YouTubeAPI:
    def __init__(self):
        """Initialize YouTube API client"""
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key not found in environment variables")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.quota_used = 0
    
    def search_videos(self, query, max_results=10):
        """
        Search for videos based on keyword
        
        Args:
            query (str): Search keyword
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of video dictionaries with id, title, description, channel
        """
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=max_results,
                relevanceLanguage='id',  # Prioritize Indonesian content
                order='relevance'
            )
            response = request.execute()
            self.quota_used += 100  # Search costs 100 units
            
            videos = []
            for item in response.get('items', []):
                video = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt']
                }
                videos.append(video)
            
            return videos
        
        except HttpError as e:
            if e.resp.status == 403:
                return {'error': 'API quota exceeded or invalid API key'}
            else:
                return {'error': f'HTTP error occurred: {e}'}
        except Exception as e:
            return {'error': f'An error occurred: {str(e)}'}
    
    def get_video_comments(self, video_id, max_results=100):
        """
        Fetch comments from a specific video
        
        Args:
            video_id (str): YouTube video ID
            max_results (int): Maximum number of comments to fetch
            
        Returns:
            list: List of comment dictionaries with text, author, likes, published_at
        """
        try:
            comments = []
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(max_results, 100),  # API max is 100 per request
                order='relevance',
                textFormat='plainText'
            )
            
            while request and len(comments) < max_results:
                response = request.execute()
                self.quota_used += 1  # Each request costs 1 unit
                
                for item in response.get('items', []):
                    comment_data = item['snippet']['topLevelComment']['snippet']
                    comment = {
                        'text': comment_data['textDisplay'],
                        'author': comment_data['authorDisplayName'],
                        'likes': comment_data['likeCount'],
                        'published_at': comment_data['publishedAt'],
                        'video_id': video_id
                    }
                    comments.append(comment)
                
                # Check if there are more comments
                if 'nextPageToken' in response and len(comments) < max_results:
                    request = self.youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        maxResults=min(max_results - len(comments), 100),
                        pageToken=response['nextPageToken'],
                        order='relevance',
                        textFormat='plainText'
                    )
                else:
                    break
            
            return comments
        
        except HttpError as e:
            if e.resp.status == 403:
                # Comments might be disabled or quota exceeded
                return {'error': 'Comments disabled or API quota exceeded'}
            else:
                return {'error': f'HTTP error occurred: {e}'}
        except Exception as e:
            return {'error': f'An error occurred: {str(e)}'}
    
    def get_quota_usage(self):
        """Return estimated quota usage"""
        return {
            'quota_used': self.quota_used,
            'daily_limit': 10000,
            'remaining': 10000 - self.quota_used
        }
