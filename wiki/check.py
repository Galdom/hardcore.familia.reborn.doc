#!/usr/bin/env python3
"""Vérifie les références et les invariants du wiki généré, sans dépendance."""

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent / "docs"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.ids = set()
        self.references = []
        self.titles = 0
        self.tables = 0
        self.captions = 0
        self.headers = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        identifier = attributes.get("id")
        if identifier:
            assert identifier not in self.ids, f"{self.path.name}: id dupliqué {identifier}"
            self.ids.add(identifier)
        for attribute in ("href", "src", "action"):
            if attribute in attributes:
                self.references.append(attributes[attribute])
        self.titles += tag == "h1"
        self.tables += tag == "table"
        self.headers += tag == "thead"


def main():
    pages = {}
    for path in sorted(ROOT.glob("*.html")):
        parser = Page(path)
        parser.feed(path.read_text(encoding="utf-8"))
        assert parser.titles == 1, f"{path.name}: il faut exactement un h1"
        assert parser.tables == parser.headers, f"{path.name}: tableau sans en-tête"
        pages[path.resolve()] = parser
    assert pages, "Le site doit être généré avant la vérification."
    count = 0
    for path, page in pages.items():
        for reference in page.references:
            url = urlsplit(reference)
            assert not url.scheme and not url.netloc, f"Référence externe inattendue : {reference}"
            assert not url.path.startswith("/"), f"Lien incompatible avec un sous-dossier : {reference}"
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            assert target.is_relative_to(ROOT.resolve()), f"Référence hors du site : {reference}"
            assert target.is_file(), f"{path.name}: fichier introuvable {reference}"
            if url.fragment:
                assert target in pages, f"{path.name}: ancre sur une ressource non HTML"
                assert unquote(url.fragment) in pages[target].ids, f"{path.name}: ancre introuvable {reference}"
            count += 1
    index = (ROOT / "assets" / "search-index.js").read_text(encoding="utf-8")
    entries = json.loads(index.removeprefix("window.WIKI_SEARCH_INDEX = ").removesuffix(";\n"))
    assert len(entries) == len(pages) - 1, "Index de recherche incomplet"
    for entry in entries:
        assert (ROOT / entry["url"]).resolve() in pages
        assert entry["text"], f"Article vide : {entry['title']}"
    assert (ROOT / ".nojekyll").is_file()
    print(f"OK : {len(pages)} pages, {count} références locales et {len(entries)} articles indexés.")


if __name__ == "__main__":
    main()
