-- init.sql loads the CSV with explicit ids, which leaves the id sequence at 1.
-- Move it past the loaded rows so a later INSERT (BusinessService.AddBusiness) does not collide.
SELECT setval(pg_get_serial_sequence('business', 'id'), COALESCE((SELECT MAX(id) FROM business), 1));
