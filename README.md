# Classe Accès — Plateforme de cours à distance

Plateforme web de gestion des cours à distance, utilisée le week-end par une association scolaire (environ **100 élèves** et **10 professeurs**). Le staff crée les comptes et les cours, les professeurs saisissent l'assiduité et la progression, les élèves et leurs parents consultent leur suivi.

Projet réalisé dans le cadre du **Portfolio Stage 4** (Holberton School), développé en sprints Agile.

## Sommaire

- [Fonctionnalités du MVP](#fonctionnalités-du-mvp)
- [Rôles et droits d'accès](#rôles-et-droits-daccès)
- [Architecture](#architecture)
- [Base de données](#base-de-données)
- [Choix techniques](#choix-techniques)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Variables d'environnement](#variables-denvironnement)
- [Routes de l'API](#routes-de-lapi)
- [Tests](#tests)
- [Documentation](#documentation)
- [Organisation Git](#organisation-git)
- [Limites connues et évolutions](#limites-connues-et-évolutions)
- [Auteur](#auteur)

## Fonctionnalités du MVP

- **Comptes** : tous les comptes (élève, parent, professeur, staff) sont créés par le staff. Il n'y a pas d'inscription publique.
- **Niveaux** : chaque cours et chaque élève a un niveau (`debutant`, `intermediaire` ou `avance`). Un élève ne voit que les cours de son niveau.
- **Cours et séances** : le staff crée et supprime les cours (matière, jour, horaires, professeur, niveau, lien Zoom). Le staff ou le professeur du cours crée les séances datées. La suppression d'un cours efface aussi ses séances, présences et progressions.
- **Suppression de comptes** : réservée au staff. Un professeur qui a encore des cours ne peut pas être supprimé.
- **Assiduité** : le professeur d'un cours enregistre le statut de chaque élève de son niveau : présent, absent ou en retard (`present`, `absent`, `late`).
- **Progression** : depuis la carte de chaque cours, le professeur enregistre pour chaque élève de son niveau le niveau atteint et une note facultative.
- **Suivi familial** : un parent lié à un élève consulte ses présences et sa progression. Il ne voit que ses propres enfants.
- **Authentification** : connexion par email et mot de passe, jeton JWT valable 60 minutes.

Hors MVP, reporté en phase future : signalements d'absence, messagerie, paiement HelloAsso.

## Rôles et droits d'accès

Le contrôle d'accès repose sur le rôle de l'utilisateur (RBAC) : la dépendance `require_role` refuse l'accès avec un `403` si le rôle ne correspond pas, et les règles de propriété (cours du professeur, enfant du parent) sont vérifiées dans chaque route.

| Action | Élève | Parent | Professeur | Staff |
| --- | :---: | :---: | :---: | :---: |
| Se connecter, voir son profil | ✅ | ✅ | ✅ | ✅ |
| Créer un compte élève, parent ou professeur | ❌ | ❌ | ❌ | ✅ |
| Lier un parent à un élève | ❌ | ❌ | ❌ | ✅ |
| Créer un cours | ❌ | ❌ | ❌ | ✅ |
| Supprimer un cours (et son historique) | ❌ | ❌ | ❌ | ✅ |
| Supprimer un compte élève, parent ou professeur | ❌ | ❌ | ❌ | ✅ |
| Créer une séance | ❌ | ❌ | ✅ (ses cours) | ✅ |
| Voir les séances d'un cours | ✅ (son niveau) | ❌ | ✅ (ses cours) | ✅ |
| Voir la liste des cours | Son niveau | ❌ | Ses cours | Tous |
| Saisir l'assiduité | ❌ | ❌ | ✅ (ses cours, niveau de l'élève) | ❌ |
| Voir l'assiduité d'une séance | ❌ | ❌ | ✅ (ses cours) | ✅ |
| Saisir la progression | ❌ | ❌ | ✅ (élèves de son niveau) | ❌ |
| Voir la progression d'un élève | ✅ (la sienne) | ✅ (ses enfants) | ✅ (élèves de son niveau) | ✅ |
| Voir l'assiduité d'un élève | ✅ (la sienne) | ✅ (ses enfants) | ❌ | ✅ |

## Architecture

L'application suit une architecture en trois couches : un client léger dans le navigateur, une API REST FastAPI, et une base PostgreSQL accédée via l'ORM SQLAlchemy.

```mermaid
flowchart LR
    subgraph Client["Navigateur"]
        FE["Pages HTML + JavaScript natif<br/>login · staff · courses (élève) · teacher · suivi (élève, parent) · parent"]
    end

    subgraph Backend["Back-end FastAPI (Python 3.12)"]
        MAIN["main.py<br/>CORS et routeurs"]
        ROUTES["routes/<br/>auth · staff · courses · attendance<br/>progress · parents · suivi"]
        DEPS["dependencies.py<br/>get_current_user · require_role"]
        SEC["security/<br/>bcrypt · JWT"]
        MODELS["models/ et schemas/<br/>SQLAlchemy · Pydantic"]
    end

    DB[("PostgreSQL 16<br/>Docker")]

    FE -- "Requêtes HTTP JSON<br/>+ en-tête Authorization: Bearer" --> MAIN
    MAIN --> ROUTES
    ROUTES --> DEPS
    DEPS --> SEC
    ROUTES --> MODELS
    MODELS -- "SQL via psycopg" --> DB
```

**Déroulement d'une requête protégée** : le navigateur envoie le jeton JWT dans l'en-tête `Authorization`. La dépendance `get_current_user` décode le jeton, charge l'utilisateur en base et vérifie qu'il est actif. Ensuite `require_role` contrôle le rôle, puis la route applique les règles de propriété et renvoie le résultat sérialisé par un schéma Pydantic.

## Base de données

```mermaid
erDiagram
    USERS ||--o{ COURSES : "enseigne (teacher_id)"
    COURSES ||--o{ COURSE_SESSIONS : "a des séances"
    COURSE_SESSIONS ||--o{ ATTENDANCE_RECORDS : "présences"
    USERS ||--o{ ATTENDANCE_RECORDS : "élève (student_id)"
    USERS ||--o{ PROGRESS_RECORDS : "élève (student_id)"
    USERS ||--o{ PROGRESS_RECORDS : "saisi par (teacher_id)"
    COURSES ||--o{ PROGRESS_RECORDS : "concerne"
    USERS ||--o{ PARENT_STUDENT : "parent (parent_id)"
    USERS ||--o{ PARENT_STUDENT : "enfant (student_id)"

    USERS {
        int id PK
        string email UK
        string password_hash
        string role "student, parent, teacher, staff"
        string level "debutant, intermediaire, avance (élèves)"
        string first_name
        string last_name
        boolean is_active
        timestamp created_at
    }
    PARENT_STUDENT {
        int parent_id PK, FK
        int student_id PK, FK
    }
    COURSES {
        int id PK
        int teacher_id FK
        string title
        string subject
        int day_of_week "0 à 6"
        time start_time
        time end_time
        string zoom_link
        string level "debutant, intermediaire, avance"
    }
    COURSE_SESSIONS {
        int id PK
        int course_id FK
        timestamp date
        string zoom_link
    }
    ATTENDANCE_RECORDS {
        int id PK
        int session_id FK
        int student_id FK
        string status "present, absent, late"
        string note
        timestamp created_at
    }
    PROGRESS_RECORDS {
        int id PK
        int student_id FK
        int course_id FK
        int teacher_id FK
        string level "niveau atteint, texte libre"
        string note
        timestamp date
    }
```

Le schéma SQL de référence est dans [`db/schema.sql`](db/schema.sql).

**Décisions de modélisation :**

- **`parent_student` en table d'association** (clé composite) : un parent peut avoir plusieurs enfants et un enfant plusieurs parents, sans duplication des données.
- **`course_sessions` séparé de `courses`** : le cours est le « modèle » récurrent, la séance est l'instance datée qui porte les présences.
- **Unicité `(session_id, student_id)`** dans `attendance_records` : une seule présence par élève et par séance. Un second enregistrement met à jour le premier.
- **Deux « niveaux » distincts** : `users.level` et `courses.level` désignent la classe de l'élève ou du cours. `progress_records.level` désigne le niveau atteint par l'élève dans sa progression (texte libre, par exemple « Niveau 2 »).
- **Suppression en cascade ou restreinte** : supprimer un élève supprime ses présences et sa progression (`CASCADE`). Supprimer un professeur encore rattaché à un cours est refusé (`RESTRICT`), pour ne pas perdre l'historique.
- **Contraintes en base** : `CHECK` sur les rôles, les niveaux, les statuts de présence, le jour de la semaine et l'ordre des horaires. Les règles sont ainsi appliquées même si le code évolue.

## Choix techniques

| Couche | Technologie | Pourquoi |
| --- | --- | --- |
| API | FastAPI (Python 3.12) | Validation automatique des données avec Pydantic, documentation OpenAPI générée, bonne lisibilité du code |
| ORM | SQLAlchemy 2.0 | Modèles Python qui décrivent les tables, requêtes sans SQL brut |
| Base de données | PostgreSQL 16 (Docker) | Base relationnelle avec contraintes et clés étrangères |
| Authentification | JWT (python-jose) | Pas de session côté serveur : le jeton contient l'identifiant et l'expiration |
| Mots de passe | bcrypt (passlib) | Hachage lent et salé : un mot de passe n'est jamais stocké en clair |
| Front-end | HTML + JavaScript natif | Pas de build ni de framework à maintenir pour un MVP simple à expliquer |
| Tests | pytest + TestClient | Tests de l'API sans serveur réel, sur une base SQLite en mémoire |
| Conteneurisation | Docker Compose | Une seule commande pour lancer la base |

**Sécurité** : les mots de passe sont hachés avec bcrypt, les routes protégées exigent un jeton valide, le contrôle des rôles est centralisé dans `require_role`, et le CORS n'autorise que les pages servies sur le port 5500.

## Structure du projet

```
Classe_Acces/
├── app/
│   ├── main.py             # Création de l'application, CORS, enregistrement des routeurs
│   ├── config.py           # Connexion à la base (engine, session, get_db)
│   ├── dependencies.py     # get_current_user et require_role
│   ├── levels.py           # Les trois niveaux possibles
│   ├── security/           # Hachage des mots de passe et tokens JWT
│   ├── models/             # Tables SQLAlchemy (une par domaine)
│   ├── schemas/            # Schémas Pydantic (données entrantes et sortantes)
│   └── routes/             # Routes de l'API (une par domaine)
├── db/
│   ├── schema.sql          # Schéma PostgreSQL de référence
│   └── migration_niveaux.sql  # Passage au système de niveaux (base existante)
├── docs/                   # Documents de conception (voir la section Documentation)
├── frontend/
│   ├── login.html          # Connexion
│   ├── staff.html          # Gestion des comptes, cours et élèves (staff)
│   ├── courses.html        # Cours disponibles pour l'élève
│   ├── teacher.html        # Saisie de l'assiduité et de la progression (professeur)
│   ├── suivi.html          # Suivi d'un élève (assiduité, progression)
│   ├── parent.html         # Espace parent (enfants liés)
│   ├── style.css           # Feuille de style commune
│   └── logo.svg            # Logo
├── postman/                # Collections Postman locales (non versionnées)
├── scripts/
│   └── create_staff.py     # Création du premier compte staff
├── tests/
│   ├── conftest.py         # Base de test, client et fixture make_user
│   ├── helpers.py          # Mot de passe de test et construction du header Authorization
│   ├── test_auth.py        # Connexion, /me
│   ├── test_staff.py       # Création de comptes et contrôle des rôles
│   ├── test_courses.py     # Cours, séances, suppression, filtre par niveau
│   ├── test_attendance.py  # Assiduité
│   ├── test_progress.py    # Progression
│   ├── test_parents.py     # Comptes parents et lien parent-élève
│   └── test_create_staff.py  # Script de création du premier compte staff
├── docker-compose.yml      # Service PostgreSQL
├── requirements.txt        # Dépendances Python
├── .env.example            # Modèle de variables d'environnement
└── README.md
```

## Installation

Prérequis : Python 3.12 et Docker Desktop.

1. Cloner le projet et entrer dans le dossier :

```bash
git clone https://github.com/madi-spec49/Classe_Acces.git
cd Classe_Acces
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

6. Lancer le front-end, dans un second terminal :

```bash
cd frontend
python3 -m http.server 5500
```

Ouvrir ensuite http://127.0.0.1:5500/login.html. Le port 5500 est autorisé par le CORS de l'API.

**Création du premier compte staff.** Il n'existe pas d'inscription publique. Le premier compte staff se crée avec le script `scripts/create_staff.py`, depuis la machine qui a accès à la base (le mot de passe doit faire au moins 8 caractères) :

```bash
python -m scripts.create_staff
```

Les autres comptes sont ensuite créés depuis la page staff.

**Base existante (avant le système de niveaux).** Lancer une seule fois `db/migration_niveaux.sql` sur la base. Ce script ajoute les colonnes de niveau, supprime l'ancienne table des demandes d'inscription, et ne supprime aucun compte, cours ni présence.

## Variables d'environnement

Le projet lit ces variables avec `os.getenv`. Si elles ne sont pas définies, le code utilise les valeurs par défaut ci-dessous, suffisantes pour le développement local avec le Docker Compose du projet.

| Variable | Rôle | Valeur par défaut |
| --- | --- | --- |
| `DATABASE_URL` | Adresse de la base PostgreSQL | `postgresql+psycopg://school:school_dev_password@localhost:5432/school_assoc` |
| `JWT_SECRET_KEY` | Clé de signature des tokens JWT | `change-me-in-production` |
| `JWT_ALGORITHM` | Algorithme de signature des tokens | `HS256` |
| `JWT_EXPIRATION_MINUTES` | Durée de validité d'un token, en minutes | `60` |

Le fichier `.env.example` liste ces variables à titre de modèle. Il n'est pas lu automatiquement : pour utiliser d'autres valeurs, il faut les exporter dans le terminal avant de lancer `uvicorn`, par exemple `export JWT_SECRET_KEY=une-longue-valeur-aleatoire`.

En production, `JWT_SECRET_KEY` doit être une valeur longue et aléatoire, jamais la valeur par défaut. Le fichier `.env` ne doit jamais être versionné.

## Routes de l'API

Toutes les routes sont préfixées par `/api`. Les réponses sont au format JSON. Les routes protégées attendent un en-tête `Authorization: Bearer <token>`.

| Méthode | Route | Accès | Rôle |
| --- | --- | --- | --- |
| POST | `/api/auth/login` | Public | Connecte un utilisateur et renvoie un token |
| GET | `/api/auth/me` | Connecté | Renvoie le profil de l'utilisateur courant |
| POST | `/api/staff/teachers` | Staff | Crée un compte professeur |
| POST | `/api/staff/students` | Staff | Crée un compte élève avec son niveau |
| GET | `/api/staff/teachers` | Staff | Liste les professeurs |
| GET | `/api/staff/students` | Staff | Liste les élèves |
| GET | `/api/staff/users` | Staff | Liste les comptes non staff |
| POST | `/api/staff/users/{user_id}/password` | Staff | Réinitialise le mot de passe d'un compte |
| POST | `/api/parents` | Staff | Crée un compte parent |
| POST | `/api/parents/{parent_id}/students/{student_id}` | Staff | Relie un parent à un élève |
| GET | `/api/parents/me/children` | Parent | Liste les enfants liés au parent |
| POST | `/api/courses` | Staff | Crée un cours |
| GET | `/api/courses` | Élève, professeur ou staff | Liste les cours : élève son niveau, professeur ses cours, staff tous (refusé au parent) |
| GET | `/api/courses/{course_id}/students` | Staff ou professeur du cours | Liste les élèves du niveau du cours |
| DELETE | `/api/courses/{course_id}` | Staff | Supprime le cours, ses séances, présences et progressions |
| DELETE | `/api/staff/users/{user_id}` | Staff | Supprime un élève, un parent ou un professeur sans cours |
| POST | `/api/courses/{course_id}/sessions` | Staff ou professeur du cours | Crée une séance |
| GET | `/api/courses/{course_id}/sessions` | Élève du niveau du cours, professeur du cours ou staff | Liste les séances d'un cours |
| POST | `/api/sessions/{session_id}/attendance` | Professeur du cours | Enregistre ou met à jour une présence |
| GET | `/api/sessions/{session_id}/attendance` | Staff ou professeur du cours | Liste les présences d'une séance |
| POST | `/api/progress` | Professeur | Enregistre une progression |
| GET | `/api/progress/students/{student_id}` | Élève, parent lié, professeur du niveau ou staff | Liste la progression d'un élève |
| GET | `/api/students/{student_id}/attendance` | Élève, parent lié ou staff | Liste les présences d'un élève |
| GET | `/health` | Public | Vérifie que l'API répond |

**Codes de réponse courants** : `400` requête invalide (élève hors niveau, email déjà utilisé), `401` identifiants incorrects ou token invalide ou expiré, `403` token valide mais rôle ou propriété insuffisants, `404` ressource introuvable, `422` données invalides (horaires incohérents, valeur hors liste).

**Exemple : connexion**

```json
{
  "email": "eleve@example.com",
  "password": "monMotDePasse123"
}
```

## Tests

Les tests utilisent une base SQLite en mémoire, séparée de la base PostgreSQL. Ils ne demandent donc pas que Docker soit lancé.

```bash
source venv/bin/activate
python -m pytest -v
```

Chaque test part d'une base vide : `conftest.py` crée les tables avant le test et les supprime après. Les comptes de test sont créés par la fixture `make_user`, qui les insère directement en base et génère un token valide. Les tests ne passent donc pas par la route de connexion pour créer leurs données, ce qui évite qu'une panne de la connexion fasse échouer tous les autres tests.

**Ce qui est testé** (58 tests) :

- **Authentification** : connexion réussie, mauvais mot de passe, compte désactivé refusé, `/me` avec et sans token, token invalide.
- **Rôles** : un élève ne peut pas créer de cours ni de séance, et un compte qui n'est pas professeur ne peut pas être lié à un cours.
- **Cours et séances** : création de cours par le staff, horaires incohérents refusés, un professeur doit avoir le rôle professeur, un élève ne voit que les cours de son niveau, suppression d'un cours réservée au staff, séances visibles seulement pour le niveau de l'élève ou le professeur du cours.
- **Suppression de comptes** : le staff supprime élèves et parents, ne supprime pas un compte staff, ne supprime pas un professeur qui a des cours, et un élève ne peut pas supprimer quelqu'un.
- **Assiduité** : seul le professeur du cours peut saisir les présences, un élève hors niveau est refusé, une seconde saisie met à jour la première.
- **Progression** : même règle de niveau, lecture limitée à l'élève, à son parent lié et au staff.
- **Premier compte staff** : le script crée un staff avec mot de passe haché, refuse un email en double, un mot de passe trop court et un email invalide.
- **Parents** : création par le staff, lien parent-élève, un parent non lié ne voit pas la progression, un parent n'a accès ni aux cours ni aux séances.

## Documentation

Les documents de conception sont dans le dossier [`docs/`](docs/) :

| # | Document | Contenu |
| --- | --- | --- |
| 0 | [User Stories et Maquettes](docs/0.%20User%20Stories%20et%20Maquettes.md) | User stories (MoSCoW) et wireframes |
| 1 | [Architecture Système](docs/1.%20Architecture%20Syst%C3%A8me.md) | Architecture en couches |
| 2 | [Composants, Classes et BDD](docs/2.%20Composants%20Classes%20et%20BDD.md) | Classes, modèle de données |
| 3 | [Diagrammes de Séquence](docs/3.%20Diagrammes%20de%20S%C3%A9quence.md) | Cas d'usage critiques |
| 4 | [Spécifications API](docs/4.%20Sp%C3%A9cifications%20API.md) | Endpoints REST |
| 5 | [SCM et QA](docs/5.%20SCM%20et%20QA.md) | Git, tests |
| 6 | [Documentation Technique Finale](docs/6.%20Documentation%20Technique%20Finale.md) | Document de référence |
| 7 | [Roadmap Phase Future](docs/7.%20Roadmap%20Phase%20Future.md) | Modules hors MVP |
| 8 | [Plan de Sprints](docs/8.%20Plan%20de%20Sprints.md) | Découpage en sprints |

> **Attention** : les documents 0 à 7 datent de la phase de conception. Ils décrivent encore des éléments abandonnés pendant le développement (SQLite, inscriptions par les élèves, signalements, messagerie). **Le README et `db/schema.sql` font foi** pour le fonctionnement actuel.

Les wireframes interactifs sont dans [`docs/maquettes.html`](docs/maquettes.html), à ouvrir dans un navigateur.

## Organisation Git

- `main` : version stable, ne reçoit que les versions livrées.
- `develop` : branche d'intégration.
- `feature/*` : une branche par fonctionnalité (par exemple `feature/auth`).

Cycle de travail : une branche `feature/*` est créée depuis `develop`, le travail est commité par petites étapes, puis la branche est fusionnée dans `develop`. `develop` est fusionnée dans `main` à la fin de chaque phase.

Les commits suivent la convention **Conventional Commits** : `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`. Exemples de l'historique :

- `feat: add course and student levels (debutant, intermediaire, avance)`
- `refactor: remove public registration and enrollment requests`
- `test: create accounts directly in the database instead of the removed register route`

## Limites connues et évolutions

- **Modification des cours** : un cours se crée et se supprime, mais ne se modifie pas. Pour changer un horaire, il faut le supprimer et le recréer.
- **Démarrage** : `Base.metadata.create_all` crée les tables mais n'ajoute pas les nouvelles colonnes sur une base existante. Il faut alors appliquer les scripts de `db/`. Un outil de migrations (Alembic) est prévu.
- **Fichier `.env`** : les variables doivent être exportées manuellement. Le chargement automatique est prévu.
- **Authentification** : il n'y a pas de rafraîchissement de jeton. À l'expiration (60 minutes par défaut), l'utilisateur doit se reconnecter.
- **Phase future** : signalements d'absence, messagerie et paiement HelloAsso (voir `docs/7. Roadmap Phase Future.md`).

## Auteur

**Madi Anli**, étudiant à Holberton School de Laval.
