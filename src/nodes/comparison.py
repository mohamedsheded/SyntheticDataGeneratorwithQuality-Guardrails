"""Real vs synthetic review comparison"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from ..state.global_state import GlobalState
from ..utils.embeddings import EmbeddingModel
from ..utils.sentiment import SentimentAnalyzer


def compare_real_vs_synthetic(
    synthetic_reviews: List[Dict[str, Any]],
    real_reviews_path: str | Path,
) -> Dict[str, Any]:
    """
    Compare synthetic reviews with real reviews.
    
    Args:
        synthetic_reviews: List of accepted review states
        real_reviews_path: Path to real reviews file (JSON or CSV)
        
    Returns:
        Dictionary of comparison metrics
    """
    # Load real reviews
    real_reviews = load_real_reviews(real_reviews_path)
    
    if not real_reviews:
        return {"error": "No real reviews found"}
    
    # Extract texts
    synthetic_texts = [
        r.get("review_text", "") for r in synthetic_reviews if r.get("review_text")
    ]
    real_texts = [r.get("text", r.get("review", "")) for r in real_reviews]
    
    # Filter empty texts
    synthetic_texts = [t for t in synthetic_texts if t.strip()]
    real_texts = [t for t in real_texts if t.strip()]
    
    if not synthetic_texts or not real_texts:
        return {"error": "No valid review texts found"}
    
    # 1. Embedding distribution overlap
    embedding_metrics = compare_embeddings(synthetic_texts, real_texts)
    
    # 2. Vocabulary richness
    vocab_metrics = compare_vocabulary(synthetic_texts, real_texts)
    
    # 3. Sentiment distribution
    sentiment_metrics = compare_sentiment(synthetic_texts, real_texts)
    
    # 4. Length distribution
    length_metrics = compare_length(synthetic_texts, real_texts)
    
    return {
        "embedding": embedding_metrics,
        "vocabulary": vocab_metrics,
        "sentiment": sentiment_metrics,
        "length": length_metrics,
    }


def load_real_reviews(path: str | Path) -> List[Dict[str, Any]]:
    """Load real reviews from JSON or CSV file"""
    path = Path(path)
    
    if not path.exists():
        return []
    
    if path.suffix.lower() == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle both list and dict formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "reviews" in data:
                return data["reviews"]
            else:
                return []
    
    elif path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
        return df.to_dict("records")
    
    return []


def compare_embeddings(synthetic: List[str], real: List[str]) -> Dict[str, float]:
    """Compare embedding distributions"""
    # Sample for efficiency if too many
    max_samples = 100
    synthetic_sample = synthetic[:max_samples] if len(synthetic) > max_samples else synthetic
    real_sample = real[:max_samples] if len(real) > max_samples else real
    
    # Compute embeddings
    synthetic_embeddings = EmbeddingModel.encode(synthetic_sample)
    real_embeddings = EmbeddingModel.encode(real_sample)
    
    # Compute mean embeddings
    synthetic_mean = np.mean(synthetic_embeddings, axis=0)
    real_mean = np.mean(real_embeddings, axis=0)
    
    # Cosine similarity between means
    mean_similarity = EmbeddingModel.cosine_similarity(synthetic_mean, real_mean)
    
    # Compute pairwise similarities
    similarities = []
    for syn_emb in synthetic_embeddings[:50]:  # Limit for efficiency
        sims = EmbeddingModel.batch_similarity(syn_emb, real_embeddings)
        similarities.append(float(np.max(sims)))
    
    avg_max_similarity = float(np.mean(similarities)) if similarities else 0.0
    
    return {
        "mean_embedding_similarity": float(mean_similarity),
        "avg_max_similarity": avg_max_similarity,
    }


def compare_vocabulary(synthetic: List[str], real: List[str]) -> Dict[str, Any]:
    """Compare vocabulary richness"""
    def get_vocab(texts: List[str]) -> set:
        vocab = set()
        for text in texts:
            words = text.lower().split()
            vocab.update(words)
        return vocab
    
    synthetic_vocab = get_vocab(synthetic)
    real_vocab = get_vocab(real)
    
    # Jaccard similarity
    intersection = len(synthetic_vocab & real_vocab)
    union = len(synthetic_vocab | real_vocab)
    jaccard = intersection / union if union > 0 else 0.0
    
    # Vocabulary size ratio
    vocab_ratio = len(synthetic_vocab) / len(real_vocab) if len(real_vocab) > 0 else 0.0
    
    return {
        "synthetic_vocab_size": len(synthetic_vocab),
        "real_vocab_size": len(real_vocab),
        "vocab_jaccard": float(jaccard),
        "vocab_ratio": float(vocab_ratio),
    }


def compare_sentiment(synthetic: List[str], real: List[str]) -> Dict[str, Any]:
    """Compare sentiment distributions"""
    synthetic_scores = [SentimentAnalyzer.analyze(t)["compound"] for t in synthetic]
    real_scores = [SentimentAnalyzer.analyze(t)["compound"] for t in real]
    
    return {
        "synthetic_mean": float(np.mean(synthetic_scores)),
        "synthetic_std": float(np.std(synthetic_scores)),
        "real_mean": float(np.mean(real_scores)),
        "real_std": float(np.std(real_scores)),
        "mean_difference": float(np.mean(synthetic_scores) - np.mean(real_scores)),
    }


def compare_length(synthetic: List[str], real: List[str]) -> Dict[str, Any]:
    """Compare length distributions"""
    synthetic_lengths = [len(t.split()) for t in synthetic]
    real_lengths = [len(t.split()) for t in real]
    
    return {
        "synthetic_mean": float(np.mean(synthetic_lengths)),
        "synthetic_std": float(np.std(synthetic_lengths)),
        "real_mean": float(np.mean(real_lengths)),
        "real_std": float(np.std(real_lengths)),
        "mean_difference": float(np.mean(synthetic_lengths) - np.mean(real_lengths)),
    }

