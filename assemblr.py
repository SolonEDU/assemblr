import urllib.parse
import urllib.request
import os
# import sqlite3
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
# from flask_sqlalchemy import SQLAlchemy
# from config import Config
# from utl import models
from google.cloud import firestore

# db = models.db
# User = models.User
# Request = models.Request
# Friend = models.Friend
# Message = models.Message
# Role = models.Role
# Technology = models.Technology
# Member = models.Member
# Team = models.Team
# Project = models.Project
# Devlog = models.Devlog

app = Flask(__name__)
# app.config.from_object(Config)

# creates secret key for sessions
app.secret_key = os.urandom(32)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"{os.path.dirname(os.path.abspath(__file__))}/static/json/assemblr-28d528f0fb82.json"
db = firestore.Client()

api_file = f"{os.path.dirname(os.path.abspath(__file__))}/static/json/api.json"

with open(api_file, 'r') as read_file:
    keys = json.load(read_file)

GITHUB_CLIENT_ID = keys['GITHUB_CLIENT_ID']
GITHUB_CLIENT_SECRET = keys['GITHUB_CLIENT_SECRET']

GITHUB_OAUTH_ROUTE = 'https://github.com/login/oauth/authorize'
GITHUB_OAUTH_REDIRECT = 'http://localhost:5000/callback'
GITHUB_API_ROUTE = 'https://api.github.com/graphql'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'


def graphql_query(query):
    req = urllib.request.Request(
        GITHUB_API_ROUTE,
        data=query,
        headers={'Authorization': f"Bearer {session['access_token']}"},
        method='POST'
    )

    req = urllib.request.urlopen(req)
    res = req.read()

    return json.loads(res)


