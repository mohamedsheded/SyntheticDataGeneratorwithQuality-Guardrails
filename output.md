# Output Documentation

This document captures the terminal output from running the review generation and comparison commands.

## Review Generation

### Command
```bash
python -m cli.main generate --config configs/examples/saas_pm_tool.yaml --target-size 5
```

### Execution Summary
- **Domain**: SaaS Project Management Tool
- **Models**: `groq:llama-3.3-70b-versatile`, `openai:gpt-4o-mini`
- **Target Size**: 5 reviews

### Generation Results

#### Accepted Reviews
1. **Review 1/5** - Rating: 5★, Model: `openai:gpt-4o-mini` ✓
2. **Review 2/5** - Rating: 3★, Model: `groq:llama-3.3-70b-versatile` ✓
3. **Review 3/5** - Rating: 5★, Model: `groq:llama-3.3-70b-versatile` ✓
4. **Review 4/5** - Rating: 5★, Model: `groq:llama-3.3-70b-versatile` ✓
5. **Review 5/5** - Rating: 4★, Model: `groq:llama-3.3-70b-versatile` ✓

#### Rejected Reviews
- **1 review rejected** - Rating: 5★, Retries: 2
  - **Reason**: Diversity FAILED
    - `vocab_overlap=0.21` (threshold: 0.30)
    - `semantic_sim=0.85` (threshold: 0.85)

### Output Files Generated
- `output/reviews.json` - 5 accepted reviews
- `output/rejected_reviews.json` - 1 rejected review
- `output/metrics.json` - Generation metrics
- `output/report.md` - Quality report

### Final Statistics
```
============================================================
Generation complete!
============================================================
✓ Accepted: 5/5
✗ Rejected: 1

Acceptance Rate: 83.3%

Rejection Reasons:
  - Diversity FAILED: 1

💡 Tip: Check GUARDRAILS_EXPLAINED.md for how to adjust thresholds
============================================================
```

## Review Comparison

### Command
```bash
python -m cli.main compare --synthetic ./output/reviews.json --real ./data/real_reviews.json
```

### Comparison Results
- **Synthetic Reviews**: 5 reviews
- **Real Reviews**: Compared against `./data/real_reviews.json`

### Comparison Summary
- **Embedding Similarity**: 0.266
- **Vocabulary Jaccard**: 0.043

### Detailed Metrics
The full comparison results are saved in `output/comparison.json` and include:
- **Embedding Similarity**: Mean similarity between synthetic and real reviews
- **Vocabulary Overlap**: Jaccard similarity of vocabulary sets
- **Sentiment Analysis**: Comparison of sentiment distributions
- **Length Statistics**: Comparison of review lengths

## Notes

- The generation process successfully created 5 reviews with an 83.3% acceptance rate
- One review was rejected due to diversity guardrail failure (vocabulary overlap and semantic similarity thresholds)
- The comparison shows relatively low similarity between synthetic and real reviews (0.266 embedding similarity, 0.043 vocabulary Jaccard), which may indicate the synthetic reviews have different characteristics than the real ones
- For more details on adjusting guardrail thresholds, see `GUARDRAILS_EXPLAINED.md`

