"""
Real client IP behind Cloudflare + Render (backend/services/client_ip.py), and
the rate-limit key: per account when signed in, per real client IP otherwise.
"""
import os

import pytest
from starlette.requests import Request

os.environ.setdefault("JWT_SECRET_KEY", "test-only-" + "a" * 32)

from backend.services.client_ip import client_ip, resolve_client_ip  # noqa: E402
from backend.services.security import rate_limit_key  # noqa: E402

RENDER_PROXY = "10.204.3.17"  # private address Render's proxy connects from


def _headers(**kv):
    return {k.replace("_", "-"): v for k, v in kv.items()}


class CI(dict):
    """Case-insensitive header mapping, like Starlette's."""
    def get(self, key, default=None):
        for k, v in self.items():
            if k.lower() == key.lower():
                return v
        return default


def resolve(peer, **headers):
    return resolve_client_ip(peer, CI(_headers(**headers)))


def test_direct_connection_ignores_forwarding_headers():
    # A client that connects directly cannot claim another address.
    assert resolve("198.51.100.7", CF_Connecting_IP="1.2.3.4", X_Forwarded_For="1.2.3.4") == "198.51.100.7"


def test_behind_render_cloudflare_header_wins():
    assert resolve(RENDER_PROXY, CF_Connecting_IP="203.0.113.9",
                   X_Forwarded_For="6.6.6.6, 203.0.113.9") == "203.0.113.9"


def test_behind_render_true_client_ip():
    assert resolve(RENDER_PROXY, True_Client_IP="203.0.113.10") == "203.0.113.10"


def test_behind_render_uses_rightmost_untrusted_forwarded_entry():
    # Render appends to a client-supplied X-Forwarded-For, so the left-most
    # entry is whatever the client sent and must not be used.
    assert resolve(RENDER_PROXY, X_Forwarded_For="6.6.6.6, 203.0.113.5") == "203.0.113.5"
    assert resolve(RENDER_PROXY, X_Forwarded_For="203.0.113.5, 10.1.2.3") == "203.0.113.5"


def test_invalid_header_values_are_ignored():
    assert resolve(RENDER_PROXY, CF_Connecting_IP="not-an-ip", X_Forwarded_For="garbage, 203.0.113.5") == "203.0.113.5"
    assert resolve(RENDER_PROXY) == RENDER_PROXY


def test_ipv6_and_ports():
    assert resolve(RENDER_PROXY, CF_Connecting_IP="2001:db8::1") == "2001:db8::1"
    assert resolve(RENDER_PROXY, X_Forwarded_For="203.0.113.5:4431") == "203.0.113.5"


def test_trusted_ranges_are_configurable():
    headers = CI({"X-Forwarded-For": "203.0.113.5"})
    # With no trusted ranges, the connecting address is always used.
    assert resolve_client_ip(RENDER_PROXY, headers, trusted_proxy_cidrs="") == RENDER_PROXY


def test_unknown_peer():
    assert resolve(None) == "unknown"


def _request(peer="203.0.113.5", headers=None, cookies=None):
    raw = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
    if cookies:
        raw.append((b"cookie", "; ".join(f"{k}={v}" for k, v in cookies.items()).encode()))
    return Request({"type": "http", "method": "GET", "path": "/", "headers": raw,
                    "client": (peer, 1234) if peer else None, "query_string": b""})


def test_client_ip_reads_a_request():
    assert client_ip(_request(RENDER_PROXY, {"CF-Connecting-IP": "203.0.113.9"})) == "203.0.113.9"


def test_rate_limit_key_is_per_account_when_signed_in():
    from backend.services.auth_service import create_access_token
    token = create_access_token("user_abc", "student@realdiag.com")
    assert rate_limit_key(_request(cookies={"access_token": token})) == "user:user_abc"
    assert rate_limit_key(_request(headers={"Authorization": f"Bearer {token}"})) == "user:user_abc"


def test_rate_limit_key_falls_back_to_client_ip():
    assert rate_limit_key(_request("198.51.100.7")) == "ip:198.51.100.7"
    assert rate_limit_key(_request("198.51.100.7", cookies={"access_token": "not-a-jwt"})) == "ip:198.51.100.7"
