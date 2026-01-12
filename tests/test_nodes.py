"""Unit tests for nodes"""

import unittest
from unittest.mock import Mock, patch
from src.state.global_state import GlobalState
from src.state.review_state import ReviewState
from src.config.schema import DomainConfig, PersonaConfig, ModelConfig, ReviewCharacteristics, GuardrailConfig
from src.nodes.sampler import sample_persona_and_rating
from src.nodes.aggregation import aggregate_guardrails


class TestSampler(unittest.TestCase):
    """Test persona and rating sampling"""
    
    def setUp(self):
        """Set up test configuration"""
        self.config = DomainConfig(
            domain="Test Domain",
            personas=[
                PersonaConfig(name="Test Persona", tone="neutral", expectations=["quality"])
            ],
            rating_distribution={1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.2},
            models=[ModelConfig(provider="openai", model="gpt-4o-mini")],
        )
        
        self.state: GlobalState = {
            "accepted_reviews": [],
            "rejected_reviews": [],
            "metrics_per_model": {},
            "current_review": {
                "persona": {},
                "rating": 0,
                "model_id": "",
                "review_text": None,
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
    
    def test_sample_persona_and_rating(self):
        """Test that sampling initializes review state correctly"""
        result = sample_persona_and_rating(self.state)
        
        review = result["current_review"]
        self.assertIn("persona", review)
        self.assertIn("name", review["persona"])
        self.assertIn(review["rating"], [1, 2, 3, 4, 5])
        self.assertIn("model_id", review)
        self.assertEqual(review["retry_count"], 0)


class TestAggregation(unittest.TestCase):
    """Test guardrail aggregation"""
    
    def setUp(self):
        """Set up test state"""
        self.state: GlobalState = {
            "accepted_reviews": [],
            "rejected_reviews": [],
            "metrics_per_model": {},
            "current_review": {
                "persona": {"name": "Test", "tone": "neutral", "expectations": []},
                "rating": 4,
                "model_id": "openai:gpt-4o-mini",
                "review_text": "Test review",
                "quality_scores": {},
                "is_valid": False,
                "rejection_reason": None,
                "generation_time": 0.0,
                "evaluation_time": 0.0,
                "retry_count": 0,
            },
            "config": Mock(),
            "target_size": 10,
            "feedback": None,
        }
    
    def test_aggregate_all_pass(self):
        """Test aggregation when all guardrails pass"""
        self.state["current_review"]["quality_scores"] = {
            "diversity": {"pass": True},
            "bias": {"pass": True},
            "realism": {"pass": True},
        }
        
        result = aggregate_guardrails(self.state)
        self.assertTrue(result["current_review"]["is_valid"])
        self.assertIsNone(result["current_review"]["rejection_reason"])
    
    def test_aggregate_some_fail(self):
        """Test aggregation when some guardrails fail"""
        self.state["current_review"]["quality_scores"] = {
            "diversity": {"pass": True, "vocab_overlap": 0.5, "semantic_similarity": 0.9},
            "bias": {"pass": False, "z_score": 3.0, "sentiment_rating_aligned": True},
            "realism": {"pass": True, "realism_score": 0.8},
        }
        
        result = aggregate_guardrails(self.state)
        self.assertFalse(result["current_review"]["is_valid"])
        self.assertIsNotNone(result["current_review"]["rejection_reason"])
        self.assertIn("Bias", result["current_review"]["rejection_reason"])


if __name__ == "__main__":
    unittest.main()

