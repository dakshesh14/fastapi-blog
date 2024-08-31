DROP TABLE IF EXISTS blogs CASCADE;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- We should ideally use id as simple int and make a new column named pk or uuid since
-- uuid can make indexing expensive but for now this should be fine
CREATE TABLE blogs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255),
  slug VARCHAR(265),
  content TEXT,

  -- author
  author_id UUID REFERENCES users(id) ON DELETE CASCADE,

  -- time audit fields
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  -- constraints
  CONSTRAINT unique_slug UNIQUE (slug)
);

CREATE INDEX idx_blogs_created_at ON blogs(created_at);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER set_updated_at
BEFORE UPDATE ON blogs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
