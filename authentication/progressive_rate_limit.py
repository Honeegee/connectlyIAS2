"""
Progressive Rate Limiting with Exponential Backoff
Implements progressive delays for repeated failed authentication attempts
"""

import time
from django.core.cache import cache
from django.conf import settings
from .rate_limit_utils import get_client_ip
from singletons.logger_singleton import LoggerSingleton

logger = LoggerSingleton().get_logger()

class ProgressiveRateLimit:
    """
    Implements progressive rate limiting with exponential backoff
    for repeated failed authentication attempts.
    """
    
    def __init__(self):
        self.base_rate = '5/m'  # Base rate limit
        self.max_delay = 300  # Maximum delay in seconds (5 minutes)
        self.failed_attempts_key = 'failed_auth_attempts:{}'
        self.lockout_key = 'auth_lockout:{}'
    
    def get_failed_attempts_count(self, ip_address):
        """Get the number of failed authentication attempts for an IP"""
        key = self.failed_attempts_key.format(ip_address)
        return cache.get(key, 0)
    
    def increment_failed_attempts(self, ip_address):
        """Increment failed authentication attempts counter"""
        key = self.failed_attempts_key.format(ip_address)
        current_count = cache.get(key, 0)
        new_count = current_count + 1
        
        # Store for 1 hour to allow gradual decay
        cache.set(key, new_count, timeout=3600)
        
        logger.warning(f"Failed authentication attempt #{new_count} from IP: {ip_address}")
        return new_count
    
    def reset_failed_attempts(self, ip_address):
        """Reset failed authentication attempts counter (on successful auth)"""
        key = self.failed_attempts_key.format(ip_address)
        cache.delete(key)
        logger.info(f"Reset failed authentication attempts for IP: {ip_address}")
    
    def calculate_delay(self, failed_attempts):
        """
        Calculate progressive delay based on failed attempts
        Uses exponential backoff with jitter
        """
        if failed_attempts <= 5:
            return 0  # No delay for first 5 attempts
        
        # Exponential backoff: 2^(n-5) seconds, capped at max_delay
        delay = min(2 ** (failed_attempts - 5), self.max_delay)
        
        # Add jitter (±20%) to prevent synchronized retries
        jitter = delay * 0.2
        delay_with_jitter = delay + (jitter * (2 * (hash(ip_address) % 100) / 100 - 1))
        
        return int(delay_with_jitter)
    
    def is_locked_out(self, ip_address):
        """Check if IP is currently locked out"""
        lockout_key = self.lockout_key.format(ip_address)
        return cache.get(lockout_key, False)
    
    def apply_lockout(self, ip_address, duration):
        """Apply temporary lockout to an IP"""
        lockout_key = self.lockout_key.format(ip_address)
        cache.set(lockout_key, True, timeout=duration)
        logger.warning(f"Applied {duration}s lockout for IP: {ip_address}")
    
    def get_rate_limit_info(self, ip_address):
        """
        Get current rate limiting status for an IP
        Returns dict with rate limit information
        """
        failed_attempts = self.get_failed_attempts_count(ip_address)
        current_delay = self.calculate_delay(failed_attempts)
        is_locked = self.is_locked_out(ip_address)
        
        return {
            'ip_address': ip_address,
            'failed_attempts': failed_attempts,
            'current_delay': current_delay,
            'is_locked_out': is_locked,
            'remaining_attempts': max(0, 5 - failed_attempts),
            'suggested_retry_after': current_delay if is_locked else 0
        }


# Global instance
progressive_rate_limit = ProgressiveRateLimit()


def get_progressive_rate_limit_key(group, request):
    """
    Custom rate limit key function that incorporates progressive delays
    """
    ip_address = get_client_ip(group, request)
    
    # Check if IP is locked out
    if progressive_rate_limit.is_locked_out(ip_address):
        return f"locked_out:{ip_address}"
    
    # Get failed attempts count
    failed_attempts = progressive_rate_limit.get_failed_attempts_count(ip_address)
    
    # Apply progressive rate limiting
    if failed_attempts > 10:
        # After 10 failed attempts, apply 5-minute lockout
        progressive_rate_limit.apply_lockout(ip_address, 300)
        return f"locked_out:{ip_address}"
    elif failed_attempts > 5:
        # After 5 failed attempts, reduce rate limit
        return f"progressive:{ip_address}:{failed_attempts}"
    
    # Normal rate limiting
    return f"normal:{ip_address}"


def handle_failed_authentication(request, endpoint_name):
    """
    Handle failed authentication attempt with progressive rate limiting
    """
    ip_address = get_client_ip(None, request)
    
    # Increment failed attempts counter
    failed_attempts = progressive_rate_limit.increment_failed_attempts(ip_address)
    
    # Calculate current delay
    current_delay = progressive_rate_limit.calculate_delay(failed_attempts)
    
    logger.warning(
        f"Failed authentication on {endpoint_name} from IP: {ip_address}. "
        f"Attempt #{failed_attempts}, current delay: {current_delay}s"
    )
    
    # Return rate limit information
    return {
        'error': 'Authentication failed',
        'detail': 'Invalid credentials provided',
        'rate_limit_info': progressive_rate_limit.get_rate_limit_info(ip_address)
    }


def handle_successful_authentication(request):
    """
    Handle successful authentication by resetting failed attempts
    """
    ip_address = get_client_ip(None, request)
    progressive_rate_limit.reset_failed_attempts(ip_address)
    logger.info(f"Successful authentication from IP: {ip_address}, resetting failed attempts counter")
