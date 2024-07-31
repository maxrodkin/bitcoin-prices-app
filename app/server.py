# server.py
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from config import app, db, BitcoinPrice
from datetime import datetime, timedelta
import os

jwt = JWTManager(app)

# Retrieve username and password from environment variables
username = os.getenv('username', 'admin')
password = os.getenv('password', 'password')

@app.route('/ping', methods=['GET'])
def pong():
    return jsonify({'msg': 'pong OK'}), 200

@app.route('/login', methods=['POST'])
def login():
    if request.json.get('username') == username and request.json.get('password') == password:  # Change this to use a secure authentication mechanism in production
        access_token = create_access_token(identity={'username': username})
        return jsonify(access_token=access_token)
    return jsonify({'msg': 'Bad username or password'}), 401

@app.route('/current_price', methods=['GET'])
@jwt_required()
def current_price():
    latest_price = BitcoinPrice.query.order_by(BitcoinPrice.timestamp.desc()).first()
    if not latest_price:
        return jsonify({'msg': 'No data available'}), 404
    response = {
        'price_eur': latest_price.price_eur,
        'price_czk': latest_price.price_czk,
        'client_request_time': datetime.utcnow().isoformat(),
        'server_data_time': latest_price.timestamp.isoformat()
    }
    return jsonify(response)

def get_end_of_month(date):
    #eturn the last moment of the current month
    next_month = date.replace(day=28) + timedelta(days=4)  # this will always get the next month
    return next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)

@app.route('/average_price', methods=['GET'])
@jwt_required()
def average_price():
    period = request.args.get('period', 'daily')  # 'daily' or 'monthly'
    date_str = request.args.get('date', None)  # 'YYYY-MM-DD' for daily or 'YYYY-MM' for monthly
    if date_str:
        try:
            if period == 'monthly':
                start_date = datetime.strptime(date_str, '%Y-%m').replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = get_end_of_month(start_date)
            else:  # daily
                start_date = datetime.strptime(date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        except ValueError:
            return jsonify({'msg': 'Invalid date format'}), 400
    else:
        now = datetime.utcnow()
        if period == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = get_end_of_month(start_date)
        else:  # default to daily
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
    prices = BitcoinPrice.query.filter(BitcoinPrice.timestamp >= start_date, BitcoinPrice.timestamp < end_date).all()
    if not prices:
        return jsonify({'msg': 'No data available'}), 404

    avg_price_usd = sum([p.price_usd for p in prices]) / len(prices)
    avg_price_eur = sum([p.price_eur for p in prices]) / len(prices)
    avg_price_czk = sum([p.price_czk for p in prices]) / len(prices)

    response = {
        'average_price_eur': avg_price_eur,
        'average_price_czk': avg_price_czk,
        'client_request_time': datetime.utcnow().isoformat(),
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()        
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
