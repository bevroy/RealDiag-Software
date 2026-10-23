"""
The real client IP for rate limiting and audit logs.

Production runs behind Cloudflare and Render's proxy. gunicorn/uvicorn only
honour X-Forwarded-For from 127.0.0.1 by default (FORWARDED_ALLOW_IPS), and
Render's proxy connects from a private address, so request.client.host is the
proxy, not the user: every user shared one rate-limit bucket.

client_ip() trusts forwarding headers only when the connection itself comes
from a trusted proxy (private/loopback ranges by default), so a client that
connects directly cannot spoof its address:

1. CF-Connecting-IP / True-Client-IP (set by Cloudflare, which overwrites any
   value the client sent), then
2. the right-most X-Forwarded-For entry that is not itself a trusted proxy
   (Render appends to, rather than replaces, a client-supplied header, so the
   left-most entry is not trustworthy), then
3. the connecting address.

Configuration (environment):
  TRUSTED_PROXY_CIDRS  comma-separated networks whose connections may set the
                       headers above (default: private and loopback ranges).
  CLIENT_IP_HEADERS    comma-separated single-IP headers to prefer
                       (default: CF-Connecting-IP,True-Client-IP).

Do not set FORWARDED_ALLOW_IPS=* on the server: uvicorn would then replace
request.client with the left-most, client-controlled X-Forwarded-For value.
"""
from __future__ import annotations

import ipaddress
import os
from typing import Iterable, List, Optional

DEFAULT_TRUSTED_PROXY_CIDRS = (
    "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,127.0.0.0/8,::1/128,fc00::/7"
)
DEFAULT_CLIENT_IP_HEADERS = "CF-Connecting-IP,True-Client-IP"


def _networks(spec: str) -> List[ipaddress._BaseNetwork]:
    out = []
    for part in (spec or "").split(","):
        part = part.strip()
        if part:
            out.append(ipaddress.ip_network(part, strict=False))
    return out


def _parse_ip(value: Optional[str]) -> Optional[ipaddress._BaseAddress]:
    if not value:
        return None
    value = value.strip().strip('"')
    if value.startswith("[") and "]" in value:  # [v6]:port
        value = value[1:value.index("]")]
    elif value.count(":") == 1:  # v4:port
        value = value.split(":", 1)[0]
    try:
        return ipaddress.ip_address(value)
    except ValueError:
        return None


def _trusted(ip, networks: Iterable) -> bool:
    return any(ip.version == n.version and ip in n for n in networks)


def resolve_client_ip(peer: Optional[str], headers, trusted_proxy_cidrs: Optional[str] = None,
                      client_ip_headers: Optional[str] = None) -> str:
    """Pure function behind client_ip(); `headers` is any case-insensitive mapping."""
    networks = _networks(trusted_proxy_cidrs if trusted_proxy_cidrs is not None
                         else os.getenv("TRUSTED_PROXY_CIDRS", DEFAULT_TRUSTED_PROXY_CIDRS))
    header_names = [h.strip() for h in (client_ip_headers if client_ip_headers is not None
                    else os.getenv("CLIENT_IP_HEADERS", DEFAULT_CLIENT_IP_HEADERS)).split(",") if h.strip()]

    peer_ip = _parse_ip(peer)
    if peer_ip is None:
        return peer or "unknown"
    if not _trusted(peer_ip, networks):
        return str(peer_ip)

    for name in header_names:
        ip = _parse_ip(headers.get(name))
        if ip is not None:
            return str(ip)

    forwarded = [_parse_ip(p) for p in (headers.get("X-Forwarded-For") or "").split(",")]
    for ip in reversed([ip for ip in forwarded if ip is not None]):
        if not _trusted(ip, networks):
            return str(ip)

    return str(peer_ip)


def client_ip(request) -> str:
    """Real client IP for a Starlette/FastAPI request (also slowapi's key_func)."""
    peer = request.client.host if getattr(request, "client", None) else None
    return resolve_client_ip(peer, request.headers)


def client_ip_debug(request) -> dict:
    """What the server sees, for checking the proxy setup after a deploy."""
    names = [h.strip() for h in os.getenv("CLIENT_IP_HEADERS", DEFAULT_CLIENT_IP_HEADERS).split(",") if h.strip()]
    return {
        "connecting_address": request.client.host if getattr(request, "client", None) else None,
        "headers": {name: request.headers.get(name) for name in names + ["X-Forwarded-For", "X-Real-IP"]},
        "resolved_client_ip": client_ip(request),
        "trusted_proxy_cidrs": os.getenv("TRUSTED_PROXY_CIDRS", DEFAULT_TRUSTED_PROXY_CIDRS),
        "forwarded_allow_ips": os.getenv("FORWARDED_ALLOW_IPS", "(unset: 127.0.0.1,::1)"),
    }
