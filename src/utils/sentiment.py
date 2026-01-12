"""Sentiment analysis utilities"""

from typing import Dict, Any
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentAnalyzer:
    """Wrapper for VADER sentiment analyzer"""
    
    _analyzer: SentimentIntensityAnalyzer = None
    
    @classmethod
    def get_analyzer(cls) -> SentimentIntensityAnalyzer:
        """Get or initialize the sentiment analyzer"""
        if cls._analyzer is None:
            cls._analyzer = SentimentIntensityAnalyzer()
        return cls._analyzer
    
    @classmethod
    def analyze(cls, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with 'compound', 'pos', 'neu', 'neg' scores
        """
        analyzer = cls.get_analyzer()
        scores = analyzer.polarity_scores(text)
        return scores
    
    @classmethod
    def get_sentiment_label(cls, text: str) -> str:
        """
        Get sentiment label (positive, neutral, negative).
        
        Args:
            text: Text to analyze
            
        Returns:
            'positive', 'neutral', or 'negative'
        """
        scores = cls.analyze(text)
        compound = scores["compound"]
        
        if compound >= 0.05:
            return "positive"
        elif compound <= -0.05:
            return "negative"
        else:
            return "neutral"
    
    @classmethod
    def rating_to_expected_sentiment(cls, rating: int) -> str:
        """
        Map rating to expected sentiment.
        
        Args:
            rating: Rating from 1-5
            
        Returns:
            Expected sentiment label
        """
        if rating >= 4:
            return "positive"
        elif rating <= 2:
            return "negative"
        else:
            return "neutral"

