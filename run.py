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

uri = "mongodb+srv://TomW:97VVD88Rob94Hav@usersandquestions.ochexzh.mongodb.net/?retryWrites=true&w=majority&appName=usersAndQuestions"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Create instance of the Flask class
app = Flask(__name__)


# Route decorator targetting root directory
@app.route("/")
def index():
    return render_template("index.html")


# Route decorator targetting expand.html page
@app.route("/expand")
def expand():
    return render_template("expand.html")


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