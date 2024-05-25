#! /usr/bin/env python3

import sys
import os
import time
import argparse
import signal
import re
from urllib import request
from urllib.error import HTTPError, URLError

from http.client import HTTPResponse
from _io import TextIOWrapper
from types import FrameType

from typing import Tuple, Any

DEFAULT_DELAY: int = 60
DEFAULT_URL: str = "https://ifconfig.me"
DEFAULT_QUIET_MODE: bool = False
DEFAULT_QUIETER_MODE: bool = False


def validate_and_translate_args(default_csv_prefix: str) -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()

    parser.add_argument(
        "--delay",
        type=int,
        default=DEFAULT_DELAY,
        help=f"Wait specified number of seconds before each check (Default={DEFAULT_DELAY})",
    )

    parser.add_argument(
        "--csv_prefix",
        type=str,
        default=default_csv_prefix,
        help="CSV filename prefix e.g. With csv_prefix XYZ, "
        "the file created will be XYZ_yyyymmdd_hhmmss.csv (Default=base name of this script)",
    )

    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_URL,
        help=f"URL to query public IP from (Default={DEFAULT_URL})",
    )
    # Other web services, that provide ip address, known at this time:
    #   https://www.ipify.org/
    #   https://api.my-ip.io/v2/ip.txt

    parser.add_argument(
        "--quiet",
        action="store_true",
        default=DEFAULT_QUIET_MODE,
        help=f"Run quietly - do not show IP updates on console (Default={DEFAULT_QUIET_MODE})",
    )

    parser.add_argument(
        "--quieter",
        action="store_true",
        default=DEFAULT_QUIETER_MODE,
        help=f"Run even quieter - do not show the name of the CSV file also. "
        f"Implies --quiet also (Default={DEFAULT_QUIETER_MODE})",
    )

    args: argparse.Namespace = parser.parse_args()

    if args.quieter:
        # imply args.quiet also
        args.quiet = True

    return args


def validate_ip_address(ip: str) -> bool:
    regex_ip_pattern = r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"
    if re.fullmatch(regex_ip_pattern, ip):
        return True
    return False


def detect_external_ip(url: str) -> Tuple[bool, str, str]:
    # Expect a single-line or multi-line response from the http request
    # If multi-line, expect the first line to be the IP address
    try:
        response: HTTPResponse = request.urlopen(url)
    except (HTTPError, URLError) as ex_connection_error:
        return False, f"Failed to query {url} ({str(ex_connection_error)})", ""

    content_bytes: bytes = response.read()
    response.close()

    content: str = content_bytes.decode()
    ip_addr: str = content.split("\n")[0]

    is_valid_ip: bool = validate_ip_address(ip_addr)
    if not is_valid_ip:
        return False, f"Invalid IP address {ip_addr}", ""

    return True, "Successful", ip_addr


def enable_ctrl_c_handler(file_handle: TextIOWrapper) -> None:
    def ctrl_c_handler(signum: int, frame: FrameType | None) -> Any:
        file_handle.close()
        print("\nCTRL-C detected. Exiting")
        exit(0)

    signal.signal(signal.SIGINT, ctrl_c_handler)


def main() -> None:

    name_of_this_script = os.path.basename(sys.argv[0])
    default_csv_prefix = os.path.splitext(name_of_this_script)[0]
    args: argparse.Namespace = validate_and_translate_args(default_csv_prefix)

    prev_ip_addr: str = ""
    start_time: time.struct_time = time.localtime()
    csv_suffix: str = time.strftime("%Y%m%d_%H%M%S", start_time)
    csv_filename: str = f"{args.csv_prefix}_{csv_suffix}.csv"

    if not args.quieter:
        print(f"Logging IP address changes to {csv_filename}", file=sys.stdout)

    if not args.quiet:
        print(
            f"Querying public IP from {args.url} every {args.delay} seconds",
            file=sys.stdout,
        )

    # Open CSV file - use low-level file access (instead of csv api) so that we can seek
    # back/forth after each IP query
    csv_file_handle: TextIOWrapper = open(csv_filename, "w")
    enable_ctrl_c_handler(csv_file_handle)

    # Write CSV file header
    print("ip_address,start_time,end_time", file=csv_file_handle)
    csv_file_handle.flush()

    ip_changed: bool = False
    while True:
        is_success: bool
        message: str
        ip_addr: str
        is_success, message, ip_addr = detect_external_ip(args.url)
        if not is_success:
            print(f"\n{message}", file=sys.stderr)
            time.sleep(args.delay)
            continue
        curr_local_time: time.struct_time = time.localtime()
        if not prev_ip_addr:
            # This is the first iteration
            start_time = curr_local_time
            prev_ip_addr = ip_addr
        elif prev_ip_addr != ip_addr:
            ip_changed = True
        else:
            ip_changed = False

        csv_file_pos = csv_file_handle.tell()
        start_time_log = time.strftime("%Y%m%d_%H%M%S", start_time)
        end_time_log = time.strftime("%Y%m%d_%H%M%S", curr_local_time)
        print(f"{prev_ip_addr},{start_time_log},{end_time_log}", file=csv_file_handle)
        csv_file_handle.flush()

        if not args.quiet:
            print(
                f"Public IP address {prev_ip_addr} - "
                f"observed last at {time.asctime(curr_local_time)}",
                file=sys.stdout,
                end="\r",
            )

        if ip_changed:
            # Update variables and prepare for the next iteration
            start_time = curr_local_time
            prev_ip_addr = ip_addr
            if not args.quiet:
                print("", file=sys.stdout)
        else:
            # IP did not change in this iteration.
            # Seek to the start of this line so that this line
            # updates in the next iteration
            csv_file_handle.seek(csv_file_pos)

        time.sleep(args.delay)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)
