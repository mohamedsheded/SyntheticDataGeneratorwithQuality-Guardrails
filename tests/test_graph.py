"""Integration tests for graph execution"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.graph.review_graph import create_review_graph
from src.state.global_state import GlobalState
from src.config.schema import DomainConfig, PersonaConfig, ModelConfig, GuardrailConfig


class TestGraphExecution(unittest.TestCase):
    """Test graph execution with mocks"""
    
    def setUp(self):
        """Set up test configuration"""
        self.config = DomainConfig(
            domain="Test Domain",
            personas=[
                PersonaConfig(name="Test Persona", tone="neutral", expectations=["quality"])
            ],
            rating_distribution={1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.2},
            models=[ModelConfig(provider="openai", model="gpt-4o-mini")],
            guardrails=GuardrailConfig(
                diversity={"vocab_overlap_threshold": 0.3, "semantic_similarity_threshold": 0.85},
                bias={"sentiment_rating_mismatch_threshold": 0.5, "z_score_threshold": 2.0},
                realism={"realism_score_threshold": 0.7},
                max_retries=2,
            ),
        )
    
    @patch("src.nodes.generator.create_provider")
    @patch("src.nodes.guardrails.realism.create_provider")
    def test_graph_single_review_flow(self, mock_realism_provider, mock_gen_provider):
        """Test graph flow for a single review"""
        # Mock providers
        mock_gen = Mock()
        mock_gen.generate.return_value = ("This is a great product!", 0.5)
        mock_gen_provider.return_value = mock_gen
        
        mock_realism = Mock()
        mock_realism.generate.return_value = ("Score: 0.85", 0.2)
        mock_realism_provider.return_value = mock_realism
        
        # Initialize state
        initial_state: GlobalState = {
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
            "target_size": 1,  # Only generate 1 review for test
            "feedback": None,
        }
        
        # Create and run graph
        graph = create_review_graph()
        
        # Note: This is a simplified test - full execution would require
        # all dependencies to be properly mocked
        # In practice, you'd want to test individual nodes separately
        # and use integration tests for the full flow
        
        # For now, just verify graph creation
        self.assertIsNotNone(graph)


if __name__ == "__main__":
    unittest.main()

