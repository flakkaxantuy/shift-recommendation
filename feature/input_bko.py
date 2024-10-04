import psycopg2
from psycopg2 import sql

DB_NAME = "paier"
DB_USER = "postgres"
DB_PASSWORD = "1"
DB_HOST = "localhost"
DB_PORT = "5432"

def insert_bko(tanggal, lokasi, shift, jumlah_personil, harga_satuan, satuan, event, personil):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        cur = conn.cursor()
        insert_query = sql.SQL(
            "INSERT INTO bko (tanggal, lokasi, shift, jumlah_personil, harga_satuan, satuan, event, personil) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"
        )
        cur.execute(insert_query, (tanggal, lokasi, shift, jumlah_personil, harga_satuan, satuan, event, personil))
        inserted_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return inserted_id

    except Exception as e:
        print(f"Error: {e}")
        return None

def fetch_all_bko():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        cur = conn.cursor()
        fetch_query = sql.SQL("SELECT * FROM bko")
        cur.execute(fetch_query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    except Exception as e:
        print(f"Error: {e}")
        return []



def delete_bko(id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        cur = conn.cursor()
        delete_query = sql.SQL("DELETE FROM bko WHERE id=%s")
        cur.execute(delete_query, (id,))
        conn.commit()
        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False