# Data Models
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 1st Entity - customer
class Customer(db.Model):
    __tablename__ = 'customer' # If we do not define this, the model auto assigns name as lower case of class name
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True, nullable = False)
    name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    role = db.Column(db.Integer, default =1)
    date_of_signup = db.Column(db.Datetime) # NEED TO CONFIRM on type
    contact_number = db.Column(db.Integer, nullable = False)
    location = db.Column(db.String, nullable = False)
    pin_code = db.Column(db.Integer, nullable = False)
    status = db.Column(db.Integer, default = 0) # Active - 0, Blocked - 1
    avg_rating = db.Column(db.Integer, default = 0)
    #Defining backreference to enable parent to have access to all the children 
    sr = db.relationship('Service_request', backref = 'customer', lazy = True) 

# 2nd Entity - service_professional
class Service_professional(db.Model):
    __tablename__ = 'service_professional' # If we do not define this, the model auto assigns name as lower case of class name
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True, nullable = False)
    name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    role = db.Column(db.Integer, default =1)
    date_of_regn = db.Column(db.Datetime)
    # document = db.Column(db.Integer, nullable = False) ## TO BE UPDATED
    service_name = db.Column(db.String, nullable = False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable = False)
    description = db.Column(db.String, nullable = False)
    price = db.Column(db.Integer, nullable = False)
    exp_since = db.Column(db.Integer) # NEED TO CONFIRM on type
    location = db.Column(db.String, nullable = False)
    pin_code = db.Column(db.Integer, nullable = False)
    contact_number = db.Column(db.Integer, nullable = False)
    status = db.Column(db.Integer, default = 0) # Registered - 0, Active - 1, Blocked - 2
    avg_rating = db.Column(db.Integer, default = 0)
    #Defining backreference to enable parent to have access to all the children 
    sr = db.relationship('Service_request', backref = 'service_professional', lazy = True)
    ratings = db.relationship('Rating', backref = 'service_professional', lazy = True)

# 3rd Entity - servie_request
class Service_request(db.Model):
    __tablename__ = 'service_request'
    id=db.Column(db.Integer,primary_key=True)
    customer_id=db.Column(db.Integer,db.ForeignKey('customer.id'), nullable = False)
    sp_id=db.Column(db.Integer,db.ForeignKey('service_professional.id'), nullable = False)
    date_of_request = db.Column(db.Datetime, nullable = False) # NEED TO CONFIRM on type
    service_id=db.Column(db.Integer,db.ForeignKey('service.id'), nullable = False)
    date_of_completion = db.Column(db.Datetime, nullable = False) # NEED TO CONFIRM on type
    status = db.Column(db.Integer, default = 0) # Requested - 0, Assigned - 1, Closed - 2
    sp_exit = db.Column(db.Integer, default = 0) # Not-exited - 0, Exited - 1
    ratings = db.relationship('Rating', backref = 'service_professional', lazy = True)

# 4th Entity - rating
class Rating(db.Model):
    __tablename__ = 'rating'
    id=db.Column(db.Integer,primary_key=True)
    sr_id=db.Column(db.Integer,db.ForeignKey('service_request.id'), nullable = False)
    review = db.Column(db.String)
    rating = db.Column(db.Integer)
    date = db.Column(db.Datetime, nullable = False) # NEED TO CONFIRM on type

# 5th Entity - service
class Service(db.Model):
    __tablename__ = 'service'
    id=db.Column(db.Integer,primary_key=True)
    sr_id=db.Column(db.Integer,db.ForeignKey('service_request.id'), nullable = False)
    name = db.Column(db.String, nullable = False)
    base_price = db.Column(db.Integer, nullable = False)
    avg_time_req = db.Column(db.Integer, nullable = False) # Time in hours
    description = db.Column(db.String, nullable = False)
    