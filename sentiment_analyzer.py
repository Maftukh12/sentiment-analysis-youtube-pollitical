"""
Sentiment Analysis Module
Analyzes sentiment of Indonesian text using pre-trained models
"""

from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

class SentimentAnalyzer:
    def __init__(self):
        """Initialize sentiment analysis model for Indonesian language"""
        try:
            # Using IndoBERT-based sentiment model for Indonesian
            # Falls back to multilingual model if specific model unavailable
            self.model = pipeline(
                "sentiment-analysis",
                model="w11wo/indonesian-roberta-base-sentiment-classifier",
                top_k=None
            )
            self.model_loaded = True
        except Exception as e:
            print(f"Warning: Could not load Indonesian model, using multilingual: {e}")
            try:
                # Fallback to multilingual model
                self.model = pipeline(
                    "sentiment-analysis",
                    model="nlptown/bert-base-multilingual-uncased-sentiment"
                )
                self.model_loaded = True
            except Exception as e2:
                print(f"Error loading sentiment model: {e2}")
                self.model_loaded = False
    
    def analyze(self, text):
        """
        Analyze sentiment of a single text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Sentiment result with label and score
        """
        if not self.model_loaded:
            return {
                'label': 'neutral',
                'score': 0.0,
                'error': 'Model not loaded'
            }
        
        if not text or len(text.strip()) == 0:
            return {
                'label': 'neutral',
                'score': 0.0
            }
        
        try:
            # Truncate text if too long (model limit is usually 512 tokens)
            text = text[:500]
            
            result = self.model(text)
            
            # Handle different model output formats
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list):
                    # Multiple labels returned, get the top one
                    top_result = max(result[0], key=lambda x: x['score'])
                    label = self._normalize_label(top_result['label'])
                    score = top_result['score']
                else:
                    # Single label returned
                    label = self._normalize_label(result[0]['label'])
                    score = result[0]['score']
            else:
                label = 'neutral'
                score = 0.0
            
            return {
                'label': label,
                'score': round(score, 3)
            }
        
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'label': 'neutral',
                'score': 0.0,
                'error': str(e)
            }
    
    def _normalize_label(self, label):
        """
        Normalize different label formats to positive/negative/neutral
        
        Args:
            label (str): Original label from model
            
        Returns:
            str: Normalized label
        """
        label_lower = label.lower()
        
        # Map various label formats
        if any(word in label_lower for word in ['positive', 'positif', '4 stars', '5 stars']):
            return 'positive'
        elif any(word in label_lower for word in ['negative', 'negatif', '1 star', '2 stars']):
            return 'negative'
        else:
            return 'neutral'
    
    def analyze_batch(self, texts):
        """
        Analyze sentiment of multiple texts
        
        Args:
            texts (list): List of texts to analyze
            
        Returns:
            list: List of sentiment results
        """
        results = []
        for text in texts:
            result = self.analyze(text)
            results.append(result)
        
        return results
    
    def get_statistics(self, sentiments):
        """
        Calculate statistics from sentiment results
        
        Args:
            sentiments (list): List of sentiment dictionaries
            
        Returns:
            dict: Statistics including counts and percentages
        """
        total = len(sentiments)
        if total == 0:
            return {
                'total': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'positive_pct': 0,
                'negative_pct': 0,
                'neutral_pct': 0
            }
        
        positive = sum(1 for s in sentiments if s.get('label') == 'positive')
        negative = sum(1 for s in sentiments if s.get('label') == 'negative')
        neutral = sum(1 for s in sentiments if s.get('label') == 'neutral')
        
        return {
            'total': total,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'positive_pct': round((positive / total) * 100, 1),
            'negative_pct': round((negative / total) * 100, 1),
            'neutral_pct': round((neutral / total) * 100, 1)
        }
