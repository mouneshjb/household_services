# Controllers
from flask import Flask, render_template, redirect, request, send_file, url_for
from flask import current_app as app
from .models import *
from io import BytesIO
from sqlalchemy import func
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt


## HOME or INDEX page##
@app.route("/")
def home():
    return render_template('index.html')

## Login Page ##
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
                return redirect(url_for('sp_dashboard', uname = uname, uid = usr.id))     
        else:
            return render_template('login.html', msg='Inavlid credentials entered!')

    return render_template('login.html', msg='')

## Service professional registration page ##
@app.route("/signup", methods= ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        uemail = request.form.get('email') or None
        pwd = request.form.get('password') or None
        name = request.form.get('name') or None
        location = request.form.get('location') or None
        pin_code = request.form.get('pin_code') or None
        contact_number = request.form.get('contact_number') or None
        
        
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
        
        
    return render_template("customer_signup.html")

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

        
        #Cheking if user already exists
        usr = Service_professional.query.filter_by(email = uemail).first()
        if usr:
            services = Service.query.all()
            # service_professionals = Service_professional.query.all()   
            return render_template("sp_registration.html", services = services, msg='User with entered email ID already exists!')
        elif (uemail == None or pwd == None or name == None or location == None or pin_code == None or contact_number == None or 
              price == None or avg_time == None or description == None or sp_doc == None or exp_since == None or service_name == None): # sp_doc == None 
            
            services = Service.query.all()  
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
    return render_template("sp_registration.html", services = services)

########################
#### ADMIN DASHBOARD ####
#########################
@app.route("/admin/<uname>")
def admin_dashboard(uname):
    services = Service.query.all()
    service_professionals1 = Service_professional.query.filter_by(status = 'Registered').all()
    service_professionals2 = Service_professional.query.filter_by(status = 'Rejected').all()
    service_professionals = service_professionals1 + service_professionals2
    
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


## SP DETAILS PAGE ##
@app.route("/admin/sp_details/<sp_id>/<uname>")
def sp_details(sp_id, uname):
    sp = Service_professional.query.filter_by(id = sp_id).first()
    return render_template('sp_details.html',sp=sp, uname=uname)

## CUSTOMER DETAILS PAGE ##
@app.route("/admin/customer_details/<customer_id>/<uname>")
def customer_details(customer_id, uname):
    customer = Customer.query.filter_by(id = customer_id).first()
    return render_template('customer_details.html',customer=customer, uname=uname)

## Changing customer status to active - unflagging or unblocking
@app.route("/admin/customer/active/<customer_id>/<uname>", methods= ['GET', 'POST'])
def admin_customer_activate(customer_id, uname):
    customer = Customer.query.filter_by(id = customer_id).first()
    customer.status = 'Active'
    db.session.commit()
    #### ADMIN DASHBOARD ####
    return redirect(url_for('admin_dashboard', uname=uname))

## Flagging customer
@app.route("/admin/customer/flag/<customer_id>/<uname>", methods= ['GET', 'POST'])
def admin_customer_flag(customer_id, uname):
    customer = Customer.query.filter_by(id = customer_id).first()
    customer.status = 'Flagged'
    db.session.commit()
    #### ADMIN DASHBOARD ####
    return redirect(url_for('admin_dashboard', uname=uname))

## Blocking customer
@app.route("/admin/customer/block/<customer_id>/<uname>", methods= ['GET', 'POST'])
def admin_customer_block(customer_id, uname):
    customer = Customer.query.filter_by(id = customer_id).first()
    customer.status = 'Blocked'
    db.session.commit()
    #### ADMIN DASHBOARD ####
    return redirect(url_for('admin_dashboard', uname=uname))

## SR details page
@app.route("/admin/sr_details/<sr_id>/<uname>")
def sr_details(sr_id, uname):
    sr = Service_request.query.filter_by(id = sr_id).first()
    return render_template('request_details.html',sr=sr, uname=uname)

## Downloading the verification document
@app.route("/admin/download/document/<sp_id>/<uname>", methods= ['GET', 'POST'])
def download_sp_doc(sp_id, uname):
    sp = Service_professional.query.filter_by(id = sp_id).first()
    return send_file(BytesIO(sp.doc_data), download_name = sp.doc_name, as_attachment=True)

## Accepting SP registration request after review 
@app.route("/admin/service_professional/accept/<sp_id>/<uname>", methods= ['GET', 'POST'])
def admin_sp_accept(sp_id, uname):
    sp = Service_professional.query.filter_by(id = sp_id).first()
    sp.status = 'Active'
    db.session.commit()
    #### ADMIN DASHBOARD ####
    return redirect(url_for('admin_dashboard', uname=uname))
    
## Rejecting SP registration request
@app.route("/admin/service_professional/reject/<sp_id>/<uname>", methods= ['GET', 'POST'])
def admin_sp_reject(sp_id, uname):
    sp = Service_professional.query.filter_by(id = sp_id).first()
    sp.status = 'Rejected'
    db.session.commit()
    #### ADMIN DASHBOARD ####
    return redirect(url_for('admin_dashboard', uname=uname))

## Blocking SP
@app.route("/admin/service_professional/block/<sp_id>/<uname>", methods= ['GET', 'POST'])
def admin_sp_block(sp_id, uname):
    sp = Service_professional.query.filter_by(id = sp_id).first()
    sp.status = 'Blocked'
    db.session.commit()
    #### ADMIN DASHBOARD ####
    return redirect(url_for('admin_dashboard', uname=uname))

### ADMIN SERACH FUNCTIONALITY ### 

@app.route("/admin/search/<uname>",  methods= ['GET', 'POST'])
def admin_search(uname):
    if request.method == 'POST':
        search_by = request.form.get('search_by') or None
        search_txt = request.form.get('search_txt')
        # Searching by service
        if search_by == 'service':
            if search_txt == '': # if nothing mentioned, show all results
                services = Service.query.all()
                return render_template('admin_search.html',search = 'service', services = services, uname=uname)
            else:
                ## SERVICE - NAME
                service_name = search_by_name(search_by, search_txt) ## SERVICE - NAME
                return render_template('admin_search.html',search = 'service', services = service_name, uname=uname)
        elif search_by == 'request': # if nothing mentioned, show all results
            if search_txt == '':
                service_requests = Service_request.query.all()
                return render_template('admin_search.html',search = 'request', service_requests = service_requests, uname=uname)
            else:
                ## REQUEST - STATUS
                request_status = search_by_status(search_by, search_txt)
                if request_status:
                    return render_template('admin_search.html',search = 'request', service_requests = request_status, uname=uname)
        
        elif search_by == 'sp': 
            if search_txt == '': # if nothing mentioned, show all results
                service_professionals = Service_professional.query.all()
                return render_template('admin_search.html',search = 'sp', service_professionals = service_professionals, uname=uname)
            else:
                ## SP - NAME or LOCATION or PINCODE or STATUS
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
            if search_txt == '': # if nothing mentioned, show all results
                customers = Customer.query.filter_by(role = 1).all()
                return render_template('admin_search.html',search = 'customer', customers = customers, uname=uname)
            else: 
                ## SP - NAME or LOCATION or PINCODE or STATUS
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

#####################
### ADMIN SUMMARY ###
#####################
@app.route("/admin/summary/<uname>",  methods= ['GET', 'POST'])
def admin_summary(uname):
    services = Service.query.all()
    
    service_names = []
    service_names_bar = []
    sr_count = []
    empty_s = []
    avg_service_rating = []
    for service in services:
        service_name = service.name
        service_id = service.id
        # Logic for pie chart - Services with at least one SR (closed or open)
        srs = Service_request.query.filter_by(service_id=service_id).all()
        
        if len(srs) != 0:
            count = len(srs)
            service_names.append(service_name)
            sr_count.append(count)
            
        else:
            # To track the services with no SRs
            empty_s.append(service_name)
        
        # Logic for bar chart - SPs with all service types of closed status
        srs_bar = Service_request.query.filter(Service_request.service_id==service_id, Service_request.status == 'Closed').all()
        if len(srs_bar) !=0:
            service_names_bar.append(service_name)
            sps = Service_professional.query.filter_by(service_id=service_id).all()
            c = 0
            sum_rating = 0
            for sp in sps:
                if sp.avg_ratings != None:
                    sum_rating += sp.avg_ratings
                    c+=1 
                    if c !=0:
                        avg_sp_rating = round((sum_rating/c),2)
                        avg_service_rating.append(avg_sp_rating)
    
    # plotting pie chart
    
    plt.clf()
    plt.pie(sr_count, labels = service_names, shadow=True, autopct='%1.1f%%')
    plt.title("Service Requests Summary")
    plt.legend(title = 'Service Name')
    plt.savefig('./static/images/admin_summary1.jpeg')
    

#### Main thread error - the plot jus being developed from the system and not from the app, it is breeaking the context that the flask
# has set in, it is generating from the server machine not from  the client side
    # plotting histogram
    x = service_names_bar
    y = avg_service_rating
    plt.clf()
    plt.bar(x, y, color='blue', width=0.5)
    plt.title("Average Ratings of Service Professionals")
    plt.xlabel("Services")
    plt.ylabel("Average Ratings")
    plt.savefig('static/images/admin_summary2.jpeg')
    
    return render_template('admin_summary.html', empty_s = empty_s, uname = uname)

# Other supported functions
# NAME and other attribute (service/ SP / customer )
def search_by_name(search_by, search_txt): 
    if search_by == 'service':
        services = Service.query.filter(Service.name.ilike(f"%{search_txt}%")).all()
        return services
   
    if search_by == 'sp':
        sp = Service_professional.query.filter(Service_professional.name.ilike(f"%{search_txt}%")).all()
        return sp
    if search_by == 'customer':
        customer = Customer.query.filter(Customer.name.ilike(f"%{search_txt}%")).all()
        return customer

# LOCATION and other attribute (service/ SP / customer )
def search_by_location(search_by, search_txt): 
    
    if search_by == 'sp':
        sp = Service_professional.query.filter(Service_professional.location.ilike(f"%{search_txt}%")).all()
        return sp
    if search_by == 'customer':
        customer = Customer.query.filter(Customer.location.ilike(f"%{search_txt}%")).all()
        return customer

# PINCODE and other attribute (service/ SP / customer )
def search_by_pincode(search_by, search_txt): 
    
    if search_by == 'sp':
        sp = Service_professional.query.filter(Service_professional.pin_code.ilike(f"%{search_txt}%")).all()
        return sp
    if search_by == 'customer':
        customer = Customer.query.filter(Customer.pin_code.ilike(f"%{search_txt}%")).all()
        return customer

# STATUS and other attribute (service/ SP / customer )
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

############################
#### CUSTOMER DASHBOARD ####
############################
@app.route("/customer/<uid>/<uname>")
def customer_dashboard(uname, uid):
    services = Service.query.all()
    customer = Customer.query.filter_by(id = uid).first()
    service_requests = Service_request.query.filter_by(customer_id = uid).all()
   
    return render_template('customer_dashboard.html', services=services, service_requests = service_requests, uname = uname, uid = uid, customer = customer, action  = 'no_show')

# Updating profile
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

    return render_template('customer_profile_update.html', uname = uname, uid = uid, customer = customer)

@app.route("/customer/show/<service_id>/service_professionals/<uid>/<uname>")
def dashboard_services(service_id, uname, uid):
    service = Service.query.filter_by(id = service_id).first()
    service_professionals = Service_professional.query.filter_by(service_id = service_id, status = 'Active').all() + Service_professional.query.filter_by(service_id = service_id, status = 'Flagged').all()
    service_requests = Service_request.query.filter_by(customer_id = uid).all()
    return render_template('customer_dashboard.html', uname = uname, uid = uid, service = service, service_requests = service_requests, service_professionals = service_professionals, action = 'show')

# Raise new SR
@app.route("/customer/raise_sr/<service_id>/<sp_id>/<uid>/<uname>", methods = ['GET', 'POST'])
def raise_sr(service_id, sp_id, uname, uid):
    service = Service.query.filter_by(id = service_id).first()
    if request.method == 'POST':
        customer_id = uid
        sp_id = sp_id
        service_id = service.id
        remarks = request.form.get('remarks')
        
        

        raw_date_of_schedule = request.form.get('date_of_schedule')
        # Processing datetime
        date_of_schedule = datetime.strptime(raw_date_of_schedule, "%Y-%m-%dT%H:%M")
    
        new_sr = Service_request(customer_id = customer_id, sp_id = sp_id, service_id = service_id, remarks = remarks, date_of_schedule = date_of_schedule)
        db.session.add(new_sr)
        db.session.commit()
        

        return redirect(url_for('customer_dashboard', uid = uid, uname = uname))

    return render_template('sr_form.html', service = service, sp_id = sp_id, uname = uname, uid = uid)

# Update an existing SR
@app.route("/customer/update_sr/<sr_id>/<uid>/<uname>", methods = ['GET', 'POST'])
def update_sr(sr_id, uname, uid):
    sr = Service_request.query.filter_by(id = sr_id).first()
    if request.method == 'POST':
        customer_id = uid
        sr.remarks = request.form.get('remarks')
        

        raw_date_of_schedule = request.form.get('date_of_schedule')
        # Processing datetime
        sr.date_of_schedule = datetime.strptime(raw_date_of_schedule, "%Y-%m-%dT%H:%M")
        db.session.commit()
        return redirect(url_for('customer_dashboard', uid = uid, uname = uname))
    else:
        return render_template('update_sr_form.html', sr=sr, uname = uname, uid = uid)

# Close a SR
@app.route("/customer/close_sr/<sr_id>/<uid>/<uname>", methods = ['GET', 'POST'])
def close_sr(sr_id, uname, uid):
    sr = Service_request.query.filter_by(id = sr_id).first()
    sr.status = 'Closed'
    db.session.commit()
    return render_template('customer_review_form.html', sr = sr, uid = uid, uname = uname)

# Rating SP after closing a SR
@app.route("/customer/rate_sr/<sr_id>/<uid>/<uname>", methods = ['GET', 'POST'])
def rate_sr(sr_id, uname, uid):
    sr = Service_request.query.filter_by(id = sr_id).first()
    sp = Service_professional.query.filter_by(id = sr.sp_id).first()
    if request.method == 'POST':
        rater_id = sr.customer.id
        ratee_id = sr.service_professional.id
        review = request.form.get('review')
        rating = request.form.get('rating')
        flag_sp = request.form.get('flag_sp')
        if flag_sp == 'yes':
            flag_sp = 1
            sp.status = 'Flagged'
            db.session.commit()
        else:
            flag_sp = 0
        new_rating = Rating(sr_id = sr_id, rater_id=rater_id,ratee_id = ratee_id, review = review, rating = rating, flag_sp=flag_sp)
        db.session.add(new_rating)
        db.session.commit()

        # Updating avg_rating for customer
        # sp_rating = Rating.query.get([func.round(func.avg(rating.rating), 2)])
        sp_rating_list = list(Rating.query.filter_by(ratee_id = sp.id).all())
        sum_rating = 0
        c = 0
        for rate in sp_rating_list:
            if rate != None:
                sum_rating += rate.rating
                c+=1 
        avg_sp_rating = round((sum_rating/c),2)
        sp.avg_ratings = avg_sp_rating
        db.session.commit()
        return redirect(url_for('customer_dashboard', uid = uid, uname = uname))

### CUSTOMER SEARCH ###

@app.route("/customer/search/<uid>/<uname>",  methods= ['GET', 'POST'])
def customer_search(uname, uid):
    if request.method == 'POST':
        search_by = request.form.get('search_by') or None
        search_txt = request.form.get('search_txt')
        if search_by == 'service':
            if search_txt == '':
                service_professionals = Service_professional.query.all()
                # service_requests = Service_request.query.filter_by(customer_id = uid).all()
                return render_template('customer_search.html', service_professionals = service_professionals, uid = uid, uname=uname)
            else:
                service_professionals = Service_professional.query.filter(Service_professional.service_name.ilike(f"%{search_txt}%")).all()
                # service_requests = Service_request.query.filter(Service_requests.service.name.ilike(f"%{search_txt}%")).all()
                return render_template('customer_search.html', service_professionals = service_professionals, uid = uid, uname=uname)
        
        elif search_by == 'location':
            if search_txt == '':
                service_professionals = Service_professional.query.all()
                service_requests = Service_request.query.filter_by(customer_id = uid).all()
                return render_template('customer_search.html', service_professionals = service_professionals, service_requests = service_requests, uid = uid, uname=uname)
            else:
                service_professionals = Service_professional.query.filter(Service_professional.location.ilike(f"%{search_txt}%")).all()
                # service_requests = Service_request.query.filter(Service_request.service_professional.location.ilike(f"%{search_txt}%")).all()
                return render_template('customer_search.html', service_professionals = service_professionals, uid = uid, uname=uname)

    return redirect(url_for('customer_dashboard', uid = uid, uname=uname))

### CUSTOMER SUMMARY ###

@app.route("/customer/summary/<uid>/<uname>",  methods= ['GET', 'POST'])
def customer_summary(uid, uname):
    
    customer = Customer.query.filter_by(id=uid).first()
    empty_s = ['Requested','Assigned', 'Closed', 'Rejected']
    

    sr_list = list(Service_request.query.filter(Service_request.customer_id==uid).all())
    d = {}
    for sr in sr_list:
        d[sr.status] = 0
    for sr in sr_list:
        d[sr.status]+=1
    
    for key in d:
        if d[key] == 0:
            d.pop(key)
        else:
            empty_s.remove(key)
    count = list(d.values())
    status_li = list(d.keys())

    # plotting pie chart
    if d != {}:
        plt.clf()
        plt.pie(count, labels = status_li, shadow=True, autopct='%1.1f%%')
        plt.title("Service Requests Status Summary")
        plt.legend(title = 'Status')
        plt.savefig('./static/images/customer_summary1.jpeg')
    


#### Main thread error - the plot jus being developed from the system and not from the app, it is breeaking the context that the flask
# has set in, it is generating from the server machine not from  the client side
    # plotting histogram
    if customer.avg_ratings != None:
        x = customer.name
        y = customer.avg_ratings
        plt.clf()
        plt.bar(x, y, color='blue', width=0.5)
        plt.title(f"Average Ratings for {customer.name}")
        plt.xlabel(f"Customer: {customer.name}")
        plt.ylabel("Average Ratings")
        plt.savefig('static/images/customer_summary2.jpeg')
        
    return render_template('customer_summary.html', uname = uname, empty_s = empty_s, uid = uid)


##### SP CONTROLS #####

######################
#### SP DASHBOARD ####
######################

@app.route("/sp/<uid>/<uname>")
def sp_dashboard(uid, uname):
    open_service_requests = Service_request.query.filter_by(sp_id = uid, status = 'Requested').all() + Service_request.query.filter_by(sp_id = uid, status = 'Assigned').all()
    closed_service_requests = Service_request.query.filter_by(sp_id = uid, status = 'Closed').all() + Service_request.query.filter_by(sp_id = uid, status = 'Rejected').all()
    sp = Service_professional.query.filter_by(id = uid).first()
    return render_template('sp_dashboard.html', sp = sp, open_service_requests=open_service_requests, 
                           closed_service_requests=closed_service_requests, uname = uname, uid = uid)

## SP Response on SR ##
@app.route("/sp/accept/<sr_id>/<uid>/<uname>")
def sp_accept(sr_id, uid, uname):
    sr = Service_request.query.filter_by(id = sr_id).first()
    sr.status = 'Assigned'
    db.session.commit()
    return redirect(url_for('sp_dashboard', uid = uid, uname = uname))

@app.route("/sp/reject/<sr_id>/<uid>/<uname>")
def sp_reject(sr_id, uid, uname):
    sr = Service_request.query.filter_by(id = sr_id).first()
    sr.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('sp_dashboard', uid = uid, uname = uname))

