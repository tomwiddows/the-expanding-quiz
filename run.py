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

if mongo.db is not None:
    print("mongo.db is correctly instantiated.")
else:
    print("mongo.db is None.")


# Constant
SHOWN_QUESTION_IDS = set()


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



# Function for generating a random question from questions database
def get_random_question():
    try:
        # Count the total number of questions in the collection
        total_questions = mongo.db.questions.count_documents(
            {}
        )

        if total_questions == 0:
            return ('There are currently no quiz questions in the database. '
                'Login to add some questions')

        if total_questions - len(SHOWN_QUESTION_IDS) == 0:
            return('You have seen all the questions on the quiz. '
                'Login to add more')

        # Generate a random index to select a random question
        random_index = random.randint(0, total_questions - 1)

        # Fetch the random question from the collection
        random_question = mongo.db.questions.find({}).limit(1).skip(
            random_index).next()

        while random_question['_id'] in SHOWN_QUESTION_IDS:
            random_index = random.randint(0, total_questions - 1)
            random_question = mongo.db.questions.find({}).limit(1).skip(
                random_index).next()
        
        # Add the question ID to the set of shown questions
        SHOWN_QUESTION_IDS.add(random_question['_id'])

        # Add 1 to the shown_x_times variable in the questions document
        mongo.db.questions.update_one(
            {'_id': random_question['_id']},
            {'$inc': {"shown_x_times": 1}}
        )

        return random_question

    except Exception as e:
        print("Error fetching random question:", e)
        return "An error occurred while fetching a random question."


# Route decorator targetting root directory
@app.route('/', methods=["GET", "POST"])
def index():
    question_info = get_random_question()
    print(question_info)
    return render_template('index.html', question_info=question_info)


@app.route('/add_question_page', methods=['POST'])
def add_question_page():
    if 'user' in session:
        return render_template('add_question.html')
    return render_template(url_for('login_or_register'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:

        return redirect(url_for('login_or_register'))
    user = session['user']
    
    if mongo.db.users.find_one({'username': user})['is_admin'] == 'false':
        print(mongo.db.users.find_one({'username': user})['is_admin'])
        user_questions = list(mongo.db.questions.find({'user.username': user}))

    else:
        user_questions = list(mongo.db.questions.find())

    return render_template('profile.html', user=user, user_questions=user_questions)


# Route decorator targetting add_question.html page
# or login_or_signup.html page
@app.route('/login_or_register', methods=['GET', 'POST'])
def login_or_register():
    return render_template('login_or_register.html')


# Route decorators for when user is in login_or_register.html page
# and chooses an option. First option is for login.html
@app.route('/login_page')
def login_page():
    return render_template('login.html')


# Second option is for register.html
@app.route('/register_page')
def register_page():
    return render_template('register.html')


# Route decorator targetting add_question_page route decorator
# or login_or_signup.html page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check if username exists in db
        existing_user = mongo.db.users.find_one(
            {'username': request.form.get('username').lower()}
        )

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user['password'], request.form.get('password')):
                        session['user'] = request.form.get('username').lower()
                        flash('Welcome, {}'.format(
                            request.form.get('username')))
                        return redirect(url_for('profile'))
            else:
                # invalid password match
                flash('Incorrect Username and/or Password. Please try again')
                return redirect(url_for('login'))
        else:
            # username doesn't exist
            flash('Incorrect Username and/or Password. Please try again')
    return render_template('login.html')


# Route decorator for targetting login route decorator
# or add_question.html page
@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':
        print('posting...')
        #Check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {'username': request.form.get('username').lower()})

        if existing_user:
            flash('Username already exists.'
                'Please choose another username or go to login page', 'info')
            return redirect(url_for('register'))

        # Generate user_id
        user_id = ObjectId()

        # Create dictionary for new user
        new_user = {
            '_id': user_id,
            'username': request.form.get('username').lower(),
            'password': generate_password_hash(request.form.get('password')),
            'question_count': 0,
            'is_admin': False
        }

        # Store new user in users dictionary
        mongo.db.users.insert_one(new_user)

        # put the new user into 'session' cookie
        session['user'] = request.form.get('username').lower()
        session['user_id'] = str(user_id)
        
        flash('Registration Successful!', 'success')
        return redirect(url_for('profile'))
    flash('There was an error in the registration process. Please try again.')
    return render_template('register.html')


# logout route decorator
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# add_question route decorator
@app.route('/add_question', methods=['POST'])
def add_question():

    if 'user' in session:
        user = session['user']
        user_id = mongo.db.users.find_one({'username': user})['_id']

        # Get the next overall question count
        overall_question_count = get_next_question_count()

        # Prepare question data
        question = {
            '_id': ObjectId(),
            'question': request.form.get('question'),
            'answer': request.form.get('answer'),
            'shown_x_times': 0,
            'suggested_corrections': [],
            'status': 'active',
            'user': [{'username': user},
                     {'user_id': str(user_id)}]
        }

        # Insert question into the 'questions' collection
        mongo.db.questions.insert_one(question)


        # Increment the user's question count
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$inc': {'question_count': 1}}
        )

        # Success message once quesiton has been added
        flash('Question added successfully!', 'success')
        return redirect(url_for('profile'))
    else:
        # Error handling message
        flash('Please log in or register to add a question', 'info')
        return render_template('login_or_register.html')


# 
@app.route('/edit_question', methods=['GET', 'POST'])
def edit_question():
    if request.method == 'POST':

        user = session['user']
        user_id = mongo.db.users.find_one({'username': user})['_id']

        question_id = ObjectId(request.form.get('id'))

        new_question = request.form.get('question')
        new_answer = request.form.get('answer')

        new_question_doc = {
            'question': request.form.get('question'),
            'answer': request.form.get('answer'),
            'shown_x_times': 0,
            'suggested_corrections': [],
            'status': 'active',
            'user': [{'username': user},
                     {'user_id': user_id}]
        }

        result = mongo.db.questions.replace_one({'_id': question_id}, new_question_doc)
        print(result)

    return redirect(url_for('profile'))

@app.route('/delete_question', methods=['GET', 'POST'])
def delete_question():

    if 'user' in session:

        user = session['user']
        user_id = mongo.db.users.find_one({'username': user})['_id']

        if request.method == 'POST':

            question_id = ObjectId(request.form.get('id'))

            result = mongo.db.questions.delete_one({"_id": question_id})

            # Increment the user's question count
            mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$inc': {'question_count': -1}}
            )

    return redirect(url_for('profile'))
    
# Run app if the default module is chosen
if __name__ == '__main__':
    app.run(
        host=os.environ.get('IP', '0.0.0.0'),
        port=int(os.environ.get('PORT', '5000')),
        debug=True)