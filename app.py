import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# ---------- INDEX PAGE ---------- #

# index cheeses
@app.route('/')
@app.route("/index")
def index():

    """
        Display cheese cards in index page.(limit of 3)

        Fetch all cheese data from MongoDB cocktails collection.

        Returns:
        template: index.html.
    """
    cheeses = list(mongo.db.cheeses.find({"created_by": "admin"}).limit(3))

    return render_template("index.html", cheeses=cheeses)


# ---------- REGISTER PAGE ---------- #
@app.route("/register", methods=["GET", "POST"])
def register():

    """
        Displays register page to guest user and allows to create an account.

        Prevents duplication of username by checking users
        collection field "username".
        Stores informations from website form to MongoDB.

        Returns:
        template: redirect to profile.html if registration successful.
    """
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # prevent username multiplication
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        # grabs data from form to users collection
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "user_loc": request.form.get("user_loc"),
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


# ---------- LOGIN PAGE ---------- #
@app.route("/login", methods=["GET", "POST"])
def login():

    """
        Displays log in page and allows user to log into account.

        Checks if the username exists in MongoDB users collection.
        Protect password confidentiality.
        Informs user if registration is successful or not through
        flash messages.

        Returns:
        template: profile.html if the registration is successful.
        template: login.html if registration unsuccessful.
    """
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
             existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


# ---------- PROFILE PAGE ---------- #
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    """
        Displays profile page with user informations to logged user.

        Fetch all user informations from MongoDB users collection.
        Checks previously submitted pairings from user.
        Grants access to all pairing data to admin.

        Returns:
        template: profile.html.
    """
    user = mongo.db.users.find_one({"username": username.lower()})

    # Displays profile page with user informations to logged user.
    if "user" in session.keys():
        if session["user"] == "admin":
            cheeses = list(mongo.db.cheeses.find())
        else:
            cheeses = list(
                mongo.db.cheeses.find({"created_by": username.lower()}))

    return render_template("profile.html", user=user, cheeses=cheeses)


# ---------- LOGOUT ---------- #

# Allows registered user to log out from account
@app.route("/logout")
def logout():

    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# ---------- CHEESE PAGE ---------- #
@app.route("/")
@app.route("/get_cheeses")
def get_cheeses():
    # Get all cheeses from database displayed on several pages.
    cheeses = list(mongo.db.cheeses.find())

    return render_template("cheeses.html", cheeses=cheeses)


# ---------- SEARCH BOX IN CHEESES.HTML ---------- #
@app.route("/search", methods=["GET", "POST"])
def search():
    """
       Allows the user to search for cheeses by country.

       Returns:
       template: cheeses.html with filtered results
    """
    query = request.form.get("query")
    cheeses = list(mongo.db.cheeses.find({"$text": {"$search": query}}))
    return render_template("cheeses.html", cheeses=cheeses)


# ---------- ADD PAIRING ---------- #
@app.route("/add_pairing", methods=["GET", "POST"])
def add_pairing():

    """
        Allows registered user to submit a pairing to the website through
        a form.

        Allows all form fields to be sent to the MongoDB cheese collection.
        Inserts a new entry in the pairings collection.

        Returns:
        template: add_pairing.html and redirected to main cheese page.
    """
    if request.method == "POST":
        # send form data to cheese collection

        pairing = {
            "cheese_name": request.form.get("cheese_name"),
            "country_of_origin": request.form.get("country_of_origin"),
            "type": request.form.get("type"),
            "flavour": request.form.get("flavour"),
            "texture": request.form.get("texture"),
            "description": request.form.get("description"),
            "cheese_image": request.form.get("cheese_image"),
            "wine_id": request.form.get("wine_id"),
            "origin": request.form.get("origin"),
            "regions": request.form.get("regions"),
            "sweetness": request.form.get("sweetness"),
            "colour": request.form.get("colour"),
            "wine_description": request.form.get("wine_description"),
            "wine_image": request.form.get("wine_image"),
            "created_by": session["user"],
        }
        mongo.db.cheeses.insert_one(pairing)
        flash("Thanks for the pairing!")
        return redirect(url_for("get_cheeses"))

    return render_template("add_pairing.html")


# ---------- SINGLE CHEESE PAGE ---------- #
@app.route('/single_cheese/<cheeses_id>')
def single_cheese(cheeses_id):
    """
        Grabs all data from mongoDB for cheese and
        wines from cheese collection.

        Returns:
        template: single_cheese.html with results
    """
    cheeses = mongo.db.cheeses.find_one({'_id': ObjectId(cheeses_id)})

    return render_template("single_cheese.html", cheeses=cheeses)


# ---------- EDIT PAGE ---------- #
@app.route("/edit_pairing/<cheeses_id>", methods=["GET", "POST"])
def edit_pairing(cheeses_id):
    if request.method == "POST":
        """
            Allows the user to edit their submitted pairings through a form.
            Checks for pairing ID field in MongoDB to fetch all data.

            Displays all previously submitted data of the pairing by the user.
            Checks if the user in session is the author of the entry.

            Returns:
            template: edit_pairing.html before changes if the
            user is in session.
            template: index.html if the user is logged in but not the author.
            template: login.html if user not logged in.
        """

        # send form data to MongoDB and update fields
        submit = {
            "cheese_name": request.form.get("cheese_name"),
            "country_of_origin": request.form.get("country_of_origin"),
            "type": request.form.get("type"),
            "flavour": request.form.get("flavour"),
            "texture": request.form.get("texture"),
            "description": request.form.get("description"),
            "cheese_image": request.form.get("cheese_image"),
            "wine_id": request.form.get("wine_id"),
            "origin": request.form.get("origin"),
            "regions": request.form.get("regions"),
            "sweetness": request.form.get("sweetness"),
            "colour": request.form.get("colour"),
            "wine_description": request.form.get("wine_description"),
            "wine_image": request.form.get("wine_image"),
            "created_by": session["user"],
        }

        mongo.db.cheeses.update({"_id": ObjectId(cheeses_id)}, submit)
        flash("Thanks for the updated pairing!")

        return redirect(url_for("single_cheese", cheeses_id=cheeses_id))

    cheeses = mongo.db.cheeses.find_one({"_id": ObjectId(cheeses_id)})

    # check if user in session is the author of the previous entries
    if "user" in session.keys():
        user = session["user"].lower()

        if user == session["user"].lower():
            return render_template(
                "edit_pairing.html", cheeses=cheeses)

        else:
            return redirect(url_for("index"))

    else:
        return redirect(url_for("login"))


# ---------- DELETE PAIRING ---------- #
@app.route("/delete_pairing/<cheeses_id>")
def delete_pairing(cheeses_id):
    """
        Allows user to delete pairings.

        Deletes pairing from database.

        Returns:
        template: redirects to cheeses.html
    """

    mongo.db.cheeses.remove({"_id": ObjectId(cheeses_id)})
    flash("Pairing Successfully Deleted")
    return redirect(url_for("get_cheeses"))


# ---------- DELETE PEOFILE ---------- #
@app.route("/delete_profile/<username>")
def delete_profile(username):
    """
        Allows user to delete account when in session.

        Deletes user from database.
        Sends visual confirmation.
        Removes from session.

        Returns:
        template: redirects to register
    """

    mongo.db.cheeses.remove({"created_by": username.lower()})
    mongo.db.users.remove({"username": username.lower()})

    # Sends visual confirmation.
    flash("Profile deleted")
    session.pop("user")

    return redirect(url_for("register"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
