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

mongo = pymongo(app)

# Route decorator targetting root directory
@app.route("/")
def get_user():
    return render_template("index.html",)


# Route decorator targetting expand.html page
@app.route("/add_questions")
def add_questions():
    return render_template("add_questions.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #Check if username already exists in db
        existing_user = mongo.db.user.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
    return render_template("register.html")


# Run app if the default module is chosen
if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)