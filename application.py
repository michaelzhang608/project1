import os

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from hashlib import sha1

# from helpers import login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():

    # Check if user is logged in
    if session.get("user_id") is None:
            return redirect("/login")

    return render_template("layout.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Logs user into their account """

    if request.method == "POST":

        # Remove any current active sessions
        session.clear()

        # Check for correct input
        if not request.form.get("username"):
            return render_template("error.html", error="Please provide username", back="/login")

        if not request.form.get("password"):
            return render_template("error.html", error="Please provide password", back="/login")

        # Check for user in database
        rows = db.execute("SELECT password FROM users WHERE username = :username",
                          {"username":request.form.get("username")}).fetchone()

        # Check if the is user under the username
        if not rows:
            return render_template("error.html", error="Sorry, username not found", back="/login")

        # Has input password to check
        check_pass = sha1(request.form.get("password").encode())
        check_pass = check_pass.hexdigest()

        # Check if password matches the database
        if check_pass != rows[0]:
            return render_template("error.html", error="Sorry, wrong password", back="/login")


        return "sucess"

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():

    # Remove current session
    session.clear()

    # Rdirect to main, which leads to login page
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Remove any current active sessions
        session.clear()

        # Check for correct input
        if not request.form.get("name"):
            return render_template("error.html", error="Please provide name", back="/register")

        if not request.form.get("username"):
            return render_template("error.html", error="Please provide username", back="/register")

        if not request.form.get("password"):
            return render_template("error.html", error="Please provide password", back="/register")

        if not request.form.get("check"):
            return render_template("error.html", error="Please provide password confirmation", back="/register")

        # Check if passwords match
        if request.form.get("password") != request.form.get("check"):
            return render_template("error.html", error="Passwords do not match", back="/register")

        # Hash password
        hashed_pass = sha1(request.form.get("password").encode())
        hashed_pass = hashed_pass.hexdigest()

        # Add user and check is username already exists
        try:
            db.execute("INSERT INTO users (name, username, password) VALUES (:name, :username, :password)",
                       {"name": request.form.get("name"), "username": request.form.get("username"), "password": hashed_pass})
        except:
            return render_template("error.html", error="Sorry, username is already taken", back="/register")

        db.commit()

        # Get current user_id
        rows = db.execute("SELECT user_id from users WHERE username = :username",
                          {"username":request.form.get("username")}).fetchone()
        db.commit()

        # Set current session
        session["user_id"] = rows[0]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")