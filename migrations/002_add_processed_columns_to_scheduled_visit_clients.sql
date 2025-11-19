ALTER TABLE scheduled_visit_clients 
ADD COLUMN filename_processed VARCHAR(255) NULL,
ADD COLUMN filename_url_processed TEXT NULL;

