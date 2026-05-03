from os import system
from random import choice, choices, randint, sample
from string import ascii_lowercase

import db
#import queries

def randomword(length=5):
    return "".join(choices(ascii_lowercase, k=length))

def randomwords(n=5):
    l=[]
    for i in range(n):
        l.append(randomword(randint(5,12)))
    return l

categories_queries = db.query("SELECT id FROM Categories")
categories = [i[0] for i in categories_queries]

system("rm database.db")
system("sqlite3 database.db <schema.sql")
system("sqlite3 database.db <add_categories.sql")

user_count = 10**4
recipe_count = 10**5
comment_count_big = 10**4

create_user_command = "INSERT INTO Users (username, password_hash) VALUES (?, ?)"

create_recipe_command = """
INSERT INTO Recipes (user_id, title, description, ingredients,
                     instructions)
VALUES (?, ?, ?, ?, ?)
"""

insert_categories_command = """
INSERT INTO Recipe_Categories (recipe_id, category_id) VALUES (?, ?)
"""

create_review_command = """
REPLACE INTO Reviews (user_id, recipe_id, rating, content) VALUES (?, ?, ?, ?)
"""

food_words = ["suomi", "banaani", "halloumi", "pata", "italia", "isoäidin"]
ingredient_words = ["banaani", "mansikka", "jauheliha", "random", "suola",
                    "muumio", "vetyperoksidi", "parmesaani", "juusto",
                    "mozarella"]

with db.get_cursor() as cur:
    for i in range(1, user_count+1):
        username=f"bot_user_{i}"
        password=f"bot_password_{i}"
        cur.execute(create_user_command, [username, password])

    for i in range(1, recipe_count+1):
        user_id = randint(1, user_count)

        title = " ".join([choice(food_words), randomword(),
                          choice(ingredient_words)])

        description = " ".join(randomwords(randint(1, 10))
                               + choices(food_words, k=5)
                               + choices(ingredient_words, k=5))

        ingredients = ", ".join(randomwords(randint(0, 1))
                               + choices(food_words, k=randint(0, 2))
                               + choices(ingredient_words, k=randint(0, 6)))

        instructions = " ".join(["lol"] + randomwords(randint(0, 50))
                               + choices(food_words, k=randint(0, 20))
                               + choices(ingredient_words, k=randint(0, 60)))

        params = [user_id, title, description, ingredients, instructions]

        res = cur.execute(create_recipe_command,params)
        recipe_id = res.lastrowid

        cats = sample(categories, k=randint(0,5))

        for category_id in cats:
            cur.execute(insert_categories_command, [recipe_id, category_id])

    for i in range(1, comment_count_big+1):
        user_id = randint(1,user_count)
        rating = randint(1,5)
        content = " ".join(["kommentti"] + randomwords(randint(0, 50))
                  + choices(food_words, k=randint(0, 20))
                  + choices(ingredient_words, k=randint(0, 60)))
        cur.execute(create_review_command, [user_id, 1, rating, content])
