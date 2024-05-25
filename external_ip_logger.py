#! /usr/bin/env python3

import sys
import time
import argparse
from typing import Tuple
import urllib.request
from http.client import HTTPResponse

default_delay: int = 60
default_url: str = "https://ifconfig.me"
default_csv_prefix: str = "external_ip_logger"
default_quiet_mode: bool = False


def validate_and_translate_args() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "--delay",
        type=int,
        default=default_delay,
        help=f"Wait specified number of seconds before each check (Default={default_delay})",
    )
    parser.add_argument(
        "--csv_prefix",
        type=str,
        default=default_csv_prefix,
        help="CSV filename prefix e.g. With csv_prefix XYZ, "
        f"the file created will be XYZ_yyyymmdd_hhmmss.csv (Default={default_csv_prefix})",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=default_url,
        help=f"URL to query public IP from (Default={default_url})",
    )
    # Other web services, that provide ip address, known at this time:
    #   https://www.ipify.org/
    #   https://api.my-ip.io/v2/ip.txt
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=default_quiet_mode,
        help=f"Run quietly - do not show IP updates on console (Default={default_quiet_mode})",
    )

    args: argparse.Namespace = parser.parse_args()
    return args


def detect_external_ip(url: str) -> Tuple[bool, str, str]:
    # Expect a single-line or multi-line response from the http request
    # If multi-line, expect the first line to be the IP address
    try:
        response: HTTPResponse = urllib.request.urlopen(url)
    except (urllib.error.HTTPError, urllib.error.URLError) as ex_connection_error:
        return False, f"Failed to query {url} ({str(ex_connection_error)})", ""

    content_bytes: bytes = response.read()
    response.close()
    content: str = content_bytes.decode()
    ip_addr = content.split("\n")[0]
    return True, "Successful", ip_addr


def main() -> None:

    args: argparse.Namespace = validate_and_translate_args()

    prev_ip_addr: str = ""
    start_time: time.struct_time = time.localtime()
    csv_suffix = time.strftime("%Y%m%d_%H%M%S", start_time)
    csv_filename = f"{args.csv_prefix}_{csv_suffix}.csv"

    print(f"Logging IP address changes to {csv_filename}", file=sys.stdout)

    if not args.quiet:
        print(
            f"Querying public IP from {args.url} every {args.delay} seconds",
            file=sys.stdout,
        )

    # Open CSV file - use low-level file access (instead of csv api) so that we can seek
    # back/forth after each IP query
    csv_file_handle = open(csv_filename, "w")

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
            # Seek to the start of this line so that last line
            # updates in the next iteration
            csv_file_handle.seek(csv_file_pos)

        time.sleep(args.delay)


if __name__ == "__main__":
    main()
