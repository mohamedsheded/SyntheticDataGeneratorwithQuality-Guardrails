# Real Reviews Data

This directory should contain your real reviews dataset for comparison with synthetic reviews.

## Supported Formats

### JSON Format

The file can be either:

1. **List of reviews** (recommended):
```json
[
  {
    "text": "Review text here...",
    "rating": 4
  },
  {
    "text": "Another review...",
    "rating": 5
  }
]
```

2. **Object with reviews key**:
```json
{
  "reviews": [
    {
      "text": "Review text here...",
      "rating": 4
    }
  ]
}
```

**Note**: The comparison function looks for review text in either:
- `text` field (preferred)
- `review` field (fallback)

### CSV Format

A CSV file with at least one column containing review text. The comparison function will look for:
- A column named `text` or `review`
- Or the first text-like column

Example CSV:
```csv
text,rating,author
"This is a great product!",5,John Doe
"Not bad, but could be better",3,Jane Smith
```

## Where to Get Real Reviews

You can obtain real reviews from:

1. **Public Datasets**:
   - Amazon Product Reviews datasets
   - Yelp Open Dataset
   - Google Play Store reviews
   - App Store reviews (if available)

2. **Your Own Data**:
   - Export reviews from your own platform/database
   - Scrape reviews (ensure compliance with terms of service)
   - Use reviews from your product/service

3. **Data Sources**:
   - Kaggle datasets
   - UCI Machine Learning Repository
   - Hugging Face Datasets

## Example Usage

Once you have your real reviews file:

```bash
python -m cli.main compare --synthetic output/reviews.json --real data/real_reviews.json
```

