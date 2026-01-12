"""Unit tests for guardrails"""

import unittest
from unittest.mock import patch
from src.state.global_state import GlobalState
from src.config.schema import DomainConfig, PersonaConfig, ModelConfig, GuardrailConfig
from src.nodes.guardrails.diversity import check_diversity
from src.nodes.guardrails.bias import check_bias


class TestDiversityGuardrail(unittest.TestCase):
    """Test diversity guardrail"""
    
    def setUp(self):
        """Set up test state"""
        self.config = DomainConfig(
            domain="Test Domain",
            personas=[PersonaConfig(name="Test", tone="neutral", expectations=[])],
            rating_distribution={1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.2},
            models=[ModelConfig(provider="openai", model="gpt-4o-mini")],
            guardrails=GuardrailConfig(
                diversity={"vocab_overlap_threshold": 0.3, "semantic_similarity_threshold": 0.85}
            ),
        )
        
        self.state: GlobalState = {
            "accepted_reviews": [],
            "rejected_reviews": [],
            "metrics_per_model": {},
            "current_review": {
                "persona": {"name": "Test", "tone": "neutral", "expectations": []},
                "rating": 4,
                "model_id": "openai:gpt-4o-mini",
                "review_text": "This is a unique review with different words",
                "quality_scores": {},
                "is_valid": False,
                "rejection_reason": None,
                "generation_time": 0.0,
                "evaluation_time": 0.0,
                "retry_count": 0,
            },
            "config": self.config,
            "target_size": 10,
            "feedback": None,
        }
    
    def test_diversity_no_accepted_reviews(self):
        """Test diversity check with no accepted reviews (should pass)"""
        result = check_diversity(self.state)
        scores = result["current_review"]["quality_scores"]["diversity"]
        self.assertTrue(scores["pass"])
    
    def test_diversity_with_similar_review(self):
        """Test diversity check with similar accepted review"""
        # Add a similar review
        self.state["accepted_reviews"] = [
            {
                "review_text": "This is a unique review with different words",
                "persona": {},
                "rating": 4,
                "model_id": "openai:gpt-4o-mini",
                "quality_scores": {},
                "is_valid": True,
                "rejection_reason": None,
                "generation_time": 0.0,
                "evaluation_time": 0.0,
                "retry_count": 0,
            }
        ]
        
        result = check_diversity(self.state)
        scores = result["current_review"]["quality_scores"]["diversity"]
        # Should fail due to high similarity
        self.assertFalse(scores["pass"])


class TestBiasGuardrail(unittest.TestCase):
    """Test bias guardrail"""
    
    def setUp(self):
        """Set up test state"""
        self.config = DomainConfig(
            domain="Test Domain",
            personas=[PersonaConfig(name="Test", tone="neutral", expectations=[])],
            rating_distribution={1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.2},
            models=[ModelConfig(provider="openai", model="gpt-4o-mini")],
            guardrails=GuardrailConfig(
                bias={"sentiment_rating_mismatch_threshold": 0.5, "z_score_threshold": 2.0}
            ),
        )
        
        self.state: GlobalState = {
            "accepted_reviews": [],
            "rejected_reviews": [],
            "metrics_per_model": {},
            "current_review": {
                "persona": {"name": "Test", "tone": "neutral", "expectations": []},
                "rating": 5,
                "model_id": "openai:gpt-4o-mini",
                "review_text": "This is an amazing product! I love it so much!",
                "quality_scores": {},
                "is_valid": False,
                "rejection_reason": None,
                "generation_time": 0.0,
                "evaluation_time": 0.0,
                "retry_count": 0,
            },
            "config": self.config,
            "target_size": 10,
            "feedback": None,
        }
    
    def test_bias_positive_rating_positive_sentiment(self):
        """Test bias check with aligned rating and sentiment"""
        result = check_bias(self.state)
        scores = result["current_review"]["quality_scores"]["bias"]
        # Should pass for aligned sentiment
        self.assertTrue(scores["sentiment_rating_aligned"] or scores["pass"])
    
    def test_bias_mismatch(self):
        """Test bias check with mismatched rating and sentiment"""
        self.state["current_review"]["rating"] = 1
        self.state["current_review"]["review_text"] = "This is an amazing product! I love it so much!"
        
        result = check_bias(self.state)
        scores = result["current_review"]["quality_scores"]["bias"]
        # Should fail due to mismatch
        self.assertFalse(scores["sentiment_rating_aligned"])


if __name__ == "__main__":
    unittest.main()

