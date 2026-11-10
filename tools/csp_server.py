#!/usr/bin/env python3
"""Serveur local de test avec la CSP de production.

Usage : python tools/csp_server.py [port]
Puis ouvrir http://localhost:8091/ et vérifier la console du navigateur.
"""
from __future__ import annotations

import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

CSP = (
    "default-src 'self'; base-uri 'self'; object-src 'none'; "
    "frame-ancestors 'self'; form-action 'self' mailto:; "
    "img-src 'self' data:; font-src 'self'; style-src 'self'; "
    "script-src 'self'; connect-src 'self'"
)


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        super().end_headers()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8091
    root = Path(__file__).resolve().parent.parent
    handler = lambda *args, **kwargs: Handler(*args, directory=str(root), **kwargs)
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"CSP test server: http://localhost:{port}/")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
