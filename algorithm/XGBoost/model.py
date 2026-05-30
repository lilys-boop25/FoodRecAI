from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier


def build_xgboost_pipeline(
    num_classes,
    max_features=50000,
    ngram_max=2,
    min_df=2,
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.9,
    colsample_bytree=0.9,
    random_state=42,
):
    if num_classes < 2:
        raise ValueError("XGBoost needs at least 2 classes in the training split.")

    objective = "binary:logistic" if num_classes == 2 else "multi:softprob"
    eval_metric = "logloss" if num_classes == 2 else "mlogloss"

    xgb_params = {
        "objective": objective,
        "eval_metric": eval_metric,
        "n_estimators": n_estimators,
        "learning_rate": learning_rate,
        "max_depth": max_depth,
        "subsample": subsample,
        "colsample_bytree": colsample_bytree,
        "tree_method": "hist",
        "random_state": random_state,
        "n_jobs": -1,
    }
    if num_classes > 2:
        xgb_params["num_class"] = num_classes

    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents=None,
                    analyzer="word",
                    ngram_range=(1, ngram_max),
                    max_features=max_features,
                    min_df=min_df,
                ),
            ),
            ("classifier", XGBClassifier(**xgb_params)),
        ]
    )
