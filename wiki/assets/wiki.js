"use strict";

(() => {
  const status = document.querySelector("#search-status");
  if (!status) return;

  const input = document.querySelector("#search");
  const results = document.querySelector("#search-results");
  const query = (new URLSearchParams(window.location.search).get("q") || "").trim().slice(0, 200);
  input.value = query;
  if (!query) return;

  const normalize = value => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("fr");
  const terms = normalize(query).split(/[^a-z0-9]+/).filter(Boolean);
  if (!terms.length) {
    status.textContent = "Saisissez au moins une lettre ou un chiffre.";
    return;
  }
  const matches = (window.WIKI_SEARCH_INDEX || []).map(article => {
    const title = normalize(article.title);
    const text = normalize(`${article.title} ${article.description} ${article.text}`);
    if (!terms.every(term => text.includes(term))) return null;
    return { ...article, score: terms.filter(term => title.includes(term)).length };
  }).filter(Boolean).sort((a, b) => b.score - a.score || a.title.localeCompare(b.title, "fr"));

  status.textContent = matches.length
    ? `${matches.length} article${matches.length > 1 ? "s" : ""} pour « ${query} ».`
    : `Aucun article pour « ${query} ». Essayez un mot plus court, ou consultez la navigation.`;

  for (const article of matches) {
    const item = document.createElement("li");
    const heading = document.createElement("h2");
    const link = document.createElement("a");
    link.href = article.url;
    link.textContent = article.title;
    heading.append(link);
    const description = document.createElement("p");
    description.textContent = article.description;
    item.append(heading, description);
    results.append(item);
  }
})();
