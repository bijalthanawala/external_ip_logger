#! /usr/bin/env python3

import urllib.request

response = urllib.request.urlopen("https://ifconfig.me")
content = response.read()
response.close()
ip_address = content.decode()
print(ip_address)
