import json
from pathlib import Path

from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATHS = [
    PROJECT_ROOT / "data" / "data_for_sentiment_analysis" / "data_clean.jsonl",
    PROJECT_ROOT / "data" / "data_for_sentiment_analysis" / "reviews_clean_2.jsonl",
    PROJECT_ROOT / "data" / "raw_data" / "data_clean.jsonl",
    PROJECT_ROOT / "data" / "raw_data" / "reviews_clean_2.jsonl",
]
LABELS = ["negative", "positive"]


def rating_to_label(rating):
    if rating >= 8.0:
        return "positive"
    return "negative"


def resolve_data_path(data_path=None):
    if data_path:
        path = Path(data_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path

    for path in DEFAULT_DATA_PATHS:
        if path.exists():
            return path

    candidates = "\n".join(str(path) for path in DEFAULT_DATA_PATHS)
    raise FileNotFoundError(f"Could not find clean data file. Checked:\n{candidates}")


def load_reviews(data_path=None, exclude_rating=10.0):
    path = resolve_data_path(data_path)
    texts = []
    labels = []
    skipped_excluded_rating = 0
    skipped_invalid = 0

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            try:
                item = json.loads(line)
                rating = float(item["rating"])
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                skipped_invalid += 1
                continue

            if exclude_rating is not None and rating == exclude_rating:
                skipped_excluded_rating += 1
                continue

            title = item.get("title") or ""
            content = item.get("content") or ""
            text = f"{title} {content}".strip()
            if not text:
                skipped_invalid += 1
                continue

            label = item.get("rating_label") or rating_to_label(rating)
            if label not in LABELS:
                skipped_invalid += 1
                continue

            texts.append(text)
            labels.append(label)

    stats = {
        "data_path": path,
        "total_used": len(texts),
        "skipped_excluded_rating": skipped_excluded_rating,
        "skipped_invalid": skipped_invalid,
        "exclude_rating": exclude_rating,
    }
    return texts, labels, stats


def load_train_test_split(data_path=None, test_size=0.2, random_state=42, exclude_rating=10.0):
    texts, labels, stats = load_reviews(data_path, exclude_rating=exclude_rating)
    if not texts:
        raise ValueError("No valid reviews after filtering.")

    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=test_size,
        random_state=random_state,
        stratify=labels,
    )
    stats.update({
        "train_size": len(x_train),
        "test_size": len(x_test),
        "test_ratio": test_size,
        "random_state": random_state,
    })
    return x_train, x_test, y_train, y_test, stats
