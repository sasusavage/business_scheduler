from werkzeug.security import generate_password_hash
from config_real import get_db_connection

def insert_admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    username = "admin1"
    email = "avaelise51@gamil.com"
    password = "admin2021"
    password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    query = "INSERT INTO admin_users (username, email, password_hash) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, email, password_hash))
    conn.commit()
    conn.close()
    print("Default admin user created.")

if __name__ == "__main__":
    insert_admin()