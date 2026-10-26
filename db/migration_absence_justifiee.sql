-- Migration : ajout du statut "absence justifiée" (excused) aux présences.
-- À lancer une seule fois sur une base déjà existante.
-- Ne supprime aucune présence.

ALTER TABLE attendance_records DROP CONSTRAINT IF EXISTS ck_attendance_status;

ALTER TABLE attendance_records
    ADD CONSTRAINT ck_attendance_status
    CHECK (status IN ('present', 'absent', 'late', 'excused'));
