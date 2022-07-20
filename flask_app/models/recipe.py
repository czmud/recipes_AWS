from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import user
from flask import flash

class Recipe:
    db = "recipes_schema"
    def __init__( self , data ):
        self.id = data['id']
        self.user_id = data['user_id']
        self.name = data['name']
        self.description = data['description']
        self.instructions = data['instructions']
        self.under_thirty_mins = data['under_thirty_mins']
        self.made_at = data['made_at']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.users = []
    @classmethod
    def save( cls, data ):
        query = "INSERT INTO recipes ( user_id, name, description, instructions, under_thirty_mins, made_at ) VALUES \
            ( %(user_id)s, %(name)s, %(description)s, %(instructions)s, %(under_thirty_mins)s, %(made_at)s );"
        return connectToMySQL(cls.db).query_db( query, data )
    @classmethod
    def update_recipe_by_id( cls, data ):
        query = "UPDATE recipes SET name=%(name)s, description=%(description)s, instructions=%(instructions)s, \
            under_thirty_mins=%(under_thirty_mins)s, made_at=%(made_at)s WHERE id=%(id)s;"
        return connectToMySQL(cls.db).query_db( query, data )
    @classmethod
    def get_all( cls ):
        query = "SELECT * FROM recipes LEFT JOIN users ON recipes.user_id = users.id;"
        results = connectToMySQL(cls.db).query_db(query)
        recipes = []
        for row in results:
            recipes.append(cls(row))
            user_data = {
                "id": row["users.id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "password_hash": row["password_hash"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
            recipes[-1].users.append(user.User(user_data))
        return recipes
    @classmethod
    def get_recipe_by_id( cls, data ):
        query = "SELECT * FROM recipes JOIN users ON recipes.user_id = users.id \
            WHERE recipes.id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query, data)
        recipes = False
        if len(results) > 0:
            recipes = cls(results[0])
        for row in results:
            user_data = {
                "id": row["users.id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "password_hash": row["password_hash"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
            recipes.users.append(user.User(user_data))
        return recipes
    
    @classmethod
    def delete_recipe_by_id( cls, data ):
        query = "DELETE FROM recipes WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db( query, data )

    @staticmethod
    def validate_recipe( data ):
        is_valid = True
        if len(data["name"]) < 3:
            flash("Name must be at least 3 characters", "recipes")
            is_valid = False
        if len(data["description"]) < 3:
            flash("Description must be at least 3 characters", "recipes")
            is_valid = False
        if len(data["instructions"]) < 3:
            flash("Instructions must be at least 3 characters", "recipes")
            is_valid = False
        return is_valid