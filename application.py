import os

from flask import Flask, session, render_template, request, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from hashlib import sha1

import requests
import json
from datetime import datetime

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


@app.route("/", methods=["GET", "POST"])
def search():

    if request.method == "POST":

        # Check if user is logged in
        if session.get("user_id") is None:
            return redirect("/login")

        # Check for correct input
        if not request.form.get("search"):
            return render_template("error.html", error="Please provide search query", back="/")

        # Check if input query is ZIP code or city name
        if request.form.get("search").isdigit():

            # Search for zipcode LIKE input query by considering them as strings
            places = db.execute("SELECT id, zipcode, city, state FROM zips WHERE zipcode LIKE :search LIMIT 10",
                                {"search": "%" + request.form.get("search") + "%"}).fetchall()

        # Input must be city name
        else:

            # Search for city name LIKE input query, in all caps like in databse
            places = db.execute("SELECT id, zipcode, city, state FROM zips WHERE city LIKE :search LIMIT 10",
                                {"search": "%" + request.form.get("search").upper() + "%"}).fetchall()

        if not places:
            return render_template("error.html", error="Sorry, we couldn't find your city", back="/"), 404

        # Show list of cities to user
        return render_template("result.html", places=places)

    else:

        # Check if user is logged in
        if session.get("user_id") is None:
            return redirect("/login")

        return render_template("search.html")


