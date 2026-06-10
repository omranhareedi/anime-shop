import re
import time
import html
import secrets
from collections import defaultdict
from flask import request, session, current_app


def sanitize_input(value, max_length=500):
    if not isinstance(value, str):
        value = str(value) if value is not None else ''
    value = html.escape(value.strip(), quote=True)
    return value[:max_length]


def sanitize_email(value):
    value = (value or '').strip().lower()
    return re.sub(r'[^\w@.+\-]', '', value)[:254]


def sanitize_phone(value):
    value = (value or '').strip()
    return re.sub(r'[^\d+\-() ]', '', value)[:20]


def make_token():
    return secrets.token_hex(16)


class RateLimiter:
    def __init__(self):
        self._store = defaultdict(list)

    def check(self, key=None, limit=60, window=60):
        key = key or request.remote_addr or 'unknown'
        now = time.time()
        window_start = now - window
        self._store[key] = [t for t in self._store[key] if t > window_start]
        if len(self._store[key]) >= limit:
            return False
        self._store[key].append(now)
        return True

    def get_remaining(self, key=None, limit=60, window=60):
        key = key or request.remote_addr or 'unknown'
        now = time.time()
        window_start = now - window
        active = [t for t in self._store[key] if t > window_start]
        return max(0, limit - len(active))


limiter = RateLimiter()


def build_csp(nonce):
    return (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        f"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        f"font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com https://fonts.googleapis.com; "
        f"img-src 'self' https://placehold.co data:; "
        f"connect-src 'self'; "
        f"frame-src 'none'; "
        f"object-src 'none'; "
        f"base-uri 'self'; "
        f"form-action 'self'"
    )


def apply_security_headers(response, nonce=None):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

    if nonce:
        response.headers['Content-Security-Policy'] = build_csp(nonce)

    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


def configure_session(app):
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=app.config.get('SESSION_COOKIE_SECURE', False),
        SESSION_PERMANENT=True,
        PERMANENT_SESSION_LIFETIME=7200,
    )


def sanitize_form_data(form_dict, fields):
    result = {}
    for key, rules in fields.items():
        value = form_dict.get(key, '')
        if rules.get('type') == 'email':
            result[key] = sanitize_email(value)
        elif rules.get('type') == 'phone':
            result[key] = sanitize_phone(value)
        else:
            result[key] = sanitize_input(value, rules.get('max_length', 500))
    return result
