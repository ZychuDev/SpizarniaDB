from flask import Flask, render_template, request, jsonify, redirect, url_for

from Database import Database

def connect():
    uri = "neo4j+s://576b7393.databases.neo4j.io" #os.environ['uri']
    user = "neo4j" #os.environ['user']
    password = "dPY42zYTemGTvNFRHC1Ex172Xn_NCP7CxVEuaVN7t6c" #os.environ['pass']
    return Database(uri, user, password) 

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')

@app.route("/create/recipe", methods=['POST'])
def create_recipe():
    db = connect()
    name = request.json['name']
    description = request.json['description']
    result = db.create_recipe(name, description)
    db.close()

    if result:
        msg = f"Stworzono nowy przepis {result[0]['r']}"
    else:
        msg = "Nie udało sie stworzyc nowego przepisu"

    return jsonify({"result":msg})


@app.route("/createRecipeForm")
def createRecipeForm():
    return render_template("createRecipeForm.html")

@app.route("/add/ingredient", methods=["POST"])
def add_ingredient():
    db = connect()
    name = request.json["name"]
    result = db.add_ingredient(name)
    db.close()

    if result:
        msg = f"Dodano {result[0]['i']} do posiadanych składników"
    else:
        msg = "Nie udało sie dodać nowego składnika do posiadanych"
    return jsonify({"result": msg})

@app.route("/addIngredientForm")
def addIngredientForm():
    db = connect()
    my = db.get_my_ingredients()
    all = db.get_ingredients()
    ingredients = list(set(all) - set(my))
    return render_template("addIngredientForm.html", ingredients = ingredients)

@app.route("/get/my_ingredients", methods=["GET"])
def get_my_ingredients():
    db = connect()
    result = db.get_my_ingredients()
    db.close()
    return render_template("ingredients.html", ingredients = result)

@app.route("/delete/ingredient/<string:name>")
def delete_ingredient(name):
    db = connect()
    db.delete_ingredient(name)
    db.close()
    return redirect(url_for("get_my_ingredients")) #jsonify({"result": f"Usunięto składnik {name}"})

@app.route("/get/my_recipies")
def get_my_recipies():
    db = connect()
    recipies = db.get_my_recipies()
    names = [r["name"] for r in recipies]
    db.close()
    return render_template("myRecipies.html", recipies = names)

@app.route("/update/recipe/<string:name>")
def update_recipe(name):
    db = connect()
    result = db.get_recipe(name)[0]
    my = db.get_recipe_ingredients(name)
    print(my)
    all = db.get_ingredients()
    rest = list(set(all) - set(my))
    db.close()
    return render_template("recipe.html", recipe=name, d = result["r"], nr = result["nr"], ingredients = my, rest = rest )

@app.route("/delete/recipe/<string:name>")
def delete_recipe(name):
    db = connect()
    db.delete_recipe(name)
    db.close()
    return redirect(url_for("get_my_recipies"))

@app.route("/update/recipe/<string:recipe_name>/add/<string:ingredient_name>")
def add_recipe_ingredient(recipe_name, ingredient_name):
    db = connect()
    db.add_recipe_ingredient(recipe_name, ingredient_name)
    db.close()
    return redirect(url_for("update_recipe", name=recipe_name))

@app.route("/update/recipe/<string:recipe_name>/delete/<string:ingredient_name>")
def remove_recipe_ingredient(recipe_name, ingredient_name):
    db = connect()
    db.remove_recipe_ingredient(recipe_name, ingredient_name)
    db.close()
    return redirect(url_for("update_recipe", name=recipe_name))

@app.route("/get/users")
def get_users():
    db = connect()
    all = db.get_persons()
    my = db.get_followed()
    rest = list(set(all) - set(my))
    db.close()
    return render_template("myFollowers.html", users = my, rest = rest)

@app.route("/follow/<string:name>")
def follow(name):
    db = connect()
    db.follow(name)
    db.close()
    return redirect(url_for("get_users"))

@app.route("/unfollow/<string:name>")
def unfollow(name):
    db = connect()
    db.unfollow(name)
    db.close()
    return redirect(url_for("get_users"))

@app.route("/get/recipe/<string:name>")
def get_recipe(name):
    db = connect()
    result = db.get_recipe(name)[0]
    ingredients = db.get_recipe_ingredients(name)
    db.close()
    return render_template("other_recipe.html", d=result["r"], ingredients=ingredients, a=result["a"])

@app.route("/analyze")
def analyze():
    db = connect()
    my = db.get_my_ingredients()
    all = db.get_ingredients()
    alergens = list(set(all) - set(my))
    recipies = db.analyze(my, alergens)
    print(recipies)
    db.close()
    return render_template("analyze.html", recipies=recipies)

@app.route("/rank")
def rank():
    db = connect()
    ingredients = db.rank()
    db.close()
    return render_template("rank.html", ingredients=ingredients)


if __name__ == "__main__":
    app.run(debug=True)