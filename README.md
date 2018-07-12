# Project 1

Web Programming with Python and JavaScript

Michael Zhang

## Contents of my web app:

### /templates

##### layout.html
Template file of my website, contains the constant elements of my website and the general HTML structure. By using JINJA, it contains a {% block title %} for the title of each page, and a {% block body %} for the body content of each page. Can take a message variable though JINJA that it puts into an alert. Uses bootstrap across the website for css styling.


##### error.html
Error page that takes error messsage using JINJA and puts into an alert alert-danger. Also takes a link back to the page that triggered the error, using JINJA, and puts into an <a> tag.


##### location.html
Location page for specific city. Takes a variable that contains all the info needed for the city through JINJA and displays:
* Name of the location
* Its ZIP code
* its latitude and longitude
* Its population

Under that, displays all current weather data of city in a table:
* Time of the weather report
* Textual weather summary
* Temperature
* Dew point
* Humidity

Under that, it displays the number of check-ins and the comments (if there aren't any comments, it tells the user)
Iterates over each comment, displaying the user, at what time, and the content of the message.

Under that, it has a form so users can leave a comment, sends by "POST" to /location/{Current location id}
Also contains a logout link that sends to the /logout route.

##### login.html
Login page containing a form that "POST"s to the /login route. Also contains a link to the register page.


##### register.html
Register page containing a form that "POST"s to the /register route. Also contains a link to the login page.


##### result.html
Using JINJA, it iterates over the list of possible places that match to search and puts them into a unordered list. Each list item links to /location/{that list item's id}. Also contains a logout link that sends to the /logout route.

##### search.html
Search page with a form that "POST"s to "/" to search for cities by zip code or by city name. Does not need a complete zip code or city name to function. Also contains a logout link that sends to the /logout route.

### static/styles/
##### styles.css
Some light style changes and an @media query to simplify page if its viewport width is too narrow.

### application.py
_In general, I have decided to keep my SQL queries simple enough to be more readable while doing my best to maximise their efficiency (reducing the total amount of queries required)_

##### @app.route("/")
* If user not checked in send to /login route
* Render search.html
* Via POST, use SQL "LIKE" to find cities similar to query
* Render result.html and pass in the results

##### @app.route("/location/<int:zip_id>")
* If user not checked in send to /login route
* Via GET, checks to see if location in database
* Gets api data from darksky and formats it
* Renders location.html with info
* Via POST, checks to see if user has already commented, if not, add to database
* Gets api data from darksky and formats it
* Renders location.html with info

##### @app.route("/login")
* Renders login.html
* Compares form username input with database
* Hashes password to compare with the password in database
* If successful, sends to route ("/") and makes session["user_id"] the user's id

##### @app.route("/logout")
* Removes current session[user_id] and sends to login page

##### @app.route("/register")
* Form to register user
* Hashes form password before inserting into database

##### @app.route("/api/<zipcode>")
* Gets data from database
* returns as json

### import.py
#### Pseudocode:
* set up database to db variable
* create csv reader to go through each row of csv
* in a for loop: iterate through each row and insert into db as you go
* commit changes
