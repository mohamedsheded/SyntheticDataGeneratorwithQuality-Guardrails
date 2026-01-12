"""Diversity guardrail: vocabulary and semantic similarity checks"""

import time
from typing import Dict, Any, Set
from ...state.global_state import GlobalState
from ...utils.embeddings import EmbeddingModel


def check_diversity(state: GlobalState) -> GlobalState:
    """
    Check diversity of current review against accepted reviews.
    
    Computes:
    - Vocabulary overlap (Jaccard similarity)
    - Semantic similarity (cosine similarity of embeddings)
    """
    start_time = time.time()
    
    review = state["current_review"]
    accepted_reviews = state["accepted_reviews"]
    config = state["config"]
    
    review_text = review.get("review_text")
    if not review_text:
        review["quality_scores"]["diversity"] = {
            "vocab_overlap": 1.0,
            "semantic_similarity": 1.0,
            "pass": False,
        }
        review["evaluation_time"] += time.time() - start_time
        state["current_review"] = review
        return state
    
    # If no accepted reviews yet, pass diversity check
    if len(accepted_reviews) == 0:
        review["quality_scores"]["diversity"] = {
            "vocab_overlap": 0.0,
            "semantic_similarity": 0.0,
            "pass": True,
        }
        review["evaluation_time"] += time.time() - start_time
        state["current_review"] = review
        return state
    
    # Vocabulary overlap (Jaccard similarity)
    current_words = set(review_text.lower().split())
    vocab_overlaps = []
    
    for accepted in accepted_reviews:
        accepted_text = accepted.get("review_text", "")
        if accepted_text:
            accepted_words = set(accepted_text.lower().split())
            if len(current_words | accepted_words) > 0:
                jaccard = len(current_words & accepted_words) / len(
                    current_words | accepted_words
                )
                vocab_overlaps.append(jaccard)
    
    avg_vocab_overlap = sum(vocab_overlaps) / len(vocab_overlaps) if vocab_overlaps else 0.0
    
    # Semantic similarity
    current_embedding = EmbeddingModel.encode([review_text])[0]
    
    accepted_texts = [
        r.get("review_text", "") for r in accepted_reviews if r.get("review_text")
    ]
    if accepted_texts:
        accepted_embeddings = EmbeddingModel.encode(accepted_texts)
        similarities = EmbeddingModel.batch_similarity(
            current_embedding, accepted_embeddings
        )
        max_semantic_similarity = float(max(similarities))
    else:
        max_semantic_similarity = 0.0
    
    # Check thresholds
    vocab_threshold = config.guardrails.diversity["vocab_overlap_threshold"]
    semantic_threshold = config.guardrails.diversity["semantic_similarity_threshold"]
    
    passes = (
        avg_vocab_overlap < vocab_threshold
        and max_semantic_similarity < semantic_threshold
    )
    
    review["quality_scores"]["diversity"] = {
        "vocab_overlap": avg_vocab_overlap,
        "semantic_similarity": max_semantic_similarity,
        "pass": passes,
    }
    
    review["evaluation_time"] += time.time() - start_time
    state["current_review"] = review
    
    return state

