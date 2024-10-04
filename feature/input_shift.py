import psycopg2
from psycopg2 import sql

DB_NAME = "paier"
DB_USER = "postgres"
DB_PASSWORD = "1"
DB_HOST = "localhost"
DB_PORT = "5432"

def insert_shift(nama, jabatan, lokasi_id, tanggal, hari, shift):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()

        insert_query = sql.SQL(
            "INSERT INTO schedule (nama, jabatan, lokasi_id, tanggal, hari, shift) VALUES (%s, %s, %s, %s, %s, %s)"
        )
        cur.execute(insert_query, (nama, jabatan, lokasi_id, tanggal, hari, shift))

        conn.commit()
        cur.close()
        conn.close()

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_all_shifts():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()

        cur.execute("""
            SELECT s.nama, s.jabatan, l.nama AS l.nama, s.tanggal, s.shift
            FROM schedule s
            INNER JOIN lokasi l ON s.lokasi_id = l.id
        """)
        shifts = cur.fetchall()
    
        cur.close()
        conn.close()

        return shifts
    except Exception as e:
        print(f"Error: {e}")
        return None

def delete_shift_by_id(shift_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()

        cur.execute("DELETE FROM schedule WHERE id = %s", (shift_id,))

        conn.commit()
        cur.close()
        conn.close()

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
