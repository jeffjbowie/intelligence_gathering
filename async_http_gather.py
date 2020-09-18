#!/usr/bin/env python3

import requests
import sys
import argparse
import pdb
import http
import urllib3
import re
from bs4 import BeautifulSoup
from colorama import Fore, Style, Back
import asyncio
import json
import subprocess
from timeit import default_timer
import ipaddress
import random
from concurrent.futures import ThreadPoolExecutor

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Set up our CLI argument parser.
parser = argparse.ArgumentParser(
	description="Check HTTP status codes from list of URLS and specified port."
)

parser.add_argument('-p', metavar='80', type=str, required=True)
parser.add_argument('-v', required=False, action="store_true")
parser.add_argument('-d', required=False, action="store_true")
parser.add_argument('-c', metavar='172.16.0.0/12', required=False, type=str)
parser.add_argument('-iL', metavar='/path/to/list', type=str, required=False)

# Assign arguments
port = parser.parse_args().p
ip_list = parser.parse_args().iL
verbose = parser.parse_args().v
cidr_range = parser.parse_args().c
detections_only = parser.parse_args().d

# List of up-to-date user agents. whatismybrowser.com/guides/the-latest-user-agent/
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


# Variables 
timeout = 2
url_list = []
hit_count = 0
secure_ports = ['443','8443']


''' 
Build our internal list of URLS from CIDR range , or plaintext list of IP addresses.
'''
def build_list():

	# IP List has been specified.
	if ip_list:
		with open(ip_list) as fp:
			for cnt,line in enumerate(fp):
				url_list.append("http://%s:%s" % (line.strip(), port))
	
	# CIDR range has been specified.
	elif cidr_range:

		# Grab masscan results, JSON to STDOUT 
		masscan_results = subprocess.check_output(['/usr/bin/masscan', '-p', port, '-oJ' , '-', cidr_range])
		
		# If we have masscan results, parse and append to url list.
		if len(masscan_results):

			found_hosts = json.loads(str(masscan_results).replace("b'", "").replace("\\n" , "").replace("\'", "").replace(",]", "]"))
			for host in found_hosts:
				url_list.append("http://%s:%s" % (host['ip'], port))
		# Quit if no open ports.
		else:
			print(f"{Back.WHITE}{Fore.RED}[Status]{Style.RESET_ALL} Port {port} not open for any host in {cidr_range}.\r")
			sys.exit(0)

def detect(text):


	if "owa" and "Outlook" in text: return "OWA"
	elif "wgcgi" in text: return "WatchGuard"
	elif "IIS" in text: return "IIS"
	elif "Linksys" in text: return "Linksys"
	elif "Cisco" in text: return "Cisco"
	elif "Server 2012" in text: return "Server 2012"
	elif "webmail" in text: return "webmail"
	else: return None

def fetch(session, url):

	global hit_count

	try:

		if port in secure_ports:
			url = url.replace('http', 'https')

		with session.get(url, timeout=timeout, headers={'User-agent' : f'{random.choice(user_agents)}'}, verify=False) as response:
			
			data = response.text

			# Authorization Required
			if response.status_code == 401:

				basic_realm = re.search('Basic realm="(.*)"', \
				response.headers['WWW-Authenticate'])

				if basic_realm: 
					
					hit_count += 1 # Hit

					if not detections_only:
						print(f"{Back.WHITE}{Fore.BLUE}[{basic_realm[1]}]{Style.RESET_ALL} {url}\r")

			# Response OK
			else:
				soup = BeautifulSoup(response.text, features="lxml")
				
				if soup.find('html'):
					hit_count += 1 # Hit

					detection = detect(soup.find('html').text)

					if detection is None:
						
						if not detections_only:
							# Print 256 characters of body.
							print(f"{Back.GREEN}{Fore.BLACK}[{url}]{Style.RESET_ALL}\n \
									\t{soup.find('body').prettify()[:256]}\r")
					else:

						print(f"{Back.GREEN}{Fore.BLACK}[{url}]{Back.MAGENTA}{Fore.WHITE}{detection}{Style.RESET_ALL}\r")

			return data

	except Exception as e:
	 	if verbose: print(f"{Back.WHITE}{Fore.RED}[Gen. Exception]{Style.RESET_ALL} {url}:{e}\r")

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
		
def main():

	if sys.version_info[0] < 3:
		print(f"{Back.WHITE}{Fore.RED}[Error]{Style.RESET_ALL} Python 3 or higher required. \r")
		sys.exit(0)
	
	if not ip_list and not cidr_range: 
		print(f"{Back.WHITE}{Fore.RED}[Error]{Style.RESET_ALL} No IP list/range specified. \r")
		sys.exit(0)

	START_TIME = default_timer()

	# Build url_list[]
	build_list()

	# async loop process_urls()
	loop = asyncio.get_event_loop()
	future = asyncio.ensure_future(process_urls())
	loop.run_until_complete(future)

	# Calculate elapsed time.
	elapsed = default_timer() - START_TIME
	time_completed_at = "{:5.2f} seconds".format(elapsed)
	
	if cidr_range:
		print(f"\n{Back.WHITE}{Fore.BLACK}{hit_count} hits from {ipaddress.ip_network(cidr_range).num_addresses} host(s) in {time_completed_at}!{Style.RESET_ALL}\n")
	sys.exit(0)


main()