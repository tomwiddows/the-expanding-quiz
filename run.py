import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

# Create instance of the Flask class
app = Flask(__name__)

app.config["MONGO.DBNAME"] = os.environ.get("MONGO.DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# Route decorator targetting root directory
@app.route('/')
def index():
    return render_template("index.html",)


# Route decorator targetting add_questions.html page or login_or_signup.html page
@app.route('/add_questions', methods=["GET"])
def add_questions():
    if 'username' in session:
        return render_template('add_question.html')
    else:
        return render_template('login_or_register.html')


# Route decorators for when user is in login_or_register.html page and chooses an option
@app.route('/login_page')
def login_page():
    return render_template('login.html')


@app.route('/register_page')
def register_page():
    return render_template('register.html')

# Route decorator targetting add_questions route decorator or login_or_signup.html page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((user for user in users if user['username'] == username), None)
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('add_questions'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
    return render_template('login.html')


# Route decorator for targetting login route decorator or add_questions.html page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #Check if username already exists in db
        existing_user = mongo.db.user.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists. Redirecting to Login...")
            return redirect(url_for("login"))
        else:
            register = {
                "username": request.form.get("username").lower(),
                "password": generate_password_hash(request.form.get("password"))
            }
            mongo.db.users.insert_one(register)

            # put the new user into 'session' cookie
            session["user"] = request.form.get("username").lower()
            flash("Registration Successful!")
    return render_template('add_questions.html')


# Run app if the default module is chosen
if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)