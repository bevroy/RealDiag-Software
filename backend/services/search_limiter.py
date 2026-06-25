"""
Anonymous Search Rate Limiter
==============================

Implements free trial for unauthenticated diagnostic searches.
Tracks searches by IP address with configurable limits and time windows.

Default: 10 searches per week for anonymous users.
Authenticated users have unlimited searches.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException
import logging

logger = logging.getLogger(__name__)

# Configuration
FREE_SEARCH_LIMIT = 10  # Number of free searches
FREE_SEARCH_WINDOW_DAYS = 7  # Time window in days
STORAGE_CLEANUP_HOURS = 24  # Clean old entries every 24 hours

# In-memory storage for anonymous search tracking
# Format: {ip_address: {"searches": [(timestamp, tree_id)], "first_search": timestamp}}
anonymous_searches: Dict[str, Dict] = {}
last_cleanup: Optional[datetime] = None


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.
    Handles proxies and load balancers.
    """
    # Check X-Forwarded-For header (for proxies/load balancers)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded.split(",")[0].strip()
    
    # Check X-Real-IP header (nginx)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fall back to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


def cleanup_old_entries():
    """
    Remove expired search records to prevent memory bloat.
    Called periodically during search checks.
    """
    global last_cleanup, anonymous_searches
    
    now = datetime.utcnow()
    
    # Only cleanup every STORAGE_CLEANUP_HOURS
    if last_cleanup and (now - last_cleanup).total_seconds() < STORAGE_CLEANUP_HOURS * 3600:
        return
    
    logger.info("Running anonymous search cleanup...")
    cutoff = now - timedelta(days=FREE_SEARCH_WINDOW_DAYS)
    
    # Remove old IP entries
    ips_to_remove = []
    for ip, data in anonymous_searches.items():
        # Remove searches older than the time window
        data["searches"] = [
            (ts, tree_id) for ts, tree_id in data["searches"]
            if datetime.fromisoformat(ts) > cutoff
        ]
        
        # If no searches left, mark IP for removal
        if not data["searches"]:
            ips_to_remove.append(ip)
    
    # Remove IPs with no recent searches
    for ip in ips_to_remove:
        del anonymous_searches[ip]
    
    last_cleanup = now
    logger.info(f"Cleanup complete. Removed {len(ips_to_remove)} expired IPs. Active IPs: {len(anonymous_searches)}")


