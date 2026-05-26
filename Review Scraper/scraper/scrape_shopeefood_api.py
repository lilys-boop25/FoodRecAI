from playwright.sync_api import sync_playwright
import json
import time

INPUT_FILE = "data/raw_data/restaurants.jsonl"
OUTPUT_FILE = "data/raw_data/menus.jsonl"
FAILED_FILE = "dan/failed_restaurants.txt"

BASE_URL = "https://shopeefood.vn/"


def fetch_menu_for_url(shop_url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        menu_data = None

        def handle_response(response):
            nonlocal menu_data
            if "get_delivery_dishes" in response.url and response.status == 200:
                try:
                    menu_data = response.json()
                except:
                    pass

        page.on("response", handle_response)

        page.goto(shop_url, timeout=60000)
        page.wait_for_timeout(8000)

        browser.close()

        if not menu_data:
            raise RuntimeError("Menu API not captured")

        return menu_data


def parse_menu(menu_data: dict):
    menu = []

    for group in menu_data["reply"]["menu_infos"]:
        category = group.get("dish_type_name", "Unknown")

        for dish in group.get("dishes", []):
            menu.append({
                "category": category,
                "dish_id": dish.get("id"),
                "name": dish.get("name"),
                "description": dish.get("description"),
                "price": dish.get("price", {}).get("value"),
                "price_text": dish.get("price", {}).get("text"),
                "is_available": dish.get("is_available"),
                "image_url": dish.get("photos", [{}])[-1].get("value")
            })

    return menu


def extract_restaurant_id(restaurant_url: str) -> str:
    return restaurant_url.rstrip("/").split("/")[-1]


if __name__ == "__main__":

    success = 0
    failed = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as fin, \
         open(OUTPUT_FILE, "a", encoding="utf-8") as fout, \
         open(FAILED_FILE, "a", encoding="utf-8") as ffail:

        for idx, line in enumerate(fin, 1):
            if idx < 1341:
                continue
            
            try:
                record = json.loads(line)

                restaurant_url = record.get("RestaurantUrl")
                if not restaurant_url:
                    raise ValueError("Missing RestaurantUrl")

                shop_url = BASE_URL + restaurant_url
                restaurant_id = extract_restaurant_id(restaurant_url)

                print(f"[{idx}] Fetching: {restaurant_id}")

                menu_data = fetch_menu_for_url(shop_url)
                menu = parse_menu(menu_data)

                fout.write(json.dumps({
                    "restaurant_id": restaurant_id,
                    "menu": menu
                }, ensure_ascii=False) + "\n")

                fout.flush()

                print(f"  ✅ {len(menu)} items")
                success += 1

                time.sleep(2)

            except Exception as e:
                print(f"  ❌ Error: {e}")
                ffail.write(f"{restaurant_url if 'restaurant_url' in locals() else 'UNKNOWN'}\n")
                ffail.flush()
                failed += 1

    print("\nDONE")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
