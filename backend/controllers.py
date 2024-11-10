# Controllers
from flask import Flask, render_template, redirect, request, send_file, url_for
from flask import current_app as app
from .models import *
from io import BytesIO
from sqlalchemy import or_

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
        if usr1:
            usr = usr1
        elif usr2: 
            usr = usr2
        else:
            return render_template('login.html', msg='Inavlid credentials entered!')
        uname = usr.name
    
        if usr.role == 0: # if user is admin
            #### ADMIN DASHBOARD ####
            return redirect(url_for('admin_dashboard', uname = uname))
        
        elif usr and usr.role == 1: #if user exists
            return redirect(url_for('customer_dashboard', uname = uname, uid = usr.id))
        elif usr and usr.role == 2: #if service professional exists 
            if usr.status == 'Registered': # if service professional is in verification stage
                return render_template ('login.html', msg = 'Verification is in progress. You can login only after verification')
            elif usr.status == 'Rejected':
                return render_template ('login.html', msg = 'Your registration is rejected by the admin. Please register again if needed.')
            else: # if service professional is in active or flagged or blocked stage
                return redirect(url_for('sp_dashboard', uname = uname))     
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
        
        
    return render_template("customer_signup.html", action = 'signup')

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
        avg_time = request.form.get('avg_time') or None
        description = request.form.get('description') or None
        exp_since = request.form.get('exp_since') or None
        service_id = Service.query.filter_by(name = service_name).first().id

        ### TO BE CHECKED ON THE EXACT VALIDATION
        # if (uname != '' or pwd != '' or full_name !='' or address != '' or pin_code != int('')):
            #Cheking if user already exists
        usr = Service_professional.query.filter_by(email = uemail).first()
        if usr:
            services = Service.query.all()
            # service_professionals = Service_professional.query.all()   
            return render_template("sp_registration.html", services = services, msg='User with entered email ID already exists!')
        elif (uemail == None or pwd == None or name == None or location == None or pin_code == None or contact_number == None or 
              price == None or avg_time == None or description == None or sp_doc == None or exp_since == None or service_name == None): # sp_doc == None 
            
            services = Service.query.all()
            # service_professionals = Service_professional.query.all()   
            return render_template("sp_registration.html", services = services, msg='Please enter valid details.')
        else:
            # If user is new and to push all this data, we need to create a new_usr object
            new_usr = Service_professional(email = uemail, password = pwd, name = name, location=location, pin_code = pin_code, 
                                           contact_number = contact_number, service_name = service_name, price = price, description = description, exp_since = exp_since,
                                           service_id = service_id,avg_time = avg_time, doc_name = sp_doc.filename, doc_data = sp_doc.read()) # doc_name = sp_doc.filename, doc_data = sp_doc.read()
                                           
            db.session.add(new_usr)
            db.session.commit()
            
            return render_template('login.html', msg='Registration request is submitted! Please try logging in after verification.')

    services = Service.query.all()
    # service_professionals = Service_professional.query.all()   
    return render_template("sp_registration.html", services = services)

#### ADMIN DASHBOARD ####
@app.route("/admin/<uname>")
def admin_dashboard(uname):
    services = Service.query.all()
    service_professionals1 = Service_professional.query.filter_by(status = 'Registered').all()
    service_professionals2 = Service_professional.query.filter_by(status = 'Rejected').all()
    service_professionals = service_professionals1 + service_professionals2
    # service_professionals = Service_professional.query(uname).filter(or_(status = 0, status = 1)).all()
    service_requests = Service_request.query.all()
    return render_template('admin_dashboard.html', services=services, service_professionals = service_professionals, service_requests=service_requests, uname = uname)


@app.route("/admin/service/add/<uname>", methods= ['GET', 'POST'])
def add_service(uname):
    if request.method == 'POST':
        name = request.form.get('name') 
        base_price = request.form.get('base_price')
        avg_time_req = request.form.get('avg_time_req') 
        description = request.form.get('description') 

        new_service = Service(name = name, base_price=base_price, avg_time_req=avg_time_req,description=description)
        db.session.add(new_service)
        db.session.commit()
       
        #### ADMIN DASHBOARD ####
        return redirect(url_for('admin_dashboard', uname=uname))

    else:
       return render_template("add_update_service.html", description = "What is the service about?", service_name = 'Service Name',
                              base_price = 'Base Price (in INR)', time_req = 'Average time required (in hours)', heading = 'Add new service',
                              action='Add Service', uname = uname)

