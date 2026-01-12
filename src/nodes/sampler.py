"""Persona and rating sampling node"""

import random
from typing import Dict, Any
from ..state.global_state import GlobalState
from ..state.review_state import ReviewState


def sample_persona_and_rating(state: GlobalState) -> GlobalState:
    """
    Sample persona and rating for a new review.
    
    This is a deterministic node that initializes the review state.
    """
    config = state["config"]
    
    # Sample persona (uniform distribution)
    persona = random.choice(config.personas)
    persona_dict = {
        "name": persona.name,
        "tone": persona.tone,
        "expectations": persona.expectations,
    }
    
    # Sample rating based on distribution
    ratings = list(config.rating_distribution.keys())
    probabilities = list(config.rating_distribution.values())
    rating = random.choices(ratings, weights=probabilities, k=1)[0]
    
    # Sample model (uniform distribution)
    model_config = random.choice(config.models)
    model_id = f"{model_config.provider}:{model_config.model}"
    
    # Initialize review state
    review: ReviewState = {
        "persona": persona_dict,
        "rating": rating,
        "model_id": model_id,
        "review_text": None,
        "quality_scores": {},
        "is_valid": False,
        "rejection_reason": None,
        "generation_time": 0.0,
        "evaluation_time": 0.0,
        "retry_count": 0,
    }
    
    state["current_review"] = review
    state["feedback"] = None
    
    return state

