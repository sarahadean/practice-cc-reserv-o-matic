from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, UniqueConstraint
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
import datetime

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Customer(db.Model, SerializerMixin):
    __tablename__ = "customers"

    serialize_rules = ('-customer_reservations.customer',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)

    customer_reservations = db.relationship('Reservation', back_populates='customer')
    location = association_proxy('customer_reservations', 'location')

    @validates('name', 'email')
    def validates_customer(self, key, input):
        if key == 'name':
            if not input or len(input) < 1:
                raise ValueError('Must input name')
            return input
        elif key == 'email':
            if not input or '@' not in input:
                raise ValueError('Valid Email required')
            elif Customer.query.filter(Customer.email==input).first():
                raise ValueError('Email must be unique')
            return input


class Location(db.Model, SerializerMixin):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    max_party_size = db.Column(db.Integer, nullable=False)

    location_reservations = db.relationship('Reservation', back_populates='location')

    @validates('name', 'max_party_size')
    def validates_location(self, key, input):
        if key == 'name':
            if not input:
                raise ValueError('Must input name')
            return input
        elif key == 'max_party_size':
            if not input:
                raise ValueError('Must input max party size') 
            return input             


class Reservation(db.Model, SerializerMixin):
    __tablename__ = "reservations"

    serialize_rules = ('-customer.customer_reservations', '-location.location_reservations')

    id = db.Column(db.Integer, primary_key=True)
    party_name = db.Column(db.String)
    party_size = db.Column(db.Integer)
    reservation_date = db.Column(db.Date, nullable=False)

    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))

    customer = db.relationship('Customer', back_populates='customer_reservations')
    location = db.relationship('Location', back_populates='location_reservations')

    @validates('reservation_date', 'party_name', 'customer_id', 'location_id')
    def validates_reservation(self, key, input):
        if key == 'reservation_date':
            if not input or not isinstance(input, datetime.date):
                raise ValueError('Must input date')
            return input     
        if key == 'party_name':
            if not input:
                raise ValueError('Must input party name')
            return input
        if key == 'customer_id':
            if not input:
                raise ValueError('Must input customer id')
            return input
        if key == 'location_id':
            if not input:
                raise ValueError('Must input customer id')
            return input
