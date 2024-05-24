#! /usr/bin/env python3

import sys
import time
import argparse
import urllib.request
from http.client import HTTPResponse


def validate_and_translate_args() -> argparse.Namespace:
    default_delay: int = 60

    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "--delay",
        type=int,
        default=default_delay,
        help=f"Wait specified number of seconds before each check (Default={default_delay})",
    )
    args: argparse.Namespace = parser.parse_args()
    return args


def main() -> None:

    args: argparse.Namespace = validate_and_translate_args()

    prev_ip_addr: str = ""
    start_time: str = ""

    print("start_time,end_time,ip_address", file=sys.stdout)
    while True:
        response: HTTPResponse = urllib.request.urlopen("https://ifconfig.me")
        content: bytes = response.read()
        response.close()
        ip_addr: str = content.decode()
        curr_time: str = time.strftime("%Y%m%d_%H%M%S")
        print(
            f"Current time: {curr_time}\tCurrent IP: {ip_addr}",
            file=sys.stderr,
            end="\r",
        )
        if not prev_ip_addr:
            start_time = curr_time
            prev_ip_addr = ip_addr
        elif prev_ip_addr != ip_addr:
            print("", file=sys.stderr)
            print(f"{start_time},{curr_time},{prev_ip_addr}", file=sys.stdout)
            start_time = curr_time
            prev_ip_addr = ip_addr

        time.sleep(args.delay)


if __name__ == "__main__":
    main()
