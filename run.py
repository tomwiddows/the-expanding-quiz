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

# Helper function for generating a name for each new question collection
def generate_collection_name(user_id, user_question_count, overall_question_count):
    return f"question{overall_question_count}_{user_id}{user_question_count}"

# Helper function for keeping track of the number of questions for naming collections
def get_next_question_count():
    counter = mongo.db.counters.find_one_and_update(
        {"_id": "question_count"},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True
    )
    return counter["count"]


def get_random_question():
    # Fetch all collections that start with "question"
    collections = [col for col in mongo.db.list_collection_names() if col.startswith('question')]
    if not collections:
        return None
    
    # Randomly select a collection
    random_collection = random.choice(collections)
    
    # Fetch the document with the field "question" from the selected collection
    random_question = mongo.db[random_collection].find_one({"question": {"$exists": True}})
    
    return random_question


# Route decorator targetting root directory
@app.route('/')
def index():
    question = get_random_question()
    return render_template('index.html', question=question)


# Route decorator for checking answer
@app.route('/check_answer', methods=['POST'])
def check_answer():
    if 'username' in session:
        question_id = request.form.get('question_id')
        user_answer = request.form.get('user_answer')
        
        # Fetch the correct answer from the database
        question_collection = mongo.db[question_id.split('_')[0]]
        question = question_collection.find_one({"_id": ObjectId(question_id)})
        correct_answer = question['correct_answer']
        
        # Check if the user's answer matches the correct answer
        result = 'Correct!' if user_answer.lower() == correct_answer.lower() else 'Incorrect!'
        
        return render_template('answer.html', result=result, question=question)
    else:
        flash('User not logged in')
        return redirect(url_for('login'))


# Route decorator targetting add_questions.html page or login_or_signup.html page
@app.route('/add_questions_page', methods=["GET"])
def add_questions_page():
    if 'username' in session:
        return render_template('add_question.html')
    else:
        return render_template('login_or_register.html')


# Route decorators for when user is in login_or_register.html page and chooses an option. First option is for login.html
@app.route('/login_page')
def login_page():
    return render_template('login.html')


# Second option is for register.html
@app.route('/register_page')
def register_page():
    return render_template('register.html')


# Route decorator targetting add_questions_page route decorator or login_or_signup.html page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((user for user in users if user['username'] == username), None)
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('add_questions_page'))
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
            return redirect(url_for('add_questions_page'))
    return render_template('add_questions.html')


# logout route decorator
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# add_question route decorator
@app.route('/add_question', methods=['POST'])
def add_question():
    if 'username' in session:
        user_id = session['user_id']

        # Get the user's question count
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        user_question_count = user.get('question_count', 0)
        
        # Get the next overall question count
        overall_question_count = get_next_question_count()

        # Generate the collection name
        collection_name = generate_collection_name(user_id, user_question_count, overall_question_count)

        # Prepare question data
        question = {
            "user_id": ObjectId(user_id),  # Store the user ID in the question document
            "question_text": request.form.get("question_text"),
            "correct_answer": request.form.get("correct_answer"),
            "status": "active",
            "corrections": []
        }

        # Insert question into the newly created collection
        mongo.db[collection_name].insert_one(question)

        # Increment the user's question count
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"question_count": 1}}
        )

        flash("Question added successfully!")
        return redirect(url_for('add_questions'))
    else:
        flash("Please log in to add a question")
        return redirect(url_for('login'))


# Run app if the default module is chosen
if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)