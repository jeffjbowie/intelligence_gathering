#!/usr/bin/env python

import re
import time
import pdb
import sys
import argparse
import urllib 
import random
import json

import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from colorama import Fore, Style, Back

'''
Populate URL list with Bing Searches.
'''
def populate_bing():

	def grab_links():
		
		links = browser.find_elements_by_xpath('//ol[@id="b_results"]//li//a')
		
		for link in links:
			if link.get_attribute('href'):
				if link.get_attribute('href').startswith('http'):
					url_list.append(link.get_attribute('href'))

	def fetch_results_loop():
		page = 1

		while True:
			
			page += 1
			try:
				browser.find_element_by_xpath("//a[@title='Next page']").click()
			except Exception:
				browser.quit()
				break

			grab_links()
			time.sleep(random.uniform(0.1,0.8))

			if page > limit:
				browser.quit()
				break


	url = 'https://www.bing.com'

	browser = webdriver.Chrome(options=chrome_options)
	browser.get(url)

	for letter in list(query): 
		browser.find_element_by_name('q').send_keys(letter)
		time.sleep(random.uniform(0.1,0.8))

	time.sleep(random.uniform(0.1,0.8))
	browser.find_element_by_name('q').send_keys(Keys.ENTER)

	fetch_results_loop()


'''
Populate URL list with Google Searches.
'''
def populate_google():

	def grab_links():
		results = browser.find_elements_by_class_name('r')
		for result in results:
			anchors = result.find_elements_by_tag_name('a')
			for anchor in anchors:
				if "google.com" not in anchor.get_attribute('href') and "webcache.googleusercontent.com" not in anchor.get_attribute('href'):
					url_list.append(anchor.get_attribute('href'))

	def fetch_results_loop():
		page = 1

		while True:
			
			page += 1
			try:
				browser.find_element_by_xpath("//a[@aria-label='Page %s']" % page ).click()
			except Exception:
				browser.quit()
				break

			grab_links()
			time.sleep(random.uniform(0.1,0.8))

			if page > limit:
				browser.quit()
				break

	url = 'https://www.google.com'
	
	browser = webdriver.Chrome(options=chrome_options)
	browser.get(url)

	for letter in list(query): 
		browser.find_element_by_name('q').send_keys(letter)
		time.sleep(random.uniform(0.1,0.8))
	
	time.sleep(random.uniform(0.1,0.8))
	browser.find_element_by_name('q').send_keys(Keys.ENTER)

	time.sleep(random.uniform(0.1,0.8))
	fetch_results_loop()

'''
Populate URL list with results from Yahoo. Only grabs 1st page of links.
'''
def populate_yahoo():

	def grab_links():

		links = browser.find_elements_by_xpath('//div//h3[@class="title"]//a')

		for link in links:
			url_list.append(link.get_attribute('href'))
		
	def fetch_results_loop():
		page = 1

		while True:
			page += 1

			try:
				browser.find_element_by_class_name('next').click()
			except Exception:
				browser.quit()
				break

			grab_links()
			time.sleep(random.uniform(0.1,0.8))

			if page > limit:
				browser.quit()
				break
	
	browser = webdriver.Chrome(options=chrome_options)
	browser.get('https://www.yahoo.com')

	for letter in list(query): 
		browser.find_element_by_id('header-search-input').send_keys(letter)
		time.sleep(random.uniform(0.1,0.8))

	time.sleep(random.uniform(0.1,0.8))
	browser.find_element_by_id('header-search-input').send_keys(Keys.ENTER)

	fetch_results_loop()


'''
Loop throuugh URL list and pull e-mail addresses via Regex.
'''

def process_urls():

	print("\n\r")

	print("[INFO] Found %d unique links for '%s'...\n\r" % (len(set(url_list)), query))
	print("[INFO] Scraping links for term '%s'...\n\r" % term)

	# "unique" or URL list, Loop through URLs and parse the text. 
	for url in set(url_list):
		# Request page.
		try:
			# Timeout in X seconds if URL is unavailable
			_r = requests.get(url, timeout=timeout)
			
			soup = BeautifulSoup(_r.text, "html.parser")
			term_matches = soup(text=re.compile(term))

			for m in term_matches:
				if "{" not in m and term in m:
					print(f"{Back.GREEN}{Fore.BLACK}[{url}]{Style.RESET_ALL}\n{m}\n")

					#print(f"[*] {url} \n{m}\n")			

		# Skip to next URL if page is inaccessible.
		except Exception:
			print("[DEBUG]: Skipping '%s' ...\r" % url)
			continue


# Main function of our app.
def main():

	populate_bing()
	#populate_yahoo()
	populate_google()


	if url_list:
		process_urls()


	else:
		print("\n[INFO] No URL(s) found.\n\r")


	sys.exit(0)



limit = 5 # Pages per search
timeout = 4 # Timeout (seconds)

# Define arguments, 
parser = argparse.ArgumentParser(description="Find sites containing a search term from Google/Bing searches.")
parser.add_argument('-q', metavar='query', type=str, required=True)
parser.add_argument('-t', metavar='term', type=str, required=True)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Pull arguments from parser.
query = parser.parse_args().q
term = parser.parse_args().t

# Define our lists (arrays).
url_list = []
found_sites = []

# Start our app.
main()