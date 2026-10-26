-- ============================================================
-- Schéma PostgreSQL de référence — Classe Accès (MVP)
--
-- 6 tables : users, parent_student, courses, course_sessions,
--            attendance_records, progress_records
--
-- En développement, SQLAlchemy crée ces tables automatiquement au
-- démarrage de l'API (Base.metadata.create_all). Ce fichier décrit le
-- même schéma en SQL pur, à titre de référence et pour une base
-- PostgreSQL créée à la main. Pour une base déjà existante, voir
-- db/migration_niveaux.sql.
-- ============================================================

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(20)  NOT NULL DEFAULT 'student'
                    CHECK (role IN ('student', 'parent', 'teacher', 'staff')),
    -- Niveau de l'élève (NULL pour les autres rôles et pour un élève non encore affecté)
    level           VARCHAR(20)
                    CHECK (level IN ('debutant', 'intermediaire', 'avance')),
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_role ON users(role);

-- Table d'association : un parent peut avoir plusieurs enfants,
-- un enfant peut avoir plusieurs parents.
CREATE TABLE parent_student (
    parent_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    student_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (parent_id, student_id),
    CHECK (parent_id <> student_id)
);

CREATE INDEX idx_parent_student_student ON parent_student(student_id);

CREATE TABLE courses (
    id           SERIAL PRIMARY KEY,
    teacher_id   INTEGER      NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title        VARCHAR(150) NOT NULL,
    subject      VARCHAR(100) NOT NULL,
    day_of_week  SMALLINT     NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    start_time   TIME         NOT NULL,
    end_time     TIME         NOT NULL,
    zoom_link    VARCHAR(500),
    -- Niveau du cours : seuls les élèves de ce niveau le voient
    level        VARCHAR(20)  NOT NULL DEFAULT 'debutant'
                 CHECK (level IN ('debutant', 'intermediaire', 'avance')),
    CHECK (end_time > start_time)
);

CREATE INDEX idx_courses_teacher ON courses(teacher_id);
CREATE INDEX idx_courses_subject ON courses(subject);

-- Instance datée d'un cours (une séance)
CREATE TABLE course_sessions (
    id          SERIAL PRIMARY KEY,
    course_id   INTEGER     NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    date        TIMESTAMPTZ NOT NULL,
    zoom_link   VARCHAR(500)
);

CREATE INDEX idx_course_sessions_course ON course_sessions(course_id);
CREATE INDEX idx_course_sessions_date   ON course_sessions(date);

CREATE TABLE attendance_records (
    id          SERIAL PRIMARY KEY,
    session_id  INTEGER     NOT NULL REFERENCES course_sessions(id) ON DELETE CASCADE,
    student_id  INTEGER     NOT NULL REFERENCES users(id)           ON DELETE CASCADE,
    status      VARCHAR(20) NOT NULL CHECK (status IN ('present', 'absent', 'late')),
    note        TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Une seule présence par élève et par séance
    UNIQUE (session_id, student_id)
);

CREATE INDEX idx_attendance_student ON attendance_records(student_id);
CREATE INDEX idx_attendance_session ON attendance_records(session_id);

-- Progression : "level" est le niveau atteint dans le cours (texte libre,
-- par exemple "Niveau 2"). Ce n'est PAS le niveau de la classe (users.level).
CREATE TABLE progress_records (
    id          SERIAL PRIMARY KEY,
    student_id  INTEGER     NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    course_id   INTEGER     NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    teacher_id  INTEGER     NOT NULL REFERENCES users(id)   ON DELETE RESTRICT,
    level       VARCHAR(50) NOT NULL,
    note        TEXT,
    date        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_progress_student ON progress_records(student_id);
CREATE INDEX idx_progress_course  ON progress_records(course_id);
CREATE INDEX idx_progress_teacher ON progress_records(teacher_id);
