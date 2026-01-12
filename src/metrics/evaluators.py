"""Quality metric calculators"""

import numpy as np
from typing import Dict, Any, List
from ..state.review_state import ReviewState


def calculate_model_metrics(
    accepted_reviews: List[ReviewState],
    rejected_reviews: List[ReviewState],
    metrics_per_model: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Calculate comprehensive metrics per model.
    
    Args:
        accepted_reviews: List of accepted reviews
        rejected_reviews: List of rejected reviews
        metrics_per_model: Raw metrics dictionary
        
    Returns:
        Enhanced metrics dictionary with calculated statistics
    """
    enhanced_metrics = {}
    
    for model_id, raw_metrics in metrics_per_model.items():
        accepted_count = raw_metrics.get("accepted_count", 0)
        rejected_count = raw_metrics.get("rejected_count", 0)
        total_attempts = accepted_count + rejected_count
        
        # Acceptance rate
        acceptance_rate = (
            accepted_count / total_attempts if total_attempts > 0 else 0.0
        )
        
        # Average retries
        total_retries = raw_metrics.get("total_retries", 0)
        avg_retries = (
            total_retries / total_attempts if total_attempts > 0 else 0.0
        )
        
        # Average generation time
        total_gen_time = raw_metrics.get("total_generation_time", 0.0)
        avg_gen_time = (
            total_gen_time / total_attempts if total_attempts > 0 else 0.0
        )
        
        # Average evaluation time
        total_eval_time = raw_metrics.get("total_evaluation_time", 0.0)
        avg_eval_time = (
            total_eval_time / total_attempts if total_attempts > 0 else 0.0
        )
        
        # Quality score statistics (from accepted reviews only)
        model_accepted = [
            r for r in accepted_reviews if r.get("model_id") == model_id
        ]
        
        quality_stats = calculate_quality_statistics(model_accepted)
        
        enhanced_metrics[model_id] = {
            "accepted_count": accepted_count,
            "rejected_count": rejected_count,
            "total_attempts": total_attempts,
            "acceptance_rate": float(acceptance_rate),
            "avg_retries": float(avg_retries),
            "avg_generation_time": float(avg_gen_time),
            "avg_evaluation_time": float(avg_eval_time),
            "total_generation_time": float(total_gen_time),
            "total_evaluation_time": float(total_eval_time),
            "quality_statistics": quality_stats,
        }
    
    return enhanced_metrics


def calculate_quality_statistics(reviews: List[ReviewState]) -> Dict[str, Any]:
    """Calculate quality score statistics from reviews"""
    if not reviews:
        return {}
    
    diversity_scores = []
    bias_scores = []
    realism_scores = []
    
    for review in reviews:
        quality_scores = review.get("quality_scores", {})
        
        # Diversity
        diversity = quality_scores.get("diversity", {})
        if "semantic_similarity" in diversity:
            diversity_scores.append(diversity["semantic_similarity"])
        
        # Bias
        bias = quality_scores.get("bias", {})
        if "z_score" in bias:
            bias_scores.append(bias["z_score"])
        
        # Realism
        realism = quality_scores.get("realism", {})
        if "realism_score" in realism:
            realism_scores.append(realism["realism_score"])
    
    stats = {}
    
    if diversity_scores:
        stats["diversity"] = {
            "mean": float(np.mean(diversity_scores)),
            "std": float(np.std(diversity_scores)),
            "min": float(np.min(diversity_scores)),
            "max": float(np.max(diversity_scores)),
        }
    
    if bias_scores:
        stats["bias"] = {
            "mean": float(np.mean(bias_scores)),
            "std": float(np.std(bias_scores)),
            "min": float(np.min(bias_scores)),
            "max": float(np.max(bias_scores)),
        }
    
    if realism_scores:
        stats["realism"] = {
            "mean": float(np.mean(realism_scores)),
            "std": float(np.std(realism_scores)),
            "min": float(np.min(realism_scores)),
            "max": float(np.max(realism_scores)),
        }
    
    return stats


def calculate_global_metrics(
    accepted_reviews: List[ReviewState],
    rejected_reviews: List[ReviewState],
) -> Dict[str, Any]:
    """Calculate global metrics across all models"""
    total_accepted = len(accepted_reviews)
    total_rejected = len(rejected_reviews)
    total_attempts = total_accepted + total_rejected
    
    overall_acceptance_rate = (
        total_accepted / total_attempts if total_attempts > 0 else 0.0
    )
    
    # Rating distribution
    rating_counts = {}
    for review in accepted_reviews:
        rating = review.get("rating", 0)
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    rating_distribution = {
        str(k): v / total_accepted if total_accepted > 0 else 0.0
        for k, v in rating_counts.items()
    }
    
    # Average retries
    total_retries = sum(r.get("retry_count", 0) for r in accepted_reviews + rejected_reviews)
    avg_retries = (
        total_retries / total_attempts if total_attempts > 0 else 0.0
    )
    
    return {
        "total_accepted": total_accepted,
        "total_rejected": total_rejected,
        "total_attempts": total_attempts,
        "overall_acceptance_rate": float(overall_acceptance_rate),
        "avg_retries": float(avg_retries),
        "rating_distribution": rating_distribution,
    }

