# Controllers
from flask import Flask, render_template, redirect, request, send_file
from flask import current_app as app
from .models import *
from io import BytesIO

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
            
            #### ADMIN DASHBOARD ####
            services = Service.query.all()
            service_professionals = Service_professional.query.all()
            return render_template ('admin_dashboard.html', services=services, service_professionals = service_professionals)
        
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
            services = Service.query.all()
            service_professionals = Service_professional.query.all()   
            return render_template("sp_registration.html", services = services, msg='User with entered email ID already exists!')
        elif (uemail == None or pwd == None or name == None or location == None or pin_code == None or contact_number == None or 
              price == None or description == None or sp_doc == None or exp_since == None or service_name == None): # sp_doc == None 
            
            services = Service.query.all()
            service_professionals = Service_professional.query.all()   
            return render_template("sp_registration.html", services = services, msg='Please enter valid details.')
          
        else:
            # If user is new and to push all this data, we need to create a new_usr object
            new_usr = Service_professional(email = uemail, password = pwd, name = name, location=location, pin_code = pin_code, 
                                           contact_number = contact_number, service_name = service_name, price = price, description = description, exp_since = exp_since,
                                           service_id = service_id, doc_name = sp_doc.filename, doc_data = sp_doc.read()) # doc_name = sp_doc.filename, doc_data = sp_doc.read()
                                           
            db.session.add(new_usr)
            db.session.commit()
            
            return render_template('login.html', msg='Registration request is submitted! Please try logging in after verification.')

    services = Service.query.all()
    service_professionals = Service_professional.query.all()   
    return render_template("sp_registration.html", services = services)

@app.route("/add/service/", methods= ['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        name = request.form.get('name') 
        base_price = request.form.get('base_price')
        avg_time_req = request.form.get('avg_time_req') 
        description = request.form.get('description') 

        new_service = Service(name = name, base_price=base_price, avg_time_req=avg_time_req,description=description)
        db.session.add(new_service)
        db.session.commit()
        #### ADMIN DASHBOARD ####
        services = Service.query.all()
        service_professionals = Service_professional.query.all()
        return render_template ('admin_dashboard.html', services=services, service_professionals = service_professionals)

    else:
       return render_template("add_update_service.html", description = "What is the service about?", service_name = 'Service Name',
                              base_price = 'Base Price (in INR)', time_req = 'Average time required (in hours)', heading = 'Add new service',
                              action='Add Service')

@app.route("/service/delete/<service_id>", methods= ['GET', 'POST'])
def del_service(service_id):
    service = Service.query.filter_by(id = service_id).first()
    db.session.delete(service)
    db.session.commit()
    #### ADMIN DASHBOARD ####
    services = Service.query.all()
    service_professionals = Service_professional.query.all()
    return render_template ('admin_dashboard.html', services=services, service_professionals = service_professionals)

@app.route("/service/update/<service_id>", methods= ['GET', 'POST'])
def update_service(service_id):
    if request.method == 'POST':
        updated_name = request.form.get('name') 
        updated_base_price = request.form.get('base_price')
        updated_avg_time_req = request.form.get('avg_time_req') 
        updated_description = request.form.get('description') 

        updated_service = service = Service.query.filter_by(id = service_id).first()
        updated_service.name = updated_name
        updated_service.base_price = updated_base_price
        updated_service.avg_time_req = updated_avg_time_req
        updated_service.description = updated_description
        db.session.commit()
        #### ADMIN DASHBOARD ####
        services = Service.query.all()
        service_professionals = Service_professional.query.all()
        return render_template ('admin_dashboard.html', services=services, service_professionals = service_professionals)
    
    else:
        service = Service.query.filter_by(id = service_id).first()
        return render_template ('add_update_service.html', heading = 'Update an existing service', description=service.description,
                                service_name = service.name, base_price = service.base_price, time_req = service.avg_time_req,
                                action = 'Update details')

@app.route("/admin_dashboard", methods= ['GET', 'POST'])
def add_update_cancel():
    #### ADMIN DASHBOARD ####
    services = Service.query.all()
    service_professionals = Service_professional.query.all()
    return render_template ('admin_dashboard.html', services=services, service_professionals = service_professionals)

@app.route("/download/document/<sp_id>", methods= ['GET', 'POST'])
def download_sp_doc(sp_id):
    sp = Service_professional.query.filter_by(id = sp_id).first()
    return send_file(BytesIO(sp.doc_data), download_name = sp.doc_name, as_attachment=True) 

