#!/usr/bin/env python3
"""Construit le wiki statique dans docs/ avec la bibliothèque standard Python."""

import json
import re
import shutil
from html import escape
from html.parser import HTMLParser
from pathlib import Path

from item_links import ItemLinks, item_url


ROOT = Path(__file__).resolve().parent
DESTINATION = ROOT.parent / "docs"


class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.headings = []
        self.heading = None

    def handle_starttag(self, tag, attrs):
        if tag in ("h2", "h3"):
            identifier = dict(attrs).get("id")
            if not identifier:
                raise ValueError("Chaque titre d’article doit avoir un id.")
            self.heading = [tag, identifier, ""]

    def handle_endtag(self, tag):
        if self.heading and self.heading[0] == tag:
            self.headings.append(self.heading)
            self.heading = None

    def handle_data(self, data):
        self.text.append(data)
        if self.heading:
            self.heading[2] += data


def render(article, body, headings, articles):
    title = escape(article["title"])
    navigation = "\n".join(
        f'<li><a href="{item["slug"]}.html"'
        + (' aria-current="page"' if item["slug"] == article["slug"] else "")
        + f'>{escape(item["title"])}</a></li>'
        for item in articles
    )
    contents = ""
    if headings:
        links = "".join(
            f'<li class="toc-{tag}"><a href="#{escape(identifier, quote=True)}">{escape(label)}</a></li>'
            for tag, identifier, label in headings
        )
        contents = f'      <nav class="toc" aria-label="Sommaire"><strong>Sommaire</strong><ul>{links}</ul></nav>\n'
    return f'''<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(article['description'], quote=True)}">
  <meta name="color-scheme" content="light dark">
  <script src="assets/theme.js"></script>
  <title>{title} — Wiki HardcoreFamiliaReborn</title>
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="assets/wiki.css">
  <script src="assets/search-index.js" defer></script>
  <script src="assets/wiki.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#article">Aller au contenu</a>
  <header class="site-header">
    <a class="wordmark" href="index.html">HardcoreFamiliaReborn <span>Le wiki des joueurs</span></a>
    <div class="header-controls">
      <form class="search" action="recherche.html" role="search">
        <label class="visually-hidden" for="search">Rechercher dans le wiki</label>
        <input id="search" name="q" type="search" placeholder="Rechercher dans le wiki" maxlength="200">
        <button type="submit">Rechercher</button>
      </form>
      <label class="theme-picker" hidden>Thème
        <select id="theme">
          <option value="system">Système</option>
          <option value="light">Clair</option>
          <option value="dark">Sombre</option>
        </select>
      </label>
    </div>
  </header>
  <div class="layout">
    <aside class="sidebar"><details open><summary>Navigation</summary><nav aria-label="Articles du wiki"><ul>{navigation}</ul></nav></details></aside>
    <main id="article" tabindex="-1">
      <div class="article-tab">Article</div>
      <h1>{title}</h1>
      <p class="subtitle">De HardcoreFamiliaReborn, le wiki des joueurs.</p>
{contents}      <article>{body}</article>
      <footer class="article-footer">Wiki de HardcoreFamiliaReborn · <a href="index.html">Accueil</a> · <a href="#article">Haut de page</a></footer>
    </main>
  </div>
</body>
</html>
'''


def write_article(article, body, navigation, search_index):
    url = article["slug"] + ".html"
    parser = ArticleParser()
    parser.feed(body)
    page = render(article, body, parser.headings, navigation)
    (DESTINATION / url).write_text(page, encoding="utf-8")
    search_index.append({
        "title": article["title"],
        "url": url,
        "description": article["description"],
        "text": re.sub(r"\s+", " ", " ".join(parser.text)).strip(),
    })


def main():
    articles = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
    items = json.loads((ROOT / "items.json").read_text(encoding="utf-8"))
    vanilla = json.loads((ROOT / "vanilla-items.json").read_text(encoding="utf-8"))
    links = ItemLinks(items, vanilla)
    DESTINATION.mkdir(exist_ok=True)
    shutil.copytree(ROOT / "assets", DESTINATION / "assets", dirs_exist_ok=True)
    search_index = []
    for article in articles:
        slug = article["slug"]
        body = (ROOT / "articles" / f"{slug}.html").read_text(encoding="utf-8")
        body = links.render(body, f"{slug}.html")
        if slug == "objets":
            catalog = "\n".join(
                f'<li>{links.anchor(item_url(item), escape(item["title"]))}</li>' for item in items
            )
            body += f'<h2 id="fiches">Fiches des objets personnalisés</h2>\n<ul class="portal-list">\n{catalog}\n</ul>'
        write_article(article, body, articles, search_index)
    for item in items:
        article = {**item, "slug": "objet-" + item["slug"]}
        description = links.link_text(item["description"], item_url(item))
        guide = escape(item["guide"], quote=True)
        body = f'<p>{description}</p>\n<p><a href="{guide}">Voir les règles et recettes détaillées</a> · <a href="objets.html#fiches">Toutes les fiches d’objet</a></p>'
        write_article(article, body, articles, search_index)
    search = {"slug": "recherche", "title": "Recherche", "description": "Rechercher un article du wiki HardcoreFamiliaReborn."}
    body = '''<p id="search-status" role="status">Saisissez un mot ou une expression dans le champ de recherche.</p>
<ol id="search-results" class="search-results"></ol>
<noscript><p>La recherche nécessite JavaScript. Vous pouvez consulter tous les articles depuis la navigation ou l’<a href="index.html">accueil</a>.</p></noscript>'''
    (DESTINATION / "recherche.html").write_text(render(search, body, [], articles), encoding="utf-8")
    (DESTINATION / "assets" / "search-index.js").write_text(
        "window.WIKI_SEARCH_INDEX = " + json.dumps(search_index, ensure_ascii=False) + ";\n", encoding="utf-8"
    )
    (DESTINATION / ".nojekyll").touch()
    print(f"Wiki généré : {len(articles)} articles, {len(items)} fiches d’objet et recherche dans {DESTINATION}")


if __name__ == "__main__":
    main()
