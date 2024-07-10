import os
import random
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

# Create instance of the Flask class
app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

print(app.config["MONGO_DBNAME"])
print(app.config["MONGO_URI"])

mongo = PyMongo(app)

try:
    mongo.cx.server_info()  # Attempt to get server info to verify connection
    print("MongoDB connection established successfully.")
except Exception as e:
    print("Error connecting to MongoDB:", e)

if mongo.db != None:
    print("mongo.db is correctly instantiated.")
else:
    print("mongo.db is None.")


# Custom filter for Materialize CSS classes
@app.template_filter('materialize_class')
def materialize_class(category):
    classes = {
        'success': 'green lighten-4 green-text text-darken-4',
        'error': 'red lighten-4 red-text text-darken-4',
        'info': 'blue lighten-4 blue-text text-darken-4',
        'warning': 'yellow lighten-4 yellow-text text-darken-4'
    }
    return classes.get(category, '')


shown_question_ids = set()

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
    try:
        # Count the total number of questions in the collection
        total_questions = mongo.db.questions.count_documents({})

        if total_questions == 0:
            return "There are currently no quiz questions in the database. Login to add some questions"

        # Generate a random index to select a random question
        random_index = random.randint(0, total_questions - 1)

        # Fetch the random question from the collection
        random_question = mongo.db.questions.find({}).limit(1).skip(random_index).next()

        while random_question['_id'] in shown_question_ids:
            random_index = random.randint(0, total_questions - 1)
            random_question = mongo.db.questions.find({}).limit(1).skip(random_index).next()
        
        # Add the question ID to the set of shown questions
        shown_question_ids.add(random_question['_id'])

        return random_question

    except Exception as e:
        print("Error fetching random question:", e)
        return "An error occurred while fetching a random question."


# Route decorator targetting root directory
@app.route('/')
def index():
    question = get_random_question()
    return render_template('index.html', question=question)





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
        user = mongo.db.users.find_one({"username": username})
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
        print("posting...")
        #Check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash('Username already exists. Please choose another username or go to login page', 'info')
            return redirect(url_for('register'))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }

        print(register)
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!", 'success')
        return redirect(url_for('add_questions_page'))
    return render_template('register.html')
        


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

        # Prepare question data
        question = {
            "_id": document_name,  # Unique identifier for the question
            "user_id": ObjectId(user_id),  # Store the user ID in the question document
            "question": request.form.get("question"),
            "answer": request.form.get("answer"),
            "status": "active",
            "corrections": []
        }

        # Insert question into the 'questions' collection
        mongo.db.questions.insert_one(question)

        # Increment the user's question count
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"question_count": 1}}
        )

        flash("Question added successfully!")
        return redirect(url_for('add_questions_page'))
    else:
        flash("Please log in to add a question")
        return redirect(url_for('login'))


# Run app if the default module is chosen
if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)