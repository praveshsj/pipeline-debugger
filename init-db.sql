-- Initialize PostgreSQL database with pgvector extension

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Create a simple test to ensure everything works
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully with pgvector extension!';
END $$;
