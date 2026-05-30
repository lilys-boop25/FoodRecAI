import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from dataset import load_reviews


def load_metadata(model_path):
    metadata_path = Path(model_path).parent / "train_metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


def encode_labels(labels, label_to_id, split_name):
    unknown = sorted(set(labels) - set(label_to_id))
    if unknown:
        raise ValueError(f"{split_name} contains labels not seen during training: {unknown}")
    return [label_to_id[label] for label in labels]


def main():
    parser = argparse.ArgumentParser(description="Evaluate saved TF-IDF + XGBoost model.")
    parser.add_argument("--model", default="outputs/xgboost/tfidf_xgboost_model.joblib")
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--split", default="test", choices=["train", "valid", "test"])
    parser.add_argument("--output-dir", default="outputs/xgboost")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model = joblib.load(args.model)
    metadata = load_metadata(args.model)
    label_to_id = metadata["label_to_id"]
    class_names = metadata["class_names"]

    x, y_raw, stats = load_reviews(args.split, args.data_dir)
    y_true = encode_labels(y_raw, label_to_id, args.split)
    y_pred = model.predict(x)

    labels = list(range(len(class_names)))
    report_text = classification_report(
        y_true, y_pred, labels=labels, target_names=class_names, zero_division=0
    )
    report_dict = classification_report(
        y_true, y_pred, labels=labels, target_names=class_names, zero_division=0, output_dict=True
    )
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    metrics = {
        "split": args.split,
        "data_stats": stats,
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0),
        "classification_report": report_dict,
        "confusion_matrix": cm.tolist(),
    }

    with open(output_dir / f"{args.split}_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    with open(output_dir / f"{args.split}_classification_report.txt", "w", encoding="utf-8") as f:
        f.write(report_text)

    pd.DataFrame(cm, index=class_names, columns=class_names).to_csv(
        output_dir / f"{args.split}_confusion_matrix.csv", encoding="utf-8-sig"
    )

    pd.DataFrame(
        {
            "text": x,
            "true_label": y_raw,
            "pred_label": [class_names[int(i)] for i in y_pred],
        }
    ).to_csv(output_dir / f"{args.split}_predictions.csv", index=False, encoding="utf-8-sig")

    print(report_text)
    print(f"Saved evaluation outputs to: {output_dir}")


if __name__ == "__main__":
    main()
