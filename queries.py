from flask import g

import db

def get_recipe(recipe_id):
    command="""
    SELECT Recipes.id id, user_id, username, title, description, ingredients, 
           instructions
    FROM Recipes JOIN Users ON user_id=Users.id
    WHERE Recipes.id = ?
    """
    res=db.query(command, [recipe_id])

    if len(res) < 1:
        return None

    return res[0]

def get_recipes():
    return db.query("SELECT id, title FROM Recipes")

def create_recipe(user_id,title,description,ingredients,instructions,
                  categories):
    command="""
    INSERT INTO Recipes (user_id, title, description, ingredients,
                         instructions)
    VALUES (?, ?, ?, ?, ?)
    """
    params=[user_id,title,description,ingredients,instructions]
    db.execute(command,params)
    recipe_id = g.last_insert_id

    insert_categories_command="""
    INSERT INTO Recipe_Categories (recipe_id, category_id) VALUES (?, ?)
    """
    for category_id in categories:
        db.execute(insert_categories_command, [recipe_id, category_id])

    return recipe_id

def update_recipe(title,description,ingredients,instructions,recipe_id,user_id,
                  categories):
    command="""
    UPDATE Recipes
    SET title = ?, description = ?, ingredients = ?, instructions = ?
    WHERE id = ? AND user_id = ?
    """
    params=[title,description,ingredients,instructions,recipe_id,user_id]
    db.execute(command, params)

    delete_command="DELETE FROM Recipe_Categories WHERE recipe_id = ?"
    db.execute(delete_command, [recipe_id])

    insert_categories_command="""
    INSERT INTO Recipe_Categories (recipe_id, category_id) VALUES (?, ?)
    """
    for category_id in categories:
        db.execute(insert_categories_command, [recipe_id, category_id])

def get_user_statistics(user_id):
    command="""
    SELECT id, username,
        (SELECT COUNT(*) FROM Recipes WHERE user_id=?) recipe_count,
        (SELECT COUNT(*) FROM Reviews WHERE user_id=?) review_count,
        (SELECT AVG(rating)
        FROM Reviews V JOIN Recipes R ON recipe_id = R.id
        WHERE R.user_id=?) avg_rating
    FROM Users
    WHERE id = ?
    """
    res=db.query(command, [user_id,user_id,user_id,user_id])
    if len(res)!=1:
        return None
    return res[0]

def get_user_recipes(user_id):
    command="SELECT id, title FROM Recipes WHERE user_id = ?"
    recipes=db.query(command,[user_id])
    return recipes

def get_categories():
    command="SELECT id, name FROM Categories"
    res=db.query(command)
    return res

def get_reviews(recipe_id):
    command="""
    SELECT username, user_id, rating, content
    FROM Reviews R JOIN Users U ON U.id = R.user_id
    WHERE recipe_id = ?
    """
    comments=db.query(command,[recipe_id])
    return comments

def get_user_review(recipe_id,user_id):
    if user_id is None:
        return None
    command="""
    SELECT rating, content FROM Reviews WHERE recipe_id = ? AND user_id = ?
    """
    review=db.query(command,[recipe_id,user_id])
    if len(review)!=1:
        return None
    return review[0]

def create_review(user_id,recipe_id,rating,content):
    command="""
    REPLACE INTO Reviews (user_id, recipe_id, rating, content)
    VALUES (?, ?, ?, ?)
    """
    db.execute(command,[user_id,recipe_id,rating,content])

def get_recipe_categories(recipe_id):
    command="""
    SELECT C.id, name
    FROM Recipe_Categories RC JOIN Categories C ON RC.category_id = C.id
    WHERE RC.recipe_id = ?
    """
    res=db.query(command,[recipe_id])
    return res

def delete_recipe(recipe_id):
    db.execute("DELETE FROM Recipe_Categories WHERE recipe_id = ?", [recipe_id])
    db.execute("DELETE FROM Recipes WHERE id = ?", [recipe_id])

def create_user(username,password_hash):
    command = "INSERT INTO Users (username, password_hash) VALUES (?, ?)"
    db.execute(command, [username, password_hash])

def get_login_info(username):
    command = "SELECT id, password_hash FROM Users WHERE username = ?"
    res = db.query(command,[username])
    if len(res)<1:
        return None
    return res[0]

def search_recipes(query,categories):
    n=len(categories)
    query_parameter="%"+query+"%"
    if n==0:
        command="""
        SELECT id, title
        FROM Recipes
        WHERE 
            title LIKE ? OR description LIKE ? OR ingredients LIKE ? 
            OR instructions LIKE ?
        """
        params=[query_parameter]*4
    else:
        lst='('+','.join(['?']*n)+')'
        command=f"""
        SELECT R.id, title
        FROM Recipes R JOIN Recipe_Categories C ON R.id = recipe_id
        WHERE
            (title LIKE ? OR description LIKE ? OR ingredients LIKE ? 
            OR instructions LIKE ?) 
            AND C.category_id in {lst}
        GROUP BY R.id
        HAVING COUNT(DISTINCT C.category_id) = ?
        """
        params=[query_parameter]*4+categories+[len(categories)]
    return db.query(command,params)
