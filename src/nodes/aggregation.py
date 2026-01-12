"""Aggregation node: combine guardrail results"""

import sys
from ..state.global_state import GlobalState


def aggregate_guardrails(state: GlobalState) -> GlobalState:
    """
    Aggregate all guardrail results and determine final validity.
    
    Sets is_valid based on all guardrails passing.
    Generates rejection reason if any guardrail fails.
    """
    review = state["current_review"]
    quality_scores = review.get("quality_scores", {})
    
    # Early exit if review_text is None or empty - no need to check guardrails
    review_text = review.get("review_text")
    if not review_text or (isinstance(review_text, str) and not review_text.strip()):
        review["is_valid"] = False
        review["rejection_reason"] = "Generation error: Empty or invalid review text"
        state["current_review"] = review
        return state
    
    # Check each guardrail
    diversity_pass = quality_scores.get("diversity", {}).get("pass", False)
    bias_pass = quality_scores.get("bias", {}).get("pass", False)
    realism_pass = quality_scores.get("realism", {}).get("pass", False)
    
    # All must pass
    is_valid = diversity_pass and bias_pass and realism_pass
    
    # Generate rejection reason if invalid
    rejection_reason = None
    if not is_valid:
        reasons = []
        if not diversity_pass:
            diversity_scores = quality_scores.get("diversity", {})
            vocab_overlap = diversity_scores.get("vocab_overlap", 0)
            semantic_sim = diversity_scores.get("semantic_similarity", 0)
            vocab_threshold = state["config"].guardrails.diversity["vocab_overlap_threshold"]
            semantic_threshold = state["config"].guardrails.diversity["semantic_similarity_threshold"]
            reasons.append(
                f"Diversity FAILED: vocab_overlap={vocab_overlap:.2f} (threshold: {vocab_threshold:.2f}), "
                f"semantic_sim={semantic_sim:.2f} (threshold: {semantic_threshold:.2f})"
            )
        if not bias_pass:
            bias_scores = quality_scores.get("bias", {})
            z_score = bias_scores.get("z_score", 0)
            aligned = bias_scores.get("sentiment_rating_aligned", False)
            compound = bias_scores.get("sentiment_compound", 0)
            z_threshold = state["config"].guardrails.bias["z_score_threshold"]
            reasons.append(
                f"Bias FAILED: sentiment_aligned={aligned}, sentiment_compound={compound:.2f}, "
                f"z_score={z_score:.2f} (threshold: {z_threshold:.2f})"
            )
        if not realism_pass:
            realism_scores = quality_scores.get("realism", {})
            realism_score = realism_scores.get("realism_score", 0)
            threshold = state["config"].guardrails.realism["realism_score_threshold"]
            reasons.append(f"Realism FAILED: score={realism_score:.2f} (threshold: {threshold:.2f})")
        
        rejection_reason = "; ".join(reasons)
    
    review["is_valid"] = is_valid
    review["rejection_reason"] = rejection_reason
    
    state["current_review"] = review
    return state

