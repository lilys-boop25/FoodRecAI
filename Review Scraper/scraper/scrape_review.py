import os

from playwright.sync_api import sync_playwright, TimeoutError
import json
import time

INPUT_LINKS = "D:/Hust/Năm ba/DS/prj/data/raw_data/link/foody_links_more_than_0_reviews.txt"
OUTPUT_JSONL = "D:/Hust/Năm ba/DS/prj/data/raw_data/reviews_2.jsonl"
FAILED_LINKS = "D:/Hust/Năm ba/DS/prj/data/raw_data/link/error/failed_links.txt"


def scrape_reviews_from_page(page, url):
    page.goto(url, timeout=60000)

    # Scroll to first review
    page.evaluate("""
        () => {
            document.querySelector('li.review-item')
                ?.scrollIntoView({ block: 'start' });
        }
    """)

    last_count = 0

    while True:
        reviews = page.query_selector_all("li.review-item")
        current_count = len(reviews)

        if current_count <= last_count:
            break

        last_count = current_count

        btn = page.query_selector("div.pn-loadmore a.fd-btn-more:not([href])")
        if not btn:
            break

        page.evaluate("(el) => el.scrollIntoView({block: 'center'})", btn)
        page.evaluate("(el) => el.click()", btn)

        time.sleep(0.5)

    results = []

    for item in page.query_selector_all("li.review-item"):
        title_el = item.query_selector("a.rd-title")
        content_el = item.query_selector("div.rd-des span")
        time_el = item.query_selector("span.ru-time")
        rating_el = item.query_selector("div.review-points span")

        results.append({
            "rating": rating_el.inner_text().strip() if rating_el else None,
            "title": title_el.inner_text().strip() if title_el else None,
            "content": content_el.inner_text().strip() if content_el else None,
            "date": time_el.inner_text().strip() if time_el else None
        })

    return results


def get_restaurant_id(url):
    return url.rstrip("/").split("/")[-1]

def load_done_restaurant_ids(result_file):
    done_ids = set()

    if not os.path.exists(result_file):
        return done_ids

    with open(result_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)
                restaurant_id = data.get("restaurant_id")

                if restaurant_id:
                    done_ids.add(restaurant_id)

            except json.JSONDecodeError:
                print("Bỏ qua 1 dòng JSON lỗi:", line[:100])

    return done_ids

def main():

    done_ids = load_done_restaurant_ids("D:/Hust/Năm ba/DS/prj/data/raw_data/reviews.jsonl")
    done_ids.update(load_done_restaurant_ids(OUTPUT_JSONL))

    with open(INPUT_LINKS, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    with sync_playwright() as p, \
         open(OUTPUT_JSONL, "a", encoding="utf-8") as out, \
         open(FAILED_LINKS, "a", encoding="utf-8") as failed:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for idx, url in enumerate(links, 1):
            # if idx not in [2353, 2354]:
            #     continue
            if get_restaurant_id(url) in done_ids:
                print(f"\n[{idx}/{len(links)}] Skipping (already done): {url}")
                continue
            print(f"\n[{idx}/{len(links)}] Scraping: {url}")

            try:
                reviews = scrape_reviews_from_page(page, url)

                if len(reviews) == 0:
                    failed.write(url + "\n")
                    continue

                record = {
                    "restaurant_id": get_restaurant_id(url),
                    "reviews": reviews
                }

                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                out.flush()

                print(f"✅ Saved {len(reviews)} reviews")

            except TimeoutError:
                print("⛔ Timeout")
                failed.write(url + "\n")

            except Exception as e:
                print(f"⛔ Error: {e}")
                failed.write(url + "\n")

            time.sleep(0.5)

        browser.close()

    print("\n✅ DONE")


if __name__ == "__main__":
    main()
