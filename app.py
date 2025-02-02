import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/", methods = ["GET", "POST"])
def index():
    error_message = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT password_hash FROM users WHERE username = ?"
        password_hash = db.query(sql, [username])
        
        if not password_hash:
            error_message = "Invalid username or password"
        else:
            password_hash = password_hash[0][0]
            if check_password_hash(password_hash, password):
                session["username"] = username
                return redirect("/pdm")
            else:
                error_message = "Invalid username or password"

    return render_template("index.html", error_message=error_message)

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        error_message = None
        success_message = None
        if len(password1) < 4:
            error_message = "Password must be at least 4 characters long"
        elif password1 != password2:
            error_message = "Passwords do not match"
        elif len(username) < 4:
            error_message = "Username must be at least 4 characters long"
        else:
            password_hash = generate_password_hash(password1)
            try:
                sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
                db.execute(sql, [username, password_hash])
                success_message = "Account created successfully"
            except sqlite3.IntegrityError:
                error_message = "Username is already in use"
            
        return render_template("register.html", error_message=error_message, success_message=success_message)
    else:
        return render_template("register.html")
    
@app.route("/pdm")
def pdm():
    if not session.get("username"):
        return redirect("/")
    else:
        return render_template("pdm.html")
