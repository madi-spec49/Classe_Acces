# School Assoc — Plateforme de cours à distance

Plateforme de cours à distance le week-end pour une association scolaire : environ **100 élèves** et **10 professeurs**. Le projet est le livrable du Portfolio Stage 4, développé en sprints Agile sur environ 5 semaines.

## Sommaire

- [Fonctionnalités du MVP](#fonctionnalités-du-mvp)
- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Variables d'environnement](#variables-denvironnement)
- [Utilisation de l'API](#utilisation-de-lapi)
- [Tests](#tests)
- [Documentation](#documentation)
- [Organisation Git](#organisation-git)
- [Statut](#statut)
- [Auteur](#auteur)

## Fonctionnalités du MVP

- Gestion des utilisateurs (élève, parent, professeur, staff) et authentification JWT
- Création et consultation des cours et sessions
- Demandes d'inscription et validation par le staff
- Saisie de l'assiduité par les professeurs
- Suivi de la progression des élèves

Sont reportés en phase future : les signalements d'absence, la messagerie et le paiement HelloAsso. Voir [`docs/7. Roadmap Phase Future.md`](docs/7.%20Roadmap%20Phase%20Future.md).

## Stack technique

| Couche | Technologie |
| --- | --- |
| API | Python 3.12 + FastAPI |
| ORM | SQLAlchemy 2.0 |
| Base de données | PostgreSQL 16 (Docker) |
| Authentification | JWT (python-jose) + mots de passe hachés avec bcrypt (passlib) |
| Tests | pytest + FastAPI TestClient (base SQLite en mémoire) |
| Conteneurisation | Docker Compose |
| Front-end | HTML + JavaScript natif (à venir) |

## Structure du projet

```
school-assoc/
├── app/
│   ├── main.py             # Création de l'application FastAPI et des routes
│   ├── config.py           # Connexion à la base (engine, get_db)
│   ├── dependencies.py     # get_current_user et require_role
│   ├── security/           # Hachage des mots de passe et tokens JWT
│   ├── models/             # Modèles SQLAlchemy (un fichier par domaine)
│   ├── schemas/            # Schémas Pydantic (entrées et sorties de l'API)
│   └── routes/             # Routes (un fichier par domaine)
├── db/
│   └── schema.sql          # Schéma PostgreSQL de référence
├── docs/                   # Documentation technique complète
├── tests/
│   ├── conftest.py         # Base de test et client partagés
│   ├── test_auth.py        # Inscription, connexion, /me
│   └── test_staff.py       # Contrôle des rôles
├── docker-compose.yml      # Service PostgreSQL
├── requirements.txt        # Dépendances Python
├── .env.example            # Modèle de variables d'environnement
└── README.md
```

## Installation

Prérequis : Python 3.12 et Docker Desktop.

1. Cloner le projet et entrer dans le dossier :

   ```bash
   git clone https://github.com/madi-spec49/school-assoc.git
   cd school-assoc
   ```

2. Créer et activer l'environnement virtuel :

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

4. Lancer la base PostgreSQL :

   ```bash
   docker compose up -d db
   ```

5. Lancer l'API :

   ```bash
   uvicorn app.main:app --reload
   ```

   L'API répond sur http://127.0.0.1:8000. La documentation interactive générée par FastAPI est disponible sur http://127.0.0.1:8000/docs.

## Variables d'environnement

Le projet lit ces variables avec `os.getenv`. Si elles ne sont pas définies, le code utilise les valeurs par défaut suivantes, qui suffisent pour le développement local avec le Docker Compose du projet.

| Variable | Rôle | Valeur par défaut |
| --- | --- | --- |
| `DATABASE_URL` | Adresse de la base PostgreSQL | `postgresql+psycopg://school:school_dev_password@localhost:5432/school_assoc` |
| `JWT_SECRET_KEY` | Clé de signature des tokens JWT | `change-me-in-production` |
| `JWT_ALGORITHM` | Algorithme de signature des tokens | `HS256` |
| `JWT_EXPIRATION_MINUTES` | Durée de validité d'un token, en minutes | `60` |

Le fichier `.env.example` liste ces variables à titre de modèle. Il n'est pas lu automatiquement : pour utiliser d'autres valeurs, il faut les exporter dans le terminal avant de lancer `uvicorn`, par exemple `export JWT_SECRET_KEY=une-longue-valeur-aleatoire`.

En production, `JWT_SECRET_KEY` doit être une valeur longue et aléatoire, jamais la valeur par défaut.

## Utilisation de l'API

Toutes les routes sont préfixées par `/api`. Les réponses sont au format JSON.

| Méthode | Route | Accès | Rôle |
| --- | --- | --- | --- |
| POST | `/api/auth/register` | Public | Crée un compte élève et renvoie un token |
| POST | `/api/auth/login` | Public | Connecte un utilisateur et renvoie un token |
| GET | `/api/auth/me` | Utilisateur connecté | Renvoie le profil de l'utilisateur courant |
| POST | `/api/staff/teachers` | Staff uniquement | Crée un compte professeur |
| GET | `/health` | Public | Vérifie que l'API répond |

Les routes protégées attendent un header `Authorization: Bearer <token>`. Le token est renvoyé par `register` ou `login`.

Codes de réponse courants : `400` email déjà utilisé, `401` identifiants incorrects ou token invalide ou expiré, `403` token valide mais rôle insuffisant, `422` données envoyées invalides.

Exemple d'inscription :

```json
{
  "email": "eleve@example.com",
  "password": "monMotDePasse123",
  "first_name": "Lina",
  "last_name": "Durand"
}
```

L'inscription ne permet pas de choisir son rôle : tout compte créé par cette route est un élève.

## Tests

Les tests utilisent une base SQLite en mémoire, séparée de la base PostgreSQL. Ils ne demandent donc pas que Docker soit lancé.

```bash
python -m pytest -v
```

Les tests couvrent l'inscription, la connexion, la route `/me`, et le refus de création de professeur pour un élève ou sans token.

## Documentation

La documentation technique complète est dans le dossier [`docs/`](docs/) :

| # | Document | Contenu |
| --- | --- | --- |
| 0 | [User Stories et Maquettes](docs/0.%20User%20Stories%20et%20Maquettes.md) | User stories (MoSCoW) et wireframes |
| 1 | [Architecture Système](docs/1.%20Architecture%20Syst%C3%A8me.md) | Architecture en 3 couches, flux de données |
| 2 | [Composants, Classes et BDD](docs/2.%20Composants%20Classes%20et%20BDD.md) | Classes, modèle de données, interactions front |
| 3 | [Diagrammes de Séquence](docs/3.%20Diagrammes%20de%20S%C3%A9quence.md) | Cas d'usage critiques |
| 4 | [Spécifications API](docs/4.%20Sp%C3%A9cifications%20API.md) | Endpoints REST |
| 5 | [SCM et QA](docs/5.%20SCM%20et%20QA.md) | Git, tests, pipeline CI/CD |
| 6 | [Documentation Technique Finale](docs/6.%20Documentation%20Technique%20Finale.md) | Document de référence |
| 7 | [Roadmap Phase Future](docs/7.%20Roadmap%20Phase%20Future.md) | Modules hors MVP |

Les wireframes interactifs sont dans [`docs/maquettes.html`](docs/maquettes.html), à ouvrir dans un navigateur.

## Organisation Git

- `main` : version stable, ne reçoit que les versions livrées
- `develop` : branche d'intégration
- `feature/*` : une branche par fonctionnalité (par exemple `feature/auth`)

Les commits suivent la convention Conventional Commits : `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.

Exemples :

- `feat: add POST /api/auth/login endpoint`
- `test: check students cannot create teachers`

Cycle de travail : une branche `feature/*` est créée depuis `develop`, le travail est commité par petites étapes, puis la branche est fusionnée dans `develop`. `develop` est fusionnée dans `main` à la fin de chaque phase.

Améliorations possibles après le MVP : migrations de base de données avec Alembic, chargement automatique du fichier `.env`.

## Auteur

**Madi Anli**, étudiant à Holberton School de Laval.