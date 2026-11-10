#!/usr/bin/env python3
"""Petit contrôle qualité : liens internes, ancres, JSON-LD, identifiants."""
from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
SKIP_PREFIXES = ("mailto:", "tel:", "http://", "https://", "//", "data:", "javascript:")


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.scripts = []
        self._in_jsonld = False
        self._buffer = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("href", "src"):
            if key in attrs and attrs[key]:
                self.links.append(attrs[key])
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._buffer = []

    def handle_endtag(self, tag):
        if tag == "script" and self._in_jsonld:
            self.scripts.append("".join(self._buffer))
            self._in_jsonld = False

    def handle_data(self, data):
        if self._in_jsonld:
            self._buffer.append(data)


def main():
    errors = []
    warnings = []
    html_files = sorted(ROOT.glob("*.html"))
    if not html_files:
        print("Aucun fichier HTML trouvé.")
        return 1

    parsed = {}
    for path in html_files:
        collector = Collector()
        collector.feed(path.read_text(encoding="utf-8"))
        parsed[path.name] = collector

    ids_by_file = {name: set(c.ids) for name, c in parsed.items()}

    for path in html_files:
        collector = parsed[path.name]
        duplicates = {i for i in collector.ids if collector.ids.count(i) > 1}
        if duplicates:
            warnings.append(f"{path.name} : identifiants dupliqués {sorted(duplicates)}")

        for block in collector.scripts:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{path.name} : JSON-LD invalide ({exc})")

        for raw in collector.links:
            if raw.startswith(SKIP_PREFIXES) or raw == "#":
                continue

            if raw.startswith("#"):
                anchor = raw[1:]
                if anchor not in ids_by_file.get(path.name, set()):
                    errors.append(f"{path.name} : ancre introuvable {raw}")
                continue

            parsed_url = urlparse(raw)
            if parsed_url.scheme not in ("", "file"):
                continue

            if parsed_url.path:
                target = (path.parent / parsed_url.path).resolve()
                if not target.exists():
                    errors.append(f"{path.name} : fichier introuvable {raw}")
                    continue
                if parsed_url.fragment and target.suffix.lower() == ".html":
                    target_name = target.name
                    if parsed_url.fragment not in ids_by_file.get(target_name, set()):
                        errors.append(f"{path.name} : ancre introuvable {raw}")

    print(f"Fichiers HTML : {len(html_files)}")
    print(f"Erreurs : {len(errors)}")
    for error in errors:
        print("  ✗", error)
    print(f"Avertissements : {len(warnings)}")
    for warning in warnings:
        print("  !", warning)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
