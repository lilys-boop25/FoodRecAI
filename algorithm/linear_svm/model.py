# model.py
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

def build_svm_pipeline(max_features=5000, c_param=1.0, random_state=42):
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=max_features)),
        ('svm', LinearSVC(C=c_param, random_state=random_state, dual=False, max_iter=3000))
    ])
    return pipeline
