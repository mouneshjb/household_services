# Data Models
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 1st Entity - customer
class Customer(db.Model):
    __tablename__ = 'customer' # If we do not define this, the model auto assigns name as lower case of class name
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True, nullable = False)
    name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    role = db.Column(db.Integer, default =1) # admin - 0, customer - 1
    date_of_signup = db.Column(db.DateTime, default = datetime.now) # NEED TO CONFIRM on type
    contact_number = db.Column(db.String, nullable = False)
    location = db.Column(db.String, nullable = False)
    pin_code = db.Column(db.Integer, nullable = False)
    status = db.Column(db.String, default = 'Active') # Active , Flagged ,  Blocked
    #Defining backreference to enable parent to have access to all the children 
    sr = db.relationship('Service_request', cascade = 'all, delete', backref = 'customer', lazy = True) 
    # customer.sr -> list of sr's under the customer
    # sr.customer -> customer object for that sr
    ratings = db.relationship('Rating', backref = 'customer', lazy = True)

# 2nd Entity - service_professional
class Service_professional(db.Model):
    __tablename__ = 'service_professional' # If we do not define this, the model auto assigns name as lower case of class name
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True, nullable = False)
    name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    role = db.Column(db.Integer, default =2)
    date_of_regn = db.Column(db.DateTime, default = datetime.now)
    doc_name = db.Column(db.String, nullable = False) ## TO BE UPDATED
    doc_data = db.Column(db.LargeBinary, nullable = False)
    service_name = db.Column(db.String, nullable = False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable = False)
    description = db.Column(db.String, nullable = False)
    price = db.Column(db.Integer, nullable = False)
    avg_time = db.Column(db.Float, nullable = False)
    exp_since = db.Column(db.Integer, nullable = False) # NEED TO CONFIRM on type
    location = db.Column(db.String, nullable = False)
    pin_code = db.Column(db.Integer, nullable = False)
    contact_number = db.Column(db.String, nullable = False)
    status = db.Column(db.String, default = 'Registered') # Registered - 0, Active - 1, Flagged - 2, Blocked - 3, Rejected - 4
    # avg_rating = db.Column(db.Integer, default = 0)
    #Defining backreference to enable parent to have access to all the children 
    sr = db.relationship('Service_request', backref = 'service_professional', lazy = True)
    ratings = db.relationship('Rating', cascade = 'all, delete', backref = 'service_professional', lazy = True)

# 3rd Entity - servie_request
class Service_request(db.Model):
    __tablename__ = 'service_request'
    id=db.Column(db.Integer,primary_key=True)
    customer_id=db.Column(db.Integer,db.ForeignKey('customer.id'), nullable = False)
    sp_id=db.Column(db.Integer,db.ForeignKey('service_professional.id'), nullable = False)
    date_of_request = db.Column(db.DateTime, default = datetime.now) # NEED TO CONFIRM on type
    service_id=db.Column(db.Integer,db.ForeignKey('service.id'), nullable = False)
    remarks = db.Column(db.String, nullable = False)
    date_of_schedule = db.Column(db.DateTime) # NEED TO CONFIRM on type
    date_of_completion = db.Column(db.DateTime, default = datetime.now)
    status = db.Column(db.String, default = 'Requested') # Requested - 0, Assigned - 1, Closed - 2
    sp_exit = db.Column(db.Integer, default = 0) # Not-exited - 0, Exited - 1
    ratings = db.relationship('Rating', backref = 'service_request', lazy = True)

# 4th Entity - rating
class Rating(db.Model):
    __tablename__ = 'rating'
    id=db.Column(db.Integer,primary_key=True)
    sr_id=db.Column(db.Integer,db.ForeignKey('service_request.id'), nullable = False)
    rater_id = db.Column(db.Integer,db.ForeignKey('customer.id'), nullable = False)
    ratee_id = db.Column(db.Integer,db.ForeignKey('service_professional.id'), nullable = False)
    review = db.Column(db.String)
    rating = db.Column(db.Integer)
    flag_sp = db.Column(db.Integer, default = 0) # Flagged - 1, not flagged - 0
    date_of_rating = db.Column(db.DateTime, default = datetime.now) # NEED TO CONFIRM on type
    sp_rating = db.Column(db.Integer)
    sp_remarks = db.Column(db.String)
    flag_customer = db.Column(db.Integer, default = 0) # Flagged - 1, not flagged - 0

# 5th Entity - service
class Service(db.Model):
    __tablename__ = 'service'
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String, nullable = False)
    base_price = db.Column(db.Integer, nullable = False)
    avg_time_req = db.Column(db.Float, nullable = False) # Time in hours
    description = db.Column(db.String, nullable = False)
    sp = db.relationship('Service_professional', cascade = "all, delete", backref = 'service', lazy = True)
    sr = db.relationship('Service_request', cascade = "all, delete", backref = 'service', lazy = True)