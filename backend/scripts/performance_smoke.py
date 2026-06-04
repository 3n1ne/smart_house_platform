import argparse
import concurrent.futures
import json
import statistics
import time
from urllib import request


def parse_headers(values):
    headers = {}
    for value in values or []:
        if ":" not in value:
            raise ValueError(f"Invalid header format: {value}")
        name, header_value = value.split(":", 1)
        headers[name.strip()] = header_value.strip()
    return headers


def fetch(url, method, headers, body, timeout):
    started = time.perf_counter()
    payload = body.encode("utf-8") if body is not None else None
    req = request.Request(url, data=payload, headers=headers, method=method)
    with request.urlopen(req, timeout=timeout) as response:
        response.read()
        status = response.status
    elapsed = time.perf_counter() - started
    return status, elapsed


def percentile(values, ratio):
    if not values:
        return 0
    ordered = sorted(values)
    index = min(int(len(ordered) * ratio), len(ordered) - 1)
    return ordered[index]


def main():
    parser = argparse.ArgumentParser(description="Run a lightweight HTTP performance smoke test.")
    parser.add_argument("--url", default="http://127.0.0.1:5000/api/houses")
    parser.add_argument("--method", default="GET", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    parser.add_argument("--header", action="append", default=[], help="HTTP header, for example 'Content-Type: application/json'.")
    parser.add_argument("--body", default=None, help="Raw request body for POST/PUT/PATCH requests.")
    parser.add_argument("--body-file", default=None, help="Read raw request body from a file.")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=5)
    parser.add_argument("--target-seconds", type=float, default=2)
    args = parser.parse_args()

    headers = parse_headers(args.header)
    body = args.body
    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as file:
            body = file.read()

    latencies = []
    failures = 0
    statuses = {}
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [
            executor.submit(fetch, args.url, args.method, headers, body, args.timeout)
            for _ in range(args.requests)
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                status, elapsed = future.result()
                statuses[str(status)] = statuses.get(str(status), 0) + 1
                if status >= 400:
                    failures += 1
                latencies.append(elapsed)
            except Exception:
                failures += 1

    total_elapsed = time.perf_counter() - started
    result = {
        "url": args.url,
        "method": args.method,
        "requests": args.requests,
        "concurrency": args.concurrency,
        "failures": failures,
        "statuses": statuses,
        "total_seconds": round(total_elapsed, 4),
        "avg_seconds": round(statistics.mean(latencies), 4) if latencies else None,
        "p95_seconds": round(percentile(latencies, 0.95), 4) if latencies else None,
        "target_seconds": args.target_seconds,
        "target_met": bool(latencies) and percentile(latencies, 0.95) <= args.target_seconds and failures == 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
