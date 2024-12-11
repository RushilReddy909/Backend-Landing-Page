from datetime import timedelta
import os
from flask import Flask, render_template, session, request, redirect, flash, get_flashed_messages, url_for
from dotenv import load_dotenv
from pymongo import MongoClient
from helper import check_email, login_required
from bson import ObjectId

load_dotenv() #Load all .env variables

#Flask initialization and Session setup
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.permanent_session_lifetime = timedelta(hours=1)

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URL'))
users = client["users"]

#Routing for all destinations
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        details = users['details']

        #Validation TODO
           

        #Update to Database
        data = {
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
        }

        details.insert_one(data)

    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cpassword = request.form["cpassword"]

        login_info = users['login_info']
        #Validation


        #Add to Database
        data = {
            'username': username,
            'password': password,
        }

        login_info.insert_one(data)
        return redirect(url_for('login'))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        login_info = users["login_info"]
        data = login_info.find_one({
            'username': username,
            'password': password,
        })
        #Validation


        #Add Session
        session['id'] = str(data['_id'])
        return redirect(url_for('index'))

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)