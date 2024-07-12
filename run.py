# Import necessary modules
import os
import random
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

# Import environment variables if env.py exists
if os.path.exists("env.py"):
    import env

# Create instance of the Flask class
app = Flask(__name__)

# Configure MongoDB connection using environment variables
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

# Print MongoDB configuration for debugging
print(app.config["MONGO_DBNAME"])
print(app.config["MONGO_URI"])

# Initialize PyMongo with the Flask app
mongo = PyMongo(app)

# Test MongoDB connection
try:
    mongo.cx.server_info()  # Attempt to get server info to verify connection
    print("MongoDB connection established successfully.")
except Exception as e:
    print("Error connecting to MongoDB:", e)

# Check if mongo.db is correctly instantiated
if mongo.db is not None:
    print("mongo.db is correctly instantiated.")
else:
    print("mongo.db is None.")

# Set to keep track of shown question IDs to avoid repetition
SHOWN_QUESTION_IDS = set()

# Custom filter for Materialize CSS classes
# This helps in applying the correct CSS classes for flash messages
@app.template_filter('materialize_class')
def materialize_class(category):
    classes = {
        'success': 'green lighten-4 green-text text-darken-4',
        'error': 'red lighten-4 red-text text-darken-4',
        'info': 'blue lighten-4 blue-text text-darken-4',
        'warning': 'yellow lighten-4 yellow-text text-darken-4'
    }
    return classes.get(category, '')

# Function to get a random question from the database
def get_random_question():
    try:
        # Count total questions in the collection
        total_questions = mongo.db.questions.count_documents({})

        # Handle cases where there are no questions or all questions have been shown
        if total_questions == 0:
            return 'There are currently no quiz questions in the database. Login to add some questions'
        if total_questions == len(SHOWN_QUESTION_IDS):
            return 'You have seen all the questions on the quiz. Login to add more'

        # Get a random question that hasn't been shown yet
        while True:
            random_index = random.randint(0, total_questions - 1)
            random_question = mongo.db.questions.find({}).limit(1).skip(random_index).next()
            if random_question['_id'] not in SHOWN_QUESTION_IDS:
                break

        # Mark question as shown and update its shown count in the database
        SHOWN_QUESTION_IDS.add(random_question['_id'])
        mongo.db.questions.update_one(
            {'_id': random_question['_id']},
            {'$inc': {"shown_x_times": 1}}
        )

        return random_question

    except Exception as e:
        print("Error fetching random question:", e)
        return "An error occurred while fetching a random question."

# Route for the home page
@app.route('/', methods=["GET", "POST"])
def index():
    question_info = get_random_question()
    print(question_info)  # Debug print
    return render_template('index.html', question_info=question_info)

# Route to add a question page (requires login)
@app.route('/add_question_page', methods=['POST'])
def add_question_page():
    if 'user' in session:
        return render_template('add_question.html')
    return render_template(url_for('login_or_register'))

# Route for user profile page
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('login_or_register'))
    user = session['user']
    
    # Fetch user questions (all questions for admin, user-specific for others)
    if mongo.db.users.find_one({'username': user})['is_admin'] == 'false':
        user_questions = list(mongo.db.questions.find({'user.username': user}))
    else:
        user_questions = list(mongo.db.questions.find())

    return render_template('profile.html', user=user, user_questions=user_questions)

# Route for login/register page
@app.route('/login_or_register', methods=['GET', 'POST'])
def login_or_register():
    return render_template('login_or_register.html')

# Route for login page
@app.route('/login_page')
def login_page():
    return render_template('login.html')

# Route for register page
@app.route('/register_page')
def register_page():
    return render_template('register.html')

# Route for handling login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check if username exists in db
        existing_user = mongo.db.users.find_one(
            {'username': request.form.get('username').lower()}
        )

        if existing_user:
            # Verify password
            if check_password_hash(existing_user['password'], request.form.get('password')):
                session['user'] = request.form.get('username').lower()
                flash('Welcome, {}'.format(request.form.get('username')))
                return redirect(url_for('profile'))
            else:
                flash('Incorrect Username and/or Password. Please try again')
                return redirect(url_for('login'))
        else:
            flash('Incorrect Username and/or Password. Please try again')
    return render_template('login.html')

# Route for handling registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if username already exists
        existing_user = mongo.db.users.find_one(
            {'username': request.form.get('username').lower()})

        if existing_user:
            flash('Username already exists. Please choose another username or go to login page', 'info')
            return redirect(url_for('register'))

        # Create new user
        user_id = ObjectId()
        new_user = {
            '_id': user_id,
            'username': request.form.get('username').lower(),
            'password': generate_password_hash(request.form.get('password')),
            'question_count': 0,
            'is_admin': False
        }

        # Insert new user into the database
        mongo.db.users.insert_one(new_user)

        # Start session for new user
        session['user'] = request.form.get('username').lower()
        session['user_id'] = str(user_id)
        
        flash('Registration Successful!', 'success')
        return redirect(url_for('profile'))
    flash('There was an error in the registration process. Please try again.')
    return render_template('register.html')

# Route for logout
@app.route('/logout')
def logout():
    # Remove user from session
    session.pop('user', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Route for adding a new question
@app.route('/add_question', methods=['POST'])
def add_question():
    if 'user' in session:
        user = session['user']
        user_id = mongo.db.users.find_one({'username': user})['_id']

        # Prepare question data
        question = {
            '_id': ObjectId(),
            'question': request.form.get('question'),
            'answer': request.form.get('answer'),
            'shown_x_times': 0,
            'suggested_corrections': [],
            'status': 'active',
            'user': [{'username': user}, {'user_id': str(user_id)}]
        }

        # Insert question and update user's question count
        mongo.db.questions.insert_one(question)
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$inc': {'question_count': 1}}
        )

        flash('Question added successfully!', 'success')
        return redirect(url_for('profile'))
    else:
        flash('Please log in or register to add a question', 'info')
        return render_template('login_or_register.html')

# Route for editing a question
@app.route('/edit_question', methods=['GET', 'POST'])
def edit_question():
    if request.method == 'POST':
        user = session['user']
        user_id = mongo.db.users.find_one({'username': user})['_id']
        question_id = ObjectId(request.form.get('id'))

        # Prepare updated question document
        new_question_doc = {
            'question': request.form.get('question'),
            'answer': request.form.get('answer'),
            'shown_x_times': 0,
            'suggested_corrections': [],
            'status': 'active',
            'user': [{'username': user}, {'user_id': user_id}]
        }

        # Replace the old question with the new one
        result = mongo.db.questions.replace_one({'_id': question_id}, new_question_doc)
        print(result)  # Debug print

    return redirect(url_for('profile'))

# Route for deleting a question
@app.route('/delete_question', methods=['GET', 'POST'])
def delete_question():
    if 'user' in session:
        user = session['user']
        user_id = mongo.db.users.find_one({'username': user})['_id']

        if request.method == 'POST':
            question_id = ObjectId(request.form.get('id'))
            # Delete the question from the database
            mongo.db.questions.delete_one({"_id": question_id})

            # Decrement the user's question count
            mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$inc': {'question_count': -1}}
            )

    return redirect(url_for('profile'))

# Run the app
if __name__ == '__main__':
    app.run(
        host=os.environ.get('IP', '0.0.0.0'),
        port=int(os.environ.get('PORT', '5000')),
        debug=True)  # Set to False in production