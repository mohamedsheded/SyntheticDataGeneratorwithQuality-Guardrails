"""CLI interface for review generation"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    # Load .env from project root
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
except ImportError:
    pass

from src.config.loader import load_config
from src.graph.review_graph import create_review_graph
from src.nodes.comparison import compare_real_vs_synthetic
from src.metrics.reporting import generate_report
from src.state.global_state import GlobalState


def generate_command(args):
    """Generate synthetic reviews"""
    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)
    
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
        "config": config,
        "target_size": args.target_size,
        "feedback": None,
    }
    
    # Create and run graph
    print(f"Starting generation of {args.target_size} reviews...")
    print(f"Domain: {config.domain}")
    print(f"Models: {[f'{m.provider}:{m.model}' for m in config.models]}")
    print()
    
    graph = create_review_graph()
    
    try:
        # Increase recursion limit to handle retries and multiple attempts
        # Each review attempt can take up to (max_retries + 1) iterations
        max_iterations = args.target_size * (config.guardrails.max_retries + 1) * 5  # 5x safety factor
        graph_config = {"recursion_limit": max(1000, max_iterations)}
        final_state = graph.invoke(initial_state, config=graph_config)
    except KeyboardInterrupt:
        print("\nGeneration interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during generation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Save results
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save accepted reviews
    reviews_path = output_dir / "reviews.json"
    with open(reviews_path, "w", encoding="utf-8") as f:
        json.dump(final_state["accepted_reviews"], f, indent=2, default=str)
    print(f"Saved {len(final_state['accepted_reviews'])} accepted reviews to {reviews_path}")
    
    # Save rejected reviews
    if final_state["rejected_reviews"]:
        rejected_path = output_dir / "rejected_reviews.json"
        with open(rejected_path, "w", encoding="utf-8") as f:
            json.dump(final_state["rejected_reviews"], f, indent=2, default=str)
        print(f"Saved {len(final_state['rejected_reviews'])} rejected reviews to {rejected_path}")
    
    # Save metrics
    metrics_path = output_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(final_state["metrics_per_model"], f, indent=2, default=str)
    print(f"Saved metrics to {metrics_path}")
    
    # Generate and save report
    report_path = output_dir / "report.md"
    generate_report(
        accepted_reviews=final_state["accepted_reviews"],
        rejected_reviews=final_state["rejected_reviews"],
        metrics_per_model=final_state["metrics_per_model"],
        config=config,
        output_path=report_path,
    )
    print(f"Saved quality report to {report_path}")
    
    print("\n" + "="*60)
    print("Generation complete!")
    print("="*60)
    print(f"✓ Accepted: {len(final_state['accepted_reviews'])}/{args.target_size}")
    print(f"✗ Rejected: {len(final_state['rejected_reviews'])}")
    
    if final_state['rejected_reviews']:
        total_attempts = len(final_state['accepted_reviews']) + len(final_state['rejected_reviews'])
        acceptance_rate = len(final_state['accepted_reviews']) / total_attempts * 100
        print(f"\nAcceptance Rate: {acceptance_rate:.1f}%")
        
        # Show rejection reasons breakdown
        print("\nRejection Reasons:")
        rejection_reasons = {}
        for review in final_state['rejected_reviews']:
            reason = review.get('rejection_reason', 'Unknown')
            # Extract main reason (first part before semicolon)
            main_reason = reason.split(';')[0].split(':')[0] if ':' in reason else 'Unknown'
            rejection_reasons[main_reason] = rejection_reasons.get(main_reason, 0) + 1
        
        for reason, count in sorted(rejection_reasons.items(), key=lambda x: -x[1]):
            print(f"  - {reason}: {count}")
        
        print("\n💡 Tip: Check GUARDRAILS_EXPLAINED.md for how to adjust thresholds")
    print("="*60)


def compare_command(args):
    """Compare synthetic reviews with real reviews"""
    # Load synthetic reviews
    synthetic_path = Path(args.synthetic)
    if not synthetic_path.exists():
        print(f"Error: Synthetic reviews file not found: {synthetic_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(synthetic_path, "r", encoding="utf-8") as f:
        synthetic_reviews = json.load(f)
    
    # Compare
    print(f"Comparing {len(synthetic_reviews)} synthetic reviews with real reviews...")
    comparison_metrics = compare_real_vs_synthetic(synthetic_reviews, args.real)
    
    if "error" in comparison_metrics:
        print(f"Error: {comparison_metrics['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Save comparison results
    output_path = Path(args.output) if args.output else Path(args.synthetic).parent / "comparison.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison_metrics, f, indent=2, default=str)
    
    print(f"Comparison results saved to {output_path}")
    
    # Print summary
    print("\nComparison Summary:")
    if "embedding" in comparison_metrics:
        emb = comparison_metrics["embedding"]
        print(f"  Embedding Similarity: {emb.get('mean_embedding_similarity', 0):.3f}")
    if "vocabulary" in comparison_metrics:
        vocab = comparison_metrics["vocabulary"]
        print(f"  Vocabulary Jaccard: {vocab.get('vocab_jaccard', 0):.3f}")


def report_command(args):
    """Generate quality report"""
    # Load data
    metrics_path = Path(args.metrics)
    if not metrics_path.exists():
        print(f"Error: Metrics file not found: {metrics_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_per_model = json.load(f)
    
    # Load reviews if provided
    accepted_reviews = []
    rejected_reviews = []
    
    if args.reviews:
        reviews_path = Path(args.reviews)
        if reviews_path.exists():
            with open(reviews_path, "r", encoding="utf-8") as f:
                accepted_reviews = json.load(f)
    
    if args.rejected:
        rejected_path = Path(args.rejected)
        if rejected_path.exists():
            with open(rejected_path, "r", encoding="utf-8") as f:
                rejected_reviews = json.load(f)
    
    # Load comparison if provided
    comparison_metrics = None
    if args.comparison:
        comparison_path = Path(args.comparison)
        if comparison_path.exists():
            with open(comparison_path, "r", encoding="utf-8") as f:
                comparison_metrics = json.load(f)
    
    # Generate report
    output_path = Path(args.output) if args.output else metrics_path.parent / "report.md"
    generate_report(
        accepted_reviews=accepted_reviews,
        rejected_reviews=rejected_reviews,
        metrics_per_model=metrics_per_model,
        comparison_metrics=comparison_metrics,
        output_path=output_path,
    )
    
    print(f"Report generated: {output_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Synthetic Review Generator with Quality Guardrails"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate synthetic reviews")
    gen_parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to configuration file (YAML or JSON)",
    )
    gen_parser.add_argument(
        "--target-size",
        type=int,
        default=300,
        help="Target number of accepted reviews (default: 300)",
    )
    gen_parser.add_argument(
        "--output-dir",
        type=str,
        default="./output",
        help="Output directory (default: ./output)",
    )
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare synthetic vs real reviews")
    compare_parser.add_argument(
        "--synthetic",
        type=str,
        required=True,
        help="Path to synthetic reviews JSON file",
    )
    compare_parser.add_argument(
        "--real",
        type=str,
        required=True,
        help="Path to real reviews file (JSON or CSV)",
    )
    compare_parser.add_argument(
        "--output",
        type=str,
        help="Output path for comparison results (default: same dir as synthetic)",
    )
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate quality report")
    report_parser.add_argument(
        "--metrics",
        type=str,
        required=True,
        help="Path to metrics JSON file",
    )
    report_parser.add_argument(
        "--reviews",
        type=str,
        help="Path to accepted reviews JSON file",
    )
    report_parser.add_argument(
        "--rejected",
        type=str,
        help="Path to rejected reviews JSON file",
    )
    report_parser.add_argument(
        "--comparison",
        type=str,
        help="Path to comparison metrics JSON file",
    )
    report_parser.add_argument(
        "--output",
        type=str,
        help="Output path for report (default: same dir as metrics)",
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "generate":
        generate_command(args)
    elif args.command == "compare":
        compare_command(args)
    elif args.command == "report":
        report_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

