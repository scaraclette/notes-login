''' 
    NOTES WITH LOGIN FORM
    Done but lacks storing notes to database functionality. Is that possible without ORM? Want to ideally store reviews in database so other users can see but for now stick with requirements of user not being able to comment on the same book.
'''

import os

from flask import Flask, session, render_template, request, url_for, redirect
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
user_id = 0

# TODO: can just direct to login page
# @app.route("/")
# def index():
#     return render_template("index.html")

@app.route("/", methods=["POST", "GET"])
def index():
    global user_id

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if db.execute("SELECT * FROM user_test WHERE user_name = :username AND user_password = :password", {"username": username, "password": password}).rowcount != 0:
            current_user = db.execute("SELECT * FROM user_test WHERE user_name = :username AND user_password = :password", {"username": username, "password": password}).fetchone()
            # Set session
            user_id = current_user.id
            session[current_user.id] = []
            # TODO create note page
            return render_template("notes.html", notes=session[current_user.id])
                
        return render_template("error.html")

    # Default at GET method
    session.pop(user_id, None)
    return render_template("index.html")

# Sign up method -> do not allow same user
@app.route("/signup", methods=["POST", "GET"])
def signup():

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if db.execute("SELECT * FROM user_test WHERE user_name = :username", {"username": username}).rowcount != 0:
            # Username already exists, go to error page with different message
            return render_template("username-taken.html")

        #commit to DB, send to success page TODO
        db.execute("INSERT INTO user_test (user_name, user_password) VALUES (:username, :password)", {"username":username, "password":password})
        db.commit()
        return render_template("success.html")

    # Default GET method goes to signup page
    return render_template("signup.html")

@app.route("/add-note", methods=["POST", "GET"])
def add_note():
    global user_id

    if request.method == "POST":
        note = request.form.get("note")
        session[user_id].append(note)
        
    return render_template("notes.html", notes=session[user_id])

@app.route("/logout")
def logout():
    global user_id
    session.pop(user_id, None)
    return redirect(url_for('index'))