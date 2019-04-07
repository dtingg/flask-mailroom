import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session

from model import Donor, Donation

app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('all_donations'))


@app.route('/donations/')
def all_donations():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)


@app.route("/add", methods=["GET", "POST"])
def add():
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
            Donation(donor=request.form["donor"], value=amount).save()

        return redirect(url_for("all_donations"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)