@app.route("/sp/exit/<sr_id>/<uid>/<uname>")
def sp_exit(sr_id, uid, uname):
    sr = Service_request.query.filter_by(id = sr_id).first()
    sr.sp_exit = 1
    db.session.commit()
    return render_template('sp_review_form.html', sr = sr, uid = uid, uname = uname)

## SP rating customer ##

@app.route("/sp/rate_sr/<sr_id>/<uid>/<uname>", methods = ['GET', 'POST'])
def sp_rate_sr(sr_id, uname, uid):
    sr = Service_request.query.filter_by(id = sr_id).first()
    if request.method == 'POST':
        rating_obj = Rating.query.filter(Rating.sr_id == sr_id).first()
        customer = Customer.query.filter(Customer.id == sr.customer_id).first()
        rating_obj.sp_remarks = request.form.get('sp_review')
        rating_obj.sp_rating = request.form.get('sp_rating')
        flag_customer = request.form.get('flag_customer')
        if flag_customer == 'yes':
            flag_customer = 1
            customer.status = 'Flagged'
            db.session.commit()
        else:
            flag_customer = 0
        rating_obj.flag_customer = flag_customer
        db.session.commit()
        
        # Updating avg_rating for customer
        cust_rating_list = list(Rating.query.filter_by(rater_id = customer.id).all())
        sum_rating = 0
        c = 0
        for rate in cust_rating_list:
            if rate != None:
                sum_rating += rate.sp_rating
                c+=1 
        avg_cust_rating = round((sum_rating/c),2)
        customer.avg_ratings = avg_cust_rating
        db.session.commit()
        return redirect(url_for('sp_dashboard', uid = uid, uname = uname))
    return render_template('service_rating.html', sr = sr, uid = uid, uname = uname, reviewer = 'sp')

