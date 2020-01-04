from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from config import Config
from utl import models
db = models.db
User = models.User
Request = models.Request
Friend = models.Friend
Message = models.Message
# Role = models.Role
# Technology = models.Technology
Member = models.Member
Team = models.Team
Project = models.Project
import sqlite3
import os


app = Flask(__name__)
app.config.from_object(Config)

#creates secret key for sessions
app.secret_key = os.urandom(32)

#decorator that redirects user to login page if not logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "uid" not in session:
            flash("You must be logged in to view this page", "error")
            return redirect(url_for('root'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def root():
    if "uid" in session:
        return redirect(url_for('home'))
    else:
        return render_template(
            "landing.html",
        )


@app.route("/login")
def login():
    if "uid" in session:
        return redirect(url_for('home'))
    else:
        return render_template(
            "login.html",
        )

#authenticates user upon a login attempt
@app.route("/auth", methods=["POST"])
def auth():
    if "uid" in session:
        flash("You were already logged in, "+session['email']+".", "error")
        return redirect(url_for('home'))
    # information inputted into the form by the user
    email = request.form['email']
    password = request.form['password']
    # looking for email & password from database
    user = User.query.filter_by(email=email).first()
    if user == None: # if email not found
        flash("No user found with given email", "error")
        return redirect(url_for('login'))
    elif password != user.password: # if password is incorrect
        flash("Incorrect password", "error")
        return redirect(url_for('login'))
    else: # hooray! the email and password are both valid
        session['uid'] = user.uid
        session['email'] = user.email
        flash("Welcome " + email + ". You have been logged in successfully.", "success")
        return redirect(url_for('home'))

@app.route("/signup")
def signup():
    if "uid" in session:
        return redirect(url_for('home'))
    else:
        return render_template(
            "register.html"
        )

#creates a new user in the database if provided valid signup information
@app.route("/register", methods=["POST"])
def register():
    if "uid" in session:
        return redirect(url_for('home'))
    #gets user information from POST request
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    password2 = request.form['password2']
    age = int(request.form['age'])
    city = request.form['city']
    bio = request.form['bio']
    #looking if user with email in database already exists
    user = User.query.filter_by(email=email).first()
    if user != None:
        flash("Account with that email already exists", "error")
        return redirect(url_for('signup'))
    elif password != password2:
        flash("Passwords do not match", "error")
        return redirect(url_for('signup'))
    elif len(password) < 8:
        flash("Password must be at least 8 characters in length", "error")
        return redirect(url_for('signup'))
    #successfully add user to database
    else:
        newuser = User(firstname=firstname, lastname=lastname, email=email, password=password, age=age, city=city, bio=bio)
        db.session.add(newuser)
        db.session.commit()
        flash("Successfully created user", "success")
        return redirect(url_for('login'))

#logs out user by deleting info from the session
@app.route("/logout")
def logout():
    if not "uid" in session:
        flash("Already logged out, no need to log out again", "error")
    else:
        session.pop('uid')
        session.pop('email')
        flash("Successfully logged out", "success")
    return redirect(url_for('root')) # should redirect back to login page

@app.route("/home")
@login_required
def home():
    uid = session['uid'] 
    teams = Member.query.filter_by(uid=uid).all() 
    teamsData = {}
    for team in teams:
        membersUserArr = []
        teamid = team.teamid
        # print(teamid)
        teamObject = Team.query.filter_by(id=teamid).first()
        members = Member.query.filter_by(teamid=teamid).all()
        for member in members:
            memberUser = User.query.filter_by(uid=member.uid).first()
            # print(memberUser.firstname)
            membersUserArr.append(memberUser)
        # print(teamObject.teamname)
        # print(members)
        teamsData[teamObject] = membersUserArr
    return render_template(
        "home.html",
        teams=teamsData
    )


@app.route("/network")
@login_required
def network():
    return render_template(
        "network.html"
    )


@app.route("/my_people")
@login_required
def my_people():
    return render_template(
        "my_people.html"
    )


@app.route("/other_people")
@login_required
def other_people():
    return render_template(
        "other_people.html"
    )


@app.route("/new_project")
@login_required
def new_project():
    return render_template(
        "new_project.html"
    )


@app.route("/new_team")
@login_required
def new_team():
    return render_template(
        "new_team.html"
    )


@app.route("/profile/<uid>")
@login_required
def profile():
    user = User.query.filter_by(uid=uid).first()
    return render_template(
        "profile.html", 
        user=user
    )


@app.route("/project")
@login_required
def project():
    return render_template(
        "project.html"
    )


@app.route("/team/<teamid>")
@login_required
def team(teamid):
    print(teamid)
    teamName = Team.query.filter_by(id=teamid).first().teamname
    print(teamName)
    members = Member.query.filter_by(teamid=teamid).all()
    memberUsers = []
    for member in members:
        user = User.query.filter_by(uid=member.uid).first()
        print(user.firstname)
        memberUsers.append(user)
    return render_template(
        "team.html",
        teamName = teamName,
        members = memberUsers
    )

if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0')
