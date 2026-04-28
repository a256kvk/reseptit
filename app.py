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
    recipes = queries.get_recipes()
    return render_template("index.html", recipes=recipes,
                           categories=queries.get_categories())

@app.route("/user/<int:user_id>")
def user(user_id):
    userdata = queries.get_user_statistics(user_id)
    if userdata is None:
        abort(404)
    recipes = queries.get_user_recipes(user_id)
    return render_template("user.html", user=userdata, recipes=recipes)

@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    recipe_data = queries.get_recipe(recipe_id)
    if recipe_data is None:
        abort(404)
    categories = queries.get_recipe_categories(recipe_id)
    user_id = session.get("user_id")
    user_review = queries.get_user_review(recipe_id, user_id)
    return render_template("recipe.html", recipe=recipe_data,
                           categories=categories,
                           reviews=queries.get_reviews(recipe_id),
                           user_review=user_review)

USERNAME_MINLENGTH = 1
USERNAME_MAXLENGTH = 20
USERNAME_REGEX = "[a-zA-Z0-9_]{1,20}"
PASSWORD_MINLENGTH = 3

TITLE_MINLENGTH = 1
TITLE_MAXLENGTH = 50
DESCRIPTION_MAXLENGTH = 500
INGREDIENTS_MAXLENGTH = 5000
INSTRUCTIONS_MAXLENGTH = 5000

REVIEW_MAXLENGTH = 500

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", username_regex=USERNAME_REGEX,
                               username_minlength=USERNAME_MINLENGTH,
                               username_maxlength=USERNAME_MAXLENGTH,
                               password_minlength=PASSWORD_MINLENGTH)
    if request.method == "POST":
        username = request.form["username"]
        if len(username) < USERNAME_MINLENGTH:
            flash("liian lyhyt käyttäjänimi", "error")
            return redirect("/register")
        if len(username) > USERNAME_MAXLENGTH:
            flash("liian pitkä käyttäjänimi", "error")
            return redirect("/register")
        if not re.fullmatch(USERNAME_REGEX, username):
            flash("VÄÄRÄNLAINEN KÄYTTÄJÄNIMI", "error")
            return redirect("/register")
        password1 = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            flash("SALASANOJEN TÄYTYY OLLA SAMAT", "error")
            return redirect("/register")

        if len(password1) < PASSWORD_MINLENGTH:
            flash("liian lyhyt salasana", "error")
            return redirect("/register")

        password_hash = generate_password_hash(password1)

        try:
            queries.create_user(username, password_hash)
        except sqlite3.IntegrityError:
            flash("Jollain muulla käyttäjällä on jo tämä nimi", "error")
            return redirect("/register")

        flash("KÄYTTÄJÄTUNNUKSEN LUOMINEN ONNISTUI!", "info")
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", username_regex=USERNAME_REGEX)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        res = queries.get_login_info(username)
        if res is None:
            flash("Käyttäjää ei ole olemassa", "error")
            return redirect("/login")

        password_hash = res["password_hash"]

        if not check_password_hash(password_hash, password):
            flash("Väärä salasana", "error")
            return redirect("/login");

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

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return render_template("editor.html", recipe={},
                               title="Uusi resepti",
                               post_url="/create",
                               categories=queries.get_categories(),
                               title_minlength=TITLE_MINLENGTH,
                               title_maxlength=TITLE_MAXLENGTH,
                               description_maxlength=DESCRIPTION_MAXLENGTH,
                               ingredients_maxlength=INGREDIENTS_MAXLENGTH,
                               instructions_maxlength=INSTRUCTIONS_MAXLENGTH)
    if request.method == "POST":
        check_csrf()

        user_id = session["user_id"]
        title = request.form["title"]
        description = request.form["description"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]
        categories = request.form.getlist("category")

        if len(title) < TITLE_MINLENGTH:
            flash("liian lyhyt otsikko", "error")
            return redirect("/create")
        if len(title) > TITLE_MAXLENGTH:
            flash("liian pitkä otsikko", "error")
            return redirect("/create")
        if len(description) > DESCRIPTION_MAXLENGTH:
            flash("liian pitkä kuvaus", "error")
            return redirect("/create")
        if len(ingredients) > INGREDIENTS_MAXLENGTH:
            flash("liian pitkä ainesosat", "error")
            return redirect("/create")
        if len(instructions) > INSTRUCTIONS_MAXLENGTH:
            flash("liian pitkät ohjeet", "error")
            return redirect("/create")

        recipe_id=queries.create_recipe(user_id,title, description,
                                        ingredients, instructions,
                                        categories)

        return redirect(f"/recipe/{recipe_id}")

