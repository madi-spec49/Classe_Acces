# Documentation technique — Classe Accès (Portfolio, Stage 4)

Plateforme de cours à distance pour une association scolaire. MVP pour ~100 élèves et 10 professeurs, cours le week-end. Stack : **FastAPI + SQLAlchemy + PostgreSQL + JWT**, front-end HTML/JavaScript natif.

Pour l'installation, les routes et l'usage, voir le [README du projet](../README.md).

## Sommaire

| # | Document | Contenu |
| --- | --- | --- |
| 0 | [User Stories et Maquettes](<0. User Stories et Maquettes.md>) | User stories (MoSCoW), écrans réalisés, écarts entre la conception et le MVP |
| 1 | [Architecture Système](<1. Architecture Système.md>) | Architecture en trois couches, composants, flux de données, décisions |
| 2 | [Composants, Classes et BDD](<2. Composants Classes et BDD.md>) | Classes, ERD, détail des tables, pages du front-end |
| 3 | [Diagrammes de Séquence](<3. Diagrammes de Séquence.md>) | Trois cas d'usage : connexion, assiduité, suivi d'un enfant |
| 4 | [Spécifications API](<4. Spécifications API.md>) | Routes REST, droits d'accès, règles métier |
| 5 | [SCM et QA](<5. SCM et QA.md>) | Git, pull requests, 58 tests pytest, limites |
| 6 | [Documentation Technique Finale](<6. Documentation Technique Finale.md>) | **Document maître** : synthèse des documents 0 à 5, justifications techniques, limites |
| 7 | [Roadmap Phase Future](<7. Roadmap Phase Future.md>) | Modules hors MVP et améliorations prévues |
| 8 | [Plan de Sprints](<8. Plan de Sprints.md>) | Découpage prévisionnel du MVP en sprints |

## Maquettes interactives

Les wireframes sont dans [`maquettes.html`](maquettes.html), à ouvrir directement dans un navigateur. Ils ont été dessinés pendant la phase de conception : certains écrans (inscription, signalements, messagerie) n'ont pas été réalisés dans le MVP. Les écrans livrés sont décrits dans le document 0.

## Lecture recommandée

- **Vue d'ensemble rapide** : le document 6, qui résume tout.
- **Détail par thème** : les documents 0 à 5.

## Notes

- Les diagrammes (architecture, ERD, séquence) sont en syntaxe **Mermaid** et s'affichent dans le rendu Markdown de GitHub.
- Les documents 0 à 6 ont été mis à jour pour décrire le MVP livré. Le plan de sprints (8) est un plan prévisionnel daté du 8 octobre 2026.
- En cas de divergence entre cette documentation et le code, le README et `db/schema.sql` font foi.
