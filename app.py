from datetime import timedelta
import os
from flask import Flask, jsonify, render_template, session, request, redirect, flash, get_flashed_messages, url_for
from dotenv import load_dotenv
from pymongo import MongoClient
from helper import login_required, admin_required, is_valid_email, get_client_ip
from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

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
            perms = permissions.find_one({
                '_id': ObjectId(session['id'])
            })

            if perms['email'] and not is_valid_email(email):
                flash("Invalid email provided", "danger")
                return redirect(url_for('index'))
            
            if perms['phone'] and (len(phone) != 10 or not phone.isdigit()):
                flash("Invalid phone number provided", "danger")
                return redirect(url_for('index'))
            
            if perms['address'] and len(address.strip()) <= 0:
                flash("Invalid addredd provided.", "danger")
                return redirect(url_for('index'))

            #Update to Database
            details.update_one(
            {'_id': ObjectId(session['id'])},
            {
                '$set': {
                    'name': name,
                    'email': email if perms['email'] else None,
                    'phone': phone if perms['phone'] else None,
                    'address': address if perms['address'] else None,
                    'time': datetime.now(),
                    'ip': request.remote_addr if request.remote_addr else get_client_ip(),
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
        if not username or not password or not cpassword:
            flash("All fields are required.", "danger")
            return redirect(url_for('register'))
        
        if len(username) != 12 or not username.isdigit():
            flash("Aadhar must be 12 digits", "danger")
            return redirect(url_for('register'))
        
        if len(password) < 3:
            flash("Password must be atleast 3 characters long.", "danger")
            return redirect(url_for('register'))
        
        if password != cpassword:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('register'))
        
        if login_info.find_one({'username': username}):
            flash("Account already exists, please login.", "danger")
            return redirect(url_for('register'))

        #Add to Database
        data = {
            'username': username,
            'password': generate_password_hash(password),
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

        flash("Successfully Registered, now please login.", "success")
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
        #Validation
        if len(username) != 12 or not username.isdigit():
            flash("Invalid Aadhar Number.", "danger")
            return redirect(url_for('login'))
        
        if len(password) < 3:
            flash("Password must be atleast 3 characters.", "danger")
            return redirect(url_for('login'))
        
        data = login_info.find_one({
            'username': username,
        })

        if not data:
            flash("Error retrieving account or does not exist", "danger")
            return redirect(url_for('login'))
        
        if not check_password_hash(data['password'], password):
            flash("Incorrect Password", "danger")
            return redirect(url_for('login'))

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
            if not value or not value.strip():
                return jsonify(success=False, message="Provide a valid value"), 400
            
            if field == 'email' and not is_valid_email(value):
                return jsonify(success=False, message="Invalid Email provided"), 400
            
            if field == 'phone' and (len(value) != 10 or not value.isdigit()):
                return jsonify(success=False, message="Invalid Phone number provided"), 400

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
    
@app.route('/admin', methods=["GET", "POST"])
@admin_required
def admin():
    details = users['details']
    fields = ['ip', 'name', 'time', 'email', 'phone', 'address']
    filters = {field: 1 for field in fields}

    #Implement Filters
    if request.method == "POST":
        filters.clear()
        for field, value in request.form.items():
            field = field.split('-')[0]
            if value == "yes":
                filters[field] = 1

    table_data = list(details.find({}, filters))
    return render_template('admin.html', table_data=table_data, len=len(table_data), filters=filters)

if __name__ == "__main__":
    app.run(debug=True)