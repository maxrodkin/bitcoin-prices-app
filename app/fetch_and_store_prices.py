# fetch_and_store_prices.py
import requests
import logging
from datetime import datetime, timedelta
from config import app, db, BitcoinPrice
from apscheduler.schedulers.background import BackgroundScheduler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_and_store_prices():
    with app.app_context():
        try:
            # Fetch Bitcoin price in USD
            response = requests.get('https://api.coindesk.com/v1/bpi/currentprice/USD.json')
            data = response.json()
            price_usd = data['bpi']['USD']['rate_float']

            # Fetch exchange rates for USD to EUR and USD to CZK
            exchange_rate_response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
            exchange_rate_data = exchange_rate_response.json()
            usd_to_eur = exchange_rate_data['rates']['EUR']
            usd_to_czk = exchange_rate_data['rates']['CZK']

            # Convert prices to EUR and CZK
            price_eur = price_usd * usd_to_eur
            price_czk = price_usd * usd_to_czk

            new_price = BitcoinPrice(price_usd=price_usd, price_eur=price_eur, price_czk=price_czk)
            db.session.add(new_price)
            db.session.commit()

            logging.info(f"Fetched and stored new prices: USD: {price_usd}, EUR: {price_eur}, CZK: {price_czk}")

        except Exception as e:
            logging.error(f"Error fetching or storing prices: {e}")

def cleanup_old_prices():
    with app.app_context():
        try:
            twelve_months_ago = datetime.now(pytz.utc) - timedelta(days=365)
            deleted_count = db.session.query(BitcoinPrice).filter(BitcoinPrice.timestamp < twelve_months_ago).delete()
            db.session.commit()
            
            logging.info(f"Deleted {deleted_count} old price records older than 12 months")

        except Exception as e:
            logging.error(f"Error cleaning up old prices: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_store_prices, 'interval', minutes=1)
scheduler.add_job(cleanup_old_prices, 'interval', days=1)
scheduler.start()

# Keep the script running to ensure the scheduler keeps working
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
