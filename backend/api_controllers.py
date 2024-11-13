from flask_restful import Api, Resource, reqparse 
# Resource class does many backend things like how the app is connecting to  get function when we request via API, we have not called
# the get function anywhere. It is defined in the Resources
from flask import request
from .models import *
from datetime import datetime

api = Api()

parser = reqparse.RequestParser()

# Defined and notified API that the app needs a request body
# customer_id and sp_id taken from user in URL
parser.add_argument('description')
parser.add_argument('date_of_schedule')


class SRApi (Resource):
    def get(self, customer_id): # Retrieve SR details for a particular customer
        user = Customer.query.filter(Customer.id == customer_id).first()
        if user:
            user_sr = user.sr # list of objects
            user_srs = []
            
            for sr in user_sr: # sr_id, service_name, customer_pincode, description, date of schedule, status
                service_request = {}
                service_request['id'] = sr.id
                service_request['service_name'] = sr.service.name
                service_request['customer_pincode'] = sr.customer.pin_code
                service_request['description'] = sr.remarks
                service_request['date_of_schedule'] = str(sr.date_of_schedule)
                service_request['status'] = sr.status
                user_srs.append(service_request)
            return user_srs # list of dictionaries
        
        else:
            return {"message": "Customer ID not found"}, 404

    def post(self, customer_id, sp_id):
        sr_data = parser.parse_args()
        sp = Service_professional.query.filter_by(id = sp_id).first()
        user = Customer.query.filter(Customer.id == customer_id).first()
        if sp and user: 
            service_id = sp.service_id
            sch_date = sr_data['date_of_schedule']
            date_of_schedule = datetime.strptime(sch_date, '%Y-%m-%d %H:%M:%S')
            new_sr = Service_request(customer_id = customer_id, sp_id = sp_id, service_id = service_id, 
                                    remarks = sr_data['description'], 
                                    date_of_schedule = date_of_schedule)
            db.session.add(new_sr)
            db.session.commit()
            return {"message": "Created SR Successfully"}, 201
        else:
            return {"message": "Either customer ID or service professional ID is not found"}, 404

    def put(self, sr_id):
        sr = Service_request.query.filter_by(id = sr_id).first()
        if sr and (sr.status == 'Requested' or sr.status == 'Rejected'):
            sr_data = parser.parse_args()
            sr.remarks = sr_data['description']
            sch_date = sr_data['date_of_schedule']
            sr.date_of_schedule = datetime.strptime(sch_date, '%Y-%m-%d %H:%M:%S')
            db.session.commit()

            return {"message": "SR Updated Successfully"}, 200
        else:
            return {"message": "Service Request ID either not found or the request is in already 'Assigned' or 'Closed' status and cannot be edited. "}, 404 # Always, we need to return the data in json format only


    def delete(self, sr_id):
        sr = Service_request.query.filter_by(id = sr_id).first()
        if sr:
            db.session.delete(sr)
            db.session.commit()
        
            return {"message": "SR Deleted Successfully"}, 200 # Always, we need to return the data in json format only

        else:
            return {"message": "Service Request ID not found"}, 404 

api.add_resource(SRApi, '/api/service_requests/customer/<int:customer_id>', 
                 '/api/service_requests/customer/<int:customer_id>/sp/<int:sp_id>',
                 '/api/service_requests/sr/<int:sr_id>')





