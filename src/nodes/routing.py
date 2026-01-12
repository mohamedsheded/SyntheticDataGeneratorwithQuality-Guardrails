"""Routing logic: accept, reject, or regenerate"""

from typing import Literal
from ..state.global_state import GlobalState


def accept_review(state: GlobalState) -> GlobalState:
    """Accept review and add to accepted_reviews"""
    review = state["current_review"].copy()
    
    # Add to accepted reviews
    state["accepted_reviews"].append(review)
    
    # Update metrics for this model
    model_id = review["model_id"]
    if model_id not in state["metrics_per_model"]:
        state["metrics_per_model"][model_id] = {
            "accepted_count": 0,
            "rejected_count": 0,
            "total_generation_time": 0.0,
            "total_evaluation_time": 0.0,
            "total_retries": 0,
        }
    
    metrics = state["metrics_per_model"][model_id]
    metrics["accepted_count"] += 1
    metrics["total_generation_time"] += review["generation_time"]
    metrics["total_evaluation_time"] += review["evaluation_time"]
    metrics["total_retries"] += review["retry_count"]
    
    # Print progress
    accepted = len(state["accepted_reviews"])
    target = state["target_size"]
    print(f"✓ Accepted review {accepted}/{target} (Rating: {review['rating']}★, Model: {review['model_id']})")
    
    return state


def reject_review(state: GlobalState) -> GlobalState:
    """Reject review after max retries and add to rejected_reviews"""
    review = state["current_review"].copy()
    
    # Add to rejected reviews
    state["rejected_reviews"].append(review)
    
    # Update metrics for this model
    model_id = review["model_id"]
    if model_id not in state["metrics_per_model"]:
        state["metrics_per_model"][model_id] = {
            "accepted_count": 0,
            "rejected_count": 0,
            "total_generation_time": 0.0,
            "total_evaluation_time": 0.0,
            "total_retries": 0,
        }
    
    metrics = state["metrics_per_model"][model_id]
    metrics["rejected_count"] += 1
    metrics["total_generation_time"] += review["generation_time"]
    metrics["total_evaluation_time"] += review["evaluation_time"]
    metrics["total_retries"] += review["retry_count"]
    
    # Print rejection reason
    rejection_reason = review.get("rejection_reason", "Unknown reason")
    rating = review.get("rating", "?")
    print(f"✗ Rejected review (Rating: {rating}★, Retries: {review.get('retry_count', 0)}): {rejection_reason}")
    
    return state


def prepare_regeneration(state: GlobalState) -> GlobalState:
    """Prepare for regeneration by incrementing retry count and setting feedback"""
    review = state["current_review"]
    
    # Increment retry count
    review["retry_count"] += 1
    
    # Set feedback based on rejection reason
    rejection_reason = review.get("rejection_reason", "Quality check failed")
    state["feedback"] = f"Previous attempt failed: {rejection_reason}. Please generate a different review."
    
    # Reset quality scores for new evaluation
    review["quality_scores"] = {}
    review["is_valid"] = False
    review["rejection_reason"] = None
    
    state["current_review"] = review
    return state


def should_continue(state: GlobalState) -> Literal["continue", "finish"]:
    """
    Determine if generation should continue.
    
    Returns:
        "continue" if more reviews needed, "finish" if target reached
    """
    target_size = state["target_size"]
    accepted_count = len(state["accepted_reviews"])
    total_attempts = len(state["accepted_reviews"]) + len(state["rejected_reviews"])
    
    # Stop if we've reached target
    if accepted_count >= target_size:
        return "finish"
    
    # Safety: Stop if we've tried way too many times (10x target) without success
    # This prevents infinite loops
    if total_attempts > target_size * 10:
        print(f"\nWarning: Stopping after {total_attempts} attempts. "
              f"Only {accepted_count}/{target_size} reviews accepted. "
              f"Acceptance rate may be too low.", file=__import__("sys").stderr)
        return "finish"
    
    return "continue"


def should_retry(state: GlobalState) -> Literal["retry", "reject"]:
    """
    Determine if review should be retried or rejected.
    
    Returns:
        "retry" if retries remaining, "reject" if max retries reached
    """
    review = state["current_review"]
    config = state["config"]
    
    max_retries = config.guardrails.max_retries
    current_retries = review.get("retry_count", 0)
    
    if current_retries < max_retries:
        return "retry"
    return "reject"

