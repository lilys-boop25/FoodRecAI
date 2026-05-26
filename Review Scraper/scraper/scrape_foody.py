import requests
import time
import random
from lxml import html
from requests.exceptions import ReadTimeout, ConnectionError

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
}

with open('data/raw_data/restaurant_links.txt', 'r', encoding='utf-8') as f:
    links = [l.strip() for l in f if l.strip()]

session = requests.Session()
session.headers.update(HEADERS)

with open('data/raw_data/restaurants.jsonl', 'a', encoding='utf-8') as out:
    for idx, url in enumerate(links):
        try:
            resp = session.get(url, timeout=(5, 30))
            if resp.status_code != 200:
                print(f"[{idx}] BAD STATUS {resp.status_code}: {url}")
                continue

            tree = html.fromstring(resp.text)
            scripts = tree.xpath("//script/text()")

            script_text = None
            for s in scripts:
                if "var initData =" in s and '"RestaurantID"' in s:
                    script_text = s
                    break

            if not script_text:
                print(f"[{idx}] initData not found: {url}")
                continue

            start = script_text.find("var initData")
            start = script_text.find("{", start)

            brace = 0
            end = start

            for i in range(start, len(script_text)):
                if script_text[i] == "{":
                    brace += 1
                elif script_text[i] == "}":
                    brace -= 1
                    if brace == 0:
                        end = i + 1
                        break

            initData = script_text[start:end]

            out.write(initData + "\n")
            out.flush()

            print(f"[{idx}] OK")

            time.sleep(random.uniform(1.5, 3.0))

        except ReadTimeout:
            print(f"[{idx}] TIMEOUT: {url}")
            continue
        except ConnectionError:
            print(f"[{idx}] CONNECTION ERROR: {url}")
            continue
        except Exception as e:
            print(f"[{idx}] ERROR {url}: {e}")
            continue
