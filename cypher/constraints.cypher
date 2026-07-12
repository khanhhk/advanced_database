CREATE CONSTRAINT movie_tmdb_id IF NOT EXISTS FOR (n:Movie) REQUIRE n.tmdb_id IS UNIQUE;
CREATE CONSTRAINT person_id IF NOT EXISTS FOR (n:Person) REQUIRE n.person_id IS UNIQUE;
CREATE CONSTRAINT genre_id IF NOT EXISTS FOR (n:Genre) REQUIRE n.genre_id IS UNIQUE;
CREATE CONSTRAINT keyword_id IF NOT EXISTS FOR (n:Keyword) REQUIRE n.keyword_id IS UNIQUE;
CREATE CONSTRAINT studio_id IF NOT EXISTS FOR (n:Studio) REQUIRE n.company_id IS UNIQUE;
CREATE INDEX movie_title IF NOT EXISTS FOR (n:Movie) ON (n.title);
CREATE INDEX person_name IF NOT EXISTS FOR (n:Person) ON (n.name);

