"""
Flask Application for YouTube Political Sentiment Analysis
Main application file with API endpoints and web interface
"""

from flask import Flask, render_template, request, jsonify
from youtube_api import YouTubeAPI
from sentiment_analyzer import SentimentAnalyzer
from data_handler import DataHandler
import os

app = Flask(__name__)

# Initialize components
youtube_api = YouTubeAPI()
sentiment_analyzer = SentimentAnalyzer()
data_handler = DataHandler()

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_videos():
    """
    Search for videos based on keyword
    
    Request JSON:
        {
            "query": "politik indonesia",
            "max_results": 10
        }
    
    Returns:
        JSON with video list or error
    """
    data = request.get_json()
    query = data.get('query', '')
    max_results = data.get('max_results', 10)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    videos = youtube_api.search_videos(query, max_results)
    
    if isinstance(videos, dict) and 'error' in videos:
        return jsonify(videos), 500
    
    return jsonify({
        'videos': videos,
        'quota': youtube_api.get_quota_usage()
    })

@app.route('/api/comments', methods=['POST'])
def get_comments():
    """
    Fetch comments from a video
    
    Request JSON:
        {
            "video_id": "abc123",
            "max_results": 100
        }
    
    Returns:
        JSON with comments or error
    """
    data = request.get_json()
    video_id = data.get('video_id', '')
    max_results = data.get('max_results', 100)
    
    if not video_id:
        return jsonify({'error': 'Video ID is required'}), 400
    
    comments = youtube_api.get_video_comments(video_id, max_results)
    
    if isinstance(comments, dict) and 'error' in comments:
        return jsonify(comments), 500
    
    return jsonify({
        'comments': comments,
        'count': len(comments),
        'quota': youtube_api.get_quota_usage()
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_sentiment():
    """
    Analyze sentiment of comments
    
    Request JSON:
        {
            "comments": [
                {"text": "comment 1", ...},
                {"text": "comment 2", ...}
            ]
        }
    
    Returns:
        JSON with analyzed comments and statistics
    """
    data = request.get_json()
    comments = data.get('comments', [])
    
    if not comments:
        return jsonify({'error': 'Comments are required'}), 400
    
    # Analyze sentiment for each comment
    for comment in comments:
        sentiment = sentiment_analyzer.analyze(comment.get('text', ''))
        comment['sentiment'] = sentiment['label']
        comment['sentiment_score'] = sentiment['score']
    
    # Calculate statistics
    sentiments = [{'label': c.get('sentiment', 'neutral')} for c in comments]
    statistics = sentiment_analyzer.get_statistics(sentiments)
    
    return jsonify({
        'comments': comments,
        'statistics': statistics
    })

@app.route('/api/analyze-video', methods=['POST'])
def analyze_video():
    """
    Complete workflow: fetch comments and analyze sentiment
    
    Request JSON:
        {
            "video_id": "abc123",
            "max_comments": 100
        }
    
    Returns:
        JSON with analyzed comments, statistics, and save path
    """
    data = request.get_json()
    video_id = data.get('video_id', '')
    max_comments = data.get('max_comments', 100)
    query = data.get('query', 'politik')
    
    if not video_id:
        return jsonify({'error': 'Video ID is required'}), 400
    
    # Fetch comments
    comments = youtube_api.get_video_comments(video_id, max_comments)
    
    if isinstance(comments, dict) and 'error' in comments:
        return jsonify(comments), 500
    
    if not comments:
        return jsonify({'error': 'No comments found'}), 404
    
    # Analyze sentiment
    for comment in comments:
        sentiment = sentiment_analyzer.analyze(comment.get('text', ''))
        comment['sentiment'] = sentiment['label']
        comment['sentiment_score'] = sentiment['score']
    
    # Calculate statistics
    sentiments = [{'label': c.get('sentiment', 'neutral')} for c in comments]
    statistics = sentiment_analyzer.get_statistics(sentiments)
    
    # Save results
    save_path = data_handler.export_analysis_report(comments, statistics, query)
    
    return jsonify({
        'comments': comments,
        'statistics': statistics,
        'saved_to': save_path,
        'quota': youtube_api.get_quota_usage()
    })

@app.route('/api/export', methods=['POST'])
def export_data():
    """
    Export analyzed data to CSV or JSON
    
    Request JSON:
        {
            "comments": [...],
            "format": "csv" or "json"
        }
    
    Returns:
        JSON with file path
    """
    data = request.get_json()
    comments = data.get('comments', [])
    format_type = data.get('format', 'csv')
    
    if not comments:
        return jsonify({'error': 'Comments are required'}), 400
    
    if format_type == 'csv':
        filepath = data_handler.save_comments_csv(comments)
    else:
        filepath = data_handler.save_comments_json(comments)
    
    return jsonify({
        'success': True,
        'filepath': filepath
    })

@app.route('/api/quota', methods=['GET'])
def get_quota():
    """Get current API quota usage"""
    return jsonify(youtube_api.get_quota_usage())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
