import requests
from bs4 import BeautifulSoup
import queue
import threading
import concurrent.futures


def scrapeProxies():
    url = "https://free-proxy-list.net/"

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        tbody = soup.find("tbody")

        tr_elements = tbody.find_all("tr")

        with open("proxy_list.txt", "w") as file:
            for tr in tr_elements:
                first_td = tr.find_all("td")[0]
                second_td = tr.find_all("td")[1]

                if first_td and second_td:
                    concatenated_td = f"{first_td.text}:{second_td.text}"
                    print(concatenated_td)
                    file.write(concatenated_td + "\n")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")


def validate_proxies():
    q = queue.Queue()

    with open("proxy_list.txt", "r") as f:
        proxies = f.read().split("\n")
        for p in proxies:
            q.put(p)

    valid_proxies = []

    def check_proxy(proxy):
        try:
            res = requests.get(
                "https://www.linkedin.com/",
                proxies={"http": proxy, "https": proxy},
                timeout=15
            )
            if res.status_code == 200:
                with valid_proxies_lock:
                    if len(proxy):
                        valid_proxies.append(proxy)
                        with open("valid_proxies.txt", "a") as valid_proxy_file:
                            valid_proxy_file.write(f"{proxy}\n")
                    if len(valid_proxies) >= 10:
                        executor.shutdown(wait=False)
        except Exception as e:
            pass

    valid_proxies_lock = threading.Lock()
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        while len(valid_proxies) < 10:
            try:
                proxy = q.get_nowait()
                if proxy is not None:
                    executor.submit(check_proxy, proxy)
            except queue.Empty:
                break

    return valid_proxies[:10]


def automation():
    with open("valid_proxies.txt", "r") as f:
        proxies = f.read().split("\n")

    sites_to_check = [
        "https://www.linkedin.com/",
        "https://www.linkedin.com/",
        "https://www.linkedin.com/",
        "https://www.linkedin.com/",
        "https://www.linkedin.com/",
        "https://www.linkedin.com/",
    ]

    i = 0

    for idx in range(len(sites_to_check)):
        print(f"\n{sites_to_check[idx]}")
        cnt = 0
        for tries in range(len(proxies)):
            try:
                print(f"Using PROXY : {proxies[i]}")
                res = requests.get(sites_to_check[idx], proxies={"http": proxies[i], "https": proxies[i]}, timeout=10)
                print(res.status_code)
                cnt = 1
                i += 1
                if i == len(proxies) - 1:
                    i = 0
                break
            except:
                print("Failed")
                print(f"Again trying for website {sites_to_check[idx]} with another proxy")
            finally:
                i += 1
                if i == len(proxies) - 1:
                    i = 0 
            tries += 1
        
        if cnt == 0:
            print("All proxies have expired, need to scrape new ones...Scraping...")
            with open("valid_proxies.txt", "w") as file:
                file.write("")
            scrapeProxies()
            proxies = validate_proxies()
            idx -= 1
    
    with open("valid_proxies.txt", "w") as file:
        file.write("")


if __name__ == "__main__":
    scrapeProxies()
    valid_proxies = validate_proxies()
    print("\n\nThe valid proxies are : ", end="")
    for proxy in valid_proxies:
        print(proxy, end=" ")
    print()
    automation()
