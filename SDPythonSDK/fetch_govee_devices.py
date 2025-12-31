#!/usr/bin/env python3
import argparse
import json
import os
import sys

import requests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Govee devices using the OpenAPI endpoint."
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("GOVEE_API_KEY"),
        help="Govee API key (or set GOVEE_API_KEY).",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print raw response text instead of pretty JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.api_key:
        print("Missing API key. Use --api-key or set GOVEE_API_KEY.", file=sys.stderr)
        return 2

    url = "https://openapi.api.govee.com/router/api/v1/user/devices"
    headers = {"Govee-API-Key": args.api_key}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1

    if args.raw:
        print(resp.text)
        return 0 if resp.ok else 1

    try:
        data = resp.json()
    except ValueError:
        print(resp.text)
        return 1

    print(json.dumps(data, indent=2))
    return 0 if resp.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
