import secrets
import re
import sqlite3

from flask import Flask
from flask import abort, g, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import db
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

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

def get_user(user_id):
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

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    recipes=db.query("SELECT id, title FROM Recipes")
    return render_template("index.html",recipes=recipes)

@app.route("/user/<int:user_id>")
def user(user_id):
    userdata=get_user(user_id)
    if userdata is None:
        abort(404)
    recipes=get_user_recipes(user_id)
    return render_template("user.html",user=userdata,recipes=recipes)

@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    recipe_data=get_recipe(recipe_id)
    if recipe_data is None:
        abort(404)
    categories=get_recipe_categories(recipe_id)
    user_id=session.get("user_id")
    user_review=get_user_review(recipe_id,user_id)
    return render_template("recipe.html", recipe=recipe_data,
                           categories=categories,
                           reviews=get_reviews(recipe_id),
                           user_review=user_review)

USERNAME_REGEX="[a-zA-Z0-9_]{1,20}"

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="GET":
        return render_template("register.html",username_regex=USERNAME_REGEX)
    if request.method=="POST":
        username = request.form["username"]
        if not re.fullmatch(USERNAME_REGEX,username):
            return "VÄÄRÄNLAINEN KÄYTTÄJÄNIMI"
        password1 = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return "SALASANOJEN TÄYTYY OLLA SAMAT"

        password_hash = generate_password_hash(password1)

        try:
            command = "INSERT INTO Users (username, password_hash) VALUES (?, ?)"
            db.execute(command, [username, password_hash])
        except sqlite3.IntegrityError:
            return "Jollain muulla käyttäjällä on jo tämä nimi"

        return "KÄYTTÄJÄTUNNUKSEN LUOMINEN ONNISTUI!"


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html",username_regex=USERNAME_REGEX)
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]

        command = "SELECT id, password_hash FROM Users WHERE username = ?"
        res = db.query(command,[username])

        if len(res) < 1:
            return "Käyttäjää ei ole olemassa"

        password_hash = res[0]["password_hash"]

        if not check_password_hash(password_hash,password):
            return "Väärä salasana"

        user_id = res[0]["id"]
        session["username"] = username
        session["user_id"] = user_id
        session["csrf_token"] = secrets.token_hex(16)

        return redirect("/")

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    del session["csrf_token"]
    return redirect("/")

@app.route("/create", methods=["GET","POST"])
def create():
    if request.method=="GET":
        return render_template("create.html",categories=get_categories())
    if request.method=="POST":
        check_csrf()

        user_id=session["user_id"]
        title=request.form["title"]
        description=request.form["description"]
        ingredients=request.form["ingredients"]
        instructions=request.form["instructions"]

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
        for category_id in request.form.getlist("category"):
            db.execute(insert_categories_command, [recipe_id, category_id])

        return redirect(f"/recipe/{recipe_id}")

@app.route("/edit/<int:recipe_id>", methods=["GET","POST"])
def edit(recipe_id):
    if request.method=="GET":
        recipe_data=get_recipe(recipe_id)
        if recipe_data is None:
            abort(404)

        if recipe_data["user_id"] != session["user_id"]:
            abort(403)

        current_categories={r["id"] for r in get_recipe_categories(recipe_id)}

        return render_template("edit.html", recipe=recipe_data,
                               categories=get_categories(),
                               current_categories=current_categories)
    if request.method=="POST":
        check_csrf()

        user_id=session["user_id"]
        title=request.form["title"]
        description=request.form["description"]
        ingredients=request.form["ingredients"]
        instructions=request.form["instructions"]

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
        for category_id in request.form.getlist("category"):
            db.execute(insert_categories_command, [recipe_id, category_id])

        return redirect(f"/recipe/{recipe_id}")

@app.route("/review", methods=["POST"])
def create_review():
    if "user_id" not in session:
        abort(403)

    check_csrf()

    user_id=session["user_id"]
    recipe_id=request.form["recipe_id"]
    rating=request.form["rating"]
    content=request.form["content"]

    command="""
    REPLACE INTO Reviews (user_id, recipe_id, rating, content)
    VALUES (?, ?, ?, ?)
    """
    db.execute(command,[user_id,recipe_id,rating,content])
    return redirect(f"/recipe/{recipe_id}")
    

@app.route("/remove/<int:recipe_id>", methods=["GET","POST"])
def remove(recipe_id):
    if request.method=="GET":
        recipe_data=get_recipe(recipe_id)

        if recipe is None:
            abort(404)

        if recipe["user_id"] != session["user_id"]:
            abort(403)

        return render_template("remove.html", recipe=recipe_data)
    if request.method=="POST":
        if "continue" not in request.form:
            return redirect(f"/recipe/{recipe_id}")
        check_csrf()

        recipe_data=get_recipe(recipe_id)
        if recipe_data["user_id"] != session["user_id"]:
            abort(403)

        delete_recipe(recipe_id)

        return redirect("/")


@app.route("/search")
def search():
    query=request.args.get("q")
    if query=="":
        return redirect("/")
    command="SELECT id, title FROM Recipes WHERE title LIKE ? OR description LIKE ? OR ingredients LIKE ? OR instructions LIKE ?"
    query_parameter="%"+query+"%"
    recipes=db.query(command,[query_parameter,query_parameter,query_parameter,query_parameter])
    return render_template("search.html",recipes=recipes,query=query)
