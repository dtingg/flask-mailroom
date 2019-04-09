import os
import base64
from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256
from model import Donor, Donation, User

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY").encode()


@app.route('/')
def home():
    return redirect(url_for('all_donations'))


@app.route('/donations')
def all_donations():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)


@app.route("/add", methods=["GET", "POST"])
def add():
    if "logged_in" not in session:
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("add.jinja2")

    if request.method == "POST":
        try:
            donor = Donor.select().where(Donor.name == request.form["donor"]).get()
            amount = request.form["amount"]
            Donation(donor=donor, value=amount).save()

        except Donor.DoesNotExist:
            # If donor doesn't exist, redisplay the add donation page with an error message.
            # return render_template("add.jinja2", error="Donor not found. Please try again.")

            # If donor doesn't exist, create a new donor with the donation amount indicated
            new_donor = Donor(name=request.form["donor"])
            new_donor.save()
            Donation(donor=new_donor, value=request.form["amount"]).save()

        except ValueError:
            return render_template("add.jinja2", error="Incorrect donation amount. Please enter whole dollars only.")

        return redirect(url_for("all_donations"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            user = User.select().where(User.name == request.form["username"]).get()

            if user and pbkdf2_sha256.verify(request.form["password"], user.password):
                session["logged_in"] = request.form["username"]
                return redirect(url_for("add"))
        except User.DoesNotExist:
            return render_template("login.jinja2", error="Incorrect username or password. Please try again.")
    else:
        return render_template("login.jinja2")


@app.route("/logout", methods=["GET"])
def logout():
    try:
        del session["logged_in"]
    except KeyError:
        pass
    return redirect(url_for("login"))


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return render_template("create.jinja2")

    if request.method == "POST":
        try:
            query = Donation.select().join(Donor).where(Donor.name == request.form["donor"])

            return render_template("report.jinja2", donations=query)
        except User.DoesNotExist:
            return render_template("create.jinja2", error="Donor not found. Please try again.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)
