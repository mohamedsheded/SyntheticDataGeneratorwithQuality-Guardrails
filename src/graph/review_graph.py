"""Main LangGraph definition for review generation pipeline"""

from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from ..state.global_state import GlobalState
from ..nodes.sampler import sample_persona_and_rating
from ..nodes.generator import generate_review
from ..nodes.guardrails.diversity import check_diversity
from ..nodes.guardrails.bias import check_bias
from ..nodes.guardrails.realism import check_realism
from ..nodes.aggregation import aggregate_guardrails
from ..nodes.routing import (
    accept_review,
    reject_review,
    prepare_regeneration,
    should_continue,
    should_retry,
)


def create_review_graph() -> CompiledStateGraph:
    """
    Create the review generation LangGraph.
    
    Graph flow:
    1. Sample persona and rating
    2. Generate review
    3. Check diversity guardrail
    4. Check bias guardrail
    5. Check realism guardrail
    6. Aggregate guardrail results
    7. Route: accept, retry, or reject
    8. Continue until target size reached
    """
    graph = StateGraph(GlobalState)
    
    # Add nodes
    graph.add_node("sample", sample_persona_and_rating)
    graph.add_node("generate", generate_review)
    graph.add_node("diversity_check", check_diversity)
    graph.add_node("bias_check", check_bias)
    graph.add_node("realism_check", check_realism)
    graph.add_node("aggregate", aggregate_guardrails)
    graph.add_node("accept", accept_review)
    graph.add_node("reject", reject_review)
    graph.add_node("prepare_retry", prepare_regeneration)
    
    # Set entry point
    graph.set_entry_point("sample")
    
    # Main flow
    graph.add_edge("sample", "generate")
    graph.add_edge("generate", "diversity_check")
    graph.add_edge("diversity_check", "bias_check")
    graph.add_edge("bias_check", "realism_check")
    graph.add_edge("realism_check", "aggregate")
    
    # Conditional routing after aggregation
    graph.add_conditional_edges(
        "aggregate",
        route_after_aggregation,
        {
            "accept": "accept",
            "retry": "prepare_retry",
            "reject": "reject",
        },
    )
    
    # After accept/reject, check if we should continue
    graph.add_conditional_edges(
        "accept",
        check_continue,
        {
            "continue": "sample",
            "finish": END,
        },
    )
    
    graph.add_conditional_edges(
        "reject",
        check_continue,
        {
            "continue": "sample",
            "finish": END,
        },
    )
    
    # Retry flow
    graph.add_edge("prepare_retry", "generate")
    
    return graph.compile()


def route_after_aggregation(state: GlobalState) -> Literal["accept", "retry", "reject"]:
    """
    Route after guardrail aggregation.
    
    Returns:
        "accept" if valid, "retry" if should retry, "reject" if max retries reached
    """
    review = state["current_review"]
    
    if review.get("is_valid", False):
        return "accept"
    
    # Check if we should retry
    retry_decision = should_retry(state)
    if retry_decision == "retry":
        return "retry"
    else:
        return "reject"


def check_continue(state: GlobalState) -> Literal["continue", "finish"]:
    """Check if generation should continue"""
    return should_continue(state)

