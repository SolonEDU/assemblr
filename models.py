from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    city = db.Column(db.Text, nullable=False)
    bio = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<User {self.email} with id {self.id} and password {self.password}>'

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    senderid = db.Column(db.Integer, nullable=False)
    receiverid = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Request with id {self.id}, sender id {self.senderid}, receiver id {self.receiverid}>'

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, nullable=False)
    friend = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<id {self.id}, uid {self.uid}, and friend {self.friend}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    senderid = db.Column(db.Integer, nullable=False)
    receiverid = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Role(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    projectmanager = db.Column(db.Boolean, nullable=False)
    frontend = db.Column(db.Boolean, nullable=False)
    backend = db.Column(db.Boolean, nullable=False)
    design = db.Column(db.Boolean, nullable=False)

class Technology(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    git = db.Column(db.Boolean, nullable=False)
    html = db.Column(db.Boolean, nullable=False)
    css = db.Column(db.Boolean, nullable=False)
    python = db.Column(db.Boolean, nullable=False)
    javascript = db.Column(db.Boolean, nullable=False)
    sql = db.Column(db.Boolean, nullable=False)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teamid = db.Column(db.Integer, nullable=False)
    uid = db.Column(db.Integer, nullable=False)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teamname = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<id {self.id} teamname {self.teamname}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projectname = db.Column(db.String(20), nullable=False)
    teamid = db.Column(db.Integer, nullable=False)

        
