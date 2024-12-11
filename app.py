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
    permissions = users['permissions']

    if request.method == "POST":
        if request.form["form-type"] == "modal-form":
            perms = permissions.find_one({
                '_id': ObjectId(session['id'])
            })

            check_email = True if "check-email" in request.form and request.form["check-email"] == 'yes' else False
            check_phone = True if "check-phone" in request.form and request.form["check-phone"] == 'yes' else False
            check_address = True if "check-address" in request.form and request.form["check-address"] == 'yes' else False


            updated_data = {
                '$set': {
                    'email': check_email,
                    'phone': check_phone,
                    'address': check_address,
                    'first': False,
                }
            }

            permissions.update_one(
                {'_id': ObjectId(session['id'])},
                updated_data,
            )

        elif request.form["form-type"] == "normal-form":  
            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            address = request.form["address"]

            details = users['details']

            #Validation TODO
            

            #Update to Database
            perms = permissions.find_one({
                '_id': ObjectId(session['id'])
            })

            data = {
                '_id': ObjectId(session['id']),
                'name': name,
                'email': email if perms['email'] else None,
                'phone': phone if perms['phone'] else None,
                'address': address if perms['address'] else None,
            }

            details.insert_one(data)
            return redirect(url_for('index'))

    perms = permissions.find_one({
        '_id': ObjectId(session['id'])
    })

    showModal = False
    if perms['first']:
        showModal = True
    return render_template("index.html", showModal=showModal)

@app.route("/register", methods=["GET", "POST"])
def register():
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

        #Set Permissions
        
        #Set Default Perms
        perms = {
            '_id': ObjectId(session['id']),
            'email': False,
            'phone': False,
            'address': False,
            'first': True,
        }

        permissions = users['permissions']
        permissions.insert_one(perms)

        return redirect(url_for('login'))

    return render_template("register.html")

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

@app.route("/logout")
@login_required
def logout():
    session.pop('id')
    return redirect(url_for('login'))

@app.route("/permissions", methods=["GET", "POST"])
@login_required
def permissions():
    return redirect(url_for('permissions'))

if __name__ == "__main__":
    app.run(debug=True)