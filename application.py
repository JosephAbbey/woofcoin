from flask import Flask, request, render_template, redirect, url_for, flash, abort, session
from flask_session import Session
from functools import wraps
import json

class User: #Individual user
    def __init__(self, json):
        self.data = {"id": json.user_id, "username": json.username, "password": json.password} #Stores user_id, username, and password

    def __dict__(self): #Get user as a dictionary
        return {"username": self.data.username, "password": self.data.password}

    def __str__(self): #Get user as a string
        return json.dumps(str(self))

class Database: #Database class
    def __init__(self, file):
        with open(file) as f: #Open database file
            data = json.loads(f.read()) #Read database file to dictionary
        self.data = {"users": [User(u) for u in data.users], "price": data.price} #Format users and Woofcoin price
        self.file = file #Store file location

    def __dict__(self): #Get database as a dictionary
        return {"users": [str(u) for u in self.data.users], "price": self.data.price}

    def __str__(self): #Get database as a string
        return json.dumps(str(self))

    def save(self): #Write changes to database file
        with open(self.file, "w") as f:
            f.write(str(self)) #Save JSON string of data

    def verify_login(self, username, password): #Verify username and password
        for u in self.data["users"]: #Linear search
            if username == u.data["username"] and password == u.data["password"]: #Verify
                return u.data["id"] #Return id
        return -1

def main():
    #Config
    app = Flask(__name__)
    db = Database("./db/index.db.json")

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"

    Session(app)

    #Decorators and helpers

    get_id = lambda : session.get("id") #Get user id from session
    empty = lambda x: not x or x == "" #Does variable exist / Is it defined
    
    def login_required(func): #Decorator for account-dependant pages
        @wraps(func)
        def decofunc(*args, **kwargs):
            user = get_id() #Get logged in user id
            if user != None: #If logged in
                return func(*args, **kwargs) #Run function
            flash("Please log in") #Flash message
            return redirect("/login") #Redirect
        return decofunc

    #Routes

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return render_template("login.html")

        form = request.form
        un = form.get("username") #Username
        pw = form.get("password") #Password

        if empty(un) or empty(pw): #Username or Password empty
            flash("One or more fields empty")
            return render_template("login.html", un=un, pw=pw)

        id = db.verify_login(un, pw) #Get id and verify login

        if id != -1: #Verify if successful auth
            #Successful
            session["id"] = 10
            return "VERIFIED"
        
        #Unsuccessful auth
        flash("Login failed")
        return render_template("login.html", un=un, pw=pw)
        
    @app.route("/api/buy")
    @login_required
    def buy():
        return "\'BUY API HERE\'"

    @app.route("/api/sell")
    @login_required
    def sell():
        return "\'SELL API HERE\'"

    @app.route("/api/mycoin")
    @login_required
    def mycoin():
        return "\'MYCOIN API HERE\'"

    return app

