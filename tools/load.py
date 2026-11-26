"""Sends blog comments to the spam filter, like readers of a busy blog would.

    python3 tools/load.py https://<your-service>.onrender.com --minutes 5

About 70% of the comments are ordinary, 10% are ordinary comments that contain
a link, and 20% are spam. At the end it prints what the clients saw, which you
can compare with what the dashboard shows. Uses only the standard library.
"""
import argparse
import json
import random
import statistics
import threading
import time
import urllib.error
import urllib.request

HAM = [
    "Great post, thanks for the clear explanation!",
    "I never thought about SLOs for a spam filter. Very useful.",
    "Could you write a follow-up about canary releases?",
    "We had exactly this problem with our deployment last month.",
    "Nice diagrams. Which tool did you use to draw them?",
    "I disagree a little: Kubernetes is worth it even for small teams.",
    "Thanks, this helped me prepare for my exam.",
    "How do you pick the bucket boundaries for the histogram?",
]
HAM_WITH_LINK = [
    "I wrote about the same topic here: https://example.org/blog/slo",
    "The Grafana docs explain this well: https://grafana.com/docs/",
    "Related talk from last year's conference: https://example.com/talk",
]
SPAM = [
    "WINNER!!! Claim your FREE crypto prize now http://example.com/win",
    "Cheap loan guaranteed, click here www.example.net",
    "Best online casino bonus offer, click http://example.com",
    "FREE BITCOIN FOR EVERY READER!!! click now",
    "Guaranteed cheap offer, limited time, click www.example.org",
]


def pick_comment():
    r = random.random()
    if r < 0.7:
        return random.choice(HAM)
    if r < 0.8:
        return random.choice(HAM_WITH_LINK)
    return random.choice(SPAM)


def post(url, text, timeout=30):
    req = urllib.request.Request(
        url + "/check",
        data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.load(res)


def wake_up(url):
    """Free Render services sleep when idle; the first request can take ~1 minute."""
    print(f"Waking up {url} ...", end="", flush=True)
    for _ in range(20):
        try:
            with urllib.request.urlopen(url + "/health", timeout=30) as res:
                health = json.load(res)
            print(f" up: version {health['version'][:7]}, prompt {health['prompt_version']}")
            return
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            print(".", end="", flush=True)
            time.sleep(5)
    raise SystemExit("\nThe service does not answer. Is the URL right? Is the Render deploy live?")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", help="base URL of the service, e.g. https://spam-filter-abcd.onrender.com")
    parser.add_argument("--minutes", type=float, default=5, help="how long to send traffic (default 5)")
    parser.add_argument("--rate", type=float, default=4, help="comments per second (default 4)")
    args = parser.parse_args()
    url = args.url.rstrip("/")

    wake_up(url)
    latencies, blocked, errors = [], [0], [0]
    lock = threading.Lock()

    def one_request():
        start = time.perf_counter()
        try:
            result = post(url, pick_comment())
        except Exception:  # noqa: BLE001 - count every failure the same way
            with lock:
                errors[0] += 1
            return
        with lock:
            latencies.append(time.perf_counter() - start)
            blocked[0] += result["spam"]

    end = time.time() + args.minutes * 60
    next_report = time.time() + 30
    print(f"Sending about {args.rate:g} comments/s for {args.minutes:g} min. Ctrl+C stops early.")
    try:
        while time.time() < end:
            threading.Thread(target=one_request, daemon=True).start()
            time.sleep(random.expovariate(args.rate))
            if time.time() >= next_report:
                with lock:
                    print(f"  {len(latencies)} answered, {errors[0]} failed")
                next_report += 30
    except KeyboardInterrupt:
        print("\nStopped.")
    time.sleep(3)  # let the last requests finish

    with lock:
        n = len(latencies)
        if not n:
            raise SystemExit("No request succeeded.")
        q = statistics.quantiles(latencies, n=100) if n >= 2 else latencies * 99
        print(f"\n{n} comments checked, {errors[0]} failed")
        print(f"blocked as spam : {blocked[0] / n:.1%}  (about 20% of the comments sent are spam)")
        print(f"client latency  : median {statistics.median(latencies):.3f} s, p99 {q[98]:.3f} s")
        print("The client latency includes the network; the dashboard shows only the model's time.")


if __name__ == "__main__":
    main()
