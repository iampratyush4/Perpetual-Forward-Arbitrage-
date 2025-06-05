import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class TimescaleDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        
    def write(self, table: str, data: dict):
        with self.conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {table} (timestamp, exchange, spot, perp, funding_rate)
                VALUES (%s, %s, %s, %s, %s)
            """, (data['timestamp'], data['exchange'], data['spot'], 
                  data['perp'], data['funding_rate']))
        self.conn.commit()