from datetime import timedelta
import os
from flask import Flask, jsonify, render_template, session, request, redirect, flash, get_flashed_messages, url_for
from dotenv import load_dotenv
from pymongo import MongoClient
from helper import login_required, admin_required
from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash

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

            return redirect(url_for('index'))

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

            details.update_one(
            {'_id': ObjectId(session['id'])},
            {
                '$set': {
                    'name': name,
                    'email': email if perms['email'] else None,
                    'phone': phone if perms['phone'] else None,
                    'address': address if perms['address'] else None,
                }
            },
            upsert=True  # If no document matches, create a new one
        )
            
        return redirect(url_for('index'))

    perms = permissions.find_one({
        '_id': ObjectId(session['id'])
    })

    showModal = False
    if perms['first']:
        showModal = True
    return render_template("index.html", showModal=showModal, perms=perms)

@app.route("/register", methods=["GET", "POST"])
def register():
    if 'id' in session:
        return redirect(url_for('index'))

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
            'role': "user",
        }

        login_info.insert_one(data)
        temp = login_info.find_one(data)

        #Set Default Perms
        perms = {
            '_id': temp['_id'],
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
    if 'id' in session:
        return redirect(url_for('index'))

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

@app.route("/permissions", methods=["GET"])
@login_required
def permissions():
    perms = users['permissions'].find_one({"_id": ObjectId(session["id"])})

    return render_template('permissions.html', perms=perms)

@app.route("/update_perm", methods=["POST"])
@login_required
def update_perm():
    try:
        #Validation of post request
        if "field" not in request.form or "action" not in request.form:
            return jsonify(success=False, message="Missing required parameters"), 400

        user_id = ObjectId(session["id"])
        field = request.form["field"]
        action = request.form["action"]

        if action == "revoke":
            # Update permissions
            users["permissions"].update_one(
                {"_id": user_id},
                {"$set": {field: False}}
            )

            # Update details
            users["details"].update_one(
                {"_id": user_id},
                {"$set": {field: None}}
            )

            return jsonify(success=True), 200
        elif action == "grant":
            if "value" not in request.form:
                return jsonify(success=False, message="Missing Parameters"), 400
            
            value = request.form["value"]

            #Validation of field

            users["permissions"].update_one(
                {"_id": user_id},
                {'$set': {field: True}},
            )

            users["details"].update_one(
                {"_id": user_id},
                {'$set': {field: value}}
            )

            return jsonify(success=True), 200

        else:
            return jsonify(success=False, message="Invalid action"), 400
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    
@app.route('/admin')
@admin_required
def admin():
    details = users['details']

    table_data = list(details.find({}, {'name': 1, 'email': 1, 'phone': 1, 'address': 1}))
    return render_template('admin.html', table_data=table_data, len=len(table_data))

if __name__ == "__main__":
    app.run(debug=True)