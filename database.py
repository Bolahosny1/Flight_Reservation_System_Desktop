import sqlite3
import os
from models import Flight, Booking, BookingStatus

DB_PATH = "flights.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Professional way to access by column name
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origin TEXT NOT NULL,
        destination TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        price REAL NOT NULL,
        capacity INTEGER NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_id INTEGER NOT NULL,
        passenger_name TEXT NOT NULL,
        status TEXT DEFAULT 'Confirmed',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (flight_id) REFERENCES flights (id)
    )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM flights")
    if cursor.fetchone()[0] == 0:
        flights_data = [
            ('New York', 'London', '2026-05-10 10:00', 500.0, 150),
            ('Paris', 'Tokyo', '2026-05-11 14:00', 850.0, 200),
            ('Dubai', 'New York', '2026-05-12 08:30', 700.0, 180),
            ('Berlin', 'Rome', '2026-05-13 19:00', 150.0, 100),
            ('Singapore', 'Sydney', '2026-05-14 22:00', 450.0, 160)
        ]
        cursor.executemany('''
        INSERT INTO flights (origin, destination, departure_time, price, capacity)
        VALUES (?, ?, ?, ?, ?)
        ''', flights_data)
        
    conn.commit()
    conn.close()

def search_flights(origin=None, destination=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Advanced query to include booking counts
    query = '''
    SELECT f.*, COALESCE(b.booked_count, 0) as booked_count
    FROM flights f
    LEFT JOIN (
        SELECT flight_id, COUNT(*) as booked_count 
        FROM bookings 
        WHERE status = 'Confirmed'
        GROUP BY flight_id
    ) b ON f.id = b.flight_id
    WHERE 1=1
    '''
    params = []
    
    if origin:
        query += " AND f.origin LIKE ?"
        params.append(f"%{origin}%")
    if destination:
        query += " AND f.destination LIKE ?"
        params.append(f"%{destination}%")
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [Flight(
        id=r['id'], 
        origin=r['origin'], 
        destination=r['destination'], 
        departure_time=r['departure_time'], 
        price=r['price'], 
        capacity=r['capacity'],
        booked_count=r['booked_count']
    ) for r in rows]

def create_booking(flight_id, passenger_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO bookings (flight_id, passenger_name, status)
    VALUES (?, ?, ?)
    ''', (flight_id, passenger_name, BookingStatus.CONFIRMED.value))
    conn.commit()
    conn.close()

def get_user_bookings(passenger_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT b.id, f.origin, f.destination, f.departure_time, f.price, b.status
    FROM bookings b
    JOIN flights f ON b.flight_id = f.id
    WHERE b.passenger_name = ?
    ''', (passenger_name,))
    rows = cursor.fetchall()
    conn.close()
    return rows # Returning rows as tuples for simple treeview insertion

def cancel_booking(booking_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status = ? WHERE id = ?", (BookingStatus.CANCELLED.value, booking_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Professional Database initialized.")
