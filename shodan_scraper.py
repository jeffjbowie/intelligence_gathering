from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from texttable import Texttable
import time
import random
import sys
import pdb

def get_sleepy():
    time.sleep(random.uniform(0.5,1.5))

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <IP Address>")
    sys.exit(0)

port_list = []
service_list = []
tech_list = []

t = Texttable()
t.add_row(['IP Address','Ports', 'Services', 'Web Tech'])

browser = webdriver.Chrome()
browser.get('https://shodan.io')

browser.find_element_by_id('search_input').send_keys(sys.argv[1])
get_sleepy()

browser.find_element_by_id('search_input').send_keys(Keys.ENTER)
get_sleepy()

# Check for rate limit error.
try:
    alert_error = browser.find_element_by_class_name('alert-error')
    if alert_error:
        if alert_error.is_displayed():
            e = browser.find_element_by_class_name('alert-error').find_element_by_tag_name('p').text
            print(f"Error: {e}")
            sys.exit(0)
except Exception:
    pass

for a in browser.find_element_by_class_name('ports').find_elements_by_tag_name('a'):
    port_list.append(a.text)

for h3 in browser.find_element_by_class_name('services').find_elements_by_tag_name('h3'):
    
    if "Ver" in h3.text:
        service_list.append(h3.text.replace('Ver', ' Ver'))
    else:
        service_list.append(h3.text)

try:
    for li in browser.find_element_by_class_name('http-components').find_elements_by_tag_name('li'):
        tech_list.append(li.text)
except Exception:
    pass

ports = ', '.join([str(p) for p in port_list])
services = ', '.join([str(s) for s in service_list])
tech = ', '.join([str(t) for t in tech_list])

t.add_row([sys.argv[1], ports, services, tech])

print(t.draw())
browser.quit()
sys.exit(0)