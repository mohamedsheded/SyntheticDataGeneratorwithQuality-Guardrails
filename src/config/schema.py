"""Pydantic models for configuration validation"""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class PersonaConfig(BaseModel):
    """Configuration for a review persona"""
    
    name: str = Field(..., description="Persona name")
    tone: str = Field(..., description="Tone of the persona (e.g., 'pragmatic', 'formal')")
    expectations: List[str] = Field(default_factory=list, description="Key expectations for this persona")


class ReviewCharacteristics(BaseModel):
    """Characteristics for generated reviews"""
    
    length: List[Literal["short", "medium", "long"]] = Field(
        default=["short", "medium"],
        description="Allowed review lengths"
    )
    include_pros_cons: bool = Field(
        default=True,
        description="Whether to include pros and cons"
    )
    mention_features: bool = Field(
        default=True,
        description="Whether to mention specific features"
    )


class ModelConfig(BaseModel):
    """Configuration for an LLM model"""
    
    provider: Literal["openai", "groq", "openrouter"] = Field(default="openai", description="LLM provider (openai, groq, or openrouter)")
    model: str = Field(..., description="Model name (e.g., gpt-4o-mini for OpenAI, llama-3.3-70b-versatile for Groq, anthropic/claude-3.7-sonnet for OpenRouter)")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")


class GuardrailConfig(BaseModel):
    """Configuration for quality guardrails"""
    
    diversity: Dict[str, float] = Field(
        default_factory=lambda: {
            "vocab_overlap_threshold": 0.3,
            "semantic_similarity_threshold": 0.85,
        },
        description="Diversity guardrail thresholds"
    )
    bias: Dict[str, float] = Field(
        default_factory=lambda: {
            "sentiment_rating_mismatch_threshold": 0.5,
            "z_score_threshold": 2.0,
        },
        description="Bias guardrail thresholds"
    )
    realism: Dict[str, float] = Field(
        default_factory=lambda: {
            "realism_score_threshold": 0.7,
        },
        description="Realism guardrail thresholds"
    )
    max_retries: int = Field(default=2, ge=0, description="Maximum regeneration attempts")


class DomainConfig(BaseModel):
    """Complete domain configuration"""
    
    domain: str = Field(..., description="Domain name (e.g., 'SaaS Project Management Tool')")
    personas: List[PersonaConfig] = Field(..., min_length=1, description="List of personas")
    rating_distribution: Dict[int, float] = Field(
        ...,
        description="Rating distribution (1-5 stars with probabilities)"
    )
    review_characteristics: ReviewCharacteristics = Field(
        default_factory=ReviewCharacteristics,
        description="Review characteristics"
    )
    models: List[ModelConfig] = Field(..., min_length=1, description="List of models to use")
    guardrails: GuardrailConfig = Field(
        default_factory=GuardrailConfig,
        description="Guardrail configuration"
    )
    
    @field_validator("rating_distribution")
    @classmethod
    def validate_rating_distribution(cls, v: Dict[int, float]) -> Dict[int, float]:
        """Validate rating distribution sums to 1.0 and contains valid ratings"""
        valid_ratings = {1, 2, 3, 4, 5}
        if not all(r in valid_ratings for r in v.keys()):
            raise ValueError("Ratings must be between 1 and 5")
        
        total = sum(v.values())
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            raise ValueError(f"Rating distribution must sum to 1.0, got {total}")
        
        return v

