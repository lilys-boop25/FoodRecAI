import json

input_file = "data/raw_data/reviews_2.jsonl"
output_file = "data/raw_data/reviews_with_restaurant_id.jsonl"

with open(input_file, "r", encoding="utf-8") as fin, \
     open(output_file, "a", encoding="utf-8") as fout:

    for line in fin:
        line = line.strip()

        if not line:
            continue

        data = json.loads(line)

        restaurant_id = data.get("restaurant_id")
        reviews = data.get("reviews", [])

        for review in reviews:
            new_review = {
                "restaurant_id": restaurant_id,
                "rating": review.get("rating"),
                "title": review.get("title"),
                "content": review.get("content"),
                "date": review.get("date")
            }

            fout.write(json.dumps(new_review, ensure_ascii=False) + "\n")

print("Done! Đã ghi file:", output_file)