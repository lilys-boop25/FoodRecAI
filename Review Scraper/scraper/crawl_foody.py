import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9",
    "Referer": "https://www.foody.vn/",
    "Origin": "https://www.foody.vn",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
    "Cookie": "bc-jcb=1; flg=vn; __ondemand_sessionid=a14o4gr35vj0lhnawlh12f25; floc=218; gcat=food; _ga=GA1.2.1159984972.1766564630; _gid=GA1.2.967712488.1766564630; fbm_395614663835338=base_domain=.foody.vn; _fbp=fb.1.1766564988830.810075820636650041; __utmc=257500956; ID_FOODY.AUTH=FCA3061086CE38BE923DD599DBC3211B5E4E4524C12A3341241A50AC9A04B8AEDA515A5749855F7E66902DCE0FD632388ED1832D61AFAF8B1319F8C730CF98C7D65BBB4A082CF275C108EBCC4BD62EFAA36147793EB5253343B11D20B3D2916C19CFEA7382AA7EEFD6F89CD626B8B221D5FC8BDD38ECB2E453C8A39C8687C2C165C1725DF237E248DC454C579E5494C0DFB160C76F5ABDDF4E37E9B853050D108B293974ACA69DB9FD986BB9C95FCEFE91B92813D4993B78BCF676941AEA0510745A0BB8FD656838B79A2D1096C153D63170431CC9B81F8753D4C9A0C1E99608B6A5201B7FC23C3B5EF92DF5F264976EE5E70574C6B5398A0D27801611477994; FOODY.AUTH.UDID=f04ab5a4-3a5d-4ede-8be4-b4f4228fbdbc; FOODY.AUTH=8AEBA71E4CD8DAA3DDA79DCD2D04E65CF6539A94AEDFDE996F59CB75CB8ECD2203A2DBF12106667384DB8DD9D4E9A927C64A4052F60FCDCBE116013E0225AC8ABD213FBFA62D8B1F2FA9355DF26CA2095E96FD7B66D29D1DC7F918E0F14CE97C306B2265F37D0F082DB37A860995F28C729AE042BCC1BD2B57BCF04C4321942B26FA07B7D0651875D3EDC155F11BC54DCF124B4C4AA68772091DCD113EDEA3435C9B51A4183E0D013D12C3672CDFA6ACFEEC49D812B7CFFC90E9A7903427CC563C9F4A8EEEB003EA6568915810CFF86DA153CA09A57005111516D4E7AA430674795C2CA83A3A26FD1CFD56BDAA1DF76E041A16260866CB36907F5BC6C8165F6D; fd.verify.password.24690847=24/12/2025; _fbc=fb.1.1766567002765.IwY2xjawO4i6hleHRuA2FlbQIxMABicmlkETFmd1hkVTlScGhTMGZnbWtrc3J0YwZhcHBfaWQQMjIyMDM5MTc4ODIwMDg5MgABHk-T0CDJfCN6h6RD9PC7KzoQjsHOlw9YnWZ2tlhdJje0KvFKCiffVIEj1Fu6_aem_sSTRKnxtY-KHkhMq6Fr-5w; _gcl_au=1.1.1557224540.1766567615; __utmz=257500956.1766715944.5.4.utmcsr=l.facebook.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=257500956.1159984972.1766564630.1766715944.1766720243.6; fd.keys=; fd.res.view.218=1092352,1243056,1000027544,223001,1024448,694536,164027,1085866,6734,8855,496,854376,19146,28877,18675,290962,637481,226321,9286,93772; fbsr_395614663835338=zcZ05R6ZeVUNItKexDRudFZGSIP3hC4uvi5WCGqBbnE.eyJ1c2VyX2lkIjoiMzIwODM4MTQ5NzM5MjMxIiwiY29kZSI6IkFRQmE2SWJfMHI5c1JZd21sT2JyX1RaRU1jaWtLNEFDdTdrVWVpTmtJaWhOUWt2TEN4RG5iSERsdk1HUVNyWUxzb0ZENjQyN3kxd1hMbjVBZzVfU0RJSDZzTFhqOUZ0YnRCckpRemZoZ2U1WTR0WlYySDRzeFBDdlQtTUQxVkdGd05GZ2VqMF90bUxsd1FfSzIyak02WUdyX191NlNUYl9TZ0hCSkFZam16REx0Nm1iOXExN0pJWm4teEl0YUh5eHBIa2VsYmlzOE5MSE1YcS1rQXh1WEpSUHdkNVFNS1JpUVU1cGNvODJ6dVFjVENLendIYmZBR2YteG9QOTY4VVNCVEx3RDlsS1hhdFl6b2FRenZ5eEZGZUhITnZieWFISHRlYlo5dTJWOFFVTE1MQ0hLTVlVZ0pVeXZwRmowTFk3cXBrSG1BMHlOV214RHJxZDBMUl9BNFMxIiwib2F1dGhfdG9rZW4iOiJFQUFGbnp6ZUJmc29CUVViVU5HblIwWkFqVTFlU0Y4ajk2ZUdtZ2RJdnFBOEJOemZPNnJUT1pCWkFmUGhaQ3d1TFk1ZXoyZ0N1QzlROUI5WkI1bmNEenN2MnFUYlRYMXRrbFNjVjhNOU95MUhCc1F6cTFZejNHM2JJdUQ2TVpCdGYxUFhQQ241eGFnVVQ1RjZFcE5oZ1B0UHhzaXNkV2VKT0hhcHZuT2pqc3E5NWNrMVVLVVBza0JhNjF0TlV6S2V5aG5rUXN3VDJRWkQiLCJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTc2NjczMTY0OX0; fbsr_395614663835338=b8z4G2ODcNJ5iY75hxPin6_ESj-uUp5UzPQkYdmTC0M.eyJ1c2VyX2lkIjoiMzIwODM4MTQ5NzM5MjMxIiwiY29kZSI6IkFRRDFTUVA1VkQwa0pJOGNlSDJRQS1BX1J4ajhycHhLV3hFcTItR1ZaSzdsa1pwOHF0STRVSFRuZmVKVC1oWm1vNDNWMDF0eTNNUDlaTndhU2RLdUpqU0phZDRWekNHY29UYmo1bVlxSTZ0dktWRGVCZ0UyemZ6ejJ1blFIOUJTYW9WeWtDMUlGaGxKeXdJQVNZZGlzTzE3TEhnbnYxZU9uZS05V3psaVdMRV9Cak9vUnJVXzJTY0ZvTEpKcnZiR0l4YkJQeTlHaTdORGFpdGVUTGFtTzd1ei1rVWczck4tdTFGcTlaWG5tMGRJSjgyM2hEWXFNQTVhRHlEWHJXaXYwOUs4cG0wRTctQkFxZ3Rjc0RhcnIyc1NHRTZ5cWRybVpWX3BPVmlPYjcxWDY2eWc3WU5ZYnBiVnVTTVEyeldvRnRES3BKVmFSMG9mRmZLVFd0TUdkQWRHIiwib2F1dGhfdG9rZW4iOiJFQUFGbnp6ZUJmc29CUVViVU5HblIwWkFqVTFlU0Y4ajk2ZUdtZ2RJdnFBOEJOemZPNnJUT1pCWkFmUGhaQ3d1TFk1ZXoyZ0N1QzlROUI5WkI1bmNEenN2MnFUYlRYMXRrbFNjVjhNOU95MUhCc1F6cTFZejNHM2JJdUQ2TVpCdGYxUFhQQ241eGFnVVQ1RjZFcE5oZ1B0UHhzaXNkV2VKT0hhcHZuT2pqc3E5NWNrMVVLVVBza0JhNjF0TlV6S2V5aG5rUXN3VDJRWkQiLCJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTc2NjcyODE2NX0; __utmt_UA-33292184-1=1; _gat=1; __utmb=257500956.82.10.1766720243; _ga_6M8E625L9H=GS2.2.s1766715944$o5$g1$t1766732980$j10$l0$h0"
})

