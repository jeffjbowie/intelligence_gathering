from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from texttable import Texttable
import sys
import pdb
import time
import random

def get_sleepy():
    time.sleep(random.uniform(0.5,1.5))

if len(sys.argv) < 2:
    print("Usage: {sys.argv[0] <IP_List.txt>")
    sys.exit(0)


browser = webdriver.Chrome()
browser.get('https://censys.io')
get_sleepy()

browser.find_element_by_class_name('btn-search-censys').click()

t = Texttable()
t.add_row(['IP ADDRESS','PORTS'])

with open(sys.argv[1], 'r') as f:
    
    for cnt,line in enumerate(f):

        open_ports = []

        browser.find_element_by_id('q').send_keys(line.strip())
        get_sleepy()

        browser.find_element_by_id('q').send_keys(Keys.ENTER)
        get_sleepy()

        protocol_details = browser.find_elements_by_class_name('protocol-details')
        for e in protocol_details:
            anchors = e.find_elements_by_tag_name('a')
            for a in anchors:
                if a.get_attribute('name') != '':
                    open_ports.append(a.get_attribute('name').strip())

        open_ports = ', '.join([str(p) for p in open_ports])
        
        if open_ports:
            t.add_row([line.strip(), open_ports])
        
        browser.find_element_by_id('q').clear()
        get_sleepy()

print(t.draw())