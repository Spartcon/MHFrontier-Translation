# Guide de style FR — MHFrontier

Conventions de rédaction pour la traduction française de MHFrontier.
S'applique à tout `target` dans `translations/fr/**/*.csv`.

## 1. Adresse au joueur

- **Tutoyer** le joueur (« Tu as obtenu un objet rare ! »).
  Cohérent avec les MH officiels FR récents et le ton communautaire.
- Les PNJ peuvent vouvoyer le joueur si le contexte le justifie
  (gardes de guilde formels, dialogues de cour) — décision au cas
  par cas, signaler dans le commit.

## 2. Typographie française

- Guillemets français : **« texte »** (avec espaces insécables si
  possible). Jamais `"…"` sauf à l'intérieur de balises de contrôle.
- Ligature **œ** (cœur, sœur, œuf) — jamais `oe`.
- Apostrophe courbe `'` non requise ; l'apostrophe droite `'` est
  acceptable car le moteur ne rend pas toujours les caractères Unicode
  étendus.
- Espaces avant `:` `;` `!` `?` `»` : **omettre** dans les chaînes UI
  courtes (contraintes de largeur écran). Conserver dans les
  descriptions longues si la place le permet.
- Majuscules accentuées : **À É È** sont OK et préférables.

### 2bis. Encodage Shift-JIS — pièges pour les accents

Les binaires du jeu sont encodés en **Shift-JIS** (CP932), pas en
UTF-8. La pipeline FrontierTextHandler gère la conversion, mais
plusieurs pièges subsistent côté contributeur :

- **Tous les caractères latins accentués FR existent en Shift-JIS**
  (é è ê à â ô ù û î ç œ Œ æ « »), encodés sur 2 octets via le
  bloc « extensions latines » de CP932. Les utiliser librement.
- **MAIS** : si une chaîne FR transite par un outil intermédiaire
  qui suppose de l'ASCII ou du Latin-1 (un éditeur mal configuré,
  un script `sed`, un copier-coller via un terminal en mauvais
  locale), les octets accentués peuvent être réinterprétés et
  produire du **mojibake** (`Ã©` au lieu de `é`, `â€¦` au lieu de
  `…`). Une fois injecté dans le `.bin`, c'est invisible jusqu'au
  test en jeu.
- **Toujours éditer les CSV en UTF-8** (paramètre par défaut de
  Python, VS Code, etc.). Les scripts du repo lisent et écrivent
  en UTF-8 ; la conversion vers Shift-JIS se fait **uniquement**
  au moment de `build_bins.py` / `--csv-to-bin`.
- **Ne jamais ouvrir un CSV avec Excel** sans passer par
  l'assistant d'import (Excel devine mal l'encodage et corrompt
  silencieusement les accents au prochain enregistrement).
- **Caractères à éviter** car absents de Shift-JIS ou rendus
  différemment : tirets cadratins fantaisie (`—` est OK, `⸺`
  ne l'est pas), guillemets « courbes » anglais `“ ”` (préférer
  `« »`), apostrophe typographique `'` (préférer `'` droite —
  voir plus haut), espaces fines/insécables Unicode exotiques.
- En cas de doute, après `build_bins.py`, **`grep` le binaire
  produit pour la chaîne FR** (en Shift-JIS via
  `iconv -f utf-8 -t shift_jis`) et vérifier qu'elle apparaît
  sans corruption.

## 3. Longueur & contraintes UI

Le jeu a été conçu pour du texte japonais : un caractère JP occupe
visuellement la place d'environ deux caractères latins. Les boîtes
de l'UI (menus, items, boutons, infobulles) sont **dimensionnées
pour la version JP**. Quand une chaîne dépasse, le moteur **ne
tronque pas et ne renvoie pas à la ligne** : le texte **déborde**
hors de sa boîte et chevauche les éléments voisins (autres
libellés, bordures, icônes). Le résultat est lisible mais visuellement
cassé, et il n'y a aucun avertissement à la compilation.

Conséquences pratiques pour le traducteur :

- **Compter les caractères source, pas les mots.** Une chaîne JP
  de 8 caractères = ~16 caractères latins maximum, pas davantage.
- **Règle empirique** : ne pas dépasser **1.3× la longueur EN** si
  une version EN existe (l'EN a déjà subi la même contrainte et
  sert de plafond raisonnable). Sans EN, viser **≤ 2× le nombre
  de caractères JP**.
- **Abréger plutôt que laisser déborder.** « Méga potion » plutôt
  que « Potion méga-puissante » ; « Fusarb. léger » est acceptable
  dans une infobulle si « Fusarbalète léger » déborde sur l'élément
  voisin.
- **Tester en jeu** les chaînes à forte visibilité (noms d'armes,
  menus principaux) avant de figer la traduction — c'est le seul
  moyen fiable de repérer un débordement qui chevauche un libellé
  ou une icône adjacente.
- Pour les descriptions multi-lignes, **respecter le nombre de
  segments** délimités par les balises `<join at="...">` (voir §5).
  Chaque segment correspond à une ligne à l'écran avec sa propre
  largeur maximale — ne pas « rééquilibrer » en déplaçant du texte
  d'un segment à l'autre.

## 4. Casse des noms propres et objets

- Noms d'armes / armures / objets : **première lettre en majuscule**,
  reste en minuscules sauf nom propre. Ex : `Épée d'os`, `Casque en
  fer`, `Potion`.
- Noms de monstres : casse Mogapédia (Rathalos, Tigrex, Espinas).
- Noms de quêtes : majuscule initiale uniquement, sauf noms propres.

## 5. Codes de contrôle — RÈGLE CRITIQUE

Les balises `<join at="NNNN">`, `<color …>`, `<icon …>` et autres
codes binaires intégrés au texte **ne doivent JAMAIS être traduits,
supprimés, ni réordonnés**. FTH ≥ 1.5.1 réécrit les offsets `at=…`
au moment de l'application, mais le **nombre** et l'**ordre** des
balises doivent rester identiques à la source.

- Copier les balises telles quelles depuis la colonne `source`.
- Le texte FR s'insère **entre** les balises, en respectant la
  segmentation visuelle (chaque segment = une ligne à l'écran).
- Ne pas ajouter de balises absentes de la source.
- Les lignes contenant **uniquement** des codes de contrôle
  (~6 643 lignes recensées) doivent rester avec `target` vide.

## 6. Lignes spéciales à laisser vides

- Lignes `dummy` dans `dat/items/source.csv` (1 211 entrées) :
  `target` vide, ne s'affichent pas en jeu.
- Lignes ne contenant que ponctuation ou séparateurs (`−−−−−−`,
  espaces, points) : recopier la source telle quelle.
- Lignes dont la `source` est en anglais (pollution documentée
  dans CLAUDE.md §« Known data quality issues ») : traduire **depuis
  l'anglais** en signalant le cas dans le commit ; ne pas inventer
  de japonais hypothétique.

## 7. Cohérence terminologique

- Toujours consulter `docs/glossary.fr.md` avant de traduire un
  terme récurrent.
- Si un terme manque au glossaire et apparaît plusieurs fois,
  **ajouter l'entrée au glossaire d'abord**, puis traduire.
- Réutiliser les `target` déjà présents dans d'autres CSV pour
  une `source` identique (mémoire de traduction implicite).

## 8. Ton et registre

- Descriptions d'objets / d'armes : ton **factuel et concis**,
  pas de fioriture marketing. Style proche d'un manuel de jeu.
- Dialogues PNJ et scénario : conserver le **ton** du japonais
  (formel, familier, archaïque) ; l'anglais existant est souvent
  trop neutre — s'autoriser à remonter à la source JP en cas de
  doute.
- Pas d'humour ajouté ni de références culturelles FR plaquées.
  La saveur reste japonaise/médiévale-fantastique.

## 9. Workflow par section

1. Lire `docs/glossary.fr.md` et cette page.
2. Choisir **une seule section** (un seul fichier CSV) à la fois.
3. Pré-remplir les `target` triviaux par mémoire de traduction
   (exact match sur d'autres CSV).
4. Traduire les lignes restantes en respectant codes de contrôle
   et longueurs.
5. Lancer `python scripts/validate.py` avant tout commit.
6. (Optionnel) Construire le binaire avec `scripts/build_bins.py`
   et tester en jeu sur les sections à forte visibilité.

## 10. Quand demander une revue humaine

- Dialogues de scénario, monologues PNJ, textes de quêtes narratifs.
- Tout texte où la nuance culturelle compte plus que la fidélité
  littérale.
- Termes ajoutés au glossaire (validation par un membre Mogapédia).
