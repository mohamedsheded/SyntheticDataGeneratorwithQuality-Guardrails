"""Markdown report generation"""

from typing import Dict, Any, List
from pathlib import Path
from ..state.review_state import ReviewState
from .evaluators import calculate_model_metrics, calculate_global_metrics


def generate_report(
    accepted_reviews: List[ReviewState],
    rejected_reviews: List[ReviewState],
    metrics_per_model: Dict[str, Dict[str, Any]],
    comparison_metrics: Dict[str, Any] | None = None,
    config: Any = None,
    output_path: str | Path | None = None,
) -> str:
    """
    Generate comprehensive Markdown quality report.
    
    Args:
        accepted_reviews: List of accepted reviews
        rejected_reviews: List of rejected reviews
        metrics_per_model: Per-model metrics
        comparison_metrics: Real vs synthetic comparison metrics
        config: Domain configuration
        output_path: Optional path to save report
        
    Returns:
        Markdown report string
    """
    # Calculate enhanced metrics
    enhanced_metrics = calculate_model_metrics(
        accepted_reviews, rejected_reviews, metrics_per_model
    )
    global_metrics = calculate_global_metrics(accepted_reviews, rejected_reviews)
    
    # Build report
    report_lines = []
    
    # Header
    report_lines.append("# Synthetic Review Generation Quality Report\n")
    
    # Summary
    report_lines.append("## Summary\n")
    report_lines.append(f"- **Total Accepted Reviews**: {global_metrics['total_accepted']}")
    report_lines.append(f"- **Total Rejected Reviews**: {global_metrics['total_rejected']}")
    report_lines.append(
        f"- **Overall Acceptance Rate**: {global_metrics['overall_acceptance_rate']:.2%}"
    )
    report_lines.append(f"- **Average Retries**: {global_metrics['avg_retries']:.2f}\n")
    
    # Guardrail thresholds
    if config:
        report_lines.append("## Guardrail Thresholds\n")
        report_lines.append("### Diversity")
        report_lines.append(
            f"- Vocabulary Overlap Threshold: {config.guardrails.diversity['vocab_overlap_threshold']}"
        )
        report_lines.append(
            f"- Semantic Similarity Threshold: {config.guardrails.diversity['semantic_similarity_threshold']}"
        )
        report_lines.append("\n### Bias")
        report_lines.append(
            f"- Z-Score Threshold: {config.guardrails.bias['z_score_threshold']}"
        )
        report_lines.append("\n### Realism")
        report_lines.append(
            f"- Realism Score Threshold: {config.guardrails.realism['realism_score_threshold']}"
        )
        report_lines.append(f"- Max Retries: {config.guardrails.max_retries}\n")
    
    # Model comparison
    report_lines.append("## Model Comparison\n")
    report_lines.append("| Model | Accepted | Rejected | Acceptance Rate | Avg Retries | Avg Gen Time (s) |")
    report_lines.append("|-------|----------|----------|-----------------|-------------|------------------|")
    
    for model_id, metrics in enhanced_metrics.items():
        report_lines.append(
            f"| {model_id} | {metrics['accepted_count']} | {metrics['rejected_count']} | "
            f"{metrics['acceptance_rate']:.2%} | {metrics['avg_retries']:.2f} | "
            f"{metrics['avg_generation_time']:.3f} |"
        )
    
    report_lines.append("")
    
    # Quality statistics
    report_lines.append("## Quality Statistics\n")
    for model_id, metrics in enhanced_metrics.items():
        report_lines.append(f"### {model_id}\n")
        quality_stats = metrics.get("quality_statistics", {})
        
        if "diversity" in quality_stats:
            div = quality_stats["diversity"]
            report_lines.append(
                f"- **Diversity (Semantic Similarity)**: "
                f"μ={div['mean']:.3f}, σ={div['std']:.3f}, "
                f"range=[{div['min']:.3f}, {div['max']:.3f}]"
            )
        
        if "bias" in quality_stats:
            bias = quality_stats["bias"]
            report_lines.append(
                f"- **Bias (Z-Score)**: "
                f"μ={bias['mean']:.3f}, σ={bias['std']:.3f}, "
                f"range=[{bias['min']:.3f}, {bias['max']:.3f}]"
            )
        
        if "realism" in quality_stats:
            real = quality_stats["realism"]
            report_lines.append(
                f"- **Realism Score**: "
                f"μ={real['mean']:.3f}, σ={real['std']:.3f}, "
                f"range=[{real['min']:.3f}, {real['max']:.3f}]"
            )
        
        report_lines.append("")
    
    # Rating distribution
    report_lines.append("## Rating Distribution\n")
    report_lines.append("| Rating | Count | Percentage |")
    report_lines.append("|--------|-------|------------|")
    
    rating_dist = global_metrics["rating_distribution"]
    for rating in sorted(rating_dist.keys(), key=int):
        count = int(rating_dist[rating] * global_metrics["total_accepted"])
        pct = rating_dist[rating]
        report_lines.append(f"| {rating}★ | {count} | {pct:.2%} |")
    
    report_lines.append("")
    
    # Failure modes
    if rejected_reviews:
        report_lines.append("## Failure Modes\n")
        
        failure_reasons = {}
        for review in rejected_reviews:
            reason = review.get("rejection_reason", "Unknown")
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        
        report_lines.append("| Reason | Count |")
        report_lines.append("|--------|-------|")
        for reason, count in sorted(failure_reasons.items(), key=lambda x: -x[1]):
            report_lines.append(f"| {reason} | {count} |")
        
        report_lines.append("")
    
    # Real vs Synthetic Comparison
    if comparison_metrics and "error" not in comparison_metrics:
        report_lines.append("## Real vs Synthetic Comparison\n")
        
        if "embedding" in comparison_metrics:
            emb = comparison_metrics["embedding"]
            report_lines.append("### Embedding Similarity")
            report_lines.append(
                f"- Mean Embedding Similarity: {emb.get('mean_embedding_similarity', 0):.3f}"
            )
            report_lines.append(
                f"- Average Max Similarity: {emb.get('avg_max_similarity', 0):.3f}"
            )
            report_lines.append("")
        
        if "vocabulary" in comparison_metrics:
            vocab = comparison_metrics["vocabulary"]
            report_lines.append("### Vocabulary")
            report_lines.append(
                f"- Synthetic Vocab Size: {vocab.get('synthetic_vocab_size', 0)}"
            )
            report_lines.append(
                f"- Real Vocab Size: {vocab.get('real_vocab_size', 0)}"
            )
            report_lines.append(
                f"- Jaccard Similarity: {vocab.get('vocab_jaccard', 0):.3f}"
            )
            report_lines.append(
                f"- Vocab Ratio: {vocab.get('vocab_ratio', 0):.3f}"
            )
            report_lines.append("")
        
        if "sentiment" in comparison_metrics:
            sent = comparison_metrics["sentiment"]
            report_lines.append("### Sentiment Distribution")
            report_lines.append(
                f"- Synthetic Mean: {sent.get('synthetic_mean', 0):.3f} "
                f"(σ={sent.get('synthetic_std', 0):.3f})"
            )
            report_lines.append(
                f"- Real Mean: {sent.get('real_mean', 0):.3f} "
                f"(σ={sent.get('real_std', 0):.3f})"
            )
            report_lines.append(
                f"- Mean Difference: {sent.get('mean_difference', 0):.3f}"
            )
            report_lines.append("")
        
        if "length" in comparison_metrics:
            length = comparison_metrics["length"]
            report_lines.append("### Length Distribution")
            report_lines.append(
                f"- Synthetic Mean: {length.get('synthetic_mean', 0):.1f} words "
                f"(σ={length.get('synthetic_std', 0):.1f})"
            )
            report_lines.append(
                f"- Real Mean: {length.get('real_mean', 0):.1f} words "
                f"(σ={length.get('real_std', 0):.1f})"
            )
            report_lines.append(
                f"- Mean Difference: {length.get('mean_difference', 0):.1f} words"
            )
            report_lines.append("")
    
    # Trade-offs
    report_lines.append("## Trade-offs\n")
    report_lines.append(
        "- **Quality vs Speed**: Higher guardrail thresholds improve quality but reduce acceptance rate"
    )
    report_lines.append(
        "- **Diversity vs Realism**: Stricter diversity checks may reject realistic reviews"
    )
    report_lines.append(
        "- **Model Selection**: Different models have different acceptance rates and quality profiles"
    )
    report_lines.append("")
    
    report_text = "\n".join(report_lines)
    
    # Save if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)
    
    return report_text

