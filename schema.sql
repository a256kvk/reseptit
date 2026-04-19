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
);

CREATE TABLE Reviews (
	id INTEGER PRIMARY KEY,
	user_id INTEGER REFERENCES Users,
	recipe_id INTEGER REFERENCES Recipes,
	rating INTEGER CHECK (rating BETWEEN 1 AND 5),
	content TEXT,
	UNIQUE(recipe_id, user_id)
);

CREATE TABLE Categories (
	id INTEGER PRIMARY KEY,
	name TEXT UNIQUE
);

CREATE TABLE Recipe_Categories (
	id INTEGER PRIMARY KEY,
	recipe_id REFERENCES Recipes,
	category_id REFERENCES Categories
);
