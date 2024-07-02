import os
from flask import Flask, render_template, url_for
from werkzeug.security import generate_password_hash, check_password_hash

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
    return render_template("register.html")


# Run app if the default module is chosen
if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)