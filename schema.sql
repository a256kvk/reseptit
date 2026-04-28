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

CREATE VIRTUAL TABLE Recipes_Search USING fts5(title,description,ingredients,instructions);

CREATE TRIGGER Recipes_Search_insert AFTER INSERT ON Recipes
BEGIN
	INSERT INTO Recipes_Search (rowid,title,description,ingredients,instructions)
	VALUES (NEW.id,NEW.title,NEW.description,NEW.ingredients,NEW.instructions);
END;

CREATE TRIGGER Recipes_Search_update AFTER UPDATE ON Recipes
BEGIN
	UPDATE Recipes_Search 
	SET title = NEW.title,
		description = NEW.description,
		ingredients = NEW.ingredients,
		instructions = NEW.instructions
	WHERE rowid = NEW.id;
END;

CREATE TRIGGER Recipes_Search_delete AFTER DELETE ON Recipes
BEGIN
	DELETE FROM Recipes_Search WHERE rowid = OLD.id;
END;
