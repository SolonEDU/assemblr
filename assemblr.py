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
Devlog = models.Devlog
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
    github = request.form['github']
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
        newuser = User(firstname=firstname, lastname=lastname, email=email, github=github, password=password, age=age, city=city, bio=bio)
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
        teamObject = Team.query.filter_by(id=teamid).first()
        members = Member.query.filter_by(teamid=teamid).all()
        for member in members:
            memberUser = User.query.filter_by(uid=member.uid).first()
            membersUserArr.append(memberUser)
        teamsData[teamObject] = membersUserArr
    return render_template(
        "home.html",
        teams=teamsData
    )


@app.route("/network")
@login_required
def network():
    uid = session['uid']
    friendids = Friend.query.filter_by(uid=uid).all()
    friends = []
    for friendid in friendids:
        friend = User.query.filter_by(uid=friendid.friend).first()
        print(friend)
        friends.append(friend)
    return render_template(
        "network.html", friends=friends
    )


@app.route("/find")
@login_required
def find():
    uid = session['uid']
    allusers = User.query.all()
    friends = Friend.query.filter_by(uid=uid).all()
    userids = []
    friendids = []
    for user in allusers:
        userids.append(user.uid)
    for friend in friends:
        friendids.append(friend.friend)
    ids = []
    for id in userids:
        if id not in friendids:
            ids.append(id)
    users = []
    for id in ids:
        if id != uid:
            user = User.query.filter_by(uid=id).first()
            users.append(user)
    return render_template(
        "find.html",
        users=users
    )

@app.route("/addfriend", methods=['POST'])
@login_required
def addfriend():
    uid = session['uid']
    friendid = request.form['friendid']
    newfriend = Friend(uid=uid, friend=friendid)
    db.session.add(newfriend)
    db.session.commit()
    return redirect(url_for('find'))

@app.route("/new_project")
@login_required
def new_project():
    return render_template(
        "new_project.html"
    )


@app.route("/new_team", methods=['GET', 'POST'])
@login_required
def new_team():
    if request.method == 'POST':
        newTeamMemberList = request.form.getlist('members')
        newTeamMemberList = [ int(x) for x in newTeamMemberList ]
        newTeamMemberList.append(session['uid'])
        print(newTeamMemberList)
        newTeamName = request.form['teamname']
        newTeam = Team(teamname = newTeamName)
        db.session.add(newTeam)
        db.session.commit()
        newTeamRecord = Team.query.filter_by(teamname=newTeamName).first()
        newTeamId = newTeamRecord.id
        for member in newTeamMemberList:
            newMember = Member(teamid=newTeamId, uid=member)
            db.session.add(newMember)
            db.session.commit()
        return redirect(url_for('team', teamid = newTeamId))
        # for newTeamMember in newTeamMemberList:
        #     newmember = Member(teamid)
    else:
        uid = session['uid']
        friendids = Friend.query.filter_by(uid=uid).all()
        friends = []
        for friendid in friendids:
            friend = User.query.filter_by(uid=friendid.friend).first()
            print(friend)
            friends.append(friend)
        return render_template(
            "new_team.html",
            friends = friends
        )


@app.route("/profile/<uid>")
@login_required
def profile(uid):
    user = User.query.filter_by(uid=uid).first()
    return render_template(
        "profile.html",
        user=user
    )

@app.route("/team/<teamid>")
@login_required
def team(teamid):
    teamid = int(teamid)
    teamName = Team.query.filter_by(id=teamid).first().teamname
    members = Member.query.filter_by(teamid=teamid).all()
    memberUsers = []
    for member in members:
        user = User.query.filter_by(uid=member.uid).first()
        memberUsers.append(user)
    projects = Project.query.filter_by(teamid=teamid).all()
    return render_template(
        "team.html",
        teamName = teamName,
        members = memberUsers,
        projects = projects
    )

@app.route("/project/<projectid>")
@login_required
def project(projectid):
    project = Project.query.filter_by(id=projectid).first()
    team = Team.query.filter_by(id=project.teamid).first()
    users = Member.query.filter_by(teamid=team.id).all()
    members = []
    for user in users:
        member = User.query.filter_by(uid=user.id).first()
        members.append(member)
    entries = Devlog.query.filter_by(projectid=projectid).order_by(Devlog.timestamp.desc())
    devlog = {}
    for entry in entries:
        devlog[entry] = User.query.filter_by(uid=entry.uid).first()
    return render_template(
        "project.html",
        project = project,
        team = team,
        members = members,
        devlog = devlog
    )

@app.route("/devlogentry/<projectid>", methods=['GET','POST'])
@login_required
def devlogentry(projectid):
    projectid = int(projectid)
    if request.method == 'POST':
        uid = session['uid']
        content = request.form['content']
        entry = Devlog(projectid=projectid, uid=uid, content=content)
        db.session.add(entry)
        db.commit()
    else:
        return render_template(
            "new_devlog.html",
            projectid = projectid,
            )

if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.debug = True
    app.run(host='0.0.0.0')