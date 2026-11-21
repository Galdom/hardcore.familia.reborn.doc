# Wiki joueur — HardcoreFamiliaReborn

Wiki en français consacré aux mécaniques de jeu : Don, rituels, constructions,
objets, armes, vampirisme, lycanthropie, Mob Arenas, protections et exploration.
Présentation sobre inspirée des encyclopédies, avec navigation, sommaires,
tableaux, plans de construction et recherche locale insensible aux accents.

Dépôt : [Galdom/hardcore.familia.reborn.doc](https://github.com/Galdom/hardcore.familia.reborn.doc).

## Consulter le wiki

Ouvrir `docs/index.html` directement dans un navigateur. Les articles et la
recherche fonctionnent sans serveur, sans dépendance et sans connexion externe.

Pour servir le site localement, depuis la racine du dépôt :

```bash
python3 -m http.server 8000 --directory docs
```

Puis ouvrir <http://localhost:8000>.

## Publier sur GitHub Pages

Le site statique généré se trouve intégralement dans `docs/`. Aucun traitement
Java, Gradle, npm ou Jekyll n’est nécessaire pour le publier.

1. Ajouter, committer et pousser les fichiers dans ce dépôt GitHub, sur la branche
   `main` (ou la branche choisie pour la publication).
2. Ouvrir **Settings → Pages** dans le dépôt.
3. Dans **Build and deployment**, choisir **Deploy from a branch**.
4. Sélectionner la branche contenant les fichiers, puis le dossier **`/docs`**.
5. Enregistrer et attendre la fin du déploiement GitHub Pages.

L’adresse attendue avec ce dépôt est
<https://galdom.github.io/hardcore.familia.reborn.doc/>. Elle ne devient disponible
qu’après activation et déploiement de GitHub Pages.

Ces étapes suivent la [documentation GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
Tous les liens du site sont relatifs, ce qui permet de le servir dans le
sous-dossier du dépôt. Conserver le fichier `docs/.nojekyll`.

## Modifier le contenu

- `wiki/articles/` : articles sources en HTML, limités au contenu joueur.
- `wiki/articles.json` : titres, descriptions et ordre de navigation.
- `wiki/assets/` : feuille de style, recherche et favicon.
- `wiki/build.py` : génération des pages complètes et de l’index de recherche.
- `docs/` : résultat généré à publier et à conserver dans Git.

Après une modification :

```bash
python3 wiki/build.py
python3 wiki/check.py
node --check docs/assets/wiki.js
```

Les scripts Python utilisent uniquement la bibliothèque standard. Modifier les
sources dans `wiki/`, puis régénérer et committer aussi `docs/`. Une modification
directe des fichiers générés sera remplacée à la génération suivante.

Ajouter un `id` unique à chaque titre `h2` ou `h3` : ils alimentent le sommaire et
permettent les liens vers une section. Entourer les tableaux d’un
`<div class="table-scroll">` pour leur lecture sur téléphone.

## Périmètre éditorial

Le wiki décrit les comportements présents dans la version de travail du plugin
au moment de sa rédaction, d’après ses documents `PRODUCT.md` et le code des
mécaniques. Les commandes, permissions, réglages du serveur et détails de stockage
n’apparaissent pas dans les articles. Les instructions de publication restent
dans ce README, hors de la navigation du site.

Avant de documenter une évolution, vérifier les règles dans le dépôt du plugin,
puis mettre à jour les articles et régénérer le site. La génération du wiki ne
relit pas automatiquement le code du plugin.
