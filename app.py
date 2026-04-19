import secrets
import re
import sqlite3

from flask import Flask
from flask import abort, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import queries
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    recipes=queries.get_recipes()
    return render_template("index.html",recipes=recipes,
                           categories=queries.get_categories())

@app.route("/user/<int:user_id>")
def user(user_id):
    userdata=queries.get_user_statistics(user_id)
    if userdata is None:
        abort(404)
    recipes=queries.get_user_recipes(user_id)
    return render_template("user.html",user=userdata,recipes=recipes)

@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    recipe_data=queries.get_recipe(recipe_id)
    if recipe_data is None:
        abort(404)
    categories=queries.get_recipe_categories(recipe_id)
    user_id=session.get("user_id")
    user_review=queries.get_user_review(recipe_id,user_id)
    return render_template("recipe.html", recipe=recipe_data,
                           categories=categories,
                           reviews=queries.get_reviews(recipe_id),
                           user_review=user_review)

USERNAME_REGEX="[a-zA-Z0-9_]{1,20}"

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="GET":
        return render_template("register.html",username_regex=USERNAME_REGEX)
    if request.method=="POST":
        username = request.form["username"]
        if not re.fullmatch(USERNAME_REGEX,username):
            return flash("VÄÄRÄNLAINEN KÄYTTÄJÄNIMI")
        password1 = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return flash("SALASANOJEN TÄYTYY OLLA SAMAT")

        password_hash = generate_password_hash(password1)

        try:
            queries.create_user(username,password_hash)
        except sqlite3.IntegrityError:
            return flash("Jollain muulla käyttäjällä on jo tämä nimi")

        return flash("KÄYTTÄJÄTUNNUKSEN LUOMINEN ONNISTUI!")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html",username_regex=USERNAME_REGEX)
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]

        res=queries.get_login_info(username)
        if res is None:
            return flash("Käyttäjää ei ole olemassa")

        password_hash = res["password_hash"]

        if not check_password_hash(password_hash,password):
            return flash("Väärä salasana")

        user_id = res["id"]
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
        return render_template("create.html",categories=queries.get_categories())
    if request.method=="POST":
        check_csrf()

        user_id=session["user_id"]
        title=request.form["title"]
        description=request.form["description"]
        ingredients=request.form["ingredients"]
        instructions=request.form["instructions"]
        categories=request.form.getlist("category")

        recipe_id=queries.create_recipe(user_id,title,description,ingredients,
                                        instructions,categories)

        return redirect(f"/recipe/{recipe_id}")

@app.route("/edit/<int:recipe_id>", methods=["GET","POST"])
def edit(recipe_id):
    if request.method=="GET":
        recipe_data=queries.get_recipe(recipe_id)
        if recipe_data is None:
            abort(404)

        if recipe_data["user_id"] != session["user_id"]:
            abort(403)

        categories=queries.get_recipe_categories(recipe_id)
        current_categories={r["id"] for r in categories}

        return render_template("edit.html", recipe=recipe_data,
                               categories=queries.get_categories(),
                               current_categories=current_categories)
    if request.method=="POST":
        check_csrf()

        user_id=session["user_id"]
        title=request.form["title"]
        description=request.form["description"]
        ingredients=request.form["ingredients"]
        instructions=request.form["instructions"]
        categories=request.form.getlist("category")

        queries.update_recipe(title,description,ingredients,instructions,
                              recipe_id,user_id,categories)

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

    queries.create_review(user_id,recipe_id,rating,content)
    return redirect(f"/recipe/{recipe_id}")


@app.route("/remove/<int:recipe_id>", methods=["GET","POST"])
def remove(recipe_id):
    if request.method=="GET":
        recipe_data=queries.get_recipe(recipe_id)

        if recipe is None:
            abort(404)

        if recipe_data["user_id"] != session["user_id"]:
            abort(403)

        return render_template("remove.html", recipe=recipe_data)
    if request.method=="POST":
        if "continue" not in request.form:
            return redirect(f"/recipe/{recipe_id}")
        check_csrf()

        recipe_data=queries.get_recipe(recipe_id)
        if recipe_data["user_id"] != session["user_id"]:
            abort(403)

        queries.delete_recipe(recipe_id)

        return redirect("/")


@app.route("/search")
def search():
    query=request.args.get("q")

    categories=request.args.getlist("category")

    if query is not None:
        recipes=queries.search_recipes(query,categories)
    else:
        recipes=get_recipes()
        query=""

    return render_template("search.html",recipes=recipes,query=query,
                           categories=queries.get_categories(),
                           current_categories=set([int(i) for i in categories]))