# DELETING SERVICE FROM DB
@app.route("/admin/service/delete/<service_id>/<uname>", methods= ['GET', 'POST'])
def del_service(service_id, uname):
    service = Service.query.filter_by(id = service_id).first()
    db.session.delete(service)
    db.session.commit()
    #### ADMIN DASHBOARD ####
    return redirect(url_for('admin_dashboard', uname=uname))

# UPDATING SERVICE FROM DB
@app.route("/admin/service/update/<service_id>/<uname>", methods= ['GET', 'POST'])
def update_service(service_id, uname):
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
        return redirect(url_for('admin_dashboard', uname=uname))
    
    else:
        service = Service.query.filter_by(id = service_id).first()
        return render_template ('add_update_service.html', heading = 'Update an existing service', service = service,
                                action = 'Update Service', uname=uname)


@app.route("/admin/sp_details/<sp_id>/<uname>")
def sp_details(sp_id, uname):
    sp = Service_professional.query.filter_by(id = sp_id).first()
    return render_template('sp_details.html',sp=sp, uname=uname)

@app.route("/admin/customer_details/<customer_id>/<uname>")
def customer_details(customer_id, uname):
    customer = Customer.query.filter_by(id = customer_id).first()
    return render_template('customer_details.html',customer=customer, uname=uname)

@app.route("/admin/sr_details/<sr_id>/<uname>")
def sr_details(sr_id, uname):
    sr = Service_request.query.filter_by(id = sr_id).first()
    return render_template('request_details.html',sr=sr, uname=uname)

@app.route("/admin/download/document/<sp_id>/<uname>", methods= ['GET', 'POST'])
def download_sp_doc(sp_id, uname):
    sp = Service_professional.query.filter_by(id = sp_id).first()
    return send_file(BytesIO(sp.doc_data), download_name = sp.doc_name, as_attachment=True)

@app.route("/admin/service_professional/accept/<sp_id>/<uname>", methods= ['GET', 'POST'])
def sp_accept(acc_rej, sp_id, uname):
    sp = Service_professional.query.filter_by(id = sp_id).first()
    sp.status = 'Active'
    db.session.commit()
    #### ADMIN DASHBOARD ####
    return redirect(url_for('admin_dashboard', uname=uname))
    

@app.route("/admin/service_professional/reject/<sp_id>/<uname>", methods= ['GET', 'POST'])
def sp_reject(sp_id, uname):
    sp = Service_professional.query.filter_by(id = sp_id).first()
    sp.status = 'Rejected'
    db.session.commit()
    #### ADMIN DASHBOARD ####
    return redirect(url_for('admin_dashboard', uname=uname))

@app.route("/admin/search/<uname>",  methods= ['GET', 'POST'])
def admin_search(uname):
    if request.method == 'POST':
        search_by = request.form.get('search_by') or None
        search_txt = request.form.get('search_txt')
        if search_by == 'service':
            if search_txt == '':
                services = Service.query.all()
                return render_template('admin_search.html',search = 'service', services = services, uname=uname)
            else:
                service_name = search_by_name(search_by, search_txt)
                return render_template('admin_search.html',search = 'service', services = service_name, uname=uname)
        elif search_by == 'request':
            if search_txt == '':
                service_requests = Service_request.query.all()
                return render_template('admin_search.html',search = 'request', service_requests = service_requests, uname=uname)
            else:
                request_status = search_by_status(search_by, search_txt)
                if request_status:
                    return render_template('admin_search.html',search = 'request', service_requests = request_status, uname=uname)
        
        elif search_by == 'sp':
            if search_txt == '':
                service_professionals = Service_professional.query.all()
                return render_template('admin_search.html',search = 'sp', service_professionals = service_professionals, uname=uname)
            else:
                sp_name = search_by_name(search_by, search_txt)
                sp_location = search_by_location(search_by, search_txt)
                sp_pin = search_by_pincode(search_by, search_txt)
                sp_status = search_by_status(search_by, search_txt)
                if sp_name:
                    return render_template('admin_search.html',search = 'sp', service_professionals = sp_name, uname=uname)
                elif sp_location:
                    return render_template('admin_search.html',search = 'sp', service_professionals = sp_location, uname=uname)
                elif sp_pin:
                    return render_template('admin_search.html',search = 'sp', service_professionals = sp_pin, uname=uname)
                elif sp_status:
                    return render_template('admin_search.html',search = 'sp', service_professionals = sp_status, uname=uname)
        
        
        elif search_by == 'customer':
            if search_txt == '':
                customers = Customer.query.all()
                return render_template('admin_search.html',search = 'customer', customers = customers, uname=uname)
            else:
                customer_name = search_by_name(search_by, search_txt)
                customer_location = search_by_location(search_by, search_txt)
                customer_pin = search_by_pincode(search_by, search_txt)
                customer_status = search_by_status(search_by, search_txt)
                if customer_name:
                    return render_template('admin_search.html',search = 'customer', customers = customer_name, uname=uname)
                elif customer_location:
                    return render_template('admin_search.html',search = 'customer', customers = customer_location, uname=uname)
                elif customer_pin:
                    return render_template('admin_search.html',search = 'customer', customers = customer_pin, uname=uname)
                elif customer_status:
                    return render_template('admin_search.html',search = 'customer', customers = customer_status, uname=uname)
            
        else:
            return redirect(url_for('admin_dashboard', uname=uname))
    
    return redirect(url_for('admin_dashboard', uname=uname))



