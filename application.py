from flask import Flask, request, render_template, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user

def main():
    app = Flask(__name__)
    login_manager = LoginManager()
    login_manager.init_app(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Here we use a class of some kind to represent and validate our
        # client-side form data. For example, WTForms is a library that will
        # handle this for us, and we use a custom LoginForm to validate.
        form = LoginForm()
        if form.validate_on_submit():
            # Login and validate the user.
            # user should be an instance of your `User` class
            login_user(user)

            flash('Logged in successfully.')

            next = request.args.get('next')
            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            if not is_safe_url(next):
                return abort(400)

            return redirect(next or url_for('index'))
        return render_template('login.html', form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(somewhere)

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

