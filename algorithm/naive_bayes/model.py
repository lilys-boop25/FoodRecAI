from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


def build_model(max_features=50000, ngram_range=(1, 2), alpha=1.0):
    return Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                max_features=max_features,
                ngram_range=ngram_range,
                lowercase=True,
                strip_accents=None,
            ),
        ),
        ("clf", MultinomialNB(alpha=alpha)),
    ])
