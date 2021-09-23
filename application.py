from flask import Flask, request, render_template, redirect, url_for, flash, abort
import json

class Session:
    def __init__(self, json):
        self.data = json

    def __dict__(self):
        return self.data

class User:
    def __init__(self, json):
        self.data = {"username": json.username, "password": json.password, "sessions": [Session(s) for s in json.sessions]}

    def __dict__(self):
        return {"username": self.data.username, "password": self.data.password, "sessions": [str(s) for s in self.data.sessions]}

class Database:
    def __init__(self, json):
        self.data = {"users": [User(u) for u in json.users], "price": json.price}

    def save(self):
        with open("./db/index.db.json", "w") as f:
            f.write(str(self))

    def __dict__(self):
        return {"users": [str(u) for u in self.data.users], "price": self.data.price}

    def __str__(self):
        return json.dumps(str(self))

def main():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if (request.method == "GET"):
            return render_template('login.html')
        if (request.method == "POST"):

            return "loggin"

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect("/")

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