# Other supported functions
def search_by_name(search_by, search_txt):
    if search_by == 'service':
        services = Service.query.filter(Service.name.ilike(f"%{search_txt}%")).all()
        return services
    # if search_by == 'request':
    #     # requests = Service_request.query.filter(service_request.service.name.ilike(f"%{search_txt}%")).all()
    #     requests = Service.query.filter(Service.name.ilike(f"%{search_txt}%")).all()
    #     return requests
    if search_by == 'sp':
        sp = Service_professional.query.filter(Service_professional.name.ilike(f"%{search_txt}%")).all()
        return sp
    if search_by == 'customer':
        customer = Customer.query.filter(Customer.name.ilike(f"%{search_txt}%")).all()
        return customer

def search_by_location(search_by, search_txt):
    # if search_by == 'request':
    #     requests = Service_request.query.filter(Service_request.customer.location.ilike(f"%{search_txt}%")).all()
    #     return requests
    if search_by == 'sp':
        sp = Service_professional.query.filter(Service_professional.location.ilike(f"%{search_txt}%")).all()
        return sp
    if search_by == 'customer':
        customer = Customer.query.filter(Customer.location.ilike(f"%{search_txt}%")).all()
        return customer

def search_by_pincode(search_by, search_txt):
    # if search_by == 'request':
    #     requests = Service_request.query.filter(Service_request.customer.pin_code.ilike(f"%{search_txt}%")).all()
    #     return requests
    if search_by == 'sp':
        sp = Service_professional.query.filter(Service_professional.pin_code.ilike(f"%{search_txt}%")).all()
        return sp
    if search_by == 'customer':
        customer = Customer.query.filter(Customer.pin_code.ilike(f"%{search_txt}%")).all()
        return customer

def search_by_status(search_by, search_txt):
    if search_by == 'request':
        requests = Service_request.query.filter(Service_request.status.ilike(f"%{search_txt}%")).all()
        return requests
    if search_by == 'sp':
        sp = Service_professional.query.filter(Service_professional.status.ilike(f"%{search_txt}%")).all()
        return sp
    if search_by == 'customer':
        customer = Customer.query.filter(Customer.status.ilike(f"%{search_txt}%")).all()
        return customer
    
#### CUSTOMER CONTROLS ########
#### USER DASHBOARD ####
@app.route("/customer/<uid>/<uname>")
def customer_dashboard(uname, uid):
    services = Service.query.all()
    customer = Customer.query.filter_by(id = uid).first()
    return render_template('customer_dashboard.html', services=services, uname = uname, uid = uid, customer = customer)

@app.route("/customer/profile/update/<uid>/<uname>", methods = ['GET', 'POST'])
def update_customer_profile(uname, uid):
    customer = Customer.query.filter_by(id = uid).first()
    if request.method == 'POST':
        updated_name = request.form.get('name') 
        updated_password = request.form.get('password')
        updated_location = request.form.get('location') 
        updated_pin_code = request.form.get('pin_code') 
        updated_contact_number = request.form.get('contact_number') 

        updated = Customer.query.filter_by(id = uid).first()
        updated.name = updated_name
        updated.password = updated_password
        updated.location = updated_location
        updated.pin_code = updated_pin_code
        updated.contact_number = updated_contact_number

        db.session.commit()
        #### ADMIN DASHBOARD ####
        return redirect(url_for('customer_dashboard', uname=updated.name, uid=uid))

    return render_template('customer_signup.html', uname = uname, uid = uid, customer = customer, action = 'update_profile')


#### SP DASHBOARD ####
@app.route("/sp/<uname>")
def sp_dashboard(uname):
    
    return render_template('sp_dashboard.html', uname = uname)