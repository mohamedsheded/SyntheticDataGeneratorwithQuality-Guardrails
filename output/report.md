# Synthetic Review Generation Quality Report

## Summary

- **Total Accepted Reviews**: 15
- **Total Rejected Reviews**: 17
- **Overall Acceptance Rate**: 46.88%
- **Average Retries**: 2.69

## Guardrail Thresholds

### Diversity
- Vocabulary Overlap Threshold: 0.6
- Semantic Similarity Threshold: 0.95

### Bias
- Z-Score Threshold: 4.0

### Realism
- Realism Score Threshold: 0.5
- Max Retries: 5

## Model Comparison

| Model | Accepted | Rejected | Acceptance Rate | Avg Retries | Avg Gen Time (s) |
|-------|----------|----------|-----------------|-------------|------------------|
| openai:gpt-4o-mini | 4 | 8 | 33.33% | 3.42 | 2.706 |
| openrouter:anthropic/claude-3.7-sonnet | 11 | 9 | 55.00% | 2.25 | 4.560 |

## Quality Statistics

### openai:gpt-4o-mini

- **Diversity (Semantic Similarity)**: μ=0.599, σ=0.361, range=[0.000, 0.913]
- **Bias (Z-Score)**: μ=0.578, σ=0.497, range=[0.000, 1.259]
- **Realism Score**: μ=0.863, σ=0.022, range=[0.850, 0.900]

### openrouter:anthropic/claude-3.7-sonnet

- **Diversity (Semantic Similarity)**: μ=0.774, σ=0.152, range=[0.327, 0.911]
- **Bias (Z-Score)**: μ=1.280, σ=1.186, range=[0.022, 3.768]
- **Realism Score**: μ=0.859, σ=0.019, range=[0.850, 0.900]

## Rating Distribution

| Rating | Count | Percentage |
|--------|-------|------------|
| 4★ | 5 | 33.33% |
| 5★ | 10 | 66.67% |

## Failure Modes

| Reason | Count |
|--------|-------|
| Bias FAILED: sentiment_aligned=False, sentiment_compound=0.59, z_score=0.00 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=False, sentiment_compound=0.89, z_score=0.00 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=False, sentiment_compound=-0.57, z_score=1.50 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=False, sentiment_compound=0.78, z_score=8.23 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=False, sentiment_compound=-0.52, z_score=67.47 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=False, sentiment_compound=0.20, z_score=23.43 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=False, sentiment_compound=0.54, z_score=12.75 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=True, sentiment_compound=-0.83, z_score=62.44 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=False, sentiment_compound=0.69, z_score=9.33 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=True, sentiment_compound=-0.86, z_score=63.47 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=False, sentiment_compound=0.26, z_score=21.96 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=False, sentiment_compound=0.83, z_score=3.59 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=True, sentiment_compound=-0.74, z_score=53.92 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=False, sentiment_compound=0.39, z_score=18.34 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=True, sentiment_compound=-0.87, z_score=63.44 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=False, sentiment_compound=0.82, z_score=4.22 (threshold: 4.00) | 1 |
| Bias FAILED: sentiment_aligned=False, sentiment_compound=0.56, z_score=12.92 (threshold: 4.00) | 1 |

## Trade-offs

- **Quality vs Speed**: Higher guardrail thresholds improve quality but reduce acceptance rate
- **Diversity vs Realism**: Stricter diversity checks may reject realistic reviews
- **Model Selection**: Different models have different acceptance rates and quality profiles
