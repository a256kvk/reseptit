from random import choice, choices, randint, sample
from string import ascii_lowercase

import db

def randomword(length=5):
    return "".join(choices(ascii_lowercase, k=length))

def randomwords(n=5):
    l=[]
    for _ in range(n):
        l.append(randomword(randint(5,12)))
    return l

categories_queries = db.query("SELECT id FROM Categories")
categories = [i[0] for i in categories_queries]

USER_COUNT = 10**4
RECIPE_COUNT = 10**5

CREATE_USER_COMMAND = "INSERT INTO Users (username, password_hash) VALUES (?, ?)"

CREATE_RECIPE_COMMAND = """
INSERT INTO Recipes (user_id, title, description, ingredients,
                     instructions)
VALUES (?, ?, ?, ?, ?)
"""

INSERT_CATEGORIES_COMMAND = """
INSERT INTO Recipe_Categories (recipe_id, category_id) VALUES (?, ?)
"""

CREATE_REVIEW_COMMAND = """
REPLACE INTO Reviews (user_id, recipe_id, rating, content) VALUES (?, ?, ?, ?)
"""

food_words = ["suomi", "banaani", "halloumi", "pata", "italia", "isoäidin"]
ingredient_words = ["banaani", "mansikka", "jauheliha", "random", "suola",
                    "muumio", "vetyperoksidi", "parmesaani", "juusto",
                    "mozarella"]

with db.get_cursor() as cur:
    for i in range(1, USER_COUNT+1):
        username=f"bot_user_{i}"
        password=f"bot_password_{i}"
        cur.execute(CREATE_USER_COMMAND, [username, password])

    for i in range(1, RECIPE_COUNT+1):
        if i<=1000:
            user_id = 1
        elif i<=2000:
            user_id = 2
        else:
            user_id = randint(1, USER_COUNT)

        title = " ".join([choice(food_words), randomword(),
                          choice(ingredient_words)])

        description = " ".join(randomwords(randint(1, 10))
                               + choices(food_words, k=5)
                               + choices(ingredient_words, k=5))

        if i%1000==0:
            description += " tuhat"

        if i%100==0:
            description += " sata"

        if i%10==0:
            description += " kymmenen"

        ingredients = ", ".join(randomwords(randint(0, 1))
                               + choices(food_words, k=randint(0, 2))
                               + choices(ingredient_words, k=randint(0, 6)))

        instructions = " ".join(["lol"] + randomwords(randint(0, 50))
                               + choices(food_words, k=randint(0, 20))
                               + choices(ingredient_words, k=randint(0, 60)))

        params = [user_id, title, description, ingredients, instructions]

        res = cur.execute(CREATE_RECIPE_COMMAND,params)
        recipe_id = res.lastrowid

        cats = sample(categories, k=randint(0,5))

        for category_id in cats:
            cur.execute(INSERT_CATEGORIES_COMMAND, [recipe_id, category_id])

    for i in range(1, USER_COUNT+1):
        user_id = i
        rating = randint(1,5)
        content = " ".join(["kommentti"] + randomwords(randint(0, 50))
                  + choices(food_words, k=randint(0, 20))
                  + choices(ingredient_words, k=randint(0, 60)))
        cur.execute(CREATE_REVIEW_COMMAND, [user_id, 1, rating, content])

    for i in range(1, 10**6+1):
        user_id = randint(1,USER_COUNT)
        recipe_id = randint(1,1000)
        rating = randint(1,5)
        content = " ".join(["kommentti"] + randomwords(randint(0, 50))
                  + choices(food_words, k=randint(0, 20))
                  + choices(ingredient_words, k=randint(0, 60)))
        cur.execute(CREATE_REVIEW_COMMAND, [user_id, recipe_id, rating, content])


    for i in range(1, 10**6+1):
        user_id = randint(1,USER_COUNT)
        recipe_id = randint(1,RECIPE_COUNT)
        rating = randint(1,5)
        content = " ".join(["kommentti"] + randomwords(randint(0, 50))
                  + choices(food_words, k=randint(0, 20))
                  + choices(ingredient_words, k=randint(0, 60)))
        cur.execute(CREATE_REVIEW_COMMAND, [user_id, recipe_id, rating, content])

    for i in range(1, 10**5):
        user_id = randint(1,USER_COUNT)
        recipe_id = randint(1001,2000)
        rating = randint(1,5)
        content = " ".join(["kommentti"] + randomwords(randint(0, 50))
                  + choices(food_words, k=randint(0, 20))
                  + choices(ingredient_words, k=randint(0, 60)))
        cur.execute(CREATE_REVIEW_COMMAND, [user_id, recipe_id, rating, content])
