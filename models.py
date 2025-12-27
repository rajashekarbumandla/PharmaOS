from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    otp = db.Column(db.String(6), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    safety_stock = db.Column(db.Integer, nullable=False)
    current_stock = db.Column(db.Integer, nullable=False)


class Batch(db.Model):
    __tablename__ = "batches"

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id"), nullable=False)
    batch_number = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    medicine = db.relationship("Medicine", backref="batches")
