import argparse
from pathlib import Path
import sys

import joblib

try:
    from .dataset import load_train_test_split
    from .model import build_model
except ImportError:
    from dataset import load_train_test_split
    from model import build_model


OUTPUT_DIR = Path(__file__).resolve().parent / "result"
DEFAULT_MODEL_PATH = OUTPUT_DIR / "naive_bayes_model.joblib"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def train_model(
    data_path=None,
    model_path=DEFAULT_MODEL_PATH,
    test_size=0.2,
    random_state=42,
    max_features=50000,
    alpha=1.0,
    exclude_rating=10.0,
):
    x_train, x_test, y_train, y_test, stats = load_train_test_split(
        data_path=data_path,
        test_size=test_size,
        random_state=random_state,
        exclude_rating=exclude_rating,
    )

    model = build_model(max_features=max_features, alpha=alpha)
    model.fit(x_train, y_train)

    model_path = Path(model_path)
    model_path.parent.mkdir(exist_ok=True)
    joblib.dump(model, model_path)

    stats.update({
        "model_path": model_path,
        "max_features": max_features,
        "alpha": alpha,
    })
    return model, stats


def main():
    parser = argparse.ArgumentParser(description="Train Naive Bayes sentiment model.")
    parser.add_argument("--data", help="Path to data_clean.jsonl or reviews_clean.jsonl")
    parser.add_argument("--model-out", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--max-features", type=int, default=50000)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--exclude-rating", type=float, default=10.0)
    args = parser.parse_args()

    _, stats = train_model(
        data_path=args.data,
        model_path=args.model_out,
        test_size=args.test_size,
        random_state=args.random_state,
        max_features=args.max_features,
        alpha=args.alpha,
        exclude_rating=args.exclude_rating,
    )

    print("===== TRAIN =====")
    print(f"Data file: {stats['data_path']}")
    print(f"Total used: {stats['total_used']}")
    print(f"Train size: {stats['train_size']}")
    print(f"Test size: {stats['test_size']}")
    print(f"Skipped rating == {stats['exclude_rating']}: {stats['skipped_excluded_rating']}")
    print(f"Skipped invalid rows: {stats['skipped_invalid']}")
    print(f"Saved model: {stats['model_path']}")


if __name__ == "__main__":
    main()
