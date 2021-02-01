#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time 
import random
from bs4 import BeautifulSoup
import sys
import pdb

def extract(source):
	soup = BeautifulSoup(source, "html.parser")
	try:
		content = soup.find_all('textarea', {"name":"content"})[0].text
	except Exception:
		content = False
	
	return content

def random_int_scrape(word):


	random_int = str(int(random.random() * random.randint(1,9999)))
	url = f"https://cl1p.net/{word+random_int}"
	browser.get(url)
	
	try:
		browser.find_element_by_id('content')
	except NoSuchElementException:
		

		result = extract(browser.page_source)
		if result:
			output_f.write("*******************************\n")
			output_f.write(f"{time.ctime()}\n{word}\n\n{result}\n\n")
			
			print("*******************************")
			print(f"[{time.ctime()}\n{word}\n\n{result}\n\n")


def plain_scrape(word):


	url = f"https://cl1p.net/{word}"
	browser.get(url)
	
	try:
		browser.find_element_by_id('content')
	except NoSuchElementException:

		result = extract(browser.page_source)
		if result:

			output_f.write("*******************************\n")
			output_f.write(f"{time.ctime()}\nURL: /{word}\n\n{result}\n\n")
			
			print("*******************************")
			print(f"{time.ctime()}\nURL: /{word}\n\n{result}\n\n")

if len(sys.argv) < 3:
	print("Please supply a wordlist & output filename.")
	print(f"Usage: {sys.argv[0]} <wordlist> <output_file>")
	sys.exit(1)

print("\n")
print(r"""
  _______  ___       __   _______ _______   __   __  ___   _______  _______  _______ 
 |       ||   |    /   | |       ||  ____  |  \ |  ||   | |       ||       ||        |    
 |      _||   |    |   | |   |_| ||  |_____|   \   ||   | |   |_| ||   |___ |   |_|  |
 |     |  |   |___ |   | |    ___||_____  ||    \  ||   | |    ___||    ___||    __  |
 |     |_ |       ||   | |   |     _____| || |  |  ||   | |   |    |   |___ |   |  | |
 |_______||_______||___| |___|    |_______||_|  |__||___| |___|    |_______||___|  |_|
		>>> * Created by Jeff Bowie  github.com/jeffjbowie * <<<
""")

browser = webdriver.Chrome()
print("\n\n")

f = open(sys.argv[1], 'r')
sleep_time = 15

output_filename = sys.argv[2]
output_f = open(output_filename, 'w')

try:
	while True:

		for line in f.readlines():
			
			plain_scrape(line.strip())
			time.sleep(random.uniform(0.9,1.8))
			
			random_int_scrape(line.strip())
			time.sleep(random.uniform(0.9,1.8))
		
		print("*******************************")
		print(f"[{time.ctime()}] Sleeping for {sleep_time} seconds...\n")
		output_f.write( "*******************************\n")
		output_f.write(f"[{time.ctime()}] Sleeping for {sleep_time} seconds...\n")
		time.sleep(sleep_time)

		f.seek(0)

except Exception:
		output_f.close()
		print("\nBye...")
		browser.quit()
		sys.exit()
