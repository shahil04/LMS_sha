# Database schema

Primary keys are UUIDs. `profiles.id` is the Supabase Auth subject; account credentials remain in Supabase Auth. Courses have unique slugs. Modules and topics are ordered beneath their parents; drafts do not appear in public catalog or student views. Enrollment and progress rows are retained when content is archived. Deletion is restricted where it could erase learning history.

Entities and relations are diagrammed in the root README. Key uniqueness rules include one enrollment per student/course pair, one progress row per student/topic, and one bookmark per student/topic. Quiz answer keys are stored server-side and excluded from student question responses until policy permits revealing them.

`alembic upgrade head` applies the versioned initial schema. `Base.metadata.create_all()` is not used as a production migration strategy.
