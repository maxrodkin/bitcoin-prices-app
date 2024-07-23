# config.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pytz
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/bitcoin'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this to a random secret key in production

db = SQLAlchemy(app)

class BitcoinPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(pytz.utc))
    price_usd = db.Column(db.Float, nullable=False)
    price_eur = db.Column(db.Float, nullable=False)
    price_czk = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()
