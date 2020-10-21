from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from texttable import Texttable
import sys
import random
import time
import pdb

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <IP_List.txt>")
    sys.exit()

browser = webdriver.Chrome()
browser.get('https://talosintelligence.com/')

t = Texttable()
t.add_row(['IP Address','Location', 'Web Reputation', 'E-mail Reputation', 'Hostname', 'Network Owner'])

with open(sys.argv[1], 'r') as f:
    
    for cnt,line in enumerate(f):

        browser.find_element_by_id('rep-lookup').send_keys(line.strip())
        time.sleep(random.uniform(0.5,1.5))

        browser.find_element_by_id('rep-lookup').send_keys(Keys.ENTER)
        time.sleep(random.uniform(6,10))

        location = browser.find_elements_by_class_name('lookup-data')[0].find_element_by_tag_name('td').text
        web_rep =  browser.find_element_by_class_name('new-legacy-label').text.split('|')[0].strip()
        hostname = browser.find_elements_by_class_name('lookup-data')[1].find_elements_by_tag_name('tr')[2].find_elements_by_tag_name('td')[1].text
        email_rep = browser.find_elements_by_class_name('lookup-data')[3].find_elements_by_tag_name('td')[1].text
        network_owner = browser.find_element_by_id('network-owner-row').find_elements_by_tag_name('td')[1].text

        t.add_row([line.strip(), location, web_rep, email_rep, hostname, network_owner])
        time.sleep(random.uniform(0.5,1.5))

        browser.find_element_by_id('rep-lookup').clear()
        time.sleep(random.uniform(0.5,1.5))

print(t.draw())