@app.route("/location/<int:zip_id>", methods=["GET", "POST"])
def location(zip_id):

    if request.method == "POST":

        # Check if user is logged in
        if session.get("user_id") is None:
            return redirect("/login")

        if not request.form.get("comment"):
            return render_template("error.html", error="Please write a comment", back="/location/" + str(zip_id)), 400

        # Check if comment has already been left
        already_commented = db.execute("SELECT id FROM comments WHERE user_id = :current_user AND zip_id = :current_zip",
                                       {"current_user": session["user_id"], "current_zip": zip_id}).fetchone()

        if already_commented:
            return render_template("error.html", error="Sorry you can only leave a comment once", back="/location/" + str(zip_id)), 400

        # Add comment with current date
        db.execute("INSERT INTO comments (content, user_id, zip_id, date) VALUES (:content, :user_id, :zip_id, :date)",
                   {"content": request.form.get("comment"), "user_id": session["user_id"], "zip_id": zip_id, "date": datetime.now().strftime("%Y-%m-%d")})

        db.commit()

        # Get location info and comments
        location = db.execute("SELECT * FROM zips WHERE id = :place",
                              {"place": zip_id}).fetchone()

        comments = db.execute("SELECT content, date, name FROM comments JOIN users ON users.id = comments.user_id WHERE comments.zip_id = :place",
                              {"place": zip_id}).fetchall()

        # Get weather data from Darksky https://www.darksky.net/dev by passing in lat and long
        weather = requests.get("https://api.darksky.net/forecast/6b7e8cc7918c1a5bef816ace40eed401/" + str(location[4]) + "," +
                               str(location[5])).json()

        # Get comments count in seperate query from location quary to make code clear and easy to read
        check_ins = db.execute("SELECT COUNT(*) FROM comments WHERE zip_id = :zip_id GROUP BY zip_id",
                               {"zip_id": location[0]}).fetchone()

        # Assign 0 to check_ins if there are none, keep tuple format to keep return format consistent
        if not check_ins:
            check_ins = (0,)

        # Format UNIX time and reassign to weather
        weather["currently"]["time"] = datetime.fromtimestamp(weather["currently"]["time"]).strftime('%Y-%m-%d %H:%M:%S')

        # Format humidity to percentage
        weather["currently"]["humidity"] = "{0:.0f}".format(weather["currently"]["humidity"] * 100) + "%"

        return render_template("location.html", location=location, comments=comments, weather=weather["currently"], check_ins=check_ins[0])

    # Else it is a GET request
    else:

        # Check if user is logged in
        if session.get("user_id") is None:
            return redirect("/login")

        # Check if location in database by searching with zip id because it's the quickest search column
        location = db.execute("SELECT * FROM zips WHERE id = :place",
                              {"place": zip_id}).fetchone()

        if not location:
            return render_template("error.html", error="If you entered the URL manually please check the url and try again.", back="/"), 404

        # Get comments for city
        comments = db.execute("SELECT content, date, name FROM comments JOIN users ON users.id = comments.user_id WHERE comments.zip_id = :place",
                              {"place": zip_id}).fetchall()

        # Get weather data from Darksky https://www.darksky.net/dev by passing in lat and long
        weather = requests.get("https://api.darksky.net/forecast/6b7e8cc7918c1a5bef816ace40eed401/" + str(location[4]) + "," +
                               str(location[5])).json()

        # Format UNIX time and reassign to weather
        weather["currently"]["time"] = datetime.fromtimestamp(weather["currently"]["time"]).strftime('%Y-%m-%d %H:%M:%S')

        # Format humidity to percentage
        weather["currently"]["humidity"] = "{0:.0f}".format(weather["currently"]["humidity"] * 100) + "%"

        # If there are no comments, assign a string to no_comments
        no_comments = None
        if not comments:
            no_comments = "No one has checked in yet! Be the first one to leave a comment."

        # Get comments count in seperate query from location quary to make code clear and easy to read
        check_ins = db.execute("SELECT COUNT(*) FROM comments WHERE zip_id = :zip_id GROUP BY zip_id",
                               {"zip_id": location[0]}).fetchone()

        # Assign 0 to check_ins if there are none, keep tuple format to keep return format consistent
        if not check_ins:
            check_ins = (0,)

        # Load page with location info, no_comments if there are no comments, comments if there are and current weather info
        return render_template("location.html", location=location, no_comments=no_comments, comments=comments, weather=weather["currently"], check_ins=check_ins[0])


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Logs user into their account """

    if request.method == "POST":

        # Remove any current active sessions
        session.clear()

        # Check for correct input
        if not request.form.get("username"):
            return render_template("error.html", error="Please provide username", back="/login"), 400

        if not request.form.get("password"):
            return render_template("error.html", error="Please provide password", back="/login"), 400

        # Check for user in database
        user = db.execute("SELECT id, password, name FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchone()

        # Check if the is user under the username
        if not user:
            return render_template("error.html", error="Sorry, username not found", back="/login"), 400

        # Has input password to check
        check_pass = sha1(request.form.get("password").encode())
        check_pass = check_pass.hexdigest()

        # Check if password matches the database
        if check_pass != user[1]:
            return render_template("error.html", error="Sorry, wrong password", back="/login"), 400

        # Add user to current session
        session["user_id"] = user[0]

        # Send to main page once logged in
        return render_template("search.html", message="Welcome back, " + user[2].capitalize())

    # Else it is a GET request
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
            return render_template("error.html", error="Please provide name", back="/register"), 400

        if not request.form.get("username"):
            return render_template("error.html", error="Please provide username", back="/register"), 400

        if not request.form.get("password"):
            return render_template("error.html", error="Please provide password", back="/register"), 400

        if not request.form.get("check"):
            return render_template("error.html", error="Please provide password confirmation", back="/register"), 400

        # Check if passwords match
        if request.form.get("password") != request.form.get("check"):
            return render_template("error.html", error="Passwords do not match", back="/register"), 400

        # Hash password
        hashed_pass = sha1(request.form.get("password").encode())
        hashed_pass = hashed_pass.hexdigest()

        # Add user and check is username already exists
        try:
            db.execute("INSERT INTO users (name, username, password) VALUES (:name, :username, :password)",
                       {"name": request.form.get("name"), "username": request.form.get("username"), "password": hashed_pass})
        except:
            return render_template("error.html", error="Sorry, username is already taken", back="/register"), 400

        db.commit()

        # Get current user id
        user = db.execute("SELECT id from users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchone()
        db.commit()

        # Set current session
        session["user_id"] = user[0]

        # Redirect user to home page
        return redirect("/")

    # Else it is a GET request
    else:
        return render_template("register.html")


@app.route("/api/<zipcode>")
def api(zipcode):

    # Get zip info
    city = db.execute("SELECT * FROM zips WHERE zipcode = :zipcode",
                      {"zipcode": zipcode}).fetchone()

    # Confirm that city exists
    if not city:
        return jsonify(error="Error 404, not found"), 404

    # Get comments count if city exists
    check_ins = db.execute("SELECT zip_id, COUNT(*) FROM comments WHERE zip_id = :zip_id GROUP BY zip_id",
                           {"zip_id": city[0]}).fetchone()

    # Assign 0 to check_ins if there are none
    if not check_ins:
        check_ins = (0,)

    # Return json of city info
    return jsonify(place_name=city[2],
                   state=city[3],
                   latitude=float(city[4]),
                   longidute=float(city[5]),
                   zip=city[1],
                   population=city[6],
                   check_ins=check_ins[0])
