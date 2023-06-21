#!/usr/bin/env python3

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DATABASE = os.environ.get(
#     "DB_URI", f"sqlite://{os.path.join(BASE_DIR, 'instance/app.db')}"
# )

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from models import db, Customer, Location, Reservation
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    BASE_DIR, "instance/app.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def home():
    return ""

class Customers(Resource):
    def get(self):
        customer_list=[customer.to_dict(only=('id','name', 'email')) for customer in Customer.query.all()]
        return customer_list, 200
    
    def post(self):
        data = request.get_json()
        try:
            new_cust=Customer(
                name=data.get('name'),
                email=data.get('email')
            )
            db.session.add(new_cust)
            db.session.commit()
            return make_response(new_cust.to_dict(), 201)
        except:
            return {"error":"400: Validation error"}, 400
    
api.add_resource(Customers, '/customers')

class CustomersById(Resource):
    def get(self,id):
        try:
            customer = Customer.query.filter_by(id=id).first()
            return make_response(customer.to_dict(), 200)
        except:
            return {"error":"404: Customer not found"}, 404

api.add_resource(CustomersById, '/customers/<int:id>')

class Locations(Resource):
    def get(self):
        locations_list=[location.to_dict(only=('name', 'id', 'max_party_size')) for location in Location.query.all()]
        return make_response(locations_list, 200)

api.add_resource(Locations, '/locations')

class Reservations(Resource):
    def get(self):
        all_reservations = [ressy.to_dict() for ressy in Reservation.query.all()]
        return make_response(all_reservations, 200)
    
    def post(self):
        data = request.get_json()
        try:
            new_ressy=Reservation(
                reservation_date=datetime.datetime.strptime(data.get('reservation_date'), '%y-%m-$d').date(),
                customer_id=data.get('customer_id'),
                location_id=data.get('location_id'),
                party_size=data.get('party_size'),
                party_name=data.get('party_name')
            )
            db.session.add(new_ressy)
            db.session.commit()
            return new_ressy.to_dict(), 201
        except:
            return {"error":"400: Validation error"}, 400

api.add_resource(Reservations, '/reservations')

class ReservationsbyId(Resource):
    def patch(self, id):
        try:
            ressy = Reservation.query.filter_by(id=id).first()
            data = request.get_json()
            for attr in data:
                setattr(ressy, attr, data.get(attr))
            db.session.add(ressy)
            db.session.commit()
            return make_response(ressy.to_dict(), 200)
        except:
            return {"error":"404: Reservation not found"}

    def delete(self, id):
        try:
            reservation = Reservation.query.filter_by(id=id)
            db.session.delete()
            db.session.commit()
            return {}, 204
        except:
            return {"error":"Reservation not found"},404


api.add_resource(ReservationsbyId, '/reservations/<int:id>')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