## Update profile
@app.route("/sp/profile/update/<uid>/<uname>", methods = ['GET', 'POST'])
def update_sp_profile(uname, uid):
    sp = Service_professional.query.filter_by(id = uid).first()
    if request.method == 'POST':
        updated_name = request.form.get('name') 
        updated_password = request.form.get('password')
        updated_location = request.form.get('location') 
        updated_pin_code = request.form.get('pin_code') 
        updated_contact_number = request.form.get('contact_number')
        updated_price = request.form.get('price')
        updated_avg_time = request.form.get('avg_time')
        updated_description = request.form.get('description')

        
        sp.name = updated_name
        sp.password = updated_password
        sp.location = updated_location
        sp.pin_code = updated_pin_code
        sp.contact_number = updated_contact_number
        sp.price = updated_price
        sp.avg_time = updated_avg_time
        sp.description = updated_description

        db.session.commit()
        #### ADMIN DASHBOARD ####
        return redirect(url_for('sp_dashboard', uname=sp.name, uid=uid))

    return render_template('sp_profile_update.html', uname = sp.name, uid = uid, sp = sp)

### SP SEARCH ###

@app.route("/sp/search/<uid>/<uname>",  methods= ['GET', 'POST'])
def sp_search(uname, uid):
    if request.method == 'POST':
        search_by = request.form.get('search_by') or None
        search_txt = request.form.get('search_txt')
        if search_by == 'date':
            if search_txt == '':
                service_requests = Service_request.query.filter_by(sp_id = uid).all()
                return render_template('sp_search.html', service_requests = service_requests, uid = uid, uname=uname)
            else:
                service_requests = Service_request.query.filter(Service_request.date_of_schedule.ilike(f"%{search_txt}%"), Service_request.sp_id == uid).all()
                return render_template('sp_search.html', service_requests = service_requests, uid = uid, uname=uname)
        
        elif search_by == 'status':
            if search_txt == '':
                service_requests = Service_request.query.filter_by(sp_id = uid).all()
                return render_template('sp_search.html', service_requests = service_requests, uid = uid, uname=uname)
            else:
                service_requests = Service_request.query.filter(Service_request.status.ilike(f"%{search_txt}%"), Service_request.sp_id == uid).all()
                # service_requests = Service_request.query.filter(Service_request.service_professional.location.ilike(f"%{search_txt}%")).all()
                return render_template('sp_search.html', service_requests = service_requests, uid = uid, uname=uname)

    return redirect(url_for('customer_dashboard', uid = uid, uname=uname))