params_base = {
    "lat": 21.0333,
    "lng": 105.85,
}

page = 1
all_links = []
result_file = "foodcourt.json"
while True:
    params = {
        **params_base,
        "page": page,
        "t": int(time.time() * 1000)
    }
    # base_url = "https://www.foody.vn/__get/Place/HomeListPlace?t=1766713179047&page=" + str(page) + "&lat=21.033333&lon=105.85&count=12&districtId=&cateId=&cuisineId=&isReputation=&type=1"
    base_url_2 = "https://www.foody.vn/ha-noi/foodcourt?ds=Restaurant&vt=row&st=1&c=79&page=" + str(page) + "&provinceId=218&categoryId=79&append=true"
    # data = requests.get(base_url, headers=headers, params=params).json()

    try:
        data = session.get(base_url_2, params=params, timeout=15)
    except requests.exceptions.ConnectionError as e:
        print("❌ Bị server đóng kết nối")
        time.sleep(5)
        continue

    # print("STATUS:", data.status_code)

    if data.status_code != 200:
        break

    # soup = BeautifulSoup(data, "html.parser")
    # print(data["CityId"])
    try:
        data = data.json()
    except:
        print(data)
        continue
    with open("out_json.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    if "error" in data:
        print(len(all_links))
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(all_links, f, ensure_ascii=False, indent=4)
        
        with open("error.jsonl", "w", encoding="utf-8") as jf:
            jf.write(json.dumps({
                "base_url": base_url_2,
                "text": None
            }, ensure_ascii=False) + "\n")
        continue

    if data["searchItems"] != []:
        print("First_shop: ",data["searchItems"][0]["Id"])
    else:
        print(len(all_links))
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(all_links, f, ensure_ascii=False, indent=4)
        
        with open("error.jsonl", "w", encoding="utf-8") as jf:
            jf.write(json.dumps({
                "base_url": base_url_2,
                "text": None
            }, ensure_ascii=False) + "\n")
        continue
    # items = soup.select("div.title.fd-text-ellip a")
    # print(len(data["searchItems"]))
    if not data or data["searchItems"][0]["City"]!="Hà Nội":
        print("Hết dữ liệu")
        break

    for cur in data["searchItems"]:
        if cur["DetailUrl"] is None or cur["DetailUrl"] == "":
            with open("error.jsonl", "w", encoding="utf-8") as jf:

                jf.write(json.dumps({
                    "base_url": base_url_2,
                    "text": cur
                }, ensure_ascii=False) + "\n")
        elif cur["DetailUrl"].startswith("/ha-noi"):
            if cur["DetailUrl"] not in all_links:
                all_links.append(cur["DetailUrl"])
            else:
                print(len(all_links))
                with open(result_file, "w", encoding="utf-8") as f:
                    json.dump(all_links, f, ensure_ascii=False, indent=4)
                print("reputation")
        else: print(cur["DetailUrl"])
        

    # with open("out_json.json", "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)
    # print(items)
    
    # all_items.extend(items)
    # print(f"Page {page}: {len(items)} items")

    page += 1
    print(page)
    time.sleep(1)
print(len(all_links))
with open(result_file, "w", encoding="utf-8") as f:
    json.dump(all_links, f, ensure_ascii=False, indent=4)
# for a in soup.select("table a.reference.internal"):
#         url = urljoin(base_url, a.get("href"))
#         if urlparse(url).netloc == domain:
#             links.add(url.split("#")[0])