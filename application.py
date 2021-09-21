from flask import Flask, request

def main():
    app = Flask(__name__)

    @app.route("/api/buy")
    def buy():
        print(request.args)
        return "hello"

    app.run(host="0.0.0.0", port=8000)
