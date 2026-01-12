# Why Reviews Get Rejected - Guardrail Explanation

Reviews are rejected if they fail **ANY** of the three quality guardrails. All three must pass for a review to be accepted.

## 1. Diversity Guardrail

**Purpose**: Ensure reviews are diverse and not too similar to each other.

**Fails if**:
- **Vocabulary Overlap** >= 0.3 (30% of words overlap with existing reviews)
- **Semantic Similarity** >= 0.85 (meaning is 85%+ similar to existing reviews)

**Current Thresholds** (from your config):
- `vocab_overlap_threshold: 0.3`
- `semantic_similarity_threshold: 0.85`

**How to fix**: If reviews are too similar, you can:
- Increase thresholds (e.g., `vocab_overlap_threshold: 0.4`, `semantic_similarity_threshold: 0.90`)
- Or make the prompts more varied

## 2. Bias Guardrail

**Purpose**: Ensure sentiment matches the rating and reviews aren't too extreme.

**Fails if**:
- **Sentiment-Rating Mismatch**: Rating doesn't match sentiment (e.g., 5-star but negative sentiment)
- **Z-Score** >= 2.0 (sentiment is too far from the average of accepted reviews)

**Current Thresholds**:
- `z_score_threshold: 2.0`

**How to fix**: If sentiment alignment is too strict:
- Increase `z_score_threshold` to 2.5 or 3.0
- The sentiment alignment logic has some flexibility built in

## 3. Realism Guardrail

**Purpose**: Ensure reviews sound realistic and domain-appropriate.

**Fails if**:
- **Realism Score** < 0.7 (LLM judges it as not realistic enough)

**Current Threshold**:
- `realism_score_threshold: 0.7`

**How to fix**: If reviews are being judged as unrealistic:
- Lower threshold to 0.6 or 0.5
- Improve the generation prompt to be more specific about the domain

## Summary

A review is **ACCEPTED** only if:
- ✅ Diversity: vocab_overlap < 0.3 AND semantic_similarity < 0.85
- ✅ Bias: sentiment aligns with rating AND z_score < 2.0
- ✅ Realism: realism_score >= 0.7

If any guardrail fails, the review is rejected and retried (up to `max_retries: 2` times).

## Recommendations

If you're seeing too many rejections:

1. **Check the rejection reasons** in the console output
2. **Adjust thresholds** in your config file to be less strict
3. **Check the generated reviews** - maybe the LLM is generating low-quality text
4. **Increase max_retries** to give more chances (currently 2)

Example: If diversity is failing often, try:
```yaml
guardrails:
  diversity:
    vocab_overlap_threshold: 0.4  # Increased from 0.3
    semantic_similarity_threshold: 0.90  # Increased from 0.85
```

