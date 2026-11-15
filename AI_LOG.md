# Journal d'utilisation de l'IA

## Entrée — 2026-11-14 — modèles et administration TransConnect

- Outil IA utilisé : assistant de programmation (Codex).
- Prompt utilisateur, résumé : poursuivre et terminer les travaux pratiques TransConnect fournis, vérifier les règles des modèles et de l'administration, puis documenter les écarts.
- Sortie obtenue : implémentation des modèles, migrations, administration personnalisée, commande locale `seed_demo` et tableau de bord d'intégrité.
- Écarts identifiés par rapport au premier jet Offre de l'énoncé Models, partie 1 : `prix` ne devait pas être du texte ; `delai_jours` devait interdire les valeurs négatives ou nulles ; `date_proposition` devait être définie à la création et non à chaque mise à jour ; `vehicule` ne devait pas être nullable.
- Corrections et justification : `DecimalField` avec minimum positif, entier positif avec minimum 1, `DateField(auto_now_add=True)` et clé étrangère obligatoire. Les règles métier et la cascade sont exécutées par `clean()`/`save()`.
- Limites : les fichiers de seed officiels annoncés sur Blackboard n'étaient pas dans le dossier. Une commande locale de démonstration a été créée et cette différence est signalée dans le rapport d'administration.

## Entrée — 2026-11-14 — vues, formulaires et revue des champs

- Outil IA utilisé : assistant de programmation (Codex).
- Prompt utilisateur, résumé : intégrer les ateliers Views FBV/URLs/Templates et CBV/Forms ainsi que le chapitre d'administration au projet existant.
- Sortie obtenue : vues FBV conservées comme références, routes actives avec CBVs génériques, ModelForms à champs explicites, templates partagés et tests des parcours Web.
- `fields = '__all__'` proposé spontanément pour la CreateView d'Offre : non. La branche ne contenait auparavant aucun formulaire de création d'Offre ; la vue a été écrite directement avec une liste blanche explicite après lecture de la section Mass Assignment.
- Champs revus : `Offre.statut`, `Offre.transporteur`, les clés d'appartenance des expéditions et véhicules, `Vehicule.disponible`, les champs automatiques (`reference`, dates). Ils ne sont pas modifiables depuis les formulaires Web concernés ; les valeurs d'appartenance sont fixées côté serveur à partir du contexte de route.
- Corrections appliquées : la création d'offre fixe le transporteur côté serveur et ne permet pas de choisir le statut ; les choix d'expédition et de véhicule sont filtrés. Les vues de création et de modification de véhicule et d'expédition fixent aussi l'entreprise côté serveur. Les mises à jour d'offre ne modifient que prix et délai.
- Risque restant à comprendre : l'identifiant d'entreprise fourni dans l'URL sert de contexte pédagogique en l'absence d'authentification. Il ne constitue pas un contrôle d'accès pour un déploiement public.
- Vérification : tests Django des pages, des formulaires, des champs falsifiés, des limites d'entreprise et des suppressions GET/POST.

## Entrée — 2026-11-14 — revue du chapitre Administration

- Outil IA utilisé : assistant de programmation (Codex).
- Prompt utilisateur, résumé : vérifier le chapitre Administration et terminer les livrables de l'atelier.
- Sortie obtenue : ModelAdmin dédiés, filtres, inlines, badges, action de clôture, export CSV, branding et page de contrôle d'intégrité.
- Risque examiné : les opérations `.update()` et autres mises à jour en masse n'appellent pas les méthodes de modèle. Le dashboard utilise des requêtes ORM et l'action de clôture traite chaque objet par validation puis sauvegarde.
- Observation : aucune proposition `.update()`/`.bulk_update()` n'a été retenue pour l'action de clôture ou les contrôles d'intégrité ; les usages en masse restent uniquement dans le scénario pédagogique qui sert à démontrer le contournement.
