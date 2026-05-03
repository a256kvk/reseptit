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

def get_after():
    after = request.args.get("after")
    if after is None:
        return 0
    return int(after)

def get_page_last_id(results):
    if len(results) > 1:
        return int(results[-2]["id"])
    return 0

@app.route("/")
def index():
    after = get_after()
    recipes = queries.get_recipes(after)
    last_id = get_page_last_id(recipes)
    return render_template("index.html", recipes=recipes[:100],
                           categories=queries.get_categories(),
                           last_id=last_id,
                           next_page_needed=len(recipes) > 100)

@app.route("/user/<int:user_id>")
def user(user_id):
    userdata = queries.get_user_statistics(user_id)
    after = get_after()
    if userdata is None:
        abort(404)
    recipes = queries.get_user_recipes(user_id,after_id=after)
    last_id = get_page_last_id(recipes)
    return render_template("user.html", user=userdata, recipes=recipes[:100],
                           last_id=last_id,
                           next_page_needed=len(recipes) > 100)

@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    after = get_after()
    recipe_data = queries.get_recipe(recipe_id)
    if recipe_data is None:
        abort(404)
    categories = queries.get_recipe_categories(recipe_id)
    user_id = session.get("user_id")
    user_review = queries.get_user_review(recipe_id, user_id)
    reviews = queries.get_reviews(recipe_id, after)
    return render_template("recipe.html", recipe=recipe_data,
                           categories=categories, reviews=reviews,
                           user_review=user_review,
                           last_id=get_page_last_id(reviews),
                           next_page_needed=len(reviews)>100)

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

def validate_username(username):
    if len(username) < USERNAME_MINLENGTH:
        flash("liian lyhyt käyttäjänimi", "error")
        return False
    if len(username) > USERNAME_MAXLENGTH:
        flash("liian pitkä käyttäjänimi", "error")
        return False
    if not re.fullmatch(USERNAME_REGEX, username):
        flash("VÄÄRÄNLAINEN KÄYTTÄJÄNIMI", "error")
        return False
    return True

def validate_password(password1, password2):
    if password1 != password2:
        flash("SALASANOJEN TÄYTYY OLLA SAMAT", "error")
        return False

    if len(password1) < PASSWORD_MINLENGTH:
        flash("liian lyhyt salasana", "error")
        return False
    return True

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", username_regex=USERNAME_REGEX,
                               username_minlength=USERNAME_MINLENGTH,
                               username_maxlength=USERNAME_MAXLENGTH,
                               password_minlength=PASSWORD_MINLENGTH)
    if request.method == "POST":
        username = request.form["username"].lower()
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        username_valid = validate_username(username)
        password_valid = validate_password(password1, password2)
        if not username_valid or not password_valid:
            return redirect("/register")

        password_hash = generate_password_hash(password1)

        try:
            queries.create_user(username, password_hash)
        except sqlite3.IntegrityError:
            flash("Jollain muulla käyttäjällä on jo tämä nimi", "error")
            return redirect("/register")

        flash("KÄYTTÄJÄTUNNUKSEN LUOMINEN ONNISTUI!", "info")
        return redirect("/")

def verify_login(username, password):
    res = queries.get_login_info(username)
    if res is None:
        flash("Käyttäjää ei ole olemassa", "error")
        return None

    password_hash = res["password_hash"]

    if not check_password_hash(password_hash, password):
        flash("Väärä salasana", "error")
        return None
    return res["id"]

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", username_regex=USERNAME_REGEX)
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        user_id = verify_login(username, password)
        if user_id is None:
            return redirect("/login")

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

