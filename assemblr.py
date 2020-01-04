from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
import sqlite3
import os
import json

app = Flask(__name__)

@app.route("/")
def root():
    return render_template(
        "landing.html",
    )

@app.route("/login")
def login():
    return render_template(
        "login.html",
    )

@app.route("/register")
def register():
    return render_template(
        "register.html"
    )

@app.route("/home")
def home():
    return render_template(
        "home.html"
    )

@app.route("/network")
def network():
    return render_template(
        "network.html"
    )

@app.route("/my_people")
def my_people():
    return render_template(
        "my_people.html"
    )

@app.route("/other_people")
def other_people():
    return render_template(
        "other_people.html"
    )

@app.route("new_project")
def new_project():
    return render_template(
        "new_project.html"
    )

@app.route("new_team")
def new_team():
    return render_template(
        "new_team.html"
    )

@app.route("profile")
def profile():
    return render_template(
        "profile.html"
    )

@app.route("project")
def project():
    return render_template(
        "project.html"
    )

@app.route("team")
def team():
    return render_template(
        "team.html"
    )
if __name__ == "__main__":
    app.run(host='0.0.0.0')
