from flask import Flask, request, render_template, redirect, url_for, flash, abort, session
from flask_session import Session
from functools import wraps

def main():
    #Config
    app = Flask(__name__)

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"

    Session(app)

    #Decorators and helpers

    get_id = lambda : session.get("id") #Get user id from session
    empty = lambda x: not x or x == "" #Does variable exist / Is it defined

    def verify_login(username, password): #Verify username and password
        if username == "TestUsername" and password == "TestPassword": #Testing condition - REPLACE so returns ID or -1
            return 1
        return -1
    
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

        id = verify_login(un, pw) #Get id and verify login

        if id != -1: #Verify if successful auth
            session["id"] = 10
            return "VERIFIED"

        flash("Login failed") #Unsuccessful auth
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

