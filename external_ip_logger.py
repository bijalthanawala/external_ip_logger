#! /usr/bin/env python3

import sys
import time
import argparse
from typing import Tuple
import urllib.request
from http.client import HTTPResponse


def validate_and_translate_args() -> argparse.Namespace:
    default_delay: int = 60
    default_url: str = "https://ifconfig.me"
    # Other web services known at this time:
    #   https://www.ipify.org/
    #   https://api.my-ip.io/v2/ip.txt

    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "--delay",
        type=int,
        default=default_delay,
        help=f"Wait specified number of seconds before each check (Default={default_delay})",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=default_url,
        help=f"URL to query public IP from (Default={default_url})",
    )
    args: argparse.Namespace = parser.parse_args()
    return args


def detect_external_ip(url: str) -> Tuple[bool, str, str]:
    # Expect a single-line or multi-line response from the http request
    # If multi-line, expect the first line to be the IP address
    try:
        response: HTTPResponse = urllib.request.urlopen(url)
    except urllib.error.HTTPError as ex_http_error:
        return False, f"Failed to query {url} ({str(ex_http_error)})", ""

    content_bytes: bytes = response.read()
    response.close()
    content: str = content_bytes.decode()
    ip_addr = content.split("\n")[0]
    return True, "Successful", ip_addr


def main() -> None:

    args: argparse.Namespace = validate_and_translate_args()

    prev_ip_addr: str = ""
    start_time: str = ""

    print(
        f"Querying public IP from {args.url} every {args.delay} seconds",
        file=sys.stderr,
    )
    print("start_time,end_time,ip_address", file=sys.stdout)
    while True:
        is_success: bool
        ip_addr: str
        is_success, message, ip_addr = detect_external_ip(args.url)
        if not is_success:
            print(f"{message}", file=sys.stderr)
            time.sleep(args.delay)
            continue
        curr_time: str = time.strftime("%Y%m%d_%H%M%S")
        print(
            f"Current time: {curr_time}\tCurrent IP: {ip_addr}",
            file=sys.stderr,
            end="\r",
        )
        if not prev_ip_addr:
            # This is the first iteration
            start_time = curr_time
            prev_ip_addr = ip_addr
        elif prev_ip_addr != ip_addr:
            # Handle IP address change
            print("", file=sys.stderr)
            print(f"{start_time},{curr_time},{prev_ip_addr}", file=sys.stdout)
            start_time = curr_time
            prev_ip_addr = ip_addr

        time.sleep(args.delay)


if __name__ == "__main__":
    main()
