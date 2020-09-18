import csv,requests
from bs4 import BeautifulSoup

urls = [
    'aliasinfosec.com',
    'github.com',
    'news.ycombinator.com'
]

for u in urls:
    _r = requests.get(f"https://{u}")

    if _r.status_code == 200:

        soup = BeautifulSoup(_r.text, 'lxml')
        title = soup.find('title')

        with open(f"{u}.csv") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "URL"])
            writer.writerow([title.text, _r.url])