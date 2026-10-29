# Documentation technique — Plateforme de cours (Portfolio Project, Stage 3)

Plateforme de cours à distance pour une association scolaire. MVP pour ~100 élèves et 10 professeurs, cours le week-end. Stack : **FastAPI + SQLAlchemy + SQLite + JWT**, front-end HTML/JavaScript natif.

## Sommaire

| # | Document | Contenu |
| --- | --- | --- |
| 0 | [User Stories et Maquettes](<0. User Stories et Maquettes.md>) | User stories priorisées (MoSCoW) + wireframes des écrans principaux |
| 1 | [Architecture Système](<1. Architecture Système.md>) | Diagramme d'architecture haut niveau, flux de données |
| 2 | [Composants, Classes et BDD](<2. Composants Classes et BDD.md>) | Classes back-end (attributs + méthodes), ERD, détail des tables, interactions front-end |
| 3 | [Diagrammes de Séquence](<3. Diagrammes de Séquence.md>) | 3 cas d'usage critiques (inscription, connexion/agenda, signalement) |
| 4 | [Spécifications API](<4. Spécifications API.md>) | API externes (HelloAsso) et endpoints internes REST |
| 5 | [SCM et QA](<5. SCM et QA.md>) | Stratégie Git, revues de code, tests, pipeline CI/CD |
| 6 | [Documentation Technique Finale](<6. Documentation Technique Finale.md>) | **Document maître** — synthèse complète des sections 0 à 5 + justifications techniques |
| 7 | [Roadmap Phase Future](<7. Roadmap Phase Future.md>) | Modules hors MVP et améliorations prévues |
| 8 | [Plan de Sprints](<8. Plan de Sprints.md>) | Découpage du MVP en sprints |

## Maquettes interactives

Les wireframes des 5 écrans principaux sont dans [`maquettes.html`](maquettes.html) — à ouvrir directement dans un navigateur (double-clic, ou clonez le repo et ouvrez le fichier localement). GitHub ne rend pas le HTML interactif dans sa prévisualisation ; pour un aperçu en ligne, activer **GitHub Pages** sur ce dossier `docs/` rendrait le fichier accessible via une URL directe.

## Lecture recommandée

- **Vue d'ensemble rapide** : commencer par le document 6 (Documentation Technique Finale), qui contient tout.
- **Détail par thème** : les documents 0 à 5 permettent de creuser un point précis sans parcourir le document complet.

## Notes

- Les diagrammes (architecture, ERD, séquence) sont en syntaxe **Mermaid** et s'affichent automatiquement dans le rendu Markdown de GitHub.
- Toute divergence entre cette documentation et le code doit être signalée et corrigée en priorité (voir section 6.1 du document 5 pour la procédure de revue de code).
