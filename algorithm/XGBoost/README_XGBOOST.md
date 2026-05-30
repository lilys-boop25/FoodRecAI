# TF-IDF + XGBoost sentiment pipeline

This version assumes the dataset has already been split into:

```text
data/data_for_sentiment_analysis/train.jsonl
data/data_for_sentiment_analysis/valid.jsonl
data/data_for_sentiment_analysis/test.jsonl
```

Each JSONL record should contain at least:

- `title` and/or `content`
- `rating_label`, or `rating` so the loader can infer a label

Run training:

```bash
python algorithm/xgboost/train.py \
  --data-dir data/data_for_sentiment_analysis \
  --output-dir outputs/xgboost
```

Run evaluation:

```bash
python algorithm/xgboost/evaluate.py \
  --model outputs/xgboost/tfidf_xgboost_model.joblib \
  --data-dir data/data_for_sentiment_analysis \
  --split test \
  --output-dir outputs/xgboost
```

Outputs include:

- `tfidf_xgboost_model.joblib`
- `train_metadata.json`
- `metrics.json`
- `test_metrics.json`
- `test_classification_report.txt`
- `test_confusion_matrix.csv`
- `test_predictions.csv`
