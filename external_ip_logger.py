#! /usr/bin/env python3

import sys
import time
import datetime
import urllib.request
from http.client import HTTPResponse

prev_ip_addr: str = ""
start_time: str = ""
end_time: str = ""

while True:
    now: datetime.datetime = datetime.datetime.now()
    response: HTTPResponse = urllib.request.urlopen("https://ifconfig.me")
    content: bytes = response.read()
    response.close()
    ip_addr: str = content.decode()
    curr_time: str = time.strftime("%Y%m%d_%H%M%S")
    print(
        f"Current time: {curr_time}\tCurrent IP: {ip_addr}", file=sys.stderr, end="\r"
    )
    if not prev_ip_addr:
        start_time = curr_time
        prev_ip_addr = ip_addr
    elif prev_ip_addr != ip_addr:
        print("", file=sys.stderr)
        print(f"{start_time},{curr_time},{prev_ip_addr}")
        start_time = curr_time
        prev_ip_addr = ip_addr

    time.sleep(5)
