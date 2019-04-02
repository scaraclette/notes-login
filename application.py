# Notes with login form

import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

notes = []

@app.route("/", methods=["POST", "GET"])
def index():
    
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if db.execute("SELECT * FROM user_test WHERE user_name = :username AND user_password = :password", {"username": username, "password": password}).rowcount != 0:
            current_user = db.execute("SELECT * FROM user_test WHERE user_name = :username AND user_password = :password", {"username": username, "password": password}).fetchone()
            # Set session
            session["notes"] = current_user.id
            # TODO create note page
            
            return render_template("notes.html", notes=session["notes"])
        
        session.pop("notes", None)
        return render_template("error.html")

    # Default at GET method
    session.pop("notes", None)
    return render_template("index.html")

@app.route("/add-note", methods=["POST", "GET"])
def add_note():
    if request.method == "POST":
        note = request.form.get("note")
        session["notes"].append(note)
        
    # TODO potentially change notes = session
    return render_template("notes.html", notes=session["notes"])
