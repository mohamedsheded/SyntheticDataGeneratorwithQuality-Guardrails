"""Domain realism validator"""

import os
import time
from typing import Dict, Any
from ...state.global_state import GlobalState
from ...models.providers import create_provider
from ...config.schema import ModelConfig


def check_realism(state: GlobalState) -> GlobalState:
    """
    Check domain realism using LLM-as-judge.
    
    Validates:
    - Mentions real domain concepts
    - Avoids hallucinated features
    - Tone matches persona
    """
    start_time = time.time()
    
    review = state["current_review"]
    config = state["config"]
    
    review_text = review.get("review_text")
    if not review_text:
        review["quality_scores"]["realism"] = {
            "realism_score": 0.0,
            "pass": False,
        }
        review["evaluation_time"] += time.time() - start_time
        state["current_review"] = review
        return state
    
    # Use a model for validation (prefer groq models, then openai if available)
    validation_model = None
    for m in config.models:
        if m.provider == "groq":
            validation_model = m
            break
        elif m.provider == "openai" and "gpt" in m.model.lower():
            validation_model = m
            break
    
    # Fallback to first model if no preferred model found
    if validation_model is None:
        validation_model = config.models[0]
    
    # Build validation prompt
    prompt = build_realism_prompt(
        domain=config.domain,
        review_text=review_text,
        persona=review["persona"],
    )
    
    # Get validation score
    try:
        # Will use OPENAI_API_KEY from environment automatically
        provider = create_provider(validation_model, api_key=None)
        response, _ = provider.generate(
            prompt,
            temperature=0.1,  # Low temperature for consistent evaluation
            max_tokens=100,
        )
        
        # Parse score from response (expect format like "Score: 0.85" or just "0.85")
        if response and response.strip():
            realism_score = parse_realism_score(response)
        else:
            # Empty response, use heuristic
            realism_score = heuristic_realism_score(review_text, config.domain)
        
    except Exception as e:
        # If validation fails, use a heuristic fallback
        # Log the error but don't fail completely
        import sys
        print(f"Warning: Realism validation failed: {e}. Using heuristic fallback.", file=sys.stderr)
        realism_score = heuristic_realism_score(review_text, config.domain)
    
    # Check threshold
    threshold = config.guardrails.realism["realism_score_threshold"]
    passes = realism_score >= threshold
    
    review["quality_scores"]["realism"] = {
        "realism_score": realism_score,
        "pass": passes,
    }
    
    review["evaluation_time"] += time.time() - start_time
    state["current_review"] = review
    
    return state


def build_realism_prompt(domain: str, review_text: str, persona: Dict[str, Any]) -> str:
    """Build prompt for realism validation"""
    return f"""Evaluate the realism of this product review on a scale of 0.0 to 1.0.

Domain: {domain}
Expected Persona Tone: {persona['tone']}

Review:
{review_text}

Consider:
1. Does it mention realistic features/concepts for this domain?
2. Does it avoid obviously fake or hallucinated details?
3. Does the tone match the expected persona tone ({persona['tone']})?
4. Does it sound like a genuine user review?

Respond with only a single number between 0.0 and 1.0 representing the realism score.
Format: "Score: 0.XX" or just "0.XX"
"""


def parse_realism_score(response: str) -> float:
    """Parse realism score from LLM response"""
    import re
    
    # Look for "Score: 0.XX" or "0.XX" pattern
    patterns = [
        r"Score:\s*([0-9.]+)",
        r"([0-9]\.[0-9]+)",
        r"([0-9])",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response)
        if match:
            score = float(match.group(1))
            # Normalize to 0-1 range
            if score > 1.0:
                score = score / 10.0 if score <= 10.0 else 1.0
            return max(0.0, min(1.0, score))
    
    # Default if parsing fails
    return 0.5


def heuristic_realism_score(review_text: str, domain: str) -> float:
    """
    Fallback heuristic for realism when LLM validation fails.
    
    Checks for:
    - Reasonable length
    - Domain-relevant keywords
    - Balanced language (not too extreme)
    """
    if not review_text or not review_text.strip():
        return 0.0
    
    score = 0.5  # Base score
    
    # Length check
    word_count = len(review_text.split())
    if 10 <= word_count <= 200:
        score += 0.2
    elif word_count < 5:
        # Too short, reduce score
        score -= 0.2
    
    # Domain keyword check (simple heuristic)
    domain_lower = domain.lower()
    review_lower = review_text.lower()
    
    # Check for common domain-related terms
    domain_terms = ["feature", "use", "tool", "product", "service", "app", "software", "platform"]
    if any(term in review_lower for term in domain_terms):
        score += 0.2
    
    # Check for balanced language (not all caps, not too many exclamation marks)
    if not review_text.isupper() and review_text.count("!") < 5:
        score += 0.1
    
    return max(0.0, min(1.0, score))

