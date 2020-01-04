from flask import Flask, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from config import Config
from utl import models
db = models.db
User = models.User
Request = models.Request
Friend = models.Friend
Message = models.Message
Role = models.Role
Technology = models.Technology
Member = models.Member
Team = models.Team
Project = models.Project
import sqlite3
import os


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
    # uid = session['uid']
    uid = 0 # replace uid lata
    teams = Member.query.filter_by(uid=uid).all() 
    teamsData = {}
    for team in teams:
        membersUserArr = []
        teamid = team.teamid
        print(teamid)
        teamObject = Team.query.filter_by(id=teamid).first()
        members = Member.query.filter_by(teamid=teamid).all()
        for member in members:
            memberUser = User.query.filter_by(uid=member.uid).first()
            print(memberUser.firstname)
            membersUserArr.append(memberUser)
        print(teamObject.teamname)
        print(members)
        teamsData[teamObject] = membersUserArr
    return render_template(
        "home.html",
        teams=teamsData
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
    app.run(host='0.0.0.0')