def validate_recipe(title, description, ingredients, instructions):
    if len(title) < TITLE_MINLENGTH:
        flash("liian lyhyt otsikko", "error")
        return False
    if len(title) > TITLE_MAXLENGTH:
        flash("liian pitkä otsikko", "error")
        return False
    if len(description) > DESCRIPTION_MAXLENGTH:
        flash("liian pitkä kuvaus", "error")
        return False
    if len(ingredients) > INGREDIENTS_MAXLENGTH:
        flash("liian pitkä ainesosat", "error")
        return False
    if len(instructions) > INSTRUCTIONS_MAXLENGTH:
        flash("liian pitkät ohjeet", "error")
        return False
    return True


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

        if not validate_recipe(title, description, ingredients, instructions):
            return redirect("/create")

        recipe_data = queries.Recipe(title, description, ingredients,
                                     instructions, categories)
        recipe_id=queries.create_recipe(user_id, recipe_data)

        return redirect(f"/recipe/{recipe_id}")

@app.route("/edit/<int:recipe_id>", methods=["GET", "POST"])
def edit(recipe_id):
    if request.method == "GET":
        recipe_data=queries.get_recipe(recipe_id)
        if recipe_data is None:
            abort(404)

        if recipe_data["user_id"] != session.get("user_id"):
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

        if not validate_recipe(title, description, ingredients, instructions):
            return redirect(f"/edit/{recipe_id}")

        # checking privileges is done in update_recipe in the sql command

        recipe_data = queries.Recipe(title, description, ingredients,
                                     instructions, categories)
        queries.update_recipe(recipe_id, user_id, recipe_data)

        return redirect(f"/recipe/{recipe_id}")

@app.route("/review", methods=["POST"])
def create_review():
    if "user_id" not in session:
        abort(403)

    check_csrf()

    user_id = session["user_id"]
    recipe_id = request.form["recipe_id"]
    rating = request.form["rating"] # validation in the sql schema
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

        if recipe_data is None:
            abort(404)

        if recipe_data["user_id"] != session.get("user_id"):
            abort(403)

        return render_template("remove.html", recipe=recipe_data)
    if request.method == "POST":
        if "continue" not in request.form:
            return redirect(f"/recipe/{recipe_id}")
        check_csrf()

        recipe_data = queries.get_recipe(recipe_id)
        if recipe_data["user_id"] != session.get("user_id"):
            abort(403)

        queries.delete_recipe(recipe_id)

        return redirect("/")

@app.route("/remove_review/<int:review_id>", methods=["GET", "POST"])
def remove_review(review_id):
    if request.method == "GET":
        review_data = queries.get_review(review_id)

        if review_data is None:
            abort(404)

        if review_data["user_id"] != session.get("user_id"):
            abort(403)

        return render_template("remove_review.html", review_id=review_id,
                               review=review_data)
    if request.method == "POST":
        if "continue" not in request.form:
            return redirect(f"/recipe/{recipe_id}")
        check_csrf()

        review_data = queries.get_review(review_id)
        if review_data["user_id"] != session.get("user_id"):
            abort(403)
        recipe_id = review_data["recipe_id"]

        queries.delete_review(review_id)

        return redirect(f"/recipe/{recipe_id}")

@app.route("/search")
def search():
    query = request.args.get("q")
    user_id = request.args.get("u")
    if query is None:
        query = ""

    categories_set = {int(i) for i in request.args.getlist("category")}
    categories = list(categories_set)
    all_categories = queries.get_categories()
    all_category_ids = {int(i["id"]) for i in all_categories}
    invalid_categories = (
        len(categories_set) > len(all_categories)
        or not categories_set.issubset(all_category_ids)
    )

    after = get_after()

    if user_id is None:
        if invalid_categories:
            recipes = []
        else:
            recipes = queries.search_recipes(query, categories, after)
        username = None
    else:
        user_id = int(user_id)
        if invalid_categories:
            recipes = []
        else:
            recipes = queries.search_user_recipes(user_id, query, categories,
                                                  after)
        username = queries.get_username(user_id)

    new_args = request.args.to_dict(flat=False)
    new_args["after"] = get_page_last_id(recipes)

    return render_template("search.html", recipes=recipes[:100], query=query,
                           categories=all_categories,
                           current_categories=categories_set, user_id=user_id,
                           username=username, next_page_args=new_args,
                           next_page_needed=len(recipes) > 100)