#### SP SUMMARY ####

@app.route("/sp/summary/<uid>/<uname>",  methods= ['GET', 'POST'])
def sp_summary(uid, uname):
    
    sp = Service_professional.query.filter_by(id=uid).first()
    empty_s = ['Requested','Assigned', 'Closed', 'Rejected']
    
    sr_list = list(Service_request.query.filter(Service_request.sp_id==uid).all())
    d = {}
    for sr in sr_list:
        d[sr.status] = 0
    for sr in sr_list:
        d[sr.status]+=1
    
    for key in d:
        if d[key] == 0:
            d.pop(key)
        else:
            empty_s.remove(key)
    count = list(d.values())
    status_li = list(d.keys())

    # plotting pie chart
    if status_li != []:
        plt.clf()
        plt.pie(count, labels = status_li, shadow=True, autopct='%1.1f%%')
        plt.title("Service Requests Status Summary")
        plt.legend(title = 'Status')
        plt.savefig('./static/images/sp_summary1.jpeg')
    


#### Main thread error - the plot jus being developed from the system and not from the app, it is breeaking the context that the flask
# has set in, it is generating from the server machine not from  the client side
    # plotting histogram
    if sp.avg_ratings != None:
        x = sp.name
        y = sp.avg_ratings
        plt.clf()
        plt.bar(x, y, color='blue', width=0.5)
        plt.title(f"Average Ratings for {sp.name}")
        plt.xlabel("Service Professional")
        plt.ylabel("Average Ratings")
        plt.savefig('static/images/sp_summary2.jpeg')
    
    return render_template('sp_summary.html', uname = uname, empty_s = empty_s, uid = uid)