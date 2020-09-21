import requests
import xml.etree.ElementTree as ET
import sys
import re
import pdb
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio

def fetch(session, url):
	try:

		with session.get(url, verify=False) as r:
			
			if r.status_code == 200:
				root = ET.fromstring(r.text)
				for child in root:
					if "Contents" in child.tag:
						for e in child:
							if "Key" in e.tag:
								if "." in e.text and "/" in e.text:
									print(f"[DL] {url}/{e.text}")
									if DOWNLOAD_CONTENTS:
										try:
											r =  requests.get(f"{url}/{e.text}")
											filename = e.text.split('/')[-1]
											open(f"{FOLDER_NAME}/{filename}", 'wb').write(r.content)
										except Exception:
											print(f"[DL_ERR] {url}")

	except Exception as e:
	 	print(f"[!] Exception: {e}")

async def process_buckets(buckets):

	with ThreadPoolExecutor(max_workers=10) as executor:
		with requests.Session() as session:
			loop = asyncio.get_event_loop()

			tasks = [
				loop.run_in_executor(
					executor,
					fetch,
					*(session, b) # Allows us to pass in multiple arguments to `fetch`
				)
				for b in buckets
			]

			for response in await asyncio.gather(*tasks):
				pass


def bucketNameValid(bucket_name):    
	pattern = r'(?=^.{3,63}$)(?!^(\d+\.)+\d+$)(^(([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])\.)*([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])$)'
	return bool(re.match(pattern, bucket_name))

def main():

	global DOWNLOAD_CONTENTS
	
	buckets = []
	
	if len(sys.argv) < 2:
		print(f"Error: Specify a wordlist. \nUsage: \t {sys.argv[0]} <wordlist>")
		sys.exit(0)

	if len(sys.argv) >= 3:
		if sys.argv[2] == "-d":

			DOWNLOAD_CONTENTS = True 

			if not os.path.isdir(FOLDER_NAME):
				try:
					os.makedirs(FOLDER_NAME)
				except Exception:
					print(f"Error creating folder '{FOLDER_NAME}'.")
					sys.exit(0)

	# Import wordlist.
	with open(sys.argv[1]) as fp:
		for cnt,line in enumerate(fp):
			bn = line.strip()
			if bucketNameValid(bn):
				buckets.append(f"http://{bn}.s3.amazonaws.com")

	# async loop process_urls()
	loop = asyncio.get_event_loop()
	future = asyncio.ensure_future(process_buckets(buckets))
	loop.run_until_complete(future)


DOWNLOAD_CONTENTS = False
FOLDER_NAME = "buckets_dump"

main()