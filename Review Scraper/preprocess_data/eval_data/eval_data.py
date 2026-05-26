import json
from pathlib import Path
import re

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_FILE = PROJECT_ROOT / "data" / "raw_data" / "reviews_with_restaurant_id.jsonl"
OUTPUT_FILE = PROJECT_ROOT / "data" / "data_for_sentiment_analysis" / "reviews_clean_2.jsonl"
RESULT_DIR = Path(__file__).resolve().parent / "result_eval"
RESULT_DIR.mkdir(exist_ok=True)


def normalize_text(text):
    if text is None:
        return ""

    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\u00C0-\u1EF9]", "", text)
    return text.strip()


def count_words(text):
    text = normalize_text(text)
    return len(text.split()) if text else 0


# label rating: 8.0-10.0 = positive, 6.0-7.9 = neutral, <6.0 = negative
def rating_to_label(rating):
    if rating >= 8.0:
        return "positive"
    if rating >= 6.0:
        return "neutral"
    return "negative"


positive_words = [
    "ngon", "tốt", "ổn", "ok", "okie", "tuyệt", "thích", "ưng",
    "recommend", "rẻ", "hợp lý", "sạch", "đẹp", "nhiệt tình",
    "chu đáo", "thân thiện", "quay lại", "must try", "đáng tiền",
    "rất ngon", "xuất sắc", "hài lòng",
]

negative_words = [
    "dở", "tệ", "chán", "đắt", "bẩn", "lâu", "chậm", "không ngon",
    "không tốt", "thất vọng", "khó chịu", "kém", "không quay lại",
    "phục vụ kém", "quá tệ", "nhạt", "nguội", "mặn", "ít", "không đáng",
]


def keyword_sentiment(text):
    text_norm = normalize_text(text)

    pos_count = sum(1 for word in positive_words if word in text_norm)
    neg_count = sum(1 for word in negative_words if word in text_norm)

    if pos_count > neg_count:
        return "positive"
    if neg_count > pos_count:
        return "negative"
    return "unknown"


rows = []
bad_rating_rows = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line_num, line in enumerate(f, start=1):
        line = line.strip()

        if not line:
            continue

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        try:
            rating = float(data.get("rating"))
        except (ValueError, TypeError):
            bad_rating_rows.append({
                "line": line_num,
                "rating": data.get("rating"),
                "data": data,
            })
            continue

        title = data.get("title", "")
        content = data.get("content", "")
        text = f"{title} {content}".strip()

        rows.append({
            "line": line_num,
            "restaurant_id": data.get("restaurant_id", ""),
            "rating": rating,
            "title": title,
            "content": content,
            "text": text,
            "text_norm": normalize_text(text),
            "word_count": count_words(text),
            "rating_label": rating_to_label(rating),
            "keyword_label": keyword_sentiment(text),
        })


df = pd.DataFrame(rows)

print("\n===== TONG QUAN =====")
print("Valid reviews:", len(df))
print("Bad rating rows:", len(bad_rating_rows))

print("\n===== RATING LABEL DISTRIBUTION =====")
print(df["rating_label"].value_counts())
print(df["rating_label"].value_counts(normalize=True))

print("\n===== 1. DUPLICATES =====")
duplicate_mask = df.duplicated(subset=["text_norm"], keep=False)
duplicates = df[duplicate_mask]
print("Duplicate reviews:", len(duplicates))
print("Duplicate ratio:", round(len(duplicates) / len(df) * 100, 2), "%")
duplicates.to_csv(RESULT_DIR / "duplicate_reviews.csv", index=False, encoding="utf-8-sig")

print("\n===== 2. SPAM / AD CANDIDATES =====")
ad_keywords = [
    "must try", "recommend", "cực ngon", "siêu ngon", "rất ngon",
    "ngon phết", "chuẩn âu", "giá rẻ", "giá hợp lý",
    "sẽ tới nữa", "sẽ quay lại", "i like it", "đáng thử", "nên thử",
]

df["has_ad_keyword"] = df["text"].apply(
    lambda text: any(keyword in normalize_text(text) for keyword in ad_keywords)
)

text_counts = df["text_norm"].value_counts()
df["text_repeat_count"] = df["text_norm"].map(text_counts)

spam_mask = (
    ((df["rating"] >= 9.0) & (df["has_ad_keyword"])) |
    (df["text_repeat_count"] >= 3) |
    ((df["rating"] >= 9.0) & (df["word_count"] <= 5))
)
spam_candidates = df[spam_mask].copy()

print("Spam/ad candidates:", len(spam_candidates))
print("Spam/ad ratio:", round(len(spam_candidates) / len(df) * 100, 2), "%")
spam_candidates.to_csv(RESULT_DIR / "spam_candidates.csv", index=False, encoding="utf-8-sig")

print("\n===== 3. SHORT REVIEWS =====")
short_mask = df["word_count"] <= 3
short_reviews = df[short_mask]
print("Short reviews <= 3 words:", len(short_reviews))
print("Short review ratio:", round(len(short_reviews) / len(df) * 100, 2), "%")
short_reviews.to_csv(RESULT_DIR / "short_reviews.csv", index=False, encoding="utf-8-sig")

print("\n===== 4. RATING-CONTENT MISMATCH =====")
mismatch_mask = (
    ((df["rating"] >= 8.0) & (df["keyword_label"] == "negative")) |
    ((df["rating"] < 6.0) & (df["rating"] >= 5.0) & (df["keyword_label"] == "positive"))
)
mismatch_df = df[mismatch_mask].copy()

print("Mismatch reviews:", len(mismatch_df))
print("Mismatch ratio:", round(len(mismatch_df) / len(df) * 100, 2), "%")
mismatch_df.to_csv(RESULT_DIR / "rating_content_mismatch.csv", index=False, encoding="utf-8-sig")

print("\n===== EXPORT CLEAN DATA =====")
invalid_rating_mask = ~df["rating"].between(0, 10)
remove_mask = duplicate_mask | spam_mask | short_mask | mismatch_mask | invalid_rating_mask
df_clean = df[~remove_mask].copy()

df_clean[["restaurant_id", "rating", "title", "content", "rating_label"]].to_json(
    OUTPUT_FILE,
    orient="records",
    lines=True,
    force_ascii=False,
)

print("Original:", len(df))
print("Clean:", len(df_clean))
print("Removed:", len(df) - len(df_clean))
print("Removed duplicate:", int(duplicate_mask.sum()))
print("Removed spam/ad:", int(spam_mask.sum()))
print("Removed short:", int(short_mask.sum()))
print("Removed mismatch:", int(mismatch_mask.sum()))
print("Removed invalid rating:", int(invalid_rating_mask.sum()))

print("\nDone.")
