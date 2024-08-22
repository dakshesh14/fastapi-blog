DROP TABLE IF EXISTS blogs CASCADE;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE blogs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255),
  slug VARCHAR(265),
  content TEXT,

  -- author
  author_id UUID REFERENCES users(id),

  -- time audit fields
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  -- constraints
  CONSTRAINT unique_slug UNIQUE (slug)
);
