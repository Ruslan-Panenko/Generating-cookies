import sqlite3
from datetime import datetime, timedelta

DATABASE_PATH = '../cookie_data.db'

one_hour_ago = datetime.now() - timedelta(hours=1)

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Предполагается, что у вас есть колонка `creation_time` типа `DATETIME`
cursor.execute("DELETE FROM cookies WHERE created_at < ?", (one_hour_ago,))
conn.commit()
conn.close()
