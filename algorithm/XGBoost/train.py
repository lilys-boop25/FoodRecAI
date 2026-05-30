import argparse
import json
from collections import Counter
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from dataset import LABELS, load_data_splits
from model import build_xgboost_pipeline


def build_label_mapping(y_train):
    classes = [label for label in LABELS if label in set(y_train)]
    if len(classes) < 2:
        raise ValueError(f"Training split must contain at least 2 classes. Found: {classes}")
    return {label: idx for idx, label in enumerate(classes)}


def encode_labels(labels, label_to_id, split_name):
    unknown = sorted(set(labels) - set(label_to_id))
    if unknown:
        raise ValueError(
            f"{split_name} contains labels not seen in train: {unknown}. "
            "XGBoost cannot evaluate unseen classes. Please ensure train has all classes."
        )
    return [label_to_id[label] for label in labels]


def evaluate_split(model, x, y_true, class_names):
    y_pred = model.predict(x)
    labels = list(range(len(class_names)))
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0),
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=labels,
            target_names=class_names,
            zero_division=0,
            output_dict=True,
        ),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    }


def main():
    parser = argparse.ArgumentParser(description="Train TF-IDF + XGBoost for sentiment analysis.")
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Directory containing train.jsonl, valid.jsonl, test.jsonl. Default: data/data_for_sentiment_analysis",
    )
    parser.add_argument("--output-dir", default="outputs/xgboost")
    parser.add_argument("--max-features", type=int, default=50000)
    parser.add_argument("--ngram-max", type=int, default=2)
    parser.add_argument("--min-df", type=int, default=2)
    parser.add_argument("--n-estimators", type=int, default=300)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    x_train, x_valid, x_test, y_train_raw, y_valid_raw, y_test_raw, data_stats = load_data_splits(args.data_dir)

    label_to_id = build_label_mapping(y_train_raw)
    id_to_label = {idx: label for label, idx in label_to_id.items()}
    class_names = [id_to_label[idx] for idx in range(len(id_to_label))]

    y_train = encode_labels(y_train_raw, label_to_id, "valid/test train check")
    y_valid = encode_labels(y_valid_raw, label_to_id, "valid")
    y_test = encode_labels(y_test_raw, label_to_id, "test")

    model = build_xgboost_pipeline(
        num_classes=len(class_names),
        max_features=args.max_features,
        ngram_max=args.ngram_max,
        min_df=args.min_df,
        n_estimators=args.n_estimators,
        learning_rate=args.learning_rate,
        max_depth=args.max_depth,
        random_state=args.random_state,
    )

    model.fit(x_train, y_train)

    valid_metrics = evaluate_split(model, x_valid, y_valid, class_names)
    test_metrics = evaluate_split(model, x_test, y_test, class_names)

    joblib.dump(model, output_dir / "tfidf_xgboost_model.joblib")

    metadata = {
        "model": "TF-IDF + XGBoost",
        "label_to_id": label_to_id,
        "id_to_label": {str(k): v for k, v in id_to_label.items()},
        "class_names": class_names,
        "data_stats": data_stats,
        "train_label_distribution": dict(Counter(y_train_raw)),
        "valid_label_distribution": dict(Counter(y_valid_raw)),
        "test_label_distribution": dict(Counter(y_test_raw)),
        "params": vars(args),
        "valid_metrics": {
            "accuracy": valid_metrics["accuracy"],
            "macro_f1": valid_metrics["macro_f1"],
            "weighted_f1": valid_metrics["weighted_f1"],
        },
        "test_metrics": {
            "accuracy": test_metrics["accuracy"],
            "macro_f1": test_metrics["macro_f1"],
            "weighted_f1": test_metrics["weighted_f1"],
        },
    }

    with open(output_dir / "train_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    with open(output_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump({"valid": valid_metrics, "test": test_metrics}, f, ensure_ascii=False, indent=2)

    pd.DataFrame(test_metrics["confusion_matrix"], index=class_names, columns=class_names).to_csv(
        output_dir / "confusion_matrix.csv", encoding="utf-8-sig"
    )

    print("Training completed.")
    print(f"Model saved to: {output_dir / 'tfidf_xgboost_model.joblib'}")
    print("Validation metrics:")
    print(f"  Accuracy   : {valid_metrics['accuracy']:.4f}")
    print(f"  Macro F1   : {valid_metrics['macro_f1']:.4f}")
    print(f"  Weighted F1: {valid_metrics['weighted_f1']:.4f}")
    print("Test metrics:")
    print(f"  Accuracy   : {test_metrics['accuracy']:.4f}")
    print(f"  Macro F1   : {test_metrics['macro_f1']:.4f}")
    print(f"  Weighted F1: {test_metrics['weighted_f1']:.4f}")


if __name__ == "__main__":
    main()
