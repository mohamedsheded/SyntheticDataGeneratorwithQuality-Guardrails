"""Review state TypedDict for individual review tracking"""

from typing import TypedDict, Optional, Dict, Any


class ReviewState(TypedDict):
    """State for a single review being generated"""
    
    persona: Dict[str, Any]  # Persona configuration dict
    rating: int  # Rating (1-5)
    model_id: str  # Model identifier (e.g., "openai:gpt-4o-mini")
    review_text: Optional[str]  # Generated review text
    quality_scores: Dict[str, Any]  # Scores from guardrails
    is_valid: bool  # Whether review passed all guardrails
    rejection_reason: Optional[str]  # Reason for rejection if invalid
    generation_time: float  # Time taken to generate (seconds)
    evaluation_time: float  # Time taken to evaluate (seconds)
    retry_count: int  # Number of regeneration attempts

