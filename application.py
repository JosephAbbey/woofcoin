from flask import Flask, request, render_template

def main():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/buy")
    def buy():
        return "\'BUY API HERE\'"

    return app

