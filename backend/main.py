from fastapi import FastAPI
import sqlite3

DATABASE_PATH = "../cookie_data.db"

app = FastAPI()


@app.get("/")
def read_root():
    data = []
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cookies")
        rows = cursor.fetchall()
        for row in rows:
            data.append({
                'sessionid': row[1],
                'user_id': row[2],
                'lsd': row[3],
                'dtsg': row[4],
                'hs': row[5],
                'hsi': row[6],
                'c': row[7],
                'user_agent': row[8],
                'generated': row[9],
                'created_at': row[10]
            })
    return data
