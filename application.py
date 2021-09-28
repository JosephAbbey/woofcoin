from flask import Flask, request, render_template, redirect, url_for, flash, abort, session
from flask_session import Session
from functools import wraps
import json

#Needed by functions not in main scope
empty = lambda x: not x or x == "" #Does variable exist / Is it defined

class User: #Individual user
    def __init__(self, json):
        self.data = {"user_id": json["user_id"], "username": json["username"], "password": json["password"]} #Stores user_id, username, and password

    def __dict__(self): #Get user as a dictionary
        return self.data

    def __str__(self): #Get user as a string
        return json.dumps(self.data)

class Database: #Database class
    def __init__(self, file):
        with open(file) as f: #Open database file
            data = json.loads(f.read()) #Read database file to dictionary
        self.data = {"users": [User(u) for u in data["users"]], "price": data["price"]} #Format users and Woofcoin price
        self.sortedUsers = sorted(self.data["users"], key=lambda x: x.data["username"])
        self.file = file #Store file location

    def __dict__(self): #Get database as a dictionary
        return {"users": [str(u) for u in self.data["users"]], "price": self.data["price"]}

    def __str__(self): #Get database as a string
        return json.dumps({"users": [str(u) for u in self.data["users"]], "price": self.data["price"]})

    def save(self): #Write changes to database file
        with open(self.file, "w") as f:
            f.write(str(self)) #Save JSON string of data

    def verify_login(self, username, password=None, low=0, high=len(self.sortedUsers)-1): #Verify username and password
        #Binary Search
        if high >= low:
            mid = (high+low) // 2

            if self.sortedUsers[mid]["username"] == username: #Username found
                if self.sortedUsers[mid]["password"] == password:
                    return self.sortedUsers[mid]["user_id"]
                return -2 #Password incorrect

            elif self.sortedUsers[mid]["username"] > username:
                return self.verify_login(username, password, low, mid-1)

            return self.verify_login(username, password, mid+1, high)

        return -1 #Not found
    
    def max_id(self): #Get largest ID
        length = len(self.data["users"])
        if length == 0:
            return 1
        return self.data["users"][length - 1]["user_id"] + 1
    
    def add_user(self, username, password): #Add new user to DB
        if empty(username) or empty(password):
            return False

        getuser = self.verify_login(username)
        if getuser == -2: #If user exists
            return False
        
        id = self.max_id() #Get next highest ID
        u = User({"user_id": id, "username": username, "password": password}) #Create new user object

        self.data["users"].append(u) #Add user object to self.data
        self.sortedUsers = sorted(self.data["users"], key=lambda x: x.data["username"]) #Re-sort users for binary search
        self.save()

        return True

def main():
    #Config
    app = Flask(__name__)
    db = Database("template.json")

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"

    Session(app)

    #Decorators and helpers

    get_id = lambda : session.get("id") #Get user id from session
    
    def login_required(func): #Decorator for account-dependant pages
        @wraps(func)
        def decofunc(*args, **kwargs):
            user = get_id() #Get logged in user id
            if user != None: #If logged in
                return func(user, *args, **kwargs) #Run function
            flash("Please log in") #Flash message
            return redirect("/login") #Redirect
        return decofunc

    #Routes

    @app.route("/")
    def index():
        return render_template("index.html") #Homepage

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET": #GET page
            return render_template("login.html")

        #Submit form
        form = request.form
        un = form.get("username") #Username
        pw = form.get("password") #Password

        if empty(un) or empty(pw): #Username or Password empty
            flash("One or more fields empty")
            return render_template("login.html", un=un, pw=pw)

        id = db.verify_login(un, pw) #Get id and verify login

        if id > -1: #Verify if successful auth
            #Successful
            session["id"] = id
            return redirect("/")
        
        #Unsuccessful auth
        flash("Login failed")
        return render_template("login.html", un=un, pw=pw)
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            return render_template("register.html")
        
        #Submit form
        form = request.form
        un = form.get("username") #Username
        pw1 = form.get("password1") #Password
        pw2 = form.get("password2")

        if pw1 != pw2: #Passwords don't match
            flash("Passwords do not match")
            return render_template("register.html", un=un, pw1=pw1, pw2=pw2)

        if empty(un) or empty(pw1): #Username or Password empty
            flash("One or more fields empty")
            return render_template("register.html", un=un, pw1=pw1, pw2=pw2)
        
        if not db.userExists(un): #Verify if successful auth
            #Successful
            id = db.add_user(un, pw1)
            session["id"] = id
            return redirect("/")
        
        #Unsuccessful auth
        flash("User already exists")
        return render_template("register.html", un=un, pw1=pw1, pw2=pw2)
    
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/")
        
    @app.route("/api/buy")
    @login_required
    def buy(user_id):
        return str(db)

    @app.route("/api/sell")
    @login_required
    def sell(user_id):
        return str(user_id)

    @app.route("/api/mycoin")
    @login_required
    def mycoin(user_id):
        return "\'MYCOIN API HERE\'"

    return (db, app)

