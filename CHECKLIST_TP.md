# Checklist des travaux pratiques

État comparé aux neuf documents fournis : six documents initiaux et les trois documents Views / Administration ajoutés ensuite. « Vérifié » signifie que le code correspondant existe et que la vérification indiquée a réellement été exécutée. Les auto-positionnements personnels ne sont pas remplis à la place de l'étudiante.

## Atelier Python — Partie 1

| Question | Réalisation | Fichier | État / remarque |
|---|---|---|---|
| 1.a — prénom, âge et message Hello | Saisie et affichage avec `format()` | `AteliersPython/Partie1.py` | Terminé et vérifié |
| 2.a — pair / impair | Fonction réutilisable et démonstration interactive | `AteliersPython/Partie1.py` | Terminé et vérifié |
| 3.a–b — lettres et somme de 1 à 100 | Boucle sur le mot et calcul de 5050 | `AteliersPython/Partie1.py` | Terminé et vérifié |
| 4.a–b — notes, moyenne, min et max | Liste d'exemple et calculs | `AteliersPython/Partie1.py` | Terminé et vérifié |
| 5.a–b — dictionnaire student et email | Ajout puis parcours des clés/valeurs | `AteliersPython/Partie1.py` | Terminé et vérifié |
| 6.a–c — ensemble et tuple | Déduplication et parcours du tuple | `AteliersPython/Partie1.py` | Terminé et vérifié |
| Application 1 — comptage des visites par pays | Dictionnaire de fréquences et pays le plus visité | `AteliersPython/Partie1.py` | Terminé et vérifié |
| Application 2.a–d — analyse des achats | Total, quantités, produit le plus acheté et ventes par produit | `AteliersPython/Partie1.py` | Terminé et vérifié |
| Application 3.a–h — transformations de phrase | `split`, `format`, ajout/remplacement, f-string, `join`, majuscules numérotées | `AteliersPython/Partie1.py` | Terminé et vérifié |

## Atelier Python — Partie 2

| Question | Réalisation | Fichier | État / remarque |
|---|---|---|---|
| Exemple 1 — classe Personne | Constructeur et présentation | `AteliersPython/Partie2.py` | Terminé et vérifié |
| Exemple 2 — `__str__` | Affichage de Personne | `AteliersPython/Partie2.py` | Terminé et vérifié |
| Exemple 3 — héritage Etudiant | `super()`, niveau et méthode `etudier()` | `AteliersPython/Partie2.py` | Terminé et vérifié |
| Exemple 5 — `Panier.__len__` | Longueur du panier | `AteliersPython/Partie2.py` | Terminé et vérifié |
| Exemple 6 — `Panier.__getitem__` | Accès par indice | `AteliersPython/Partie2.py` | Terminé et vérifié |
| Exemple 7 — `Produit.__eq__` | Comparaison par nom | `AteliersPython/Partie2.py` | Terminé et vérifié |
| Exemple 8 — `Point.__add__` et `__str__` | Addition des coordonnées et affichage | `AteliersPython/Partie2.py` | Terminé et vérifié |
| Exemple 9 — `Personne.__del__` | Message lors de la destruction | `AteliersPython/Partie2.py` | Terminé et vérifié |
| Étude guidée — Livre, Roman, Bibliotheque et tests | Emprunt, retour, disponibilité, ajout et liste | `AteliersPython/Partie2.py` | Terminé et vérifié |

## Étude de cas TransConnect — jalon 1

| Étape / exigence | Réalisation | Fichiers | État / remarque |
|---|---|---|---|
| Projet Django, applications de domaine et configuration | Structure `config` et quatre applications installées | `config/settings.py`, applications | Terminé et vérifié |
| `.env`, secret hors dépôt et `.gitignore` | `.env` local ignoré, modèle de variables fourni | `.env.example`, `.gitignore`, `config/settings.py` | Terminé et vérifié |
| Dépendances reproductibles | Versions Django et python-dotenv déclarées | `requirements.txt` | Terminé et vérifié |
| Branche de travail jalon 1 | Branche courante `jalon-1` | Git | Vérifié ; aucune fusion vers `main` sans validation enseignante |
| Version Python du prérequis | Projet testé avec Python 3.12.6 | Environnement local | Incomplet : l'étude de cas demande 3.13 ou 3.14, qui ne sont pas installés |
| Page de bienvenue de l'initialisation | La racine actuelle redirige vers les expéditions | `config/urls.py` | L'état historique de la page de bienvenue initiale ne peut plus être vérifié |
| Jalons 2 à 4 (API, MCP, A2A) | Le PDF les présente comme feuille de route ultérieure | — | Hors du périmètre du jalon 1 ; aucun énoncé détaillé de TP fourni |

