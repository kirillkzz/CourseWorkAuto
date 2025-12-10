import psycopg2
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'autotransport')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASSWORD', 'postgres')

def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            return conn
        except psycopg2.OperationalError as e:
            if conn: conn.close()
            time.sleep(2)
            retries -= 1
    print("Не вдалося підключитися до бази даних.")
    sys.exit(1)

def run_sql_file(cursor, filename):
    full_path = os.path.join(SCRIPT_DIR, filename)
    print(f"Виконую файл: {full_path}...")
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            sql_commands = f.read()
            cursor.execute(sql_commands)
        print(f"Файл {filename} успішно виконано.")
    except Exception as e:
        print(f"Помилка при виконанні {filename}: {e}")

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    run_sql_file(cur, 'sql/schema.sql')
    run_sql_file(cur, 'sql/seed.sql')
    conn.commit()
    cur.close()
    conn.close()
    print("Ініціалізація бази даних завершена.")

if __name__ == '__main__':
    init_db()