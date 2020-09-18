import sys
import requests
import pdb
import re
from bs4 import BeautifulSoup
import shlex, subprocess
import socket

if len(sys.argv) < 2:
    print("Must specify a domain name.")
    sys.exit()

def main():

    ip_list = []

    url = 'https://dnsdumpster.com/'
    headers = {
        'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language' : 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer' : 'https://dnsdumpster.com'
    }

    _s = requests.Session()
    _r = _s.get(url)

    soup = BeautifulSoup(_r.text, 'html.parser')
    csrftokenmiddleware_tag = soup.find('input', {'name':'csrfmiddlewaretoken'})

    data = {'csrfmiddlewaretoken' : csrftokenmiddleware_tag['value'], 'targetip' : sys.argv[1]}

    _r2 = _s.post(url, headers=headers, data=data)
    soup2 = BeautifulSoup(_r2.text, 'html.parser')
    table_rows = soup2.find_all('tr')

    for row in table_rows:

        send_scan = row.find('input', {'name': 'send_scan[]'})
        if send_scan:

            try:
                hostname = socket.gethostbyaddr(send_scan['value'])
            except Exception:
                hostname = False

            ip_list.append({'hostname' : False if not hostname else hostname[0], 'ip' : send_scan['value']})

    if ip_list:

        print(f"Collected {len(ip_list)} IP address from {sys.argv[1]}\n")

        file_name = f"{sys.argv[1]}-IPs.txt"

        with open(file_name, 'w') as f:
            for i in ip_list:
                f.write(f"{i}\n")

main()