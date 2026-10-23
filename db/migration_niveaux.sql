-- Migration : passage au système de niveaux (debutant / intermediaire / avance)
-- À lancer une seule fois sur une base déjà existante.
-- Ne supprime aucun compte, ni cours, ni présence.

ALTER TABLE users ADD COLUMN IF NOT EXISTS level VARCHAR(20);

ALTER TABLE courses ADD COLUMN IF NOT EXISTS level VARCHAR(20) NOT NULL DEFAULT 'debutant';

DROP TABLE IF EXISTS enrollment_requests;
