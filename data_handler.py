"""
Data Handler Module
Manages data persistence for comments and sentiment analysis results
"""

import pandas as pd
import json
import os
from datetime import datetime

class DataHandler:
    def __init__(self, data_dir='data'):
        """Initialize data handler with data directory"""
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def save_comments_csv(self, comments, filename=None):
        """
        Save comments to CSV file
        
        Args:
            comments (list): List of comment dictionaries
            filename (str): Optional filename, auto-generated if not provided
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'comments_{timestamp}.csv'
        
        filepath = os.path.join(self.data_dir, filename)
        
        df = pd.DataFrame(comments)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    def save_comments_json(self, comments, filename=None):
        """
        Save comments to JSON file
        
        Args:
            comments (list): List of comment dictionaries
            filename (str): Optional filename, auto-generated if not provided
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'comments_{timestamp}.json'
        
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_comments_csv(self, filename):
        """
        Load comments from CSV file
        
        Args:
            filename (str): Filename to load
            
        Returns:
            list: List of comment dictionaries
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            return []
        
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        return df.to_dict('records')
    
    def load_comments_json(self, filename):
        """
        Load comments from JSON file
        
        Args:
            filename (str): Filename to load
            
        Returns:
            list: List of comment dictionaries
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_saved_files(self):
        """
        List all saved data files
        
        Returns:
            dict: Dictionary with CSV and JSON file lists
        """
        if not os.path.exists(self.data_dir):
            return {'csv': [], 'json': []}
        
        files = os.listdir(self.data_dir)
        
        return {
            'csv': [f for f in files if f.endswith('.csv')],
            'json': [f for f in files if f.endswith('.json')]
        }
    
    def export_analysis_report(self, comments, statistics, query, filename=None):
        """
        Export comprehensive analysis report
        
        Args:
            comments (list): List of comments with sentiment
            statistics (dict): Sentiment statistics
            query (str): Search query used
            filename (str): Optional filename
            
        Returns:
            str: Path to saved report
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'analysis_report_{timestamp}.json'
        
        filepath = os.path.join(self.data_dir, filename)
        
        report = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'statistics': statistics,
            'comments': comments
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return filepath
