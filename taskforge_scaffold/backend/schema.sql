CREATE TABLE people(
  id INTEGER PRIMARY KEY,
  full_name TEXT,
  email TEXT UNIQUE,
  alias TEXT
);
