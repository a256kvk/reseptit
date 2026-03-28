CREATE TABLE Users (
	id INTEGER PRIMARY KEY,
	username TEXT UNIQUE,
	password_hash TEXT
);

CREATE TABLE Recipes (
	id INTEGER PRIMARY KEY,
	user_id INTEGER REFERENCES Users,
	title TEXT,
	description TEXT,
	ingredients TEXT,
	instructions TEXT
)