## Workshop Models — partie 1

| Section / exigence | Réalisation | Fichiers | État / remarque |
|---|---|---|---|
| I–III — cinq modèles, relations et champs du diagramme | Utilisateur, Entreprise, Vehicule, Expedition, Offre | `*/models.py`, migrations | Terminé et vérifié |
| IV — Bug Hunt Offre, 4 anomalies | Prix texte, délai, date mise à jour, véhicule nullable corrigés | `OffresApp/models.py`, `AI_LOG.md` | Terminé et vérifié |
| V — traçabilité IA | Justifications et écarts consignés | `AI_LOG.md` | Terminé |
| VI — nom de base et migrations | Base locale `ons.sqlite3`, migrations des quatre apps | `config/settings.py`, `*/migrations/` | Terminé et vérifié |
| Auto-positionnement AA | Réflexion individuelle | — | À remplir par l'étudiante |

## Workshop Models — partie 2

| Section / exigence | Réalisation | Fichiers | État / remarque |
|---|---|---|---|
| III — identifiant utilisateur annuel, email Gmail, matricule fiscal, adresse | Validateurs, formats et générateurs | `EntreprisesApp/models.py` | Terminé et vérifié |
| III — types, capacités, poids, références annuelles | Choix, limites et génération de références | `VehiculesApp/models.py`, `ExpeditionsApp/models.py` | Terminé et vérifié |
| IV.1 — offre par transporteur | Validation de type d'entreprise | `OffresApp/models.py` | Terminé et vérifié |
| IV.2 — véhicule de la même entreprise | Validation croisée | `OffresApp/models.py` | Terminé et vérifié |
| IV.3 — offre uniquement sur expédition publiée | Validation lors de la création | `OffresApp/models.py` | Terminé et vérifié |
| IV.4 — une offre active par transporteur/expédition | Validation et contrainte unique conditionnelle | `OffresApp/models.py`, migration | Terminé et vérifié |
| IV.5 — cascade d'acceptation | Attribution de l'expédition, refus des concurrentes et indisponibilité du véhicule | `OffresApp/models.py` | Terminé et vérifié |
| IV.6–7 — disponibilité et capacité selon le type | Validation de véhicule pour une offre | `OffresApp/models.py`, `VehiculesApp/models.py` | Terminé et vérifié |
| V — migrations | Migrations créées et appliquées | `*/migrations/` | Terminé et vérifié |
| Auto-positionnement AA | Réflexion individuelle | — | À remplir par l'étudiante |

## Workshop Administration TransConnect

| Section / exigence | Réalisation | Fichiers | État / remarque |
|---|---|---|---|
| II–III — ModelAdmin, listes, filtres, recherche, tri, pagination, dates | Paramètres opérationnels pour les cinq modèles | `*/admin.py` | Terminé et vérifié |
| III — filtre calculé « En retard » | `SimpleListFilter` sur les expéditions publiées | `ExpeditionsApp/admin.py` | Terminé et vérifié |
| IV — fieldsets, champs readonly, autocomplete, badges | Personnalisation des formulaires et statuts | `*/admin.py` | Terminé et vérifié |
| IV — prix d'offre accepté en lecture seule | Règle dynamique par `get_readonly_fields()` | `OffresApp/admin.py` | Terminé et vérifié |
| V — inline véhicule / entreprise et offres / expédition | `TabularInline` éditable et `StackedInline` en lecture seule avec lien | `EntreprisesApp/admin.py`, `ExpeditionsApp/admin.py` | Terminé et vérifié |
| VI — action clôture et export CSV | Validation/sauvegarde individuelle, message et export relationnel | `ExpeditionsApp/admin.py`, `OffresApp/admin.py` | Terminé et vérifié |
| VII — seed et démonstration `.update()` vs `save()` | Deux scénarios reproduits, anomalie du premier conservée | `seed_demo.py`, base locale, `RAPPORT_ADMIN.md` | Terminé et vérifié ; seed officiel Blackboard absent, remplacement local fourni |
| VIII — dashboard d'intégrité | Six contrôles ORM, plus que les quatre demandés | `config/admin_site.py`, `templates/admin/health_check.html` | Terminé et vérifié |
| IX — rapport des contrôles et résultat | Règles, scénarios et instantané documentés | `RAPPORT_ADMIN.md` | Terminé |
| Branding admin | En-tête, titre et page d'accueil TransConnect | `config/admin_site.py` | Terminé et vérifié |
| Auto-positionnement AA | Réflexion individuelle | — | À remplir par l'étudiante |

