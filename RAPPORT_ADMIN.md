# Rapport — atelier Administration TransConnect

## Démonstration guidée

Le fichier seed officiel mentionné dans le workshop n'était pas fourni dans le dossier accessible. `EntreprisesApp/management/commands/seed_demo.py` crée les deux expéditions et les entreprises, véhicules et offres associés.

Le scénario a été rejoué dans la base locale `ons.sqlite3` le 14 novembre 2026 :

| Expédition | Manipulation | État observé |
|---|---|---|
| `EXP-26-00001` | Acceptation par `Offre.objects.filter(...).update(...)` | L'offre ciblée est `acceptee`, l'expédition reste `publiee` et l'autre offre reste `proposee`. |
| `EXP-26-00002` | Affectation du statut puis `full_clean()` et `save()` | L'expédition passe à `attribuee`, l'offre acceptée reste `acceptee` et l'autre passe à `refusee`. |

Les données de `EXP-26-00001` sont conservées comme le demande l'énoncé. Le scénario montre que `.update()` contourne `save()` et la cascade métier.

## Résultats du tableau de bord

Instantané du dashboard après reproduction des deux scénarios :

| Contrôle | Règle vérifiée | Résultat |
|---|---|---:|
| Offres orphelines | Une offre proposée/acceptée concerne une expédition publiée ou attribuée. | 0 |
| Acceptations sans attribution | Une offre acceptée a fait passer son expédition à attribuée. | 1 |
| Expéditions publiées depuis plus de 7 jours | Les expéditions anciennes encore publiées doivent être examinées. | 0 |
| Transporteurs sans flotte | Chaque transporteur possède au moins un véhicule. | 0 |
| Disponibilité incohérente | Un véhicule d'une offre acceptée ne doit pas être disponible. | 1 |
| Doublons de propositions actives | Un transporteur n'a qu'une proposition active par expédition. | 0 |

Les deux anomalies signalées proviennent de l'acceptation par mise à jour SQL de `EXP-26-00001`. Le tableau de bord expose six contrôles ORM, dépasse le minimum de quatre demandé et se trouve sous l'URL `/admin/health-check/` réservée au personnel.

## Scénarios de production

- Les offres orphelines peuvent apparaître si un import change le statut d'une expédition sans traiter ses offres associées.
- Une acceptation sans attribution peut résulter d'un `.update(statut='acceptee')` qui saute la cascade de `save()`.
- Une expédition peut rester publiée après sa date de suivi si aucun processus ne fait avancer son statut.
- Un transporteur sans flotte peut provenir d'une suppression/import de véhicules ou d'une activation incomplète de l'entreprise.
- Un véhicule disponible malgré une offre acceptée peut résulter d'un import ou d'une mise à jour en masse.
- Des doublons actifs peuvent être introduits par un import historique ou par des données créées avant la contrainte unique.

L'action `cloturer_expeditions` valide et sauvegarde individuellement uniquement les expéditions `en_cours`, puis affiche le nombre clôturé. L'export CSV précharge les relations utilisées.
