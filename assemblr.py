from flask import Flask, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from config import Config
from utl import models
db = models.db
User = models.User
import sqlite3
import os
import json

app = Flask(__name__)
app.config.from_object(Config)

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


@app.route("/new_project")
def new_project():
    return render_template(
        "new_project.html"
    )


@app.route("/new_team")
def new_team():
    return render_template(
        "new_team.html"
    )


@app.route("/profile")
def profile():
    return render_template(
        "profile.html"
    )


@app.route("/project")
def project():
    return render_template(
        "project.html"
    )


@app.route("/team")
def team():
    return render_template(
        "team.html"
    )

if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