@app.route("/edit/<int:recipe_id>", methods=["GET", "POST"])
def edit(recipe_id):
    if request.method == "GET":
        recipe_data=queries.get_recipe(recipe_id)
        if recipe_data is None:
            abort(404)

        if recipe_data["user_id"] != session["user_id"]:
            abort(403)

        categories = queries.get_recipe_categories(recipe_id)
        current_categories = {r["id"] for r in categories}

        return render_template("editor.html", recipe=recipe_data,
                               title="Muokkaa reseptiä",
                               post_url=f"/edit/{recipe_id}",
                               categories=queries.get_categories(),
                               current_categories=current_categories,
                               title_minlength=TITLE_MINLENGTH,
                               title_maxlength=TITLE_MAXLENGTH,
                               description_maxlength=DESCRIPTION_MAXLENGTH,
                               ingredients_maxlength=INGREDIENTS_MAXLENGTH,
                               instructions_maxlength=INSTRUCTIONS_MAXLENGTH)
    if request.method == "POST":
        check_csrf()

        user_id = session["user_id"]
        title = request.form["title"]
        description = request.form["description"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]
        categories = request.form.getlist("category")

        if len(title) < TITLE_MINLENGTH:
            flash("liian lyhyt otsikko", "error")
            return redirect("/create")
        if len(title) > TITLE_MAXLENGTH:
            flash("liian pitkä otsikko", "error")
            return redirect(f"/edit/{recipe_id}")
        if len(description) > DESCRIPTION_MAXLENGTH:
            flash("liian pitkä kuvaus", "error")
            return redirect(f"/edit/{recipe_id}")
        if len(ingredients) > INGREDIENTS_MAXLENGTH:
            flash("liian pitkä ainesosat", "error")
            return redirect(f"/edit/{recipe_id}")
        if len(instructions) > INSTRUCTIONS_MAXLENGTH:
            flash("liian pitkät ohjeet", "error")
            return redirect(f"/edit/{recipe_id}")

        queries.update_recipe(title, description, ingredients, instructions,
                              recipe_id, user_id, categories)

        return redirect(f"/recipe/{recipe_id}")

@app.route("/review", methods=["POST"])
def create_review():
    if "user_id" not in session:
        abort(403)

    check_csrf()

    user_id = session["user_id"]
    recipe_id = request.form["recipe_id"]
    rating = request.form["rating"]
    content = request.form["content"]
    if len(content) > REVIEW_MAXLENGTH:
        flash("liian pitkä kommentti", "error")
        return redirect(f"/recipe/{recipe_id}")

    queries.create_review(user_id, recipe_id, rating, content)
    return redirect(f"/recipe/{recipe_id}")


@app.route("/remove/<int:recipe_id>", methods=["GET", "POST"])
def remove(recipe_id):
    if request.method == "GET":
        recipe_data = queries.get_recipe(recipe_id)

        if recipe is None:
            abort(404)

        if recipe_data["user_id"] != session["user_id"]:
            abort(403)

        return render_template("remove.html", recipe=recipe_data)
    if request.method == "POST":
        if "continue" not in request.form:
            return redirect(f"/recipe/{recipe_id}")
        check_csrf()

        recipe_data = queries.get_recipe(recipe_id)
        if recipe_data["user_id"] != session["user_id"]:
            abort(403)

        queries.delete_recipe(recipe_id)

        return redirect("/")


@app.route("/search")
def search():
    query = request.args.get("q")

    categories = request.args.getlist("category")

    if query is not None:
        recipes = queries.search_recipes(query,categories)
    else:
        recipes = queries.get_recipes()
        query = ""

    categories_set = {int(i) for i in categories}

    return render_template("search.html", recipes=recipes, query=query,
                           categories=queries.get_categories(),
                           current_categories=categories_set)
