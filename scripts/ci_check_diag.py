#!/usr/bin/env python3
"""Headless check for the /diagnostic page using Playwright.

This script is used by CI to verify the Netlify site can reach the backend.

Usage: python3 scripts/ci_check_diag.py --url https://realdiag.netlify.app --timeout 60
"""
import argparse
import json
import sys
from playwright.sync_api import sync_playwright


def run_check(url: str, timeout: int = 60) -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page()

        # Collect console and network events for debugging
        logs = []
        page.on("console", lambda msg: logs.append(f"CONSOLE {msg.type}: {msg.text}"))
        page.on("requestfailed", lambda r: logs.append(f"REQUESTFAILED {r.url} {r.failure if r.failure else ''}"))
        page.on("response", lambda r: logs.append(f"RESPONSE {r.status} {r.url}"))

        try:
            page.goto(f"{url}/diagnostic", wait_until="networkidle", timeout=timeout * 1000)
        except Exception as e:
            print("NAV_ERROR:", e)
            for l in logs:
                print(l)
            browser.close()
            return 2

        # Wait for the diagnostic UI to populate the #result element
        try:
            page.wait_for_function("() => document.getElementById('result') && document.getElementById('result').textContent.trim() !== 'Checking backend...'", timeout=15000)
        except Exception:
            # Not fatal yet; we'll try to read whatever is present
            pass

        try:
            runtime = page.evaluate('''() => { return {runtime: window.__RUNTIME_CONFIG || null, scripts: Array.from(document.scripts).map(s=>s.src||s.innerText.slice(0,200)) } }''')
            print('PAGE_RUNTIME:', json.dumps(runtime))
        except Exception as e:
            print('RUNTIME_EVAL_ERROR:', e)

        # Read the result block
        try:
            result_text = page.evaluate("() => document.getElementById('result') ? document.getElementById('result').textContent : ''")
            print('RESULT_TEXT:\n', result_text)
        except Exception as e:
            print('RESULT_EVAL_ERROR:', e)

        # Try performing a fetch from page context to /health to ensure backend reachable
        try:
            fetch_result = page.evaluate('''async () => {
                const runtime = (window.__RUNTIME_CONFIG && window.__RUNTIME_CONFIG.NEXT_PUBLIC_API_BASE) || 'https://realdiag-software.onrender.com';
                const url = runtime + '/health';
                try {
                    const res = await fetch(url, {cache: 'no-store'});
                    const text = await res.text();
                    return {ok: res.ok, status: res.status, text, url};
                } catch (err) { return {error: String(err)}; }
            }''')
            print('FETCH_TEST:', json.dumps(fetch_result))
        except Exception as e:
            print('FETCH_EVAL_ERROR:', e)

        for l in logs:
            print(l)

        browser.close()

        # Decide exit code: success if fetch_result indicates ok
        try:
            if isinstance(fetch_result, dict) and fetch_result.get('ok'):
                return 0
            else:
                return 3
        except Exception:
            return 4


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', required=True)
    p.add_argument('--timeout', type=int, default=60)
    args = p.parse_args()

    rc = run_check(args.url, args.timeout)
    if rc == 0:
        print('Diagnostic check: OK')
    else:
        print(f'Diagnostic check: FAILED (code {rc})')
    sys.exit(rc)


if __name__ == '__main__':
    main()
