# Rapport — ateliers Views TransConnect

## Parcours livrés

Les routes par application sont incluses depuis `config/urls.py` et disposent de namespaces (`expeditions`, `vehicules`, `offres`, `entreprises`). Les listes et détails utilisent `ListView` et `DetailView`. Les fonctions FBV de lecture et de suppression restent dans les fichiers `views.py` comme référence de la migration ; les routes Web actives utilisent les CBVs.

Les trois entités centrales disposent de vues de création, modification et suppression. Les formulaires de création/modification sont des `ModelForm` à champs explicites. La page Entreprises fournit la liste, le détail et la navigation vers les expéditions ou les véhicules associés. Les templates héritent de `base.html`, affichent un état vide avec `{% empty %}` et utilisent notamment les filtres `title`, `upper`, `capfirst`, `yesno`, `pluralize` et `linebreaks`, en plus des filtres de l'exemple du cours.

Les suppressions affichent une confirmation en GET et ne suppriment qu'après POST avec `{% csrf_token %}`. `CreateView` et `UpdateView` redirigent après une sauvegarde réussie.

## Comparaison FBV / CBV

Une FBV rend le cheminement de la requête très visible dans une fonction : charger les objets, préparer le contexte, puis appeler `render()` ou `redirect()`. C'est direct pour une règle propre à une page, mais la liste, le détail, les formulaires et les confirmations répètent du code.

Les CBVs fournissent ce comportement standard avec moins de code répétitif. `get_queryset()`, `get_context_data()`, `get_form()` et `form_valid()` restent les points de personnalisation. Le comportement hérité est moins visible à la lecture et demande de connaître la classe générique utilisée. Ici, les listes et détails sont concis ; l'offre exige davantage de personnalisation pour fixer le transporteur, filtrer les choix et transformer les erreurs métier en erreurs de formulaire.

## Revue Mass Assignment

| Formulaire | Champs acceptés du client | Valeurs gardées côté serveur |
|---|---|---|
| Expédition | villes, poids, date souhaitée, description | entreprise propriétaire et statut |
| Véhicule | immatriculation, type, capacité | entreprise propriétaire et disponibilité |
| Nouvelle offre | expédition, véhicule, prix, délai | transporteur, statut et dates automatiques |
| Modification d'offre | prix, délai | expédition, véhicule, transporteur et statut |

La création d'offre ne propose que les expéditions publiées et les véhicules disponibles du transporteur sélectionné. Les erreurs `ValidationError` provenant des règles métier sont présentées comme erreurs générales du formulaire. Les mises à jour d'offre ne s'appliquent qu'aux propositions appartenant au transporteur du contexte et encore au statut `proposee`.

L'identifiant d'entreprise transmis dans l'URL est le mécanisme de contexte demandé par l'atelier, qui exclut l'authentification. Il n'identifie pas de manière fiable la personne qui envoie la requête et ne remplace donc pas une permission d'accès.

## Limites de vérification

La version disponible dans l'environnement est Python 3.12.6 ; le prérequis du dossier d'étude de cas indique Python 3.13 ou 3.14. Les contrôles ont été exécutés avec Python 3.12.6. Le positionnement personnel des acquis d'apprentissage reste à remplir par l'étudiante.
