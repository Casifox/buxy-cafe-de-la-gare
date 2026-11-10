# Pizzeria Café de la Gare — site vitrine

Refonte moderne, rapide et accessible du site de la **Pizzeria Café de la Gare** à Buxy (71390).
Site statique en HTML, CSS et JavaScript, sans dépendance externe, prêt à être déployé.

---

## 1. Ce que contient le site

- **Accueil** (`index.html`) : hero, présentation de la maison, aperçu de la carte, galerie, avis, horaires, contact, réservation, FAQ.
- **La carte** (`menu.html`) : 27 pizzas, salades, desserts, boissons, suppléments et allergènes, avec les prix.
- **Mentions légales** (`mentions-legales.html`).
- **Politique de confidentialité** (`confidentialite.html`).
- **Page 404** (`404.html`).
- **SEO** : titres et descriptions, canonical, Open Graph, JSON-LD `Restaurant` + `FAQPage`, sitemap, `robots.txt`, `llms.txt`.
- **Performance** : images WebP + JPG avec `srcset`, polices auto-hébergées, aucun framework, aucun tracker.
- **Accessibilité** : navigation clavier, liens d'évitement, labels, `dialog` natif, contrastes, `prefers-reduced-motion`.
- **Mobile** : menu plein écran, barre d'actions fixe « Réserver / Appeler », mise en page responsive.

---

## 2. Structure des fichiers

```text
Buxy de la gare/
├── index.html
├── menu.html
├── mentions-legales.html
├── confidentialite.html
├── 404.html
├── favicon.svg
├── site.webmanifest
├── robots.txt
├── sitemap.xml
├── llms.txt
├── _headers                     # en-têtes Netlify
├── .htaccess                    # en-têtes / cache Apache
├── assets/
│   ├── css/styles.css
│   ├── js/head.js
│   ├── js/main.js
│   ├── img/                     # images optimisées (WebP + JPG)
│   └── fonts/                   # Playfair Display + Inter (WOFF2)
├── tools/
│   ├── prepare_images.py        # régénère les images depuis les sources
│   └── preview.html             # prévisualisation desktop / tablette / mobile
└── README.md
```

---

## 3. Prévisualiser en local

Le site est statique. Pour un rendu fidèle (chemins versionnés, `dialog`, prévisualisation), lancez un petit serveur local :

```bash
cd buxy-cafe-de-la-gare
python -m http.server 8090
```

Puis ouvrir <http://localhost:8090/>.

Pour tester les trois tailles d'écran : <http://localhost:8090/tools/preview.html>.

---

## 4. Déploiement

### Netlify (recommandé pour aller vite)

1. Glisser le dossier sur <https://app.netlify.com/drop> ou connecter le dépôt Git.
2. Le fichier `_headers` applique automatiquement les en-têtes de sécurité et de cache.
3. Ajouter le nom de domaine personnalisé dans **Domain settings**.

### GitHub Pages (déjà activé)

Le site est publié sur GitHub Pages : <https://casifox.github.io/buxy-cafe-de-la-gare/>.

Les fichiers `_headers` et `.htaccess` ne sont pas appliqués par GitHub Pages ; ils servent pour Netlify, Vercel ou OVH. Pour un domaine personnalisé, ajouter un fichier `CNAME` et configurer le domaine dans **Settings → Pages**.

### Vercel

1. Importer le dossier comme projet statique.
2. Ajouter le domaine personnalisé.
3. Reporter les en-têtes de `_headers` dans `vercel.json` si nécessaire.

### OVH / Apache

1. Envoyer les fichiers à la racine du site (`www/`).
2. Vérifier que `mod_rewrite`, `mod_headers`, `mod_deflate` et `mod_expires` sont actifs.
3. Le fichier `.htaccess` force HTTPS, gère le 404 et applique le cache.

---

## 5. À faire avant la mise en ligne (checklist)

- [ ] **Remplacer l'URL de référence** `https://casifox.github.io/buxy-cafe-de-la-gare` par le domaine définitif dans :
  - `index.html`, `menu.html`, `mentions-legales.html`, `confidentialite.html` (canonical, Open Graph, JSON-LD) ;
  - `sitemap.xml`, `robots.txt`, `llms.txt`.
