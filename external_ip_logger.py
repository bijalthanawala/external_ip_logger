#! /usr/bin/env python3

import sys
import time
import datetime
import urllib.request

prev_ip_addr = ''
start_time = None
end_time = None
while True:
    now = datetime.datetime.now()
    response = urllib.request.urlopen("https://ifconfig.me")
    content = response.read()
    response.close()
    ip_addr = content.decode()
    curr_time = time.strftime("%Y%m%d_%H%M%S")
    print(f"Current time: {curr_time}\tCurrent IP: {ip_addr}", file=sys.stderr, end="\r")
    if not prev_ip_addr:
        start_time = curr_time
        prev_ip_addr = ip_addr
    elif prev_ip_addr != ip_addr:
        print(f"", file=sys.stderr)
        print(f"{start_time},{curr_time},{prev_ip_addr}")
        start_time = curr_time
        prev_ip_addr = ip_addr

    time.sleep(5)
