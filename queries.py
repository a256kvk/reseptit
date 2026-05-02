import re

import db

def get_recipe(recipe_id):
    command = """
    SELECT Recipes.id id, user_id, username, title, description, ingredients,
           instructions
    FROM Recipes JOIN Users ON user_id = Users.id
    WHERE Recipes.id = ?
    """
    res = db.query(command, [recipe_id])

    if len(res) < 1:
        return None

    return res[0]

def get_recipes(after_id):
    command = "SELECT id, title FROM Recipes WHERE id > ? LIMIT 100"
    return db.query(command, [after_id])

def create_recipe(user_id, title, description, ingredients, instructions,
                  categories):
    with db.get_cursor() as cur:
        command = """
        INSERT INTO Recipes (user_id, title, description, ingredients,
                             instructions)
        VALUES (?, ?, ?, ?, ?)
        """
        params = [user_id, title, description, ingredients, instructions]
        res = cur.execute(command, params)
        recipe_id = res.lastrowid

        insert_categories_command = """
        INSERT INTO Recipe_Categories (recipe_id, category_id) VALUES (?, ?)
        """
        for category_id in categories:
            cur.execute(insert_categories_command, [recipe_id, category_id])

    return recipe_id

def update_recipe(title, description, ingredients, instructions, recipe_id,
                  user_id, categories):
    with db.get_cursor() as cur:
        command = """
        UPDATE Recipes
        SET title = ?, description = ?, ingredients = ?, instructions = ?
        WHERE id = ? AND user_id = ?
        """
        params = [title, description, ingredients, instructions, recipe_id,
                  user_id]
        cur.execute(command, params)

        delete_command = "DELETE FROM Recipe_Categories WHERE recipe_id = ?"
        cur.execute(delete_command, [recipe_id])

        insert_categories_command = """
        INSERT INTO Recipe_Categories (recipe_id, category_id) VALUES (?, ?)
        """
        for category_id in categories:
            cur.execute(insert_categories_command, [recipe_id, category_id])

def get_username(user_id):
    res = db.query("SELECT username FROM Users WHERE id = ?", [user_id])
    if len(res) != 1:
        return None
    return res[0]["username"]

def get_user_statistics(user_id):
    command = """
    SELECT id, username,
        (SELECT COUNT(*) FROM Recipes WHERE user_id = ?) recipe_count,
        (SELECT COUNT(*) FROM Reviews WHERE user_id = ?) review_count,
        (SELECT AVG(rating)
        FROM Reviews V JOIN Recipes R ON recipe_id = R.id
        WHERE R.user_id = ?) avg_rating
    FROM Users
    WHERE id = ?
    """
    res = db.query(command, [user_id, user_id, user_id, user_id])
    if len(res) != 1:
        return None
    return res[0]

def get_categories():
    command = "SELECT id, name FROM Categories"
    res = db.query(command)
    return res

def get_review(review_id):
    command = "SELECT user_id, recipe_id FROM Reviews WHERE id = ?"
    review = db.query(command, [review_id])
    if len(review) != 1:
        return None
    return review[0]

def get_reviews(recipe_id):
    command = """
    SELECT username, user_id, rating, content
    FROM Reviews R JOIN Users U ON U.id = R.user_id
    WHERE recipe_id = ?
    """
    comments = db.query(command, [recipe_id])
    return comments

def get_user_review(recipe_id, user_id):
    if user_id is None:
        return None
    command = """
    SELECT id, rating, content FROM Reviews WHERE recipe_id = ? AND user_id = ?
    """
    review = db.query(command, [recipe_id, user_id])
    if len(review) != 1:
        return None
    return review[0]

def create_review(user_id, recipe_id, rating, content):
    command = """
    REPLACE INTO Reviews (user_id, recipe_id, rating, content)
    VALUES (?, ?, ?, ?)
    """
    db.execute(command, [user_id, recipe_id, rating, content])

def get_recipe_categories(recipe_id):
    command = """
    SELECT C.id, name
    FROM Recipe_Categories RC JOIN Categories C ON RC.category_id = C.id
    WHERE RC.recipe_id = ?
    """
    res = db.query(command, [recipe_id])
    return res

def delete_recipe(recipe_id):
    db.execute("DELETE FROM Recipes WHERE id = ?", [recipe_id])

