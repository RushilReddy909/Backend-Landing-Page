from datetime import timedelta
import os
from flask import Flask, render_template, session, request, redirect
from dotenv import load_dotenv

load_dotenv() #Load all .env variables

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.permanent_session_lifetime = timedelta(hours=1)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        #Validation TODO

        #Update to Database

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)