import requests
from kafka import KafkaProducer
import json
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY = 'key_here'
SYMBOL = 'IBM'  # Example symbol, change as needed
INTERVAL = '5min'  # Can be 1min, 5min, 15min, 30min, 60min
ADJUSTED = 'true'  # Can be 'true' or 'false'
EXTENDED_HOURS = 'true'  # Can be 'true' or 'false'
OUTPUTSIZE = 'compact'  # Can be 'compact' or 'full'
DATATYPE = 'json'  # Can be 'json' or 'csv'

def fetch_intraday_stock_data():
    URL = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={SYMBOL}&interval={INTERVAL}&adjusted={ADJUSTED}&extended_hours={EXTENDED_HOURS}&outputsize={OUTPUTSIZE}&datatype={DATATYPE}&apikey={API_KEY}"
    response = requests.get(URL)
    logging.info("Fetched data from API")
    data = response.json()
    logging.info("API response: %s", data)
    return data['Time Series (' + INTERVAL + ')']  # Adjust based on the exact structure of the API response

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

while True:
    try:
        stock_data = fetch_intraday_stock_data()
        logging.info("Sending data to Kafka")
        future = producer.send('intraday_stock_data', value=stock_data)
        result = future.get(timeout=10)  # Synchronously wait for send to complete
        logging.info("Data sent to Kafka: %s", result)
        producer.flush()
    except Exception as e:
        logging.error("Error: %s", e)
    time.sleep(300)  # Adjust the frequency as needed, here set to every 5 minutes to match the INTERVAL
