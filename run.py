import os
from flask import Flask

# Create instance of the Flask class
app = Flask(__name__)

# Route decorator targetting root directory
@app.route("/")
# filler function
def index():
    return render_template("index.html")

# Run app if the default module is chosen
if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)