## Workshop Views — partie 1 : FBV, URLs et templates

| Section / exigence | Réalisation | Fichiers | État / remarque |
|---|---|---|---|
| III — URLconf par application, `include()`, namespaces | Quatre URLconfs nommés et inclus au niveau projet | `*/urls.py`, `config/urls.py` | Terminé et vérifié |
| IV–VI — liste/détail FBV pour Expedition, Vehicule, Offre, Entreprise | Fonctions conservées comme références de migration | `*/views.py` | Terminé ; les routes actives emploient les CBVs de la partie 2 |
| V — templates, navigation, boucles et filtres | Base partagée, navigation nommée, états vides et filtres DTL | `templates/base.html`, `templates/{entreprises,expeditions,offres,vehicules}/` | Terminé et vérifié |
| Suppression sûre | Confirmation GET, suppression POST et protection CSRF | CBVs DeleteView, template partagé | Terminé et vérifié |
| Travail individuel — seconde entité | Listes/détails présents pour les quatre domaines | `*/views.py`, templates | Terminé et vérifié |

## Workshop Views — partie 2 : CBV et Forms

| Section / exigence | Réalisation | Fichiers | État / remarque |
|---|---|---|---|
| III — migration ListView/DetailView et contexte personnalisé | Vues génériques, filtres, relations préchargées | `*/views.py` | Terminé et vérifié |
| III — DeleteView | Confirmation GET et suppression POST pour les trois entités centrales | `*/views.py`, `templates/shared/confirm_delete.html` | Terminé et vérifié |
| IV — ModelForm explicites, CreateView et UpdateView | Expédition, véhicule et offre | `*/forms.py`, `*/views.py` | Terminé et vérifié |
| IV — CSRF et Post/Redirect/Get | Formulaires POST avec token et redirection après succès | `templates/shared/form.html`, `*/views.py` | Terminé et vérifié |
| VI — CreateView Offre sûre | `statut` et `transporteur` non exposés, choix filtrés, erreur métier rendue au formulaire | `OffresApp/forms.py`, `OffresApp/views.py` | Terminé et vérifié |
| VIII — revue d'au moins deux expositions de champs | Revue des vues Expédition, Véhicule et Offre ; listes blanches et valeurs serveur | `AI_LOG.md`, `RAPPORT_VIEWS.md` | Terminé et vérifié |
| VIII — comparaison FBV/CBV | Lisibilité, répétition et points de surcharge décrits | `RAPPORT_VIEWS.md` | Terminé |
| VII — préremplissage dynamique optionnel | `get_initial()` depuis un paramètre d'URL | — | Facultatif, non implémenté |
| Positionnement AA | Réflexion individuelle | — | À remplir par l'étudiante |

## Chapitre 04 — Administration Django

Ce chapitre est un support de cours, sans TP/livrable distinct. Ses options pertinentes pour TransConnect sont couvertes par les ModelAdmin ci-dessus : colonnes, filtres, recherche, édition de liste, pagination, navigation par date, fields/fieldsets, champs readonly, autocomplete, inlines, filtres et actions. `prepopulated_fields` ne s'applique pas aux modèles actuels, qui n'ont pas de champ slug à générer.

## Vérifications exécutées

| Commande / contrôle | Résultat |
|---|---|
| `venv\\Scripts\\python.exe manage.py check` | Aucun problème Django |
| `venv\\Scripts\\python.exe manage.py test` | 25 tests réussis ; contrôle Django inclus |
| `venv\\Scripts\\python.exe -m unittest AteliersPython.test_ateliers` | 3 tests réussis |
| `venv\\Scripts\\python.exe manage.py makemigrations --check --dry-run` | Aucune migration en attente |
| `git diff --check` | Aucun problème d'espacement |
| Version d'exécution | Python 3.12.6 ; prérequis 3.13/3.14 non satisfait dans l'environnement actuel |

## Points à valider avant remise

- Remplacer ou compléter l'environnement par Python 3.13 ou 3.14 et rejouer les vérifications.
- Remplir les auto-positionnements personnels des ateliers.
- Le commit conventionnel des nouveaux changements n'a pas été créé ; l'accès Git demandé précédemment a été refusé.
