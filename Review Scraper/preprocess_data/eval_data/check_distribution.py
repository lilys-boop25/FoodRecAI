import json
import pandas as pd
import matplotlib.pyplot as plt

ratings = []

with open("data/raw_data/reviews_with_restaurant_id.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data["rating"] is None:
            data["rating"] = "0.0"
        try:
            ratings.append(float(data["rating"]))
        except ValueError:            
            print(f"Warning: Could not convert rating '{data['rating']}' to float. Skipping this entry.")
            continue

df = pd.DataFrame({"rating": ratings})

print(df["rating"].describe())
print(df["rating"].value_counts().sort_index())

plt.hist(df["rating"], bins=20)
plt.xlabel("Rating")
plt.ylabel("Number of reviews")
plt.title("Rating Distribution")
plt.show()