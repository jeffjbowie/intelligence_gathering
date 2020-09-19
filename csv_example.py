import csv
import requests
from bs4 import BeautifulSoup
import pdb

# List of URLS
urls = [
	'aliasinfosec.com',
	'github.com',
	'news.ycombinator.com'
]

results = []

# Loop through URLs
for u in urls:

	_r = requests.get(f"https://{u}")

	# Make sure 200 OK
	if _r.status_code == 200:

		soup = BeautifulSoup(_r.text, 'html.parser')
		title = soup.find('title')

		results.append([title.text, u])

# Open a CSV file, with write attribute.
with open(f"output.csv", "w") as f:

	# Create a writer, write header.
	writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
	writer.writerow(["Title", "URL"])

	# Loop through results and write rows.
	for r in results:
		writer.writerow([r[0], r[1]])


