from flask import Flask, request, render_template, redirect, url_for, flash, abort, session, jsonify
from flask_session import Session
from functools import wraps
import json

# Needed by functions not in main scope
empty = lambda x: not x or x == "" # Does variable exist / Is it defined

def getUserFunc(obj, **kwargs):
    if obj.data["user_id"] == kwargs["id"]:
        return obj
    elif obj.data["user_id"] > kwargs["id"]:
        return -3 # Rerun call (low, mid-1)
    return -4 # Rerun call (mid+1, high)

def verifUserFunc(obj, **kwargs):
    if obj.data["username"] == kwargs["username"]:
        if obj.data["password"] == kwargs["password"]:
            return obj.data["user_id"] # Correct password
        return -2 # Wrong password
    elif obj.data["username"] > kwargs["username"]:
        return -3 # Rerun call (low, mid-1)
    return -4 # Rerun call (mid+1, high)

# Generalized binary search
def binarySearch(arr, Func, low=0, high=-1, **kwargs):
    high = len(arr)-1 if high == -1 else high # Using none as a placeholder causes an edge case to occur where the range gets stuck on 0:2 as the high var always gets reset

    if high >= low: # If range of search includes at least one item
        mid = (high+low) // 2 # Get midpoint of range
        midObj = arr[mid] # Get midpoint item
        
        ret = Func(midObj, **kwargs) # Comparison function

        if ret == -3:
            return binarySearch(arr, Func, low, mid-1, **kwargs)
        elif ret == -4:
            return binarySearch(arr, Func, mid+1, low, **kwargs)
        return ret

    return -1 # Not found

class User: # Individual user
    def __init__(self, json):
        self.data = json # Stores user_id, username, and password

    def __str__(self): # Get user as a string
        return json.dumps(self.data)

    def queryCoin(self):
        return self.data["coin"]

    def addCoin(self, coins):
        self.data["coin"] = self.queryCoin() + coins

    def resetCoins(self):
        self.data["coin"] -= self.queryCoin()

class Database: # Database class
    def __init__(self, file):
        with open(file) as f: # Open database file
            data = json.loads(f.read()) # Read database file to dictionary
        self.data = {"users": [User(u) for u in data["users"]], "price": data["price"]} # Format users and Woofcoin price
        self.sortedUsers = sorted(self.data["users"], key=lambda x: x.data["username"])
        self.file = file # Store file location

    def __dict__(self): # Get database as a dictionary
        return {"users": [u.data for u in self.data["users"]], "price": self.data["price"]}

    def __str__(self): # Get database as a string
        return json.dumps({"users": [u.data for u in self.data["users"]], "price": self.data["price"]}, indent=4)

    def save(self): # Write changes to database file
        with open(self.file, "w") as f:
            f.write(str(self)) # Save JSON string of data

    def get_user_obj(self, id): # Try to merge with get_user
        # Binary search
        return binarySearch(self.data["users"], getUserFunc, id=id)

    def get_user(self, username, password=None, low=0, high=None): # Verify username and password (and does tons of other things)
        # Binary Search
        return binarySearch(self.sortedUsers, verifUserFunc, username=username, password=password)
    
    def max_id(self): # Get largest ID
        length = len(self.data["users"])
        if length == 0:
            return 1
        return self.data["users"][length - 1].data["user_id"] + 1
    
    def add_user(self, username, password): # Add new user to DB
        if empty(username) or empty(password):
            return -1

        getuser = self.get_user(username)
        if getuser == -2: # If user exists
            return -1
        
        id = self.max_id() # Get next highest ID
        u = User({"user_id": id, "username": username, "password": password}) # Create new user object

        self.data["users"].append(u) # Add user object to self.data
        self.sortedUsers = sorted(self.data["users"], key=lambda x: x.data["username"]) # Re-sort users for binary search
        self.save()

        return id

def main():
    # Config

    app = Flask(__name__)
    db = Database("template.json")

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"

    Session(app)

    # Decorators and helpers

    get_id = lambda : session.get("id") # Get user id from session
    
    def login_required(func): # Decorator for account-dependant pages
        @wraps(func)
        def decofunc(*args, **kwargs):
            user = db.get_user_obj(get_id()) # Get logged in user id
            if user != None: # If logged in
                return func(user, *args, **kwargs) # Run function
            flash("Please log in", "warn") # Flash message
            return redirect("/login") # Redirect
        return decofunc

    # Routes

    @app.route("/")
    def index():
        return render_template("index.html") # Homepage

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET": # GET page
            return render_template("login.html")

        # Submit form
        form = request.form
        un = form.get("username") # Username
        pw = form.get("password") # Password

        if empty(un) or empty(pw): # Username or Password empty
            flash("One or more fields empty", "warn")
            return render_template("login.html", un=un, pw=pw)

        id = db.get_user(un, pw) # Get id and verify login

        if id > -1: # Verify if successful auth
            # Successful
            session["id"] = id
            return redirect("/")
        
        # Unsuccessful auth
        flash("Login failed", "warn")
        return render_template("login.html", un=un, pw=pw)
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            return render_template("register.html")
        
        # Submit form
        form = request.form
        un = form.get("username") # Username
        pw1 = form.get("password1") # Password
        pw2 = form.get("password2")

        if pw1 != pw2: # Passwords don't match
            flash("Passwords do not match", "warn")
            return render_template("register.html", un=un, pw1=pw1, pw2=pw2)

        if empty(un) or empty(pw1): # Username or Password empty
            flash("One or more fields empty", "warn")
            return render_template("register.html", un=un, pw1=pw1, pw2=pw2)
        
        id = db.add_user(un, pw1)
        if id > -1: # Verify if successful auth
            # Successful
            id = db.add_user(un, pw1)
            session["id"] = id
            return redirect("/")
        
        # Unsuccessful auth
        flash("User already exists", "warn")
        return render_template("register.html", un=un, pw1=pw1, pw2=pw2)
    
    @app.route("/logout")
    @login_required
    def logout(user_id):
        session.clear()
        return redirect("/")

    @app.route("/api/rates", methods=["POST"])
    def rates():
        frame = request.form.get("frame") # Time frame
        frames = ["day", "week", "month"] # Accepted frames

        if empty(frame) or frame not in frames:
            frame = "week" # Default frame

        id = frames.index(frame)
        if id == 0:
            return jsonify({10: 2, 15: 3})

        return jsonify({5: 2, 10: 3})
        
    @app.route("/api/debug/db")
    @login_required
    def debug_db(user):
        return jsonify(db.__dict__())

    @app.route("/api/debug/user_id")
    @login_required
    def debug_user_id(user):
        return str(user.data["user_id"])

    @app.route("/api/debug/addcoin")
    @login_required
    def debug_coins(user):
        user.addCoin(10)
        db.save()
        return "{user}'s coins: {total}".format(user=user.data["username"], total=str(user.queryCoin()))

    @app.route("/api/buy")
    @login_required
    def buy(user):
        return str(db)

    @app.route("/api/sell")
    @login_required
    def sell(user):
        return str(user)

    @app.route("/api/mycoin")
    @login_required
    def mycoin(user):
        return "\'MYCOIN API HERE\'"

    return (db, app)
