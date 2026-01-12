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



```bash
python -m cli.main compare --synthetic output/reviews.json --real data/real_reviews.json
```

