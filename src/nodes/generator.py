"""Review generation node with multi-model support"""

import os
import time
from typing import Dict, Any
from ..state.global_state import GlobalState
from ..state.review_state import ReviewState
from ..models.providers import create_provider
from ..config.schema import ModelConfig


def generate_review(state: GlobalState) -> GlobalState:
    """
    Generate a review using the selected model.
    
    Handles retries with feedback injection.
    """
    config = state["config"]
    review = state["current_review"]
    
    # Find model config
    model_id = review["model_id"]
    provider_name, model_name = model_id.split(":", 1)
    
    model_config = None
    for m in config.models:
        if m.provider == provider_name and m.model == model_name:
            model_config = m
            break
    
    if model_config is None:
        raise ValueError(f"Model config not found for {model_id}")
    
    # Create provider - will use OPENAI_API_KEY from environment automatically
    provider = create_provider(model_config, api_key=None)
    
    # Build prompt
    prompt = build_prompt(
        domain=config.domain,
        persona=review["persona"],
        rating=review["rating"],
        characteristics=config.review_characteristics,
        feedback=state.get("feedback"),
    )
    
    # Generate
    start_time = time.time()
    try:
        review_text, generation_time = provider.generate(prompt)
        
        # Validate that we got actual content
        # Check for None, empty string, or whitespace-only
        if review_text is None:
            review["review_text"] = None
            review["generation_time"] = time.time() - start_time
            review["rejection_reason"] = "Generation error: None response from model"
            review["is_valid"] = False
            import sys
            print(f"Warning: None response from {model_id}", file=sys.stderr)
        elif not isinstance(review_text, str):
            review["review_text"] = None
            review["generation_time"] = time.time() - start_time
            review["rejection_reason"] = f"Generation error: Invalid response type from model: {type(review_text)}"
            review["is_valid"] = False
            import sys
            print(f"Warning: Invalid response type from {model_id}: {type(review_text)}", file=sys.stderr)
        elif not review_text.strip():
            review["review_text"] = None
            review["generation_time"] = time.time() - start_time
            review["rejection_reason"] = "Generation error: Empty or whitespace-only response from model"
            review["is_valid"] = False
            import sys
            print(f"Warning: Empty/whitespace response from {model_id}. Original length: {len(review_text)}", file=sys.stderr)
        else:
            # Valid response - strip and store
            review["review_text"] = review_text.strip()
            review["generation_time"] = generation_time
    except Exception as e:
        review["review_text"] = None
        review["generation_time"] = time.time() - start_time
        review["rejection_reason"] = f"Generation error: {str(e)}"
        review["is_valid"] = False
        # Log for debugging
        import sys
        print(f"Error generating with {model_id}: {str(e)}", file=sys.stderr)
    
    state["current_review"] = review
    return state


def build_prompt(
    domain: str,
    persona: Dict[str, Any],
    rating: int,
    characteristics: Any,
    feedback: str | None = None,
) -> str:
    """
    Build generation prompt from configuration.
    
    Args:
        domain: Domain name
        persona: Persona dictionary
        rating: Target rating (1-5)
        characteristics: Review characteristics config
        feedback: Optional feedback for regeneration
        
    Returns:
        Formatted prompt string
    """
    tone_instruction = f"Write in a {persona['tone']} tone."
    
    expectations_text = ", ".join(persona["expectations"])
    expectations_instruction = f"Focus on: {expectations_text}."
    
    length_instruction = ""
    if "short" in characteristics.length:
        length_instruction = "Keep it concise (2-3 sentences)."
    elif "medium" in characteristics.length:
        length_instruction = "Write a medium-length review (4-6 sentences)."
    elif "long" in characteristics.length:
        length_instruction = "Write a detailed review (7+ sentences)."
    
    pros_cons = ""
    if characteristics.include_pros_cons:
        pros_cons = "Include both pros and cons."
    
    features = ""
    if characteristics.mention_features:
        features = "Mention specific features of the product."
    
    feedback_section = ""
    if feedback:
        feedback_section = f"\n\nPrevious attempt feedback: {feedback}\nPlease address this feedback in your review."
    
    # Build rating-specific guidance
    rating_guidance = ""
    if rating == 5:
        rating_guidance = "Write a very positive, enthusiastic review."
    elif rating == 4:
        rating_guidance = "Write a positive review with minor criticisms."
    elif rating == 3:
        rating_guidance = "Write a balanced, neutral review with both positives and negatives."
    elif rating == 2:
        rating_guidance = "Write a negative review highlighting significant problems."
    else:  # rating == 1
        rating_guidance = "Write a very negative review expressing strong dissatisfaction."
    
    prompt = f"""Write a {rating}-star review for a {domain}.

Persona: {persona['name']}
{tone_instruction}
{expectations_instruction}

Requirements:
{length_instruction}
{pros_cons}
{features}

Rating Guidance: {rating_guidance}
The review should clearly reflect a {rating}-star rating (where 1 is very negative and 5 is very positive).
{feedback_section}

Write the review now:"""
    
    return prompt