def get_search_stats(ip_address: str) -> Tuple[int, int, Optional[datetime]]:
    """
    Get search statistics for an IP address.
    
    Returns:
        (searches_used, searches_remaining, oldest_search_timestamp)
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(days=FREE_SEARCH_WINDOW_DAYS)
    
    if ip_address not in anonymous_searches:
        return 0, FREE_SEARCH_LIMIT, None
    
    data = anonymous_searches[ip_address]
    
    # Filter to searches within the time window
    recent_searches = [
        (ts, tree_id) for ts, tree_id in data["searches"]
        if datetime.fromisoformat(ts) > cutoff
    ]
    
    searches_used = len(recent_searches)
    searches_remaining = max(0, FREE_SEARCH_LIMIT - searches_used)
    
    oldest_search = None
    if recent_searches:
        oldest_search = datetime.fromisoformat(min(ts for ts, _ in recent_searches))
    
    return searches_used, searches_remaining, oldest_search


def check_search_limit(request: Request, tree_id: str, user_authenticated: bool = False) -> Dict:
    """
    Check if the user/IP is allowed to perform a diagnostic search.
    
    Args:
        request: FastAPI Request object
        tree_id: ID of the diagnostic tree being evaluated
        user_authenticated: Whether the user is logged in
    
    Returns:
        Dict with search allowance info:
        {
            "allowed": bool,
            "authenticated": bool,
            "searches_used": int,
            "searches_remaining": int,
            "message": str,
            "reset_date": str (ISO format, optional)
        }
    
    Raises:
        HTTPException 429: If anonymous user exceeds free search limit
    """
    # Cleanup old entries periodically
    cleanup_old_entries()
    
    # Authenticated users have unlimited searches
    if user_authenticated:
        return {
            "allowed": True,
            "authenticated": True,
            "searches_used": 0,
            "searches_remaining": "unlimited",
            "message": "Authenticated users have unlimited searches"
        }
    
    # Get client IP
    ip_address = get_client_ip(request)
    logger.info(f"Search request from IP: {ip_address}, tree: {tree_id}")
    
    # Get current stats
    searches_used, searches_remaining, oldest_search = get_search_stats(ip_address)
    
    # Check if limit exceeded
    if searches_remaining <= 0:
        # Calculate when limit will reset
        reset_date = None
        if oldest_search:
            reset_date = oldest_search + timedelta(days=FREE_SEARCH_WINDOW_DAYS)
        
        logger.warning(f"IP {ip_address} exceeded free search limit ({FREE_SEARCH_LIMIT} searches)")
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Free search limit exceeded",
                "message": f"You've used all {FREE_SEARCH_LIMIT} free diagnostic searches. Create a free account to continue with unlimited searches.",
                "searches_used": searches_used,
                "searches_remaining": 0,
                "limit": FREE_SEARCH_LIMIT,
                "window_days": FREE_SEARCH_WINDOW_DAYS,
                "reset_date": reset_date.isoformat() if reset_date else None,
                "action_required": "login",
                "login_url": "/users/login",
                "register_url": "/users/register"
            }
        )
    
    # Record this search
    now = datetime.utcnow()
    
    if ip_address not in anonymous_searches:
        anonymous_searches[ip_address] = {
            "searches": [],
            "first_search": now.isoformat()
        }
    
    anonymous_searches[ip_address]["searches"].append((now.isoformat(), tree_id))
    
    # Update stats after recording
    searches_used += 1
    searches_remaining -= 1
    
    # Prepare response
    response = {
        "allowed": True,
        "authenticated": False,
        "searches_used": searches_used,
        "searches_remaining": searches_remaining,
        "limit": FREE_SEARCH_LIMIT,
        "window_days": FREE_SEARCH_WINDOW_DAYS
    }
    
    # Add warning if getting close to limit
    if searches_remaining <= 2:
        response["warning"] = f"You have {searches_remaining} free searches remaining. Create an account for unlimited searches."
    
    # Add reset date
    if oldest_search:
        reset_date = oldest_search + timedelta(days=FREE_SEARCH_WINDOW_DAYS)
        response["reset_date"] = reset_date.isoformat()
    
    logger.info(f"IP {ip_address}: {searches_used}/{FREE_SEARCH_LIMIT} searches used, {searches_remaining} remaining")
    
    return response


def get_search_limit_info(request: Request, user_authenticated: bool = False) -> Dict:
    """
    Get search limit information without recording a search.
    Useful for displaying limit status to users.
    
    Args:
        request: FastAPI Request object
        user_authenticated: Whether the user is logged in
    
    Returns:
        Dict with search limit info
    """
    if user_authenticated:
        return {
            "authenticated": True,
            "searches_remaining": "unlimited",
            "message": "You have unlimited diagnostic searches"
        }
    
    ip_address = get_client_ip(request)
    searches_used, searches_remaining, oldest_search = get_search_stats(ip_address)
    
    response = {
        "authenticated": False,
        "searches_used": searches_used,
        "searches_remaining": searches_remaining,
        "limit": FREE_SEARCH_LIMIT,
        "window_days": FREE_SEARCH_WINDOW_DAYS
    }
    
    if oldest_search:
        reset_date = oldest_search + timedelta(days=FREE_SEARCH_WINDOW_DAYS)
        response["reset_date"] = reset_date.isoformat()
        response["message"] = f"Free trial: {searches_remaining} of {FREE_SEARCH_LIMIT} searches remaining (resets {reset_date.strftime('%Y-%m-%d')})"
    else:
        response["message"] = f"Free trial: {FREE_SEARCH_LIMIT} diagnostic searches available"
    
    if searches_remaining <= 2 and searches_remaining > 0:
        response["warning"] = "You're running low on free searches. Create an account for unlimited access!"
    
    return response


def reset_ip_searches(ip_address: str) -> bool:
    """
    Reset search count for a specific IP address.
    Useful for testing or manual intervention.
    
    Args:
        ip_address: IP address to reset
    
    Returns:
        True if IP was found and reset, False otherwise
    """
    if ip_address in anonymous_searches:
        del anonymous_searches[ip_address]
        logger.info(f"Reset search count for IP: {ip_address}")
        return True
    return False


def get_all_stats() -> Dict:
    """
    Get statistics about anonymous search usage.
    Useful for monitoring and analytics.
    
    Returns:
        Dict with overall statistics
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(days=FREE_SEARCH_WINDOW_DAYS)
    
    total_ips = len(anonymous_searches)
    total_searches = 0
    ips_at_limit = 0
    ips_near_limit = 0
    
    for ip, data in anonymous_searches.items():
        recent_searches = [
            ts for ts, _ in data["searches"]
            if datetime.fromisoformat(ts) > cutoff
        ]
        search_count = len(recent_searches)
        total_searches += search_count
        
        if search_count >= FREE_SEARCH_LIMIT:
            ips_at_limit += 1
        elif search_count >= FREE_SEARCH_LIMIT - 2:
            ips_near_limit += 1
    
    return {
        "total_tracked_ips": total_ips,
        "total_recent_searches": total_searches,
        "ips_at_limit": ips_at_limit,
        "ips_near_limit": ips_near_limit,
        "free_search_limit": FREE_SEARCH_LIMIT,
        "window_days": FREE_SEARCH_WINDOW_DAYS,
        "last_cleanup": last_cleanup.isoformat() if last_cleanup else None
    }
