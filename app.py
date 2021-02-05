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
@app.route('/')
@app.route("/index")
def index():

    return render_template("index.html")


# ---------- REGISTER PAGE ---------- #
@app.route("/register", methods=["GET", "POST"])
def register():
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
            "password": generate_password_hash(request.form.get("password"))
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
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


# ---------- LOGOUT ---------- #
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
    cheeses = list(mongo.db.cheeses.find())

    return render_template("cheeses.html", cheeses=cheeses)


# ---------- ADD PAIRING ---------- #
@app.route("/add_pairing", methods=["GET", "POST"])
def add_pairing():
    if request.method == "POST":
        # send form data to cheese collection

        pairing = {
            "cheese_name": request.form.get("cheese_name"),
            "country_of_origin": request.form.get("country_of_origin"),
            "made_from": request.form.get("made_from"),
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

    cheeses = mongo.db.cheeses.find_one({'_id': ObjectId(cheeses_id)})

    return render_template("single_cheese.html", cheeses=cheeses)


# ---------- EDIT PAGE ---------- #
@app.route("/edit_pairing/<cheeses_id>", methods=["GET", "POST"])
def edit_pairing(cheeses_id):
    if request.method == "POST":
        # send form data to MongoDB and update fields

        submit = {
            "cheese_name": request.form.get("cheese_name"),
            "country_of_origin": request.form.get("country_of_origin"),
            "made_from": request.form.get("made_from"),
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

    cheeses = mongo.db.cheeses.find_one({"_id": ObjectId(cheeses_id)})
    return render_template("edit_pairing.html", cheeses=cheeses)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