def delete_review(review_id):
    db.execute("DELETE FROM Reviews WHERE id = ?", [review_id])

def create_user(username, password_hash):
    command = "INSERT INTO Users (username, password_hash) VALUES (?, ?)"
    db.execute(command, [username, password_hash])

def get_login_info(username):
    command = "SELECT id, password_hash FROM Users WHERE username = ?"
    res = db.query(command, [username])
    if len(res) < 1:
        return None
    return res[0]

def create_fts5_query(raw_input):
    # removes all characters that aren't alphanumeric or whitespace
    sanitized = re.sub(r"[^\w\s]","",raw_input)
    keyword_list = sanitized.split()
    fts5_query = " OR ".join(keyword_list)
    return fts5_query

def get_recipes_categories(categories, after_id):
    n = len(categories)
    if n == 0:
        command = """
        SELECT id, title
        FROM Recipes
        WHERE id > ?
        LIMIT 100
        """
        params = [after_id]
    else:
        lst = "(" + ",".join(["?"]*n) + ")"
        command = f"""
        SELECT R.id id, title
        FROM Recipes R JOIN Recipe_Categories C ON R.id = recipe_id
        WHERE C.category_id in {lst} AND R.id > ?
        GROUP BY R.id
        HAVING COUNT(DISTINCT C.category_id) = ?
        LIMIT 100
        """
        params = categories + [after_id, n]
    return db.query(command, params)

def search_recipes(query, categories, after_id):
    n = len(categories)
    fts5_query = create_fts5_query(query)

    if fts5_query == "":
        return get_recipes_categories(categories, after_id)

    if not categories:
        command = """
        SELECT rowid id, title
        FROM Recipes_Search
        WHERE Recipes_Search MATCH ? AND rowid > ?
        LIMIT 100
        """
        params = [fts5_query, after_id]
    else:
        lst = "(" + ",".join(["?"]*n) + ")"
        command = f"""
        SELECT R.rowid id, title
        FROM Recipes_Search R JOIN Recipe_Categories C ON R.rowid = recipe_id
        WHERE Recipes_Search MATCH ? AND C.category_id in {lst} AND R.rowid > ?
        GROUP BY R.rowid
        HAVING COUNT(DISTINCT C.category_id) = ?
        LIMIT 100
        """
        params = [fts5_query] + categories + [after_id, n]
    return db.query(command, params)

def get_user_recipes(user_id, categories=[], after_id=0):
    n = len(categories)
    if not categories:
        command = """
        SELECT id, title
        FROM Recipes
        WHERE user_id = ? AND id > ?
        LIMIT 100
        """
        params = [user_id, after_id]
    else:
        lst = "(" + ",".join(["?"]*n) + ")"
        command = f"""
        SELECT R.id id, title
        FROM Recipes R JOIN Recipe_Categories C ON R.id = recipe_id
        WHERE C.category_id in {lst} AND user_id = ? AND R.id > ?
        GROUP BY R.id
        HAVING COUNT(DISTINCT C.category_id) = ?
        LIMIT 100
        """
        params = categories + [user_id, after_id, n]
    return db.query(command, params)

def search_user_recipes(user_id, query, categories, after_id):
    n = len(categories)
    fts5_query = create_fts5_query(query)

    if fts5_query == "":
        return get_user_recipes(user_id, categories)

    if not categories:
        command = """
        SELECT R.rowid id, R.title
        FROM Recipes_Search R JOIN Recipes S ON S.id = R.rowid
        WHERE S.user_id = ? AND R.rowid > ? AND Recipes_Search MATCH ?
        LIMIT 100
        """
        params = [user_id, after_id, fts5_query]
    else:
        lst = "(" + ",".join(["?"]*n) + ")"
        command = f"""
        SELECT R.rowid id, R.title
        FROM Recipes_Search R JOIN Recipe_Categories C ON R.rowid = recipe_id
            JOIN Recipes S ON S.id = R.rowid
        WHERE S.user_id = ? AND R.rowid > ? AND Recipes_Search MATCH ?
            AND C.category_id in {lst}
        GROUP BY R.rowid
        HAVING COUNT(DISTINCT C.category_id) = ?
        LIMIT 100
        """
        params = [user_id, after_id, fts5_query] + categories + [n]
    return db.query(command, params)
