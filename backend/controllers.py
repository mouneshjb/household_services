# Controllers
from flask import Flask, render_template, redirect, request
from flask import current_app as app
from .models import *

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login", methods= ['GET', 'POST'])
def login():
    if request.method == 'POST':
        uemail = request.form.get('email')
        pwd = request.form.get('password')
        usr1 = Customer.query.filter_by(email = uemail, password = pwd).first()
        usr2 = Service_professional.query.filter_by(email = uemail, password = pwd).first()
        if usr1 == None:
            usr = usr2
        else: 
            usr = usr1
        if usr.role == 0: # if user is admin 
            return render_template ('admin_dashboard.html')
        elif usr and usr.role == 1: #if user exists
            return render_template ('user_dashboard.html')
        elif usr and usr.role == 2: #if service professional exists 
            if usr.status == 0: # if service professional is in verification stage
                return render_template ('login.html', msg = 'Verification is in progress. You can login only after verification')
            else: # if service professional is in active (1) or blocked (2) stage
                return render_template ('sp_dashboard.html')     
        else:
            return render_template('login.html', msg='Inavlid credentials entered!')

    return render_template('login.html', msg='')

@app.route("/signup", methods= ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        uemail = request.form.get('email') or None
        pwd = request.form.get('password') or None
        name = request.form.get('name') or None
        location = request.form.get('location') or None
        pin_code = request.form.get('pin_code') or None
        contact_number = request.form.get('contact_number') or None
        
        ### TO BE CHECKED ON THE EXACT VALIDATION
        # if (uname != '' or pwd != '' or full_name !='' or address != '' or pin_code != int('')):
            #Cheking if user already exists
        usr = Customer.query.filter_by(email = uemail).first()
        if usr:
            return render_template('signup.html', msg='User with entered email ID already exists!')
        elif (uemail == None or pwd == None or name == None or location == None or pin_code == None or contact_number == None):
            return render_template('signup.html', msg='Please enter valid details.')
        else:
            # If user is new and to push all this data, we need to create a new_usr object
            new_usr = Customer(email = uemail, password = pwd, name = name, location=location, pin_code = pin_code, 
                               contact_number = contact_number)
            db.session.add(new_usr)
            db.session.commit()
            
            return render_template('login.html', msg='Signup Successful! Please try log in now.')
        
        
    return render_template("user_signup.html")

@app.route("/register", methods= ['GET', 'POST'])
def register():
    if request.method == 'POST':
        uemail = request.form.get('email') or None
        pwd = request.form.get('password') or None
        name = request.form.get('name') or None
        location = request.form.get('location') or None
        pin_code = request.form.get('pin_code') or None
        contact_number = request.form.get('contact_number') or None
        service_name = request.form.get('service_name') or None
        sp_doc = request.files['sp_doc'] or None
        price = request.form.get('price') or None
        description = request.form.get('description') or None
        exp_since = request.form.get('exp_since') or None
        service_id = Service.query.filter_by(name = service_name).first().id

        ### TO BE CHECKED ON THE EXACT VALIDATION
        # if (uname != '' or pwd != '' or full_name !='' or address != '' or pin_code != int('')):
            #Cheking if user already exists
        usr = Service_professional.query.filter_by(email = uemail).first()
        if usr:
            return render_template('sp_registration.html', msg='User with entered email ID already exists!')
        elif (uemail == None or pwd == None or name == None or location == None or pin_code == None or contact_number == None or 
              price == None or description == None or sp_doc == None or exp_since == None or service_name == None): # sp_doc == None 
            return render_template('sp_registration.html', msg='Please enter valid details.')
        else:
            # If user is new and to push all this data, we need to create a new_usr object
            new_usr = Service_professional(email = uemail, password = pwd, name = name, location=location, pin_code = pin_code, 
                                           contact_number = contact_number, service_name = service_name, price = price, description = description, exp_since = exp_since,
                                           service_id = service_id, doc_name = sp_doc.filename, doc_data = sp_doc.read()) # doc_name = sp_doc.filename, doc_data = sp_doc.read()
                                           
            db.session.add(new_usr)
            db.session.commit()
            
            return render_template('login.html', msg='Registration request is submitted! Please try logging in after verification.')
        
    return render_template("sp_registration.html")