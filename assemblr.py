import urllib.parse
import urllib.request
import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
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

file = os.path.dirname(os.path.abspath(__file__))

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"{file}/static/json/assemblr-28d528f0fb82.json"
db = firestore.Client()

api_file = f"{file}/static/json/api.json"

with open(api_file, 'r') as read_file:
    keys = json.load(read_file)

GITHUB_CLIENT_ID = keys['GITHUB_CLIENT_ID']
GITHUB_CLIENT_SECRET = keys['GITHUB_CLIENT_SECRET']

GITHUB_OAUTH_ROUTE = 'https://github.com/login/oauth/authorize'
GITHUB_OAUTH_REDIRECT = 'http://localhost:5000/callback'
# GITHUB_OAUTH_REDIRECT = 'https://assemblr.solonedu.com/callback'
GITHUB_GRAPHQL_API_ROUTE = 'https://api.github.com/graphql'
GITHUB_REST_API_ROUTE = 'https://api.github.com'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'


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


def in_database(f):
    '''
    decorator that redirects user to registration page if not registered in database
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not db.collection('users').document(session['login']).get().exists:
            flash('You must be registered to view that page', "error")
            return redirect(url_for('register'))
        return f(*args, **kwargs)
    return decorated_function


def graphql_query(query):
    '''
    function to handle graphql queries to the github api
    '''
    query = json.dumps({'query': query}).encode('utf8')

    req = urllib.request.Request(
        GITHUB_GRAPHQL_API_ROUTE,
        data=query,
        headers={'Authorization': f"Bearer {session['access_token']}"},
        method='POST'
    )

    req = urllib.request.urlopen(req)
    res = req.read()

    return json.loads(res)


def rest_query(query="", route="", method=""):
    '''
    function to handle queries to the github rest api
    '''

    query = json.dumps(query).encode('utf8')

    req = urllib.request.Request(
        f"{GITHUB_REST_API_ROUTE}{route}",
        headers={
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f"token {session['access_token']}",
        },
        data=query,
        method=method,
    )

    req = urllib.request.urlopen(req)
    res = req.read()

    return json.loads(res)


def get_register_info():
    query = '''
    {
        viewer {
            avatarUrl
            email
            topRepositories(first: 20, orderBy: {direction: ASC, field: UPDATED_AT}) {
                edges {
                    node {
                        languages(first: 3, orderBy: {direction: DESC, field: SIZE}) {
                            edges { node { color name } }
                        }
                    }
                }
            }
        }
    }
    '''

    result = graphql_query(query)

    languages = dict()

    session['image'] = result['data']['viewer']['avatarUrl']
    session['email'] = result['data']['viewer']['email']

    for edge in result['data']['viewer']['topRepositories']['edges']:
        if not edge is None:
            for language in edge['node']['languages']['edges']:
                languages[language['node']['name']
                          ] = language['node']['color']

    return languages


def get_gitignore():
    rest_query(route='/gitignore/templates', method='GET')


@app.route('/connect_to_github')
def connect_to_github():
    github_auth_parameters = {
        'client_id': GITHUB_CLIENT_ID,
        'redirect_uri': GITHUB_OAUTH_REDIRECT,
        'scope': 'user:email repo',
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

    query = '{ viewer { login name } }'

    result = graphql_query(query)

    session['login'] = result['data']['viewer']['login']
    name = result['data']['viewer']['name']
    if not name is None:
        session['name'] = name

    # checking user existence in database
    users_ref = db.collection('users')
    viewer = users_ref.document(session['login']).get()

    if viewer.exists:
        session['image'] = viewer.get('image')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('register'))


@app.route("/")
def root():
    if 'login' in session:
        return redirect(url_for('home'))
    else:
        docs = db.collection('languages').stream()

        languages = [doc.to_dict()['color'] for doc in docs]

        return render_template(
            'landing.html',
            languages=languages
        )


@app.route('/home')
@connect_required
@in_database
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/register', methods=['GET', 'POST'])
@connect_required
def register():
    if db.collection('users').document(session['login']).get().exists:
        return redirect(url_for('home'))
    if request.method == 'GET':
        languages = get_register_info()
        add_languages = dict()

        docs = db.collection('languages').stream()
        for doc in docs:
            if not doc.id in languages:
                add_languages[doc.id] = doc.to_dict()['color']

        return render_template(
            'register.html',
            languages=languages,
            add_languages=add_languages,
        )
    elif request.method == 'POST':
        languages = {language: request.form[language]
                     for language in request.form.getlist('language')}

        session['name'] = request.form['displayname']

        session.pop('email')

        doc_ref = db.collection('users').document(request.form['username'])
        doc_ref.set({
            'name': request.form['displayname'],
            'email': request.form['email'],
            'age': int(request.form['age']),
            'image': session['image'],
            'languages': languages
        })

        return redirect(url_for('home'))


@app.route('/profile/<login>')
def profile(login):
    doc_ref = db.collection('users').document(login)
    user = doc_ref.get()
    if user.exists:
        return render_template(
            'profile.html',
            login=login,
            user=user.to_dict()
        )
    else:
        flash("That user does not exist", 'error')
        return redirect(url_for('root'))


@app.route('/network')
@connect_required
@in_database
def network():
    return render_template(
        'network.html'
    )


@app.route('/projects', methods=['GET', 'POST'])
@connect_required
@in_database
def projects():
    if request.method == 'GET':
        return render_template(
            'projects.html'
        )
    elif request.method == 'POST':
        rest_query(
            query={
                'name': request.form['name'],
                'description': request.form['description'],
                'homepage': '',
            },
            route='/user/repos',
            method='POST'
        )
        return render_template(
            'projects.html'
        )


@connect_required
@app.route('/logout')
def logout():
    '''
    logs out user by deleting info from the session
    '''
    session.pop('login')
    session.pop('name')
    session.pop('access_token')
    session.pop('image')
    return redirect(url_for('root'))


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


if __name__ == "__main__":
    # db.init_app(app)
    # with app.app_context():
    #     db.create_all()
    app.debug = True
    app.run()
