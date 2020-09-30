import requests
from bs4 import BeautifulSoup
import sys
import pdb

if len(sys.argv) < 3:
	print("Please enter a product & version to search.")
	print(f"Usage: {sys.argv[0]} <product_name> <product_version>")
	sys.exit(0)

product = sys.argv[1].lower()
version = sys.argv[2].lower()

url = 'https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword='  
_r = requests.get(url + product + "+" + version)

if _r.status_code == 200:

	soup = BeautifulSoup(_r.text, "html.parser")
	table = soup.find(id="TableWithRules")

	table_rows = table.find_all("tr")

	for row in table_rows:
		
		table_datas = row.find_all('td')

		if len(table_datas) >= 2:

			cve = table_datas[0].text
			description = table_datas[1].text.lower()

			if product in description and version in description:
				print(f"[CVE]\t\t{table_datas[0].text}\n[Description]\t{table_datas[1].text}")