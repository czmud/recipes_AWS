from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import recipe
from flask import flash
import re
from flask_app import app
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

#define global reg expressions for data validation
password_regex = re.compile(r'^.*(?=.{8,})(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!#$%&? "]).*$')
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_regex = re.compile(r'^[a-zA-Z ]{2,}$')




class User:
    db = "recipes_schema"
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password_hash = data['password_hash']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.recipes = []
    @property
    def full_name(self):
        return self.first_name+" "+self.last_name
    @classmethod
    def save( cls, data ):
        query = "INSERT INTO users ( first_name, last_name, email, password_hash ) VALUES \
            ( %(first_name)s, %(last_name)s, %(email)s, %(password_hash)s );"
        return connectToMySQL(cls.db).query_db( query, data )
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users LEFT JOIN recipes ON users.id = recipes.user_id;"
        results = connectToMySQL(cls.db).query_db(query)
        users = []
        if len(results) > 0:
            users.append(cls(results[0]))
        for row in results:
            if users[-1].id != row["id"]:
                users.append( cls(row) )
            if row["recipes.id"] != None:
                recipe_data = {
                    'id': row['recipes.id'],
                    'user_id': row['user_id'],
                    'name': row['name'],
                    'description': row['description'],
                    'instructions': row['instructions'],
                    'made_at': row['made_at'],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                if row['under_thirty_mins']:
                    recipe_data['under_thirty_mins'] = 1
                else:
                    recipe_data['under_thirty_mins'] = 0
                users[-1].recipes.append(recipe.Recipe(recipe_data))
        return users
    @classmethod
    def get_user_by_id( cls, data ):
        query = "SELECT * FROM users LEFT JOIN recipes ON users.id = recipes.user_id \
            WHERE users.id=%(id)s;"
        results = connectToMySQL(cls.db).query_db(query, data)
        users = False
        if len(results) > 0:
            users = cls(results[0])
        for row in results:
            if row["recipes.id"] != None:
                recipe_data = {
                    'id': row['recipes.id'],
                    'user_id': row['user_id'],
                    'name': row['name'],
                    'description': row['description'],
                    'instructions': row['instructions'],
                    'made_at': row['made_at'],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                if row['under_thirty_mins']:
                    recipe_data['under_thirty_mins'] = 1
                else:
                    recipe_data['under_thirty_mins'] = 0
                users.recipes.append(recipe.Recipe(recipe_data))
        return users
    @classmethod
    def get_user_by_email( cls, data ):
        query = "SELECT * FROM users WHERE email=%(email)s;"
        results = connectToMySQL(cls.db).query_db(query, data)
        users = False
        print(len(results))
        if len(results) > 0:
            users = cls(results[0])
        return users




    @staticmethod
    def validate_user_form(data):
        is_valid = True
        # name validations, must be at least 2 characters
        if len(data["first_name"]) < 2:
            flash("first name must be at least 2 characters long", "register")
            is_valid = False
        elif not name_regex.match(data["first_name"]):
            flash("first name must contain only letters", "register")
            is_valid = False
        if len(data["last_name"]) < 2:
            flash("last name must be at least 2 characters long", "register")
            is_valid = False
        elif not name_regex.match(data["last_name"]):
            flash("last name must contain only letters", "register")
            is_valid = False
        # email validations, confirm it matches reg expression
        if not email_regex.match(data['email']):
            is_valid = False
            flash("must enter valid email", "register")
        # confirm it doesn't already exist in db
        elif User.get_user_by_email(data):
            flash("account already exists for this email", "register")
            is_valid = False
        # password validations
        if not password_regex.match(data['password']):
            is_valid = False
            flash("must enter valid password", "register")
        elif not password_regex.match(data['password_confirm']):
            is_valid = False
            flash("passwords and confirmation do not match", "register")
        elif data['password'] != data['password_confirm']:
            is_valid = False
            flash("passwords and confirmation do not match", "register")
        return is_valid

    @staticmethod
    def hash_password(data):
        password_hash = bcrypt.generate_password_hash(data['password'])
        return password_hash
    
    @staticmethod
    def validate_login_form(data):
        if not email_regex.match(data['email']):
            flash("email and password combination did not match", "login")
            return False
        if not password_regex.match(data["password"]):
            flash("email and password combination did not match", "login")
            return False
        return True

    @staticmethod
    def verify_login_credentials( data ):
        users = User.get_user_by_email(data)
        if not users:
            flash("email and password combination did not match", "login")
            return False
        elif not bcrypt.check_password_hash(users.password_hash, data["password"]):
            flash("email and password combination did not match", "login")
            return False
        return users.id