"""Bias and distribution guardrail: sentiment and rating alignment"""

import time
import numpy as np
from typing import Dict, Any, List
from ...state.global_state import GlobalState
from ...utils.sentiment import SentimentAnalyzer


def check_bias(state: GlobalState) -> GlobalState:
    """
    Check bias and distribution issues:
    - Sentiment vs rating alignment
    - Z-score analysis against global distribution
    """
    start_time = time.time()
    
    review = state["current_review"]
    accepted_reviews = state["accepted_reviews"]
    config = state["config"]
    
    review_text = review.get("review_text")
    if not review_text:
        review["quality_scores"]["bias"] = {
            "sentiment_rating_aligned": False,
            "z_score": 0.0,
            "pass": False,
        }
        review["evaluation_time"] += time.time() - start_time
        state["current_review"] = review
        return state
    
    rating = review["rating"]
    
    # Sentiment analysis
    sentiment_scores = SentimentAnalyzer.analyze(review_text)
    compound_score = sentiment_scores["compound"]
    
    # Check alignment: positive ratings should have positive sentiment, etc.
    expected_sentiment = SentimentAnalyzer.rating_to_expected_sentiment(rating)
    actual_sentiment = SentimentAnalyzer.get_sentiment_label(review_text)
    
    # Check if sentiment aligns with rating, with some tolerance
    # High ratings (4-5) should have positive sentiment (compound > 0.1)
    # Low ratings (1-2) should have negative sentiment (compound < -0.1)
    # Neutral rating (3) should be close to neutral (|compound| < 0.3)
    if rating >= 4:
        sentiment_aligned = compound_score >= 0.1
    elif rating <= 2:
        sentiment_aligned = compound_score <= -0.1
    else:  # rating == 3
        sentiment_aligned = abs(compound_score) < 0.3
    
    # Z-score analysis: check if sentiment distribution is reasonable
    # Collect all sentiment scores from accepted reviews
    if len(accepted_reviews) > 0:
        accepted_sentiments = []
        for r in accepted_reviews:
            text = r.get("review_text", "")
            if text:
                scores = SentimentAnalyzer.analyze(text)
                accepted_sentiments.append(scores["compound"])
        
        if accepted_sentiments:
            mean_sentiment = np.mean(accepted_sentiments)
            std_sentiment = np.std(accepted_sentiments) if len(accepted_sentiments) > 1 else 1.0
            
            if std_sentiment > 0:
                z_score = abs((compound_score - mean_sentiment) / std_sentiment)
            else:
                z_score = 0.0
        else:
            z_score = 0.0
    else:
        # No accepted reviews yet, so z-score is 0 (no comparison possible)
        z_score = 0.0
    
    # Check thresholds
    z_threshold = config.guardrails.bias["z_score_threshold"]
    
    # Pass if sentiment aligns and z-score is within threshold
    # Note: z_score of 0.0 is acceptable when there are no accepted reviews yet
    passes = sentiment_aligned and (z_score < z_threshold or z_score == 0.0)
    
    review["quality_scores"]["bias"] = {
        "sentiment_rating_aligned": sentiment_aligned,
        "sentiment_compound": compound_score,
        "z_score": float(z_score),
        "pass": passes,
    }
    
    review["evaluation_time"] += time.time() - start_time
    state["current_review"] = review
    
    return state

