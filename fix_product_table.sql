-- Fix product table by adding missing colors column
ALTER TABLE product ADD COLUMN colors TEXT NOT NULL DEFAULT "";
