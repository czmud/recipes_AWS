from flask_app import app
from flask import render_template,redirect,request,session,flash
from flask_app.models import recipe, user

@app.route('/recipes/')
def recipes_show_all():
    if 'user_id' not in session:
        return redirect('/')
    users = user.User.get_user_by_id( {"id": session["user_id"]} )
    recipes = recipe.Recipe.get_all()
    
    session.clear()
    session["user_id"] = users.id
    return render_template("recipeall.html", users=users, recipes=recipes)

@app.route('/recipes/new/')
def recipes_new_form():
    if 'user_id' not in session:
        return redirect('/')
    users = user.User.get_user_by_id( {"id": session["user_id"]} )
    return render_template("recipeadd.html", users=users)

@app.route('/recipes/<int:recipe_id>/')
def recipes_view_details(recipe_id):
    if 'user_id' not in session:
        return redirect('/')
    users = user.User.get_user_by_id( {"id": session["user_id"]} )
    recipes = recipe.Recipe.get_recipe_by_id( {"id": recipe_id} )
    return render_template("recipeview.html", users=users, recipes=recipes)

@app.route('/recipes/<int:recipe_id>/edit/')
def edit_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect('/')
    users = user.User.get_user_by_id( {"id": session["user_id"]} )
    recipes = recipe.Recipe.get_recipe_by_id( {"id": recipe_id} )
    if "recipe_id" not in session:
        session["recipe_id"] = recipe_id
        session["name"] = recipes.name
        session["description"] = recipes.description
        session["instructions"] = recipes.instructions
        session["made_at"] = recipes.made_at
        session["under_thirty_mins"] = recipes.under_thirty_mins
    return render_template("recipeedit.html", users=users)

@app.route('/recipes/<int:recipe_id>/delete/', methods=["POST"])
def delete_recipe(recipe_id):
    recipe.Recipe.delete_recipe_by_id( {"id": recipe_id} )
    return redirect('/recipes')

@app.route('/recipe_update', methods=["POST"])
def update_recipe():
    if not recipe.Recipe.validate_recipe(request.form):
        session["name"] = request.form["name"]
        session["description"] = request.form["description"]
        session["instructions"] = request.form["instructions"]
        session["made_at"] = request.form["made_at"]
        session["under_thirty_mins"] = int(request.form["under_thirty_mins"])
        return redirect('/recipes/'+str(session["recipe_id"])+"/edit")
    
    data = {
        "id": session["recipe_id"],
        "name": request.form["name"].title(),
        "description": request.form["description"],
        "instructions": request.form["instructions"],
        "under_thirty_mins": int(request.form["under_thirty_mins"]),
        "made_at": request.form["made_at"]
    }
    
    recipe.Recipe.update_recipe_by_id( data )

    return redirect('/recipes')

@app.route('/recipe_add/', methods=["POST"])
def add_new_recipe():
    if not recipe.Recipe.validate_recipe(request.form):
        session["name"] = request.form["name"]
        session["description"] = request.form["description"]
        session["instructions"] = request.form["instructions"]
        session["made_at"] = request.form["made_at"]
        session["under_thirty_mins"] = int(request.form["under_thirty_mins"])
        return redirect('/recipes/new')
    data = {
        "user_id": session["user_id"],
        "name": recipe.Recipe.curate_user_input(request.form["name"].title()),
        "description": recipe.Recipe.curate_user_input(request.form["description"]),
        "instructions": recipe.Recipe.curate_user_input(request.form["instructions"]),
        "under_thirty_mins": int(request.form["under_thirty_mins"]),
        "made_at": request.form["made_at"]
    }
    recipe.Recipe.save( data )

    return redirect('/recipes')