def connect_required(f):
    '''
    decorator that redirects user to landing page if not connected to github
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'access_token' in session:
            flash("You must be connected to Github to view that page", "error")
            return redirect(url_for('root'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/connect_to_github')
def connect_to_github():
    github_auth_parameters = {
        'client_id': GITHUB_CLIENT_ID,
        'redirect_uri': GITHUB_OAUTH_REDIRECT,
        'scope': '',
    }
    github_auth_parameters = "&".join(
        [f"{key}={value}" for key, value in github_auth_parameters.items()])
    github_auth_url = f"{GITHUB_OAUTH_ROUTE}?{github_auth_parameters}"

    return redirect(github_auth_url)


@app.route('/callback')
def callback():
    auth_token = request.args['code']
    code_payload = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': str(auth_token),
        'redirect_uri': GITHUB_OAUTH_REDIRECT,
    }

    post_request = urllib.request.Request(
        GITHUB_TOKEN_URL,
        headers={'Accept': 'application/json'},
        data=urllib.parse.urlencode(code_payload).encode()
    )

    post_request = urllib.request.urlopen(post_request)
    post_request = post_request.read()

    response_data = json.loads(post_request)
    access_token = response_data['access_token']
    scope = response_data['scope']
    token_type = response_data['token_type']

    session['access_token'] = access_token

    query = {'query': '{ viewer { login name } }'}
    query = json.dumps(query).encode('utf8')

    result = graphql_query(query)

    session['login'] = result['data']['viewer']['login']
    session['name'] = result['data']['viewer']['name']

    if db.collection('users').document(session['login']).get().exists:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('register'))


@app.route("/")
def root():
    return redirect(url_for('home')) if 'login' in session else render_template('landing.html')


@app.route('/home')
@connect_required
def home():
    return render_template(
        'home.html'
    )


@app.route('/about')
def about():
    return render_template(
        'about.html'
    )


@app.route('/help')
def help():
    return render_template(
        'help.html'
    )


@app.route('/register', methods=['GET', 'POST'])
@connect_required
def register():
    if db.collection('users').document(session['login']).get().exists:
        return redirect(url_for('home'))
    if request.method == 'GET':
        query = {'query':
                 '''
        {
            viewer {
                topRepositories(first: 20, orderBy: {direction: ASC, field: UPDATED_AT}) {
                    edges {
                        node {
                            languages(first: 3, orderBy: {direction: ASC, field: SIZE}) {
                                edges { node { color name } }
                            }
                        }
                    }
                }
            }
        }
        '''}
        query = json.dumps(query).encode('utf8')

        result = graphql_query(query)

        languages = dict()

        for edge in result['data']['viewer']['topRepositories']['edges']:
            if not edge is None:
                for language in edge['node']['languages']['edges']:
                    languages[language['node']['name']
                              ] = language['node']['color']
        return render_template(
            'register.html',
            languages=languages
        )
    else:
        languages = {language: request.form[language]
                     for language in request.form.getlist('language')}

        doc_ref = db.collection('users').document(request.form['username'])
        doc_ref.set({
            'name': request.form['displayname'],
            'email': request.form['email'],
            'age': int(request.form['age']),
            'languages': languages
        })

        return redirect(url_for('home'))


@app.route('/profile')
@connect_required
def profile():
    return render_template(
        'profile.html'
    )


@app.route('/logout')
def logout():
    '''
    logs out user by deleting info from the session
    '''
    session.pop('login')
    session.pop('name')
    session.pop('access_token')
    return redirect(url_for('root'))


# @app.route("/home")
# @login_required
# def home():
#     uid = session['uid']
#     teams = Member.query.filter_by(uid=uid).all()
#     teamsData = {}
#     for team in teams:
#         membersUserArr = []
#         teamid = team.teamid
#         teamObject = Team.query.filter_by(id=teamid).first()
#         members = Member.query.filter_by(teamid=teamid).all()
#         for member in members:
#             memberUser = User.query.filter_by(uid=member.uid).first()
#             membersUserArr.append(memberUser)
#         teamsData[teamObject] = membersUserArr
#     return render_template(
#         "home.html",
#         teams=teamsData
#     )


# @app.route("/network")
# @login_required
# def network():
#     uid = session['uid']
#     friendids = Friend.query.filter_by(uid=uid).all()
#     friends = []
#     for friendid in friendids:
#         friend = User.query.filter_by(uid=friendid.friend).first()
#         print(friend)
#         friends.append(friend)
#     return render_template(
#         "network.html", friends=friends
#     )


# @app.route("/find")
# @login_required
# def find():
#     uid = session['uid']
#     allusers = User.query.all()
#     friends = Friend.query.filter_by(uid=uid).all()
#     userids = []
#     friendids = []
#     for user in allusers:
#         userids.append(user.uid)
#     for friend in friends:
#         friendids.append(friend.friend)
#     ids = []
#     for id in userids:
#         if id not in friendids:
#             ids.append(id)
#     users = []
#     for id in ids:
#         if id != uid:
#             user = User.query.filter_by(uid=id).first()
#             users.append(user)
#     return render_template(
#         "find.html",
#         users=users
#     )


# @app.route("/addfriend", methods=['POST'])
# @login_required
# def addfriend():
#     uid = session['uid']
#     friendid = request.form['friendid']
#     newfriend = Friend(uid=uid, friend=friendid)
#     db.session.add(newfriend)
#     db.session.commit()
#     return redirect(url_for('find'))


# @app.route("/new_project/<teamid>", methods=['GET', 'POST'])
# @login_required
# def new_project(teamid):
#     if request.method == 'POST':
#         newProjectName = request.form['projectname']
#         newProjectDescription = request.form['description']
#         newProjectRepo = request.form['repo']
#         newProject = Project(projectname=newProjectName,
#                              description=newProjectDescription, teamid=teamid, repo=newProjectRepo)
#         db.session.add(newProject)
#         db.session.commit()
#         newProjectRecord = Project.query.filter_by(
#             projectname=newProjectName).first()
#         newProjectId = newProjectRecord.id
#         return redirect(url_for('project', projectid=newProjectId))
#     return render_template(
#         "new_project.html",
#         teamid=teamid
#     )


# @app.route("/new_team", methods=['GET', 'POST'])
# @login_required
# def new_team():
#     if request.method == 'POST':
#         newTeamMemberList = request.form.getlist('members')
#         newTeamMemberList = [int(x) for x in newTeamMemberList]
#         newTeamMemberList.append(session['uid'])
#         print(newTeamMemberList)
#         newTeamName = request.form['teamname']
#         newTeam = Team(teamname=newTeamName)
#         db.session.add(newTeam)
#         db.session.commit()
#         newTeamRecord = Team.query.filter_by(teamname=newTeamName).first()
#         newTeamId = newTeamRecord.id
#         for member in newTeamMemberList:
#             newMember = Member(teamid=newTeamId, uid=member)
#             db.session.add(newMember)
#             db.session.commit()
#         return redirect(url_for('team', teamid=newTeamId))
#         # for newTeamMember in newTeamMemberList:
#         #     newmember = Member(teamid)
#     else:
#         uid = session['uid']
#         friendids = Friend.query.filter_by(uid=uid).all()
#         friends = []
#         for friendid in friendids:
#             friend = User.query.filter_by(uid=friendid.friend).first()
#             print(friend)
#             friends.append(friend)
#         return render_template(
#             "new_team.html",
#             friends=friends
#         )


# @app.route("/profile/<uid>")
# @login_required
# def profile(uid):
#     user = User.query.filter_by(uid=uid).first()
#     return render_template(
#         "profile.html",
#         user=user
#     )


# @app.route("/team/<teamid>")
# @login_required
# def team(teamid):
#     teamid = int(teamid)
#     teamObject = Team.query.filter_by(id=teamid).first()
#     members = Member.query.filter_by(teamid=teamid).all()
#     memberUsers = []
#     for member in members:
#         user = User.query.filter_by(uid=member.uid).first()
#         memberUsers.append(user)
#     projects = Project.query.filter_by(teamid=teamid).all()
#     return render_template(
#         "team.html",
#         team=teamObject,
#         members=memberUsers,
#         projects=projects,
#         teamid=teamid
#     )


# @app.route("/project/<projectid>")
# @login_required
# def project(projectid):
#     project = Project.query.filter_by(id=projectid).first()
#     team = Team.query.filter_by(id=project.teamid).first()
#     users = Member.query.filter_by(teamid=team.id).all()
#     members = []
#     for user in users:
#         member = User.query.filter_by(uid=user.id).first()
#         members.append(member)
#     entries = Devlog.query.filter_by(
#         projectid=projectid).order_by(Devlog.timestamp.desc())
#     devlog = {}
#     for entry in entries:
#         devlog[entry] = User.query.filter_by(uid=entry.uid).first()
#     return render_template(
#         "project.html",
#         project=project,
#         team=team,
#         members=members,
#         devlog=devlog
#     )


# @app.route("/devlogentry/<projectid>", methods=['GET', 'POST'])
# @login_required
# def devlogentry(projectid):
#     projectid = int(projectid)
#     if request.method == 'POST':
#         uid = session['uid']
#         content = request.form['content']
#         entry = Devlog(projectid=projectid, uid=uid, content=content)
#         db.session.add(entry)
#         db.session.commit()
#         return redirect(url_for('project', projectid=projectid))
#     else:
#         return render_template(
#             "new_devlog.html",
#             projectid=projectid,
#         )


if __name__ == "__main__":
    # db.init_app(app)
    # with app.app_context():
    #     db.create_all()
    app.debug = True
    app.run()
