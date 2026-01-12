"""Global state TypedDict for LangGraph"""

from typing import TypedDict, List, Dict, Any, Optional
from ..config.schema import DomainConfig
from .review_state import ReviewState


class GlobalState(TypedDict):
    """Global state for the review generation graph"""
    
    accepted_reviews: List[ReviewState]  # Successfully generated reviews
    rejected_reviews: List[ReviewState]  # Rejected reviews after max retries
    metrics_per_model: Dict[str, Dict[str, Any]]  # Metrics aggregated by model
    current_review: ReviewState  # Current review being processed
    config: DomainConfig  # Domain configuration
    target_size: int  # Target number of accepted reviews
    feedback: Optional[str]  # Feedback for regeneration (if retrying)

