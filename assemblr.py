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
        title= "Landing"
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0')