- [ ] **Compléter l'hébergeur** dans `mentions-legales.html` et `confidentialite.html` (nom, adresse, téléphone — obligation LCEN).
- [ ] **Compléter le médiateur de la consommation** dans `mentions-legales.html`.
- [ ] **Confirmer les horaires** : la cuisine du jeudi est indiquée `12:00–13:30` (l'ancien site affichait `08:30–13:30`, probablement une coquille). Vérifier aussi les horaires des jours fériés.
- [ ] **Confirmer les prix et la carte** : la carte a été reprise du menu fourni. Vérifier les prix, les descriptions et les plats du moment.
- [ ] **Vérifier les allergènes** avec la cuisine et adapter la page `menu.html`.
- [ ] **Vérifier les liens sociaux** : Instagram, Facebook, TripAdvisor, Gault&Millau.
- [ ] **Tester le lien téléphonique** et la réception des appels.
- [ ] **Vérifier la réception des e-mails** sur `pizzeria-cafedelagare.buxy@sfr.fr` (ou remplacer par une adresse dédiée).
- [ ] **Google Search Console** : vérifier le domaine, envoyer `sitemap.xml`.
- [ ] **Google Business Profile** : mettre à jour le lien du site, les horaires, les photos et le lien de réservation.
- [ ] **Tester Lighthouse** sur le site déployé (mobile + desktop).

---

## 6. Modifier la carte

Les plats sont dans `menu.html`, section par section (`#tomate`, `#creme`, `#salades`, `#desserts`, `#boissons`, `#supplements`, `#allergenes`).

Un plat est structuré ainsi :

```html
<article class="menu-item">
  <div class="menu-line">
    <h3 class="menu-line__name">Margherita <span class="badge">V</span></h3>
    <span class="menu-line__dots" aria-hidden="true"></span>
    <span class="menu-line__price">9,50 €</span>
  </div>
  <p>Mozzarella, mozzarella de bufala.</p>
</article>
```

- `.badge` = repère végétarien.
- Pour ajouter une catégorie : dupliquer une `<section class="container menu-section" id="...">` et ajouter le lien correspondant dans `.menu-nav`.
- Pour modifier un prix : changer uniquement le texte `9,50 €`.
- Les prix sont aussi repris dans l'aperçu de l'accueil (`index.html`, section `#carte`) : penser à les synchroniser.

## 7. Modifier les horaires

Les horaires sont à **deux endroits** :

1. Le tableau visible dans `index.html` (section `#horaires`).
2. Le calcul du statut « ouvert / fermé » dans `assets/js/main.js` (constante `SCHEDULE`).

Le statut utilise le fuseau `Europe/Paris` et affiche automatiquement « Ouvert maintenant · jusqu'à 22:45 » ou « Fermé · réouverture… ».

## 8. Modifier les images

Le script `tools/prepare_images.py` régénère les variantes WebP/JPG, l'image Open Graph et les icônes à partir d'un dossier de sources :

```bash
python tools/prepare_images.py "chemin/vers/sources" "assets/img"
```

Les sources actuelles proviennent des photos du site existant. Pour remplacer une photo, conserver le même nom de fichier ou adapter les balises `<picture>` dans `index.html`.

## 9. Choix techniques

- **Aucun cookie, aucun tracker** : pas de Google Analytics, pas de pixel, pas de Google Fonts. Le site est donc dispensé de bandeau de consentement. Si vous ajoutez un outil de mesure d'audience, préférez une solution sans cookie (Plausible, Matomo en mode sans cookie) et mettez à jour la politique de confidentialité.
- **Polices auto-hébergées** : Playfair Display (titres) + Inter (texte), en WOFF2, avec `font-display: swap`.
- **Images** : WebP prioritaire, JPG en secours, `srcset` et `sizes`, largeur/hauteur pour éviter les décalages de mise en page.
- **JavaScript** : un seul fichier, sans dépendance. Le site reste lisible sans JS (le statut affiche un texte par défaut, les photos restent visibles, la réservation se fait par téléphone).
- **Cache** : les fichiers CSS/JS sont appelés avec `?v=20261110b`. Si vous modifiez `styles.css`, `head.js` ou `main.js`, changez ce numéro dans les pages HTML pour forcer le rechargement.
- **Sécurité** : CSP stricte, HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` via `_headers` / `.htaccess`. Si vous intégrez une carte Google ou un widget externe, adaptez la CSP.
- **Accessibilité** : `dialog` natif pour le menu mobile et la galerie, focus visible, `aria-label`, contrastes vérifiés, respect de `prefers-reduced-motion`.

## 10. Limites connues

- **Réservation** : elle se fait par téléphone. Pour une vraie réservation en ligne, brancher un service (TheFork, Google Reserve, Formspree…) et ajouter un formulaire dédié.
- **Commande à emporter** : pas de paiement en ligne. Le site renvoie vers le téléphone. Un click & collect pourra être ajouté plus tard.
- **Avis** : les notes affichées sont des repères publics (TripAdvisor, Google, Gault&Millau) avec liens. Elles ne sont pas mises à jour automatiquement.
- **Photos** : certaines proviennent du site existant et ont une résolution limitée (hero 1200 px, logo 42 px). Une nouvelle séance photo améliorerait encore le rendu.
- **Langues** : le site est en français. Une version anglaise pourra être ajoutée (utile pour les touristes de passage en Côte chalonnaise).

## 11. Crédits

- Photos et identité : **Pizzeria Café de la Gare**.
- Polices : Playfair Display et Inter (Google Fonts, licence SIL Open Font License), auto-hébergées.
- Développement : site statique réalisé pour la maison, 2026.

---

**Contact du restaurant** : 2 place de la Gare, 71390 Buxy — 03 58 93 36 13 — `pizzeria-cafedelagare.buxy@sfr.fr`
