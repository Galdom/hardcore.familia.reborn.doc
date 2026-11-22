"""Ajoute les liens vers les fiches d’objet dans le texte des articles."""

import re
from html import escape, unescape
from html.parser import HTMLParser


MINECRAFT_WIKI = "https://minecraft.wiki/w/"


def item_url(item):
    return f"objet-{item['slug']}.html"


class ItemLinks:
    def __init__(self, items, vanilla):
        self.targets = {}
        for page, names in vanilla.items():
            self.add_names(MINECRAFT_WIKI + page, names)
        for item in items:
            self.add_names(item_url(item), [item["title"], *item.get("aliases", [])])
        names = sorted(self.targets, key=len, reverse=True)
        alternatives = "|".join(re.escape(name).replace("’", "['’]") for name in names)
        self.pattern = re.compile(rf"(?<![\w-])(?:{alternatives})(?![\w-])", re.IGNORECASE)

    def add_names(self, target, names):
        for name in names:
            key = self.key(name)
            if self.targets.setdefault(key, target) != target:
                raise ValueError(f"Nom d’objet ambigu : {name}")

    @staticmethod
    def key(name):
        return name.casefold().replace("'", "’")

    def link_text(self, text, current_url):
        pieces = []
        end = 0
        for match in self.pattern.finditer(text):
            target = self.targets[self.key(match[0])]
            pieces.append(escape(text[end:match.start()]))
            label = escape(match[0])
            pieces.append(label if target == current_url else self.anchor(target, label))
            end = match.end()
        pieces.append(escape(text[end:]))
        return "".join(pieces)

    @staticmethod
    def anchor(target, label):
        return f'<a class="item-link" href="{escape(target, quote=True)}">{label}</a>'

    def render(self, body, current_url):
        # Les liens dont le libellé est exactement un objet pointent vers sa fiche.
        # Les autres liens éditoriaux gardent leur destination et leur libellé.
        def retarget(match):
            target = self.targets.get(self.key(unescape(match[1])))
            if target == current_url:
                return match[1]
            return self.anchor(target, match[1]) if target else match[0]

        body = re.sub(r"<a\b[^>]*>([^<]+)</a>", retarget, body)
        parser = LinkMarkup(self, current_url)
        parser.feed(body)
        parser.close()
        return "".join(parser.output)


class LinkMarkup(HTMLParser):
    def __init__(self, links, current_url):
        super().__init__()
        self.links = links
        self.current_url = current_url
        self.output = []
        self.literal_depth = 0

    def handle_starttag(self, tag, attrs):
        self.output.append(self.get_starttag_text())
        if tag in ("a", "pre", "code"):
            self.literal_depth += 1

    def handle_endtag(self, tag):
        self.output.append(f"</{tag}>")
        if tag in ("a", "pre", "code"):
            self.literal_depth -= 1

    def handle_startendtag(self, tag, attrs):
        self.output.append(self.get_starttag_text())

    def handle_comment(self, data):
        self.output.append(f"<!--{data}-->")

    def handle_data(self, data):
        self.output.append(
            escape(data, quote=False) if self.literal_depth
            else self.links.link_text(data, self.current_url)
        )
