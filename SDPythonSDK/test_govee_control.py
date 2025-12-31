#!/usr/bin/env python3
import argparse
import os
import sys
import uuid

import requests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a Govee control command via the OpenAPI endpoint."
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("GOVEE_API_KEY"),
        help="Govee API key (or set GOVEE_API_KEY).",
    )
    parser.add_argument(
        "--device",
        default=os.environ.get("GOVEE_DEVICE"),
        help="Device MAC (or set GOVEE_DEVICE).",
    )
    parser.add_argument(
        "--sku",
        default=os.environ.get("GOVEE_SKU"),
        help="Device SKU (or set GOVEE_SKU).",
    )
    parser.add_argument(
        "--value",
        choices=["on", "off"],
        default="on",
        help="Power value to send (on/off).",
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
    if not args.device:
        print("Missing device. Use --device or set GOVEE_DEVICE.", file=sys.stderr)
        return 2
    if not args.sku:
        print("Missing SKU. Use --sku or set GOVEE_SKU.", file=sys.stderr)
        return 2

    url = "https://openapi.api.govee.com/router/api/v1/device/control"
    headers = {"Govee-API-Key": args.api_key, "Content-Type": "application/json"}
    payload = {
        "requestId": uuid.uuid4().hex,
        "payload": {
            "sku": args.sku,
            "device": args.device,
            "capability": {
                "type": "devices.capabilities.on_off",
                "instance": "powerSwitch",
                "value": 1 if args.value == "on" else 0,
            },
        },
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
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

    print(data)
    return 0 if resp.